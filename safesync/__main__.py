"""Run with python -m safesync preview|run CONFIG.json."""

import argparse
import json
import sys

from .application import load_config, preview, run


def main(argv=None):
    parser = argparse.ArgumentParser(description="Preview or run one-way local folder synchronization")
    parser.add_argument("command", choices=("preview", "run"))
    parser.add_argument("config")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "preview":
            plan = preview(config)
            print(json.dumps({"actions": [{"type": a.kind.value, "path": a.path}
                                           for a in plan.actions]}, indent=2))
            return 0
        report = run(config)
        print(json.dumps(report.as_dict(), indent=2))
        return 1 if report.failed else 0
    except (OSError, ValueError, TypeError) as error:
        print(f"safesync: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
