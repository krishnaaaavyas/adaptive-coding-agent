from pathlib import Path
import json
import re
import sys

from harness.context import build_context
from harness.inference import generate
from harness.results import save_result
from harness.workspace import create_workspace, run_tests
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

def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python -m harness.run_experiment "
            "experiments/<experiment>.json"
        )
        raise SystemExit(1)

    config_path = Path(sys.argv[1])

    config = json.loads(
        config_path.read_text(encoding="utf-8")
    )
    get_scorer(config["experiment"])
    target_files, multi_file = get_target_files(config)

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

    user_prompt = f"""
TASK:
{config["task"]}

{target_description}

REPOSITORY CONTEXT:

{context}
""".strip()

    # -----------------------------
    # Condition B: episodic memory
    # -----------------------------

    if memory is not None:
        memory_context = render_memory(memory)
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
    print("Generating...")

    generation = generate(
        [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
    )

    # -----------------------------
    # Apply generated code
    # -----------------------------

    if multi_file:
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

    # -----------------------------
    # Verification
    # -----------------------------

    test_result = run_tests(workspace)

    convention_result = score_convention(
        config["experiment"],
        workspace,
    )
    overall_success = (
    test_result["passed"]
    and convention_result["passed"]
) 

    # -----------------------------
    # Save experiment evidence
    # -----------------------------

    result = {
        "experiment": config["experiment"],
        "condition": config["condition"],
        "model": config["model"],
        "workspace": str(workspace),
        "context_files": config["context_files"],
        "task": config["task"],
        "overall_success": overall_success,

        "memory_file": config.get(
            "memory_file"
        ),
        "memory": memory,

        "rule_file": config.get(
            "rule_file"
        ),
        "rule": rule,

        "system_prompt": system_prompt,
        "user_prompt": user_prompt,

        "raw_generation": generation,

        "tests_passed": test_result["passed"],
        "test_returncode": test_result[
            "returncode"
        ],
        "test_stdout": test_result["stdout"],
        "test_stderr": test_result["stderr"],

        "convention_passed": convention_result[
            "passed"
        ],
        "convention_result": convention_result,
    }

    if multi_file:
        result.update(
            {
                "target_files": target_files,
                "original_targets": originals,
                "applied_generations": applied_generations,
            }
        )
    else:
        result.update(
            {
                "target_file": target_files[0],
                "original_target": original,
                "applied_generation": clean_generation,
            }
        )

    result_path = save_result(result)

    # -----------------------------
    # Console summary
    # -----------------------------

    print()
    print("Generation saved and applied.")
    print(f"Result: {result_path}")
    if multi_file:
        print("Targets:")
        for relative_path in target_files:
            print(f"  {_workspace_target(workspace, relative_path)}")
    else:
        print(f"Target: {target}")
    print(f"Overall success: {overall_success}")
    print(
        f"Tests passed: "
        f"{test_result['passed']}"
    )
    print(
        f"Convention passed: "
        f"{convention_result['passed']}"
    )
    print(
        f"Convention reason: "
        f"{convention_result['reason']}"
    )

    if test_result["stdout"]:
        print(test_result["stdout"])

    if test_result["stderr"]:
        print(test_result["stderr"])

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
    scorers = {
    "explicit_1": score_explicit_1,
    "explicit_2": score_explicit_2,
    "explicit_3": score_explicit_3,
    "fuzzy_1": score_fuzzy_1,
    "fuzzy_2": score_fuzzy_2,
}

    if experiment not in scorers:
        raise ValueError(
            f"No scorer registered for experiment: {experiment}"
        )

    return scorers[experiment](workspace)

if __name__ == "__main__":
    main()
