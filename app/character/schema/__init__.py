import yaml
import logging
import json
import pathlib
from jsonschema.exceptions import SchemaError

from jsonschema.validators import Draft7Validator

logger = logging.getLogger(__name__)


def load_schema(filename: str):
    path = pathlib.Path(filename)
    with open(filename, 'r') as f:
        try:
            if path.suffix == '.json':
                data = json.load(f)
                return data
            elif path.suffix == '.yaml':
                data = yaml.safe_load(f)
                return data
        except Exception as e:
            logger.debug(e)
            raise SchemaError("Schema not saved in a known format")


def validate(data, filename):
    schema = load_schema(filename)
    v = Draft7Validator(schema)
    return [{'path': "/".join(str(x) for x in e.path),
             "message": e.message} for e in v.iter_errors(data)]
