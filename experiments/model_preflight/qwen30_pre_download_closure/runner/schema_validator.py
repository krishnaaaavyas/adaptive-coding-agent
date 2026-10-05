"""JSONSchema wrapper using immutable frozen schema supplied by path/hash."""
import json
from pathlib import Path
import jsonschema
from .interface import digest


def check(payload, schema_path, expected_hash):
    data = Path(schema_path).read_bytes()
    if digest(data) != expected_hash:
        raise ValueError('frozen schema drift')
    schema = json.loads(data)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(payload)
