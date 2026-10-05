"""Metadata-only Linux/CP311 dependency resolution; no weights or wheel bodies.

All resolved requirements are emitted as exact version+artifact SHA256 pins.
The dated resolution record is not an installation or build PASS.
"""
import sys
sys.dont_write_bytecode = True
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request
from packaging.requirements import Requirement
from packaging.version import Version, InvalidVersion
from packaging.tags import cpython_tags, compatible_tags, parse_tag
from packaging.utils import canonicalize_name, parse_wheel_filename

HERE = Path(__file__).resolve().parent
GOV = HERE.parent / 'qwen30_infrastructure_governance'
LIMIT = 32_000_000
CUTOFF = '2026-10-04T00:00:00'
ENV = {'implementation_name': 'cpython', 'implementation_version': '3.11.9', 'os_name': 'posix',
       'platform_machine': 'x86_64', 'platform_release': '', 'platform_system': 'Linux',
       'platform_version': '', 'python_full_version': '3.11.9', 'platform_python_implementation': 'CPython',
       'python_version': '3.11', 'sys_platform': 'linux', 'extra': ''}
PLATFORMS = [f'manylinux_2_{i}_x86_64' for i in range(35, 4, -1)] + ['manylinux2014_x86_64', 'manylinux2010_x86_64', 'manylinux1_x86_64', 'linux_x86_64']
TAGS = list(cpython_tags((3, 11), ['cp311'], PLATFORMS)) + list(compatible_tags((3, 11), 'cp311', PLATFORMS))
RANK = {t: i for i, t in enumerate(TAGS)}
ROWS = []


def get(name, version=None):
    name = canonicalize_name(name)
    rel = 'sources/pypi/' + name + ('-' + str(version) if version else '-index') + '.json'
    p = HERE / rel
    url = f'https://pypi.org/pypi/{name}/' + (str(version) + '/' if version else '') + 'json'
    if not p.exists():
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Qwen30-build-definition/1.0'}), timeout=35) as response:
            data = response.read(LIMIT + 1)
            assert len(data) <= LIMIT, (name, 'metadata response limit')
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    data = p.read_bytes()
    if not any(r['path'] == rel for r in ROWS):
        ROWS.append({'url': url, 'path': rel, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'kind': 'package metadata; no wheel body'})
    return json.loads(data)


def wheel(meta):
    candidates = []
    for f in meta['urls']:
        if f.get('yanked') or f['packagetype'] != 'bdist_wheel' or f['upload_time'] > CUTOFF:
            continue
        if f.get('requires_python'):
            if not Requirement('python' + f['requires_python']).specifier.contains('3.11.9'):
                continue
        tags = parse_wheel_filename(f['filename'])[3]
        ranks = [RANK[t] for t in tags if t in RANK]
        if ranks:
            candidates.append((min(ranks), f['filename'], f))
    if not candidates:
        return None
    f = sorted(candidates)[0][2]
    return {'filename': f['filename'], 'url': f['url'], 'sha256': f['digests']['sha256'], 'bytes': f['size'],
            'body_downloaded': False, 'body_hash_verified': False}


def deps(meta, extras):
    out = []
    for text in meta['info'].get('requires_dist') or []:
        req = Requirement(text)
        if req.marker is None or any(req.marker.evaluate(dict(ENV, extra=e)) for e in {''} | set(extras)):
            out.append(req)
    return out


def choose(name, reqs):
    spec = [r.specifier for r in reqs]
    exacts = [s.version for r in reqs for s in r.specifier if s.operator == '==' and '*' not in s.version]
    if exacts:
        versions = sorted({Version(v) for v in exacts}, reverse=True)
    else:
        index = get(name)
        versions = []
        for text, files in index['releases'].items():
            try:
                v = Version(text)
            except InvalidVersion:
                continue
            if files and not v.is_prerelease and not v.is_devrelease and any(f['upload_time'] <= CUTOFF and not f.get('yanked') for f in files):
                versions.append(v)
        versions.sort(reverse=True)
    for v in versions:
        if not all(s.contains(v, prereleases=bool(exacts)) for s in spec):
            continue
        meta = get(name, v)
        py = meta['info'].get('requires_python')
        if py and not Requirement('python' + py).specifier.contains('3.11.9'):
            continue
        w = wheel(meta)
        if w:
            return {'name': name, 'version': str(v), 'wheel': w, 'metadata_path': 'sources/pypi/' + name + '-' + str(v) + '.json'}, meta
    raise ValueError('No compatible hashed Linux/CP311 wheel: ' + name + ' constraints=' + ','.join(str(r) for r in reqs))


