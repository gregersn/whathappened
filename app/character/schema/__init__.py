
import json

from jsonschema.validators import Draft7Validator


def load_schema(filename: str):
    with open(filename, 'r') as f:
        return json.load(f)


def validate(data, filename):
    schema = load_schema(filename)
    v = Draft7Validator(schema)
    return [{'path': "/".join(str(x) for x in e.path),
             "message": e.message} for e in v.iter_errors(data)]
