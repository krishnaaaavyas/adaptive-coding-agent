"""Shared result contract for deterministic convention scorers."""


def criterion(identifier: str, passed: bool, reason: str) -> dict:
    if not identifier or not isinstance(identifier, str):
        raise ValueError("Criterion id must be a nonempty string")
    if type(passed) is not bool:
        raise TypeError("Criterion passed value must be a boolean")
    if not reason or not isinstance(reason, str):
        raise ValueError("Criterion reason must be a nonempty string")
    return {"id": identifier, "passed": passed, "reason": reason}


def scorer_result(
    scorer_version: str,
    mandatory: list[dict],
    diagnostics: list[dict],
) -> dict:
    """Build a result where diagnostics can never compensate for requirements."""
    if not scorer_version or not isinstance(scorer_version, str):
        raise ValueError("Scorer version must be a nonempty string")
    if not mandatory:
        raise ValueError("A scorer must define at least one mandatory requirement")

    identifiers = []
    for item in [*mandatory, *diagnostics]:
        if set(item) != {"id", "passed", "reason"}:
            raise ValueError("Criteria must contain exactly id, passed, and reason")
        if type(item["passed"]) is not bool:
            raise TypeError("Criterion passed value must be a boolean")
        identifiers.append(item["id"])
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Criterion ids must be unique within a scorer result")

    passed = all(item["passed"] for item in mandatory)
    count = sum(item["passed"] for item in mandatory)
    return {
        "passed": passed,
        "scorer_version": scorer_version,
        "mandatory": mandatory,
        "diagnostics": diagnostics,
        "reason": (
            f"{scorer_version}: {count}/{len(mandatory)} mandatory "
            "requirements passed."
        ),
    }
