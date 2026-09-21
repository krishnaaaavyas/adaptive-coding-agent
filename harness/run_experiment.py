from pathlib import Path
import json
import re
import sys

from harness.context import build_context
from harness.inference import generate
from harness.leakage import LeakageDetectedError, scan_leakage
from harness.results import save_result
from harness.workspace import create_workspace
from harness.evaluation import (
    TARGET_DIRECTORY, artifact_fingerprints, error_info, evaluate, finalize,
    fingerprints, new_evaluation, target_source,
)
from harness.scorers.explicit_1 import score_explicit_1
from harness.scorers.explicit_2 import score_explicit_2
from harness.scorers.explicit_3 import score_explicit_3
from harness.scorers.fuzzy_1 import score_fuzzy_1
from harness.scorers.fuzzy_2 import score_fuzzy_2
from harness.scorers.fuzzy_3 import score_fuzzy_3



BASE_REPO = Path("taskflow_base")
FILE_HEADER = re.compile(r"^=== FILE: (.+) ===$")


def extract_code(generation: str) -> str:
    text = generation.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return text


def _validate_relative_target(relative_path: str) -> None:
    if not isinstance(relative_path, str) or not relative_path:
        raise ValueError("Target file paths must be non-empty strings.")

    # Check both path syntaxes so output cannot escape a workspace even when
    # an experiment is moved between Windows and POSIX hosts.
    normalized = relative_path.replace("\\", "/")
    parts = normalized.split("/")

    if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        raise ValueError(f"Target file path must be relative: {relative_path}")

    if ".." in parts:
        raise ValueError(
            f"Target file path cannot contain '..': {relative_path}"
        )


def get_target_files(config: dict) -> tuple[list[str], bool]:
    has_target_file = "target_file" in config
    has_target_files = "target_files" in config

    if has_target_file == has_target_files:
        raise ValueError(
            "Experiment config must define exactly one of "
            "'target_file' or 'target_files'."
        )

    if has_target_file:
        targets = [config["target_file"]]
        multi_file = False
    else:
        targets = config["target_files"]
        multi_file = True

        if not isinstance(targets, list) or not targets:
            raise ValueError("'target_files' must be a non-empty list.")

    for target in targets:
        _validate_relative_target(target)

    if len(set(targets)) != len(targets):
        raise ValueError("Experiment target files must not contain duplicates.")

    return targets, multi_file


def parse_multi_file_generation(
    generation: str,
    requested_targets: list[str],
) -> dict[str, str]:
    for target in requested_targets:
        _validate_relative_target(target)

    if len(set(requested_targets)) != len(requested_targets):
        raise ValueError("Requested target files must not contain duplicates.")

    sections: dict[str, str] = {}
    current_path = None
    content_lines: list[str] = []

    for line in generation.splitlines(keepends=True):
        header_text = line.rstrip("\r\n")
        match = FILE_HEADER.fullmatch(header_text)

        if match:
            if current_path is not None:
                sections[current_path] = extract_code("".join(content_lines))

            section_path = match.group(1)
            _validate_relative_target(section_path)

            if section_path not in requested_targets:
                raise ValueError(f"Unexpected file section: {section_path}")

            if section_path in sections or section_path == current_path:
                raise ValueError(f"Duplicate file section: {section_path}")

            current_path = section_path
            content_lines = []
            continue

        if header_text.startswith("=== FILE"):
            raise ValueError(f"Malformed file header: {header_text}")

        if current_path is None:
            raise ValueError(
                "Multi-file generation must begin with an exact file header."
            )

        content_lines.append(line)

    if current_path is not None:
        sections[current_path] = extract_code("".join(content_lines))

    missing = [target for target in requested_targets if target not in sections]
    if missing:
        raise ValueError(
            "Missing requested file section(s): " + ", ".join(missing)
        )

    return sections


