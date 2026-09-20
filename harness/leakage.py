from dataclasses import dataclass
import re
from typing import Iterable, Literal


Severity = Literal["error", "warning"]


@dataclass(frozen=True)
class LeakageFinding:
    severity: Severity
    pattern: str
    match: str
    source_label: str
    line: int
    excerpt: str
    start: int
    end: int


class LeakageDetectedError(RuntimeError):
    def __init__(self, findings: list[LeakageFinding]):
        self.findings = tuple(findings)
        sources = ", ".join(
            dict.fromkeys(finding.source_label for finding in findings)
        )
        super().__init__(
            f"Model-context leakage detected in: {sources}"
        )


ERROR_PATTERNS = (
    (
        "direct scorer reference",
        re.compile(
            r"\b(?:explicit|fuzzy)[\s_-]*\d+[\s_-]+scorer\b",
            re.IGNORECASE,
        ),
    ),
    ("Explicit-N label", re.compile(r"\bexplicit[\s_-]*\d+\b", re.IGNORECASE)),
    ("Fuzzy-N label", re.compile(r"\bfuzzy[\s_-]*\d+\b", re.IGNORECASE)),
    (
        "held-out task",
        re.compile(r"\bheld[\s_-]+out[\s_-]+task\b", re.IGNORECASE),
    ),
    (
        "held-out target",
        re.compile(r"\bheld[\s_-]+out[\s_-]+target\b", re.IGNORECASE),
    ),
    ("pilot spec", re.compile(r"\bpilot[\s_-]+spec\b", re.IGNORECASE)),
    (
        "expected solution",
        re.compile(r"\bexpected[\s_-]+solution\b", re.IGNORECASE),
    ),
    (
        "benchmark target",
        re.compile(r"\bbenchmark[\s_-]+target\b", re.IGNORECASE),
    ),
    (
        "experimental condition label",
        re.compile(r"\bcondition[\s_-]+[A-E]\b", re.IGNORECASE),
    ),
)

WARNING_PATTERNS = (
    ("benchmark", re.compile(r"\bbenchmarks?\b", re.IGNORECASE)),
    ("convention", re.compile(r"\bconventions?\b", re.IGNORECASE)),
    ("scorer", re.compile(r"\bscorers?\b", re.IGNORECASE)),
    ("pilot", re.compile(r"\bpilots?\b", re.IGNORECASE)),
)


def _excerpt(text: str, match: re.Match, line: int) -> str:
    line_start = text.rfind("\n", 0, match.start()) + 1
    line_end = text.find("\n", match.end())
    if line_end == -1:
        line_end = len(text)

    raw_excerpt = text[line_start:line_end]
    relative_match_start = match.start() - line_start
    window_start = max(0, relative_match_start - 60)
    raw_excerpt = raw_excerpt[window_start:window_start + 160]
    excerpt = re.sub(r"\s+", " ", raw_excerpt).strip()
    if window_start:
        excerpt = "..." + excerpt
    if len(excerpt) > 160:
        excerpt = excerpt[:157] + "..."

    return f"line {line}: {excerpt}"


def scan_leakage(
    sources: Iterable[tuple[str, str]],
) -> list[LeakageFinding]:
    """Scan labeled model-visible text and return deterministic findings."""
    findings: list[LeakageFinding] = []

    for source_label, text in sources:
        if not isinstance(source_label, str) or not isinstance(text, str):
            raise TypeError("Leakage sources must be (str label, str text) pairs.")

        matches = []
        error_spans = []

        for pattern_index, (pattern_name, pattern) in enumerate(ERROR_PATTERNS):
            for match in pattern.finditer(text):
                span = match.span()
                if any(
                    span[0] < existing[1] and existing[0] < span[1]
                    for existing in error_spans
                ):
                    continue

                error_spans.append(span)
                matches.append(
                    (
                        match.start(),
                        0,
                        pattern_index,
                        "error",
                        pattern_name,
                        match,
                    )
                )

        for pattern_index, (pattern_name, pattern) in enumerate(WARNING_PATTERNS):
            for match in pattern.finditer(text):
                span = match.span()
                if any(
                    span[0] < error_span[1] and error_span[0] < span[1]
                    for error_span in error_spans
                ):
                    continue

                matches.append(
                    (match.start(), 1, pattern_index, "warning", pattern_name, match)
                )

        for _, _, _, severity, pattern_name, match in sorted(matches):
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                LeakageFinding(
                    severity=severity,
                    pattern=pattern_name,
                    match=match.group(0),
                    source_label=source_label,
                    line=line,
                    excerpt=_excerpt(text, match, line),
                    start=match.start(),
                    end=match.end(),
                )
            )

    return findings
