from pathlib import Path
from datetime import datetime, timezone
import json
import re
import uuid


def save_result(data: dict) -> Path:
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    experiment = re.sub(r"[^A-Za-z0-9_-]", "_", str(data["experiment"]))
    condition = re.sub(r"[^A-Za-z0-9_-]", "_", str(data["condition"]))

    path = results_dir / f"{experiment}_{condition}_{timestamp}_{uuid.uuid4().hex}.json"

    with path.open("x", encoding="utf-8") as output:
        json.dump(data, output, indent=2)

    return path