def _workspace_target(workspace: Path, relative_path: str) -> Path:
    _validate_relative_target(relative_path)
    workspace_root = workspace.resolve()
    path_parts = relative_path.replace("\\", "/").split("/")
    target = (workspace / Path(*path_parts)).resolve()

    if not target.is_relative_to(workspace_root):
        raise ValueError(f"Target file is outside workspace: {relative_path}")

    return target


def apply_multi_file_generation(
    workspace: Path,
    requested_targets: list[str],
    generation: str,
) -> tuple[dict[str, str | None], dict[str, str]]:
    # Parse and validate the complete response, including every destination,
    # before performing any filesystem mutation.
    parsed = parse_multi_file_generation(generation, requested_targets)
    destinations = {
        relative_path: _workspace_target(workspace, relative_path)
        for relative_path in requested_targets
    }
    originals = {
        relative_path: (
            destination.read_text(encoding="utf-8")
            if destination.exists()
            else None
        )
        for relative_path, destination in destinations.items()
    }

    for relative_path in requested_targets:
        destination = destinations[relative_path]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(parsed[relative_path], encoding="utf-8")

    return originals, parsed


def load_json_file(path_string: str):
    path = Path(path_string)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return json.loads(
        path.read_text(encoding="utf-8")
    )

def render_memory(memory: dict) -> str:
    memory_type = memory.get("type")

    if memory_type == "developer_correction":
        return f"""
PREVIOUS DEVELOPMENT EXPERIENCE:

Previous task:
{memory["previous_task"]}

Initial implementation:
{memory["rejected_code"]}

Developer's corrected implementation:
{memory["developer_edit"]}
""".strip()

    if memory_type == "repository_experience":
        sections = []

        for index, example in enumerate(
            memory["examples"],
            start=1,
        ):
            sections.append(
                f"""
Previous example {index}:

Task:
{example["task"]}

Implementation:
{example["implementation"]}
""".strip()
            )

        return (
            "PREVIOUS DEVELOPMENT EXPERIENCE:\n\n"
            + "\n\n".join(sections)
        )

    raise ValueError(
        f"Unsupported memory type: {memory_type}"
    )


def generate_with_preflight(
    messages: list[dict],
    sources: list[tuple[str, str]],
):
    findings = []
    covered_message_findings = set()

    for source_label, source_text in sources:
        source_findings = scan_leakage([(source_label, source_text)])
        findings.extend(source_findings)

        if not source_text:
            continue

        for message_index, message in enumerate(messages):
            content = message["content"]
            offset = content.find(source_text)

            while offset != -1:
                for finding in source_findings:
                    covered_message_findings.add(
                        (
                            message_index,
                            offset + finding.start,
                            offset + finding.end,
                            finding.severity,
                            finding.pattern,
                        )
                    )
                offset = content.find(source_text, offset + 1)

    for message_index, message in enumerate(messages):
        role = message.get("role", "unknown")
        message_label = f"message[{message_index}] ({role})"
        message_findings = scan_leakage(
            [(message_label, message["content"])]
        )

        for finding in message_findings:
            key = (
                message_index,
                finding.start,
                finding.end,
                finding.severity,
                finding.pattern,
            )
            if key not in covered_message_findings:
                findings.append(finding)

    errors = [finding for finding in findings if finding.severity == "error"]

    for finding in findings:
        if finding.severity == "warning":
            print(
                "Leakage preflight warning: "
                f"{finding.source_label}: {finding.pattern} "
                f"({finding.excerpt})"
            )

    if errors:
        print("Model-context leakage detected; inference aborted.")
        for finding in errors:
            print(
                f"  {finding.source_label}: {finding.pattern} "
                f"[{finding.match}] ({finding.excerpt})"
            )
        raise LeakageDetectedError(errors)

    print("Generating...")
    return generate(messages)

def _execute(config, config_path, result):
    target_files, multi_file = get_target_files(config)
    source = target_source(config, config_path, BASE_REPO)
    result["target_tests"] = {"source": str(source)}
    for name in config["context_files"]:
        _workspace_target(BASE_REPO, name)
    for name in target_files:
        destination = _workspace_target(BASE_REPO, name)
        if destination.is_relative_to((BASE_REPO / TARGET_DIRECTORY).resolve()):
            raise ValueError("Generated targets cannot occupy the private evaluator directory")

    # -----------------------------
    # Load adaptation information
    # -----------------------------

    memory = None
    rule = None

    if "memory_file" in config:
        memory = load_json_file(
            config["memory_file"]
        )

    if "rule_file" in config:
        rule = load_json_file(
            config["rule_file"]
        )

    # Prevent accidental condition contamination.
    if memory is not None and rule is not None:
        raise ValueError(
            "Experiment cannot load both memory and rule "
            "for A/B/C comparison."
        )

    # -----------------------------
    # Create isolated workspace
    # -----------------------------

    workspace = create_workspace(BASE_REPO)
    result["workspace"] = str(workspace)
    if (workspace / TARGET_DIRECTORY).exists():
        raise ValueError("Private target-test directory already exists before inference")
    if source.is_relative_to(workspace.resolve()):
        raise ValueError("Target tests cannot be inside the generated workspace")
    before = fingerprints(workspace)
    result["evaluation"]["regression"]["fingerprints"] = before

    context = build_context(
        workspace,
        config["context_files"],
    )

    # -----------------------------
    # Base system prompt
    # -----------------------------

    single_file_system_prompt = """
You are modifying an existing Python repository.

Study the supplied repository files and follow the patterns already
demonstrated by the codebase.

Return ONLY the complete replacement contents of the requested target file.

Do not use Markdown fences.
Do not explain your answer.
""".strip()

    if multi_file:
        requested_headers = "\n".join(
            f"=== FILE: {target} ==="
            for target in target_files
        )
        system_prompt = f"""
You are modifying an existing Python repository.

Study the supplied repository files and follow the patterns already
demonstrated by the codebase.

Return ONLY the complete replacement contents of every requested target file.
Use exactly one section for each requested file, with these exact headers:

{requested_headers}

Place each file's complete contents immediately after its header.
Do not use Markdown fences.
Do not explain your answer.
""".strip()
    else:
        system_prompt = single_file_system_prompt

    # -----------------------------
    # Base task prompt
    # -----------------------------

    if multi_file:
        target_description = "TARGET FILES:\n" + "\n".join(target_files)
    else:
        target_description = f"TARGET FILE:\n{target_files[0]}"

    task_prompt = f"""
TASK:
{config["task"]}

{target_description}

REPOSITORY CONTEXT:
""".strip()
    user_prompt = f"{task_prompt}\n\n{context}"
    model_sources = [
        ("system prompt", system_prompt),
        ("task prompt", task_prompt),
        ("repository context", context),
    ]

    # -----------------------------
    # Condition B: episodic memory
    # -----------------------------

    if memory is not None:
        memory_context = render_memory(memory)
        model_sources.append(("memory", memory_context))
        user_prompt = (
            f"{memory_context}\n\n"
            f"{user_prompt}"
        )

    # -----------------------------
    # Condition C: confirmed rule
    # -----------------------------

    if rule is not None:
        rule_context = f"""
        CONFIRMED REPOSITORY RULE:

        {rule["rule"]}
        """.strip()
        model_sources.append(("rule", rule_context))

        user_prompt = (
            f"{rule_context}\n\n"
            f"{user_prompt}"
        )

    # -----------------------------
    # Run model
    # -----------------------------

    print(f"Experiment: {config['experiment']}")
    print(f"Condition:  {config['condition']}")
    print(f"Workspace:  {workspace}")
    print(f"Memory loaded: {memory is not None}")
    print(f"Rule loaded: {rule is not None}")

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    result.update(memory=memory, rule=rule, system_prompt=system_prompt,
                  user_prompt=user_prompt)
    generation = generate_with_preflight(messages, model_sources)
    result["raw_generation"] = generation

    # -----------------------------
    # Apply generated code
    # -----------------------------

    if multi_file:
        try:
            parse_multi_file_generation(generation, target_files)
        except ValueError as exc:
            # A malformed model response is not an evaluator malfunction.
            result["model_output_error"] = str(exc)
            result["original_targets"] = {
                name: (_workspace_target(workspace, name).read_text(encoding="utf-8")
                       if _workspace_target(workspace, name).exists() else None)
                for name in target_files
            }
            result["applied_generations"] = {}
            evaluate(workspace, source, before, [],
                     lambda root: score_convention(config["experiment"], root),
                     result["evaluation"])
            target_evaluation = result["evaluation"]["target"]
            if target_evaluation["status"] == "completed":
                target_evaluation.update(passed=False, model_output_error=str(exc))
            return
        originals, applied_generations = apply_multi_file_generation(
            workspace,
            target_files,
            generation,
        )
        target = None
        original = None
        clean_generation = None
    else:
        clean_generation = extract_code(
            generation
        )
        target = _workspace_target(workspace, target_files[0])

        if target.exists():
            original = target.read_text(
                encoding="utf-8"
            )
        else:
            original = None
            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        target.write_text(
            clean_generation + "\n",
            encoding="utf-8",
        )

    if multi_file:
        result.update(original_targets=originals, applied_generations=applied_generations)
    else:
        result.update(original_target=original, applied_generation=clean_generation)
    artifact_before = artifact_fingerprints(workspace)
    result["evaluation"]["artifact"]["fingerprints"] = artifact_before
    evaluate(workspace, source, before, target_files,
             lambda root: score_convention(config["experiment"], root),
             result["evaluation"], artifact_before)


