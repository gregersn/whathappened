from typing import Dict, List, Union
import yaml
import logging
import json
import pathlib
from jsonschema.exceptions import SchemaError

from jsonschema.validators import Draft7Validator

logger = logging.getLogger(__name__)


def load_schema(filename: str) -> Dict:
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
    return {}


def validate(data, filename):
    schema = load_schema(filename)
    v = Draft7Validator(schema)
    return [{'path': "/".join(str(x) for x in e.path),
             "message": e.message} for e in v.iter_errors(data)]


def build_boolean(schema: Dict) -> bool:
    return schema['default']


def build_string(schema: Dict) -> str:
    return schema['default']


def build_integer(schema: Dict) -> int:
    return schema['default']


def build_object(schema: Dict, main_schema: Dict) -> Dict:
    output = {}
    for property, description in schema['properties'].items():
        output[property] = build_from_schema(description, main_schema)
    return output


def build_array(schema: Dict) -> List:
    if 'default' in schema:
        return schema['default']
    return []


def get_sub(d: Dict, path: List) -> Dict:
    if len(path) == 1:
        return d[path[0]]

    p = path.pop(0)
    return get_sub(d[p], path)


def sub_schema(schema: Union[List, Dict], path: str) -> \
        Union[Dict, List, str, int, bool]:
    parts = path.split("/")
    if parts[0] != '#':
        raise NotImplementedError(path)

    return get_sub(schema, parts[1:])


def build_from_schema(schema: Union[List, Dict],
                      main_schema: Union[List, Dict, None] = None) -> \
        Union[Dict, List, str, int, bool]:
    if main_schema is None:
        main_schema = schema
    if isinstance(schema, Dict):
        logger.debug("Handling a dictionary")
        if '$ref' in schema:
            return build_from_schema(sub_schema(main_schema, schema['$ref']),
                                     main_schema)
        if 'const' in schema:
            return schema['const']
        if schema.get('type') == 'object':
            return build_object(schema, main_schema)
        if schema.get('type') == 'string':
            return build_string(schema)
        if schema.get('type') == 'integer':
            return build_integer(schema)
        if schema.get('type') == 'boolean':
            return build_boolean(schema)
        if schema.get('type') == 'array':
            return build_array(schema)

    elif isinstance(schema, List):
        logger.debug("Handling a list")

    return ''
