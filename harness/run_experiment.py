from harness import workspace
from pathlib import Path
import json
import sys

from harness.context import build_context
from harness.inference import generate
from harness.results import save_result
from harness.workspace import create_workspace, run_tests


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

    workspace = create_workspace(BASE_REPO)

    context = build_context(
        workspace,
        config["context_files"],
    )

    system_prompt = """
You are modifying an existing Python repository.

Study the supplied repository files and follow the patterns already
demonstrated by the codebase.

Return ONLY the complete replacement contents of the requested target file.

Do not use Markdown fences.
Do not explain your answer.
""".strip()

    user_prompt = f"""
TASK:
{config["task"]}

TARGET FILE:
{config["target_file"]}

REPOSITORY CONTEXT:

{context}
""".strip()

    print(f"Experiment: {config['experiment']}")
    print(f"Condition:  {config['condition']}")
    print(f"Workspace:  {workspace}")
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

clean_generation = generation.strip()

if clean_generation.startswith("```"):
    lines = clean_generation.splitlines()

    if lines[0].startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    clean_generation = "\n".join(lines).strip()

    target = workspace / config["target_file"]

    # Preserve the original before modifying the workspace.
    original = target.read_text(encoding="utf-8")

    target.write_text(
    clean_generation + "\n",
    encoding="utf-8",
    )
    test_result = run_tests(workspace)

    result = {
        "experiment": config["experiment"],
        "condition": config["condition"],
        "model": config["model"],
        "workspace": str(workspace),
        "context_files": config["context_files"],
        "target_file": config["target_file"],
        "task": config["task"],
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "original_target": original,
        "raw_generation": generation,
        "tests_passed": test_result["passed"],
        "test_returncode": test_result["returncode"],
        "test_stdout": test_result["stdout"],
        "test_stderr": test_result["stderr"],
        "convention_passed": None,
    }

    result_path = save_result(result)

    print()
    print("Generation saved and applied.")
    print(f"Result: {result_path}")
    print(f"Target: {target}")
    print(f"Tests passed: {test_result['passed']}")

    if test_result["stdout"]:
        print(test_result["stdout"])

    if test_result["stderr"]:
        print(test_result["stderr"])


if __name__ == "__main__":
    main()