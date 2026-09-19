from pathlib import Path
from datetime import datetime, timezone
import json


def save_result(data: dict) -> Path:
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    experiment = data["experiment"]
    condition = data["condition"]

    path = results_dir / f"{experiment}_{condition}_{timestamp}.json"

    path.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    return path