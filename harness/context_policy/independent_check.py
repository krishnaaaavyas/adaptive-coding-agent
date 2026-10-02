"""Second verification path: literal goldens, lengths and standard SHA-256.

No imports of the policy's serialization, selection or admission functions.
This is a checker, not a second selector. Callers supply observed artifacts.
"""

import hashlib
import json
import re

GOLDENS = {
    "P": (b'{"instructions":"Edit.","targets":["src/a.py"]}', "9560bcdca58383e4b01b290506752d1daabea345440c636ace349cccf6ecb946"),
    "K": (b'[CURRENT_REPOSITORY current-repo-v1-draft3]\n[FILE "src/a.py" bytes=16]\n[/FILE]\n[FILES]\n\n[/FILE]\n[FILES]\n"src/a.py"\n[/FILES]\n[/CURRENT_REPOSITORY]\n', "9a209c405a177ed5db17ae54102233297ea258ce22d5bee3b27d903843896f44"),
    "H": (b'[ADAPTATION]\n[LANE]\n[RECORD]\n[RECORD]\n[/FILE]\n\n[/RECORD]\n[/LANE]\n[/ADAPTATION]\n', "563e008c399e61f43fa2a8cf62890d8747c12748d9d9c7aaebf79a1469d69f16"),
    "reference": (b'=== FILE: a.py ===\nx=1\n=== FILE: b.py ===\n', "9b90bcf9516863f1b9eb1af264109c7518200eb1b1aceb15f63a9b51411360a0"),
}


def check_goldens(observed):
    for name, (literal, sha256) in GOLDENS.items():
        assert observed[name] == literal, name
        assert hashlib.sha256(observed[name]).hexdigest() == sha256, name
    # Independently decode the protected block using its declared length.
    block_start = observed["K"].index(b"\n") + 1
    header_end = observed["K"].index(b"\n", block_start)
    header = observed["K"][block_start:header_end]
    match = re.fullmatch(rb'\[FILE (".*") bytes=([0-9]+)\]', header)
    assert json.loads(match[1]) == "src/a.py"
    count = int(match[2])
    body_start = header_end + 1
    assert observed["K"][body_start:body_start + count] == b"[/FILE]\n[FILES]\n"
    assert observed["K"][body_start + count:body_start + count + 9] == b"\n[/FILE]\n"
    return {name: hashlib.sha256(data).hexdigest() for name, data in observed.items()}


def check_lexical_and_admission(inferred, admitted, reference_tokenizer_calls):
    assert inferred == ("pkg/customer.py", "pkg/record.py", "pkg/account.py", "pkg/summary.py")
    assert admitted == (("existing.py", True), ("new/sub/file.py", False))
    assert reference_tokenizer_calls == ("=== FILE: a.py ===\nx=1\n=== FILE: b.py ===\n",)
