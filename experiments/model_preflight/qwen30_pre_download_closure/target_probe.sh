#!/bin/sh
# CPU host / driver inventory only; call before acquisition, never launches a model.
set -eu
exec python3 -B "$(dirname "$0")/target_probe.py" "$@"
