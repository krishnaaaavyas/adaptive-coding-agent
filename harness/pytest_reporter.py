"""Private subprocess plugin: machine-readable pytest outcomes, not stdout parsing."""

import json
import os
from pathlib import Path
import sys

import pytest


REPORT = {"reports": [], "internal_errors": [], "finished": False}


def _exception_paths(exc):
    paths = set()
    seen = set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        traceback = exc.__traceback__
        while traceback is not None:
            paths.add(str(Path(traceback.tb_frame.f_code.co_filename).resolve()))
            traceback = traceback.tb_next
        if isinstance(exc, SyntaxError) and exc.filename:
            paths.add(str(Path(exc.filename).resolve()))
        if isinstance(exc, ImportError) and exc.path:
            paths.add(str(Path(exc.path).resolve()))
        if isinstance(exc, AttributeError):
            obj = getattr(exc, "obj", None)
            module = obj if hasattr(obj, "__file__") else sys.modules.get(
                getattr(type(obj), "__module__", ""))
            filename = getattr(module, "__file__", None)
            if filename:
                paths.add(str(Path(filename).resolve()))
        exc = exc.__cause__ or exc.__context__
    return paths


def pytest_exception_interact(node, call, report):
    # Pytest sometimes renders import/collection errors as plain strings.
    # Preserve actual exception-chain provenance instead of parsing that text.
    for record in REPORT["reports"]:
        if record["nodeid"] == report.nodeid and record["outcome"] == "failed":
            record["traceback_paths"] = sorted(
                set(record["traceback_paths"]) | _exception_paths(call.excinfo.value))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if call.excinfo:
        report.evaluator_paths = sorted(_exception_paths(call.excinfo.value))
        report.evaluator_assertion = isinstance(
            call.excinfo.value, (AssertionError, pytest.fail.Exception))


@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    outcome = yield
    report = outcome.get_result()
    if report.failed:
        REPORT["reports"].append(_record(report, "collection"))


def _record(report, phase):
    representation = report.longrepr
    paths = list(getattr(report, "evaluator_paths", []))
    traceback = getattr(representation, "reprtraceback", None)
    for entry in getattr(traceback, "reprentries", []):
        location = getattr(entry, "reprfileloc", None)
        if location:
            paths.append(str(Path(location.path).resolve()))
    crash = getattr(representation, "reprcrash", None)
    if crash:
        paths.append(str(Path(crash.path).resolve()))
    return {
        "nodeid": report.nodeid,
        "phase": phase,
        "outcome": report.outcome,
        "traceback_paths": paths,
        "assertion_failure": getattr(report, "evaluator_assertion", False),
        "detail": str(representation) if report.failed else None,
    }


def pytest_runtest_logreport(report):
    REPORT["reports"].append(_record(report, report.when))


def pytest_internalerror(excrepr, excinfo):
    REPORT["internal_errors"].append(str(excrepr))


def pytest_sessionfinish(session, exitstatus):
    REPORT.update(finished=True, exitstatus=int(exitstatus), collected=session.testscollected)
    Path(os.environ["HARNESS_PYTEST_REPORT"]).write_text(
        json.dumps(REPORT), encoding="utf-8"
    )
