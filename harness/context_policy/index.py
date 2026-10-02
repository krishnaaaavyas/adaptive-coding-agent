"""Pinned, static Python graph. Repository code is parsed, never executed."""

import ast
from collections import defaultdict
from dataclasses import dataclass
import re

from .core import POLICY_SHA256, fail, u, verify_parser


def structural(p):
    return p.endswith((".py", ".pyi"))


def ordinary_test(p):
    if not structural(p) or p.rsplit("/", 1)[-1] == "conftest.py":
        return False
    base = p.rsplit("/", 1)[-1]
    return any(d in ("test", "tests") for d in p.split("/")[:-1]) or bool(re.fullmatch(r"test_.*\.py|.*_test\.py", base))


@dataclass(frozen=True)
class Route:
    base: str
    provider: str
    prefixed: bool


class PythonIndex:
    def __init__(self, snapshot, config):
        verify_parser()
        if (not isinstance(config, dict) or set(config) != {"policy_id", "policy_sha256", "root_alias_mode", "root_alias_basename"}
                or config["policy_id"] != "current-repo-v1-draft3" or config["policy_sha256"] != POLICY_SHA256):
            fail("infrastructure_invalid", "configuration_invalid", 1)
        mode, root = config["root_alias_mode"], config["root_alias_basename"]
        init = next((p for p in ("__init__.py", "__init__.pyi") if p in snapshot.files), None)
        if (mode not in ("enabled", "disabled") or (mode == "disabled" and root != "")
                or (mode == "enabled" and (not isinstance(root, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", root) or init is None))):
            fail("infrastructure_invalid", "invalid_root_alias_configuration", 1)
        self.root = root if mode == "enabled" else ""
        self.root_init = init if self.root else None
        self.files = tuple(sorted((p for p in snapshot.files if structural(p)), key=u))
        self.owned, contenders = {}, defaultdict(list)
        for p in self.files:
            parts = p.split("/")
            base = parts[-1]
            initializer = base in ("__init__.py", "__init__.pyi")
            name = ".".join(parts[:-1]) if initializer else ".".join(parts[:-1] + [base.rsplit(".", 1)[0]])
            self.owned[p] = name
            if name:
                priority = (0 if p.endswith("/__init__.py") else 2 if p.endswith("/__init__.pyi")
                            else 1 if p.endswith(".py") else 3)
                contenders[name].append((priority, p))
        self.providers = {name: min(rows, key=lambda row: (row[0], u(row[1])))[1] for name, rows in contenders.items()}
        routes = defaultdict(set)
        for base, p in self.providers.items():
            routes[base].add(Route(base, p, False))
            if self.root:
                routes[self.root + "." + base].add(Route(base, p, True))
        if self.root:
            routes[self.root].add(Route("", self.root_init, True))
        self.routes = {name: tuple(sorted(rows, key=lambda r: (u(r.provider), r.base, r.prefixed))) for name, rows in routes.items()}
        self.modules = {name: tuple(sorted({r.provider for r in rows}, key=u)) for name, rows in self.routes.items()}
        self.declarations, self.names = defaultdict(set), defaultdict(list)
        self.edges, self.edge_reasons, self.diagnostics = {}, {}, []
        for p in self.files:
            try:
                tree = ast.parse(snapshot.files[p], filename=p, mode="exec", type_comments=True)
            except SyntaxError as exc:
                self.diagnostics.append({"path": p, "reason": "parse_failure", "line": exc.lineno})
                self.edges[p], self.edge_reasons[p] = set(), []
                continue
            def visit(node, parents=()):
                next_parents = parents
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    owners = parents + (node.name,)
                    qualified = ".".join(owners)
                    aliases = {node.name, qualified}
                    base = self.owned[p]
                    if base:
                        aliases.add(base + "." + qualified)
                    if self.root:
                        aliases.add(".".join(filter(None, (self.root, base, qualified))))
                    for alias in aliases:
                        self.declarations[alias].add(p)
                    self.names[p].append(node.name)
                    next_parents = owners
                for child in ast.iter_child_nodes(node):
                    visit(child, next_parents)
            visit(tree)
            edges, reasons = set(), []
            for node in ast.walk(tree):
                requests = []
                if isinstance(node, ast.Import):
                    requests = [(alias.name, "module") for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    base = node.module or ""
                    if node.level:
                        package = self.package(p)
                        if node.level > len(package):
                            self.diagnostics.append({"path": p, "reason": "relative_ascent", "line": node.lineno})
                            continue
                        base = ".".join(package[:len(package) - node.level + 1] + ([base] if base else []))
                    if base:
                        requests.append((base, "base"))
                    requests.extend((base + "." + alias.name if base else alias.name, "member") for alias in node.names if alias.name != "*")
                for name, kind in requests:
                    found = self.routes.get(name, ())
                    if not found:
                        self.diagnostics.append({"path": p, "reason": "unresolved_import", "module": name, "line": node.lineno})
                    for route in found:
                        for target, edge_type in [(route.provider, kind)] + [(s, "initializer") for s in self.initializers(route)]:
                            edges.add(target)
                            reasons.append({"target": target, "module": name, "base": route.base,
                                            "prefixed": route.prefixed, "edge_type": edge_type, "line": node.lineno})
            self.edges[p] = edges
            self.edge_reasons[p] = reasons
        self.reverse = defaultdict(set)
        for source, targets in self.edges.items():
            for target in targets:
                self.reverse[target].add(source)

    def package(self, p):
        parts = p.split("/")[:-1]
        return ([self.root] if self.root else []) + parts

    def initializers(self, route):
        parts = route.base.split(".") if route.base else []
        package_provider = route.provider.endswith(("/__init__.py", "/__init__.pyi"))
        count = len(parts) if package_provider else max(0, len(parts) - 1)
        found = []
        for n in range(1, count + 1):
            provider = self.providers.get(".".join(parts[:n]))
            if provider and provider.endswith(("/__init__.py", "/__init__.pyi")):
                found.append(provider)
        if route.prefixed and self.root_init:
            found.append(self.root_init)
        return sorted(set(found), key=u)
