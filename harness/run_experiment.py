from pathlib import Path
import json
import sys

from harness.context import build_context
from harness.inference import generate
from harness.results import save_result
from harness.workspace import create_workspace, run_tests
from harness.scorers.explicit_1 import score_explicit_1
from harness.scorers.explicit_2 import score_explicit_2
from harness.scorers.explicit_3 import score_explicit_3
from harness.scorers.fuzzy_1 import score_fuzzy_1


BASE_REPO = Path("taskflow_base")


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


def load_json_file(path_string: str):
    path = Path(path_string)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return json.loads(
        path.read_text(encoding="utf-8")
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

    system_prompt = """
You are modifying an existing Python repository.

Study the supplied repository files and follow the patterns already
demonstrated by the codebase.

Return ONLY the complete replacement contents of the requested target file.

Do not use Markdown fences.
Do not explain your answer.
""".strip()

    # -----------------------------
    # Base task prompt
    # -----------------------------

    user_prompt = f"""
TASK:
{config["task"]}

TARGET FILE:
{config["target_file"]}

REPOSITORY CONTEXT:

{context}
""".strip()

    # -----------------------------
    # Condition B: episodic memory
    # -----------------------------

    if memory is not None:
        memory_context = f"""
PREVIOUS DEVELOPMENT EXPERIENCE:

Previous task:
{memory["previous_task"]}

Initial implementation:
{memory["rejected_code"]}

Developer's corrected implementation:
{memory["developer_edit"]}
""".strip()

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

    clean_generation = extract_code(
        generation
    )

    # -----------------------------
    # Apply generated code
    # -----------------------------

    target = workspace / config["target_file"]

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
        "target_file": config["target_file"],
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

        "original_target": original,
        "raw_generation": generation,
        "applied_generation": clean_generation,

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

    result_path = save_result(result)

    # -----------------------------
    # Console summary
    # -----------------------------

    print()
    print("Generation saved and applied.")
    print(f"Result: {result_path}")
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

def score_convention(experiment: str, workspace: Path) -> dict:
    scorers = {
    "explicit_1": score_explicit_1,
    "explicit_2": score_explicit_2,
    "explicit_3": score_explicit_3,
    "fuzzy_1": score_fuzzy_1,
}

    if experiment not in scorers:
        raise ValueError(
            f"No scorer registered for experiment: {experiment}"
        )

    return scorers[experiment](workspace)

if __name__ == "__main__":
    main()