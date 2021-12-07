from typing import Dict, List, Mapping, Union, Any
import yaml
import logging
import json
import pathlib
from jsonschema.exceptions import SchemaError

from jsonschema.validators import Draft7Validator

logger = logging.getLogger(__name__)


def load_schema(filename: pathlib.Path) -> Dict:
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


SchemaValidationError = Dict[str, str]


def validate(data: Mapping[str, Any], filename: pathlib.Path) -> List[SchemaValidationError]:
    schema = load_schema(filename)
    v = Draft7Validator(schema)
    assert v is not None
    for e in v.iter_errors(data):
        print("New error: ")
        print(e.path)
        for x in e.path:
            print(x)
        print(e.message)
        print("----")

    # return []
    return [
        {'path': "/".join(str(x) for x in e.path),
         "message": e.message} for e in v.iter_errors(data)
    ]


def build_boolean(schema: Dict[str, bool]) -> bool:
    return schema['default']


def build_string(schema: Dict[str, str]) -> str:
    if 'default' not in schema:
        raise KeyError(schema)
    return schema['default']


def build_integer(schema: Dict[str, int]) -> int:
    return schema['default']


def build_object(schema: Dict[str, Any],
                 main_schema: Dict[str, Any]) -> Dict[str, Any]:
    output = {}
    for property, description in schema['properties'].items():
        output[property] = build_from_schema2(description, main_schema)
    return output


def build_array(schema: Dict[str, List[Any]]) -> List[Any]:
    if 'default' in schema:
        return schema['default']
    return []


def get_sub(d: Dict[str, Any], path: List[str]) -> Dict:
    if len(path) == 1:
        return d[path[0]]

    p = path.pop(0)
    return get_sub(d[p], path)


def sub_schema(schema: Union[List, Dict], path: str) -> \
        Union[Dict, List, str, int, bool]:
    parts = path.split("/")
    if parts[0] != '#':
        raise NotImplementedError(path)

    assert isinstance(schema, dict)

    return get_sub(schema, parts[1:])


def build_from_schema2(schema: Union[List, Dict[str, Any]],
                       main_schema: Dict[str, Any]) -> \
        Union[Dict, List, str, int, bool]:

    if isinstance(schema, Dict):
        logger.debug("Handling a dictionary")
        if '$ref' in schema:
            sub = sub_schema(main_schema, schema['$ref'])

            assert isinstance(sub, Dict) or isinstance(sub, List)

            return build_from_schema2(sub,
                                      main_schema)
        if 'const' in schema:
            return schema['const']
        if 'default' in schema:
            return schema['default']
        if schema.get('type') == 'object' and isinstance(main_schema, dict):
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

    raise TypeError(schema)


def build_from_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    nc = build_from_schema2(schema, schema)
    assert isinstance(nc, Dict)
    return nc