def run_experiment(config_path: Path) -> dict:
    """Execute and persist one v2 run, including infrastructure-invalid attempts."""
    config_path = Path(config_path)
    result = {
        "evaluation_protocol": "v2", "run_status": "invalid_infrastructure",
        "experiment": config_path.stem, "condition": "unknown",
        "config_path": str(config_path), "evaluation": new_evaluation(),
        "errors": [],
    }
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("Experiment configuration must be an object")
        result["config"] = config
        for field in ("experiment", "condition", "model", "context_files", "task",
                      "target_file", "target_files", "memory_file", "rule_file"):
            if field in config:
                result[field] = config[field]
        _execute(config, config_path, result)
    except LeakageDetectedError as exc:
        # Preserve Step-2's exception and fail-fast diagnostics after recording it.
        result["errors"].append(error_info("leakage_preflight", exc))
        finalize(result)
        save_result(result)
        raise
    except Exception as exc:
        result["errors"].append(error_info("execution", exc))
    finalize(result)
    path = save_result(result)
    print(f"Result: {path}")
    print(f"Run status: {result['run_status']}")
    print(f"Overall success: {result['overall_success']}")
    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m harness.run_experiment experiments/<experiment>.json")
        raise SystemExit(1)
    result = run_experiment(Path(sys.argv[1]))
    if result["run_status"] != "valid":
        raise SystemExit(2)


def get_scorer(experiment: str):
    scorers = {
        "explicit_1": score_explicit_1,
        "explicit_2": score_explicit_2,
        "explicit_3": score_explicit_3,
        "fuzzy_1": score_fuzzy_1,
        "fuzzy_2": score_fuzzy_2,
        "fuzzy_3": score_fuzzy_3,
    }

    if experiment not in scorers:
        raise ValueError(
            f"No scorer registered for experiment: {experiment}"
        )

    return scorers[experiment]

def score_convention(experiment: str, workspace: Path) -> dict:
    return get_scorer(experiment)(workspace)


if __name__ == "__main__":
    main()