def main():
    core = ['vllm==0.11.2', 'torch==2.9.0', 'transformers==4.57.6', 'peft==0.18.0',
        'tokenizers==0.22.2', 'jinja2==3.1.6', 'triton==3.5.0', 'flashinfer-python==0.5.2',
        'pip==25.0.1', 'setuptools==80.9.0', 'setuptools-scm==9.2.2', 'wheel==0.45.1',
        'cmake==3.31.6', 'ninja==1.11.1.3', 'packaging==25.0', 'build==1.2.2.post1',
        'jsonschema==4.25.1', 'numpy==2.2.6', 'huggingface-hub==0.36.2',
        'flashinfer-cubin==0.5.2']
    # All candidate selection occurs before outputs, is date-bounded, and final artifacts use no ranges/latest tags.
    roots = [Requirement(r) for r in core]
    selected, metadata = {}, {}
    failure = None
    try:
        for iteration in range(40):
            constraints, extras, todo, visited = {}, {}, list(roots), set()
            while todo:
                req = todo.pop()
                name = canonicalize_name(req.name)
                constraints.setdefault(name, []).append(req)
                before = set(extras.get(name, set()))
                extras.setdefault(name, set()).update(req.extras)
                if name in selected and (name not in visited or before != extras[name]):
                    visited.add(name)
                    todo.extend(deps(metadata[name], extras[name]))
            jobs = [(name, reqs) for name, reqs in constraints.items() if name not in selected or
                    not all(r.specifier.contains(selected[name]['version']) for r in reqs)]
            if not jobs and set(selected) == set(constraints):
                break
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                futures = {pool.submit(choose, name, reqs): name for name, reqs in jobs}
                for future in concurrent.futures.as_completed(futures):
                    name = futures[future]
                    package, meta = future.result()
                    results.append((name, package, meta))
            for name, package, meta in results:
                selected[name], metadata[name] = package, meta
            for name in set(selected) - set(constraints):
                selected.pop(name)
                metadata.pop(name)
            print(json.dumps({'iteration': iteration, 'resolved_packages': len(selected)}), flush=True)
        else:
            raise ValueError('Dependency closure did not converge within40 metadata rounds')
        for name, reqs in constraints.items():
            assert all(r.specifier.contains(selected[name]['version']) for r in reqs), name
        for name in selected:
            selected[name]['extras'] = sorted(extras.get(name, set()))
            selected[name]['active_requires_dist'] = [str(r) for r in deps(metadata[name], extras.get(name, set()))]
        # Source-build vLLM replaces its wheel. Torch uses the immutable officialcu128 wheel.
        selected['vllm']['wheel_unselected_source_build'] = selected['vllm'].pop('wheel')
        selected['vllm']['source_commit'] = '275de34170654274616082721348b7edd9741d32'
        torch = json.loads((GOV / 'runtime_lock.json').read_text(encoding='utf-8'))['torch']
        selected['torch']['version'] = '2.9.0+cu128'
        selected['torch']['wheel'] = {k: torch[k] for k in ['filename', 'url', 'sha256', 'body_downloaded', 'body_hash_verified']}
    except Exception as exc:
        failure = repr(exc)
    lock = {'status': 'METADATA_CLOSURE_RESOLVED_NOT_BUILT' if failure is None else 'PENDING_DEPENDENCY_RESOLUTION',
        'failure': failure, 'target_marker_environment': ENV, 'candidate_cutoff_utc': CUTOFF + 'Z',
        'wheel_platform_ceiling': 'manylinux2.35 Linuxamd64; actual base libc validation required at build',
        'roots': core, 'packages': sorted(selected.values(), key=lambda p: p['name']),
        'validation': 'Exact metadata constraints verified at LinuxCP311 markers; installation/compiled-ABI compatibility not executed',
        'vllm_artifact_expected_hash': None, 'final_image_digest': None}
    (HERE / 'python_dependency_lock.json').write_text(json.dumps(lock, indent=2) + '\n', encoding='utf-8')
    (HERE / 'metadata_sources.json').write_text(json.dumps({'files': sorted(ROWS, key=lambda r: r['path'])}, indent=2) + '\n', encoding='utf-8')
    lines = []
    if failure is None:
        for p in lock['packages']:
            if p['name'] != 'vllm':
                lines.append(p['name'] + '==' + p['version'] + ' --hash=sha256:' + p['wheel']['sha256'])
    (HERE / 'requirements-linux-cp311.lock').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'status': lock['status'], 'packages': len(selected), 'failure': failure}), flush=True)
    if failure:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
