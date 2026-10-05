"""Resolve named build-package closure from hash-checked dated Ubuntu indexes.

Does not install packages. InRelease signature verification is a target-build
precondition using the keyring bound by the pinned base image.
"""
import sys
sys.dont_write_bytecode = True
import concurrent.futures
from functools import cmp_to_key
import hashlib
import json
import lzma
from pathlib import Path
import re
import urllib.request

HERE = Path(__file__).resolve().parent
SNAPSHOT = 'https://snapshot.ubuntu.com/ubuntu/20261003T000000Z/'


def versioncmp(a, b):
    def split(v):
        e, rest = v.split(':', 1) if ':' in v else ('0', v)
        u, rev = rest.rsplit('-', 1) if '-' in rest else (rest, '0')
        return int(e), u, rev
    def order(c):
        return -1 if c == '~' else 0 if not c else ord(c) if c.isalpha() else ord(c) + 256
    def part(x, y):
        while x or y:
            while (x and not x[0].isdigit()) or (y and not y[0].isdigit()):
                xc = x[0] if x and not x[0].isdigit() else ''
                yc = y[0] if y and not y[0].isdigit() else ''
                if order(xc) != order(yc):
                    return (order(xc) > order(yc)) - (order(xc) < order(yc))
                x = x[1:] if xc else x
                y = y[1:] if yc else y
            xm, ym = re.match(r'\d*', x).group(), re.match(r'\d*', y).group()
            xd, yd = xm.lstrip('0'), ym.lstrip('0')
            if len(xd) != len(yd):
                return (len(xd) > len(yd)) - (len(xd) < len(yd))
            if xd != yd:
                return (xd > yd) - (xd < yd)
            x, y = x[len(xm):], y[len(ym):]
        return 0
    ae, au, ar = split(a)
    be, bu, br = split(b)
    return (ae > be) - (ae < be) if ae != be else part(au, bu) or part(ar, br)


def fetch(job):
    suite, component, expected, size = job
    rel = f'sources/apt/{suite}-{component}-Packages.xz'
    p = HERE / rel
    url = SNAPSHOT + f'dists/{suite}/{component}/binary-amd64/Packages.xz'
    if not p.exists():
        with urllib.request.urlopen(url, timeout=45) as response:
            data = response.read(size + 1)
        assert len(data) == size
        p.write_bytes(data)
    data = p.read_bytes()
    assert len(data) == size and hashlib.sha256(data).hexdigest() == expected
    return {'path': rel, 'url': url, 'bytes': size, 'sha256': expected, 'suite': suite, 'component': component}


def main():
    jobs = []
    for suite in ['jammy', 'jammy-updates', 'jammy-security']:
        text = (HERE / f'sources/apt/{suite}-InRelease').read_text()
        section = text.split('SHA256:\n', 1)[1].split('\nSHA512:', 1)[0]
        for component in ['main', 'universe']:
            match = re.search(r'^ ([a-f0-9]{64})\s+(\d+) ' + component + r'/binary-amd64/Packages.xz$', section, re.M)
            assert match
            jobs.append((suite, component, match[1], int(match[2])))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        indexes = list(pool.map(fetch, jobs))
    packages, providers = {}, {}
    for index in indexes:
        text = lzma.decompress((HERE / index['path']).read_bytes()).decode()
        for block in text.split('\n\n'):
            fields = {}
            for line in block.splitlines():
                if line and not line.startswith(' ') and ': ' in line:
                    key, value = line.split(': ', 1)
                    fields[key] = value
            if fields.get('Architecture') not in {'amd64', 'all'} or 'SHA256' not in fields:
                continue
            name = fields['Package']
            fields['_suite'] = index['suite']
            packages.setdefault(name, []).append(fields)
            for provided in fields.get('Provides', '').split(', '):
                if provided:
                    providers.setdefault(provided.split(' ')[0], []).append(name)
    for name in packages:
        packages[name].sort(key=cmp_to_key(lambda a, b: versioncmp(a['Version'], b['Version'])), reverse=True)
    roots = ['gcc-10', 'g++-10', 'make', 'binutils', 'git', 'ca-certificates', 'pkg-config', 'patch', 'tar', 'xz-utils',
        'zlib1g-dev', 'libssl-dev', 'libffi-dev', 'libbz2-dev', 'liblzma-dev', 'libreadline-dev', 'libsqlite3-dev', 'libncurses-dev', 'uuid-dev']
    chosen, todo, decisions = {}, list(roots), []
    def pick(expression):
        for alternative in expression.split(' | '):
            m = re.match(r'([a-z0-9+.-]+)(?::(?:any|native))?(?: \((<<|<=|=|>=|>>) ([^)]+)\))?', alternative.strip())
            if not m:
                continue
            name, op, ver = m.groups()
            names = [name] if name in packages else sorted(providers.get(name, []))
            for n in names:
                for candidate in packages[n]:
                    cmp = versioncmp(candidate['Version'], ver) if ver else 0
                    if not op or {'<<': cmp < 0, '<=': cmp <= 0, '=': cmp == 0, '>=': cmp >= 0, '>>': cmp > 0}[op]:
                        return candidate
        raise ValueError('Unresolved apt dependency: ' + expression)
    failure = None
    try:
        while todo:
            expression = todo.pop(0)
            c = pick(expression)
            name = c['Package']
            if name in chosen:
                if chosen[name]['Version'] != c['Version']:
                    raise ValueError('Apt exact-version conflict: ' + expression)
                continue
            chosen[name] = c
            decisions.append({'dependency': expression, 'chosen': name, 'version': c['Version']})
            for key in ['Pre-Depends', 'Depends']:
                todo.extend(c.get(key, '').split(', ') if c.get(key) else [])
    except Exception as exc:
        failure = repr(exc)
    lock = {'snapshot': SNAPSHOT, 'architecture': 'amd64', 'roots': roots, 'status': 'METADATA_PACKAGE_CLOSURE_RESOLVED_TARGET_DPKG_REVIEW_REQUIRED' if failure is None else 'PENDING_APT_DEPENDENCY',
        'failure': failure, 'indexes': indexes, 'packages': [
            {'name': n, 'version': c['Version'], 'architecture': c['Architecture'], 'url': SNAPSHOT + c['Filename'],
             'filename': Path(c['Filename']).name, 'bytes': int(c['Size']), 'sha256': c['SHA256'],
             'depends': c.get('Depends', ''), 'pre_depends': c.get('Pre-Depends', ''), 'suite': c['_suite'], 'body_downloaded': False}
            for n, c in sorted(chosen.items())], 'alternative_decisions': decisions,
        'signature_verification': 'PENDING_TARGET_GPGV using Ubuntu keyring in pinned base image before installing anything',
        'base_installed_inventory_compatibility': 'PENDING_TARGET_BUILD; metadata closure is not dpkg ABI/install proof',
        'recommends_suggests_installed': False}
    (HERE / 'apt_dependency_lock.json').write_text(json.dumps(lock, indent=2) + '\n', encoding='utf-8')
    (HERE / 'apt-packages.lock').write_text('\n'.join(p['name'] + '=' + p['version'] for p in lock['packages']) + '\n', encoding='utf-8')
    print(json.dumps({'status': lock['status'], 'packages': len(chosen), 'failure': failure}))


if __name__ == '__main__':
    main()
