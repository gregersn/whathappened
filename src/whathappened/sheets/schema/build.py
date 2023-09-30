from typing import Dict, List, MutableMapping, Union, Any
import yaml
import logging
import json
from pathlib import Path
from jsonschema.exceptions import SchemaError

from jsonschema.validators import Draft7Validator

CHARACTER_SCHEMA_DIR = Path(__file__).parent.parent / "schema"

assert CHARACTER_SCHEMA_DIR.is_dir(), CHARACTER_SCHEMA_DIR

logger = logging.getLogger(__name__)

SCHEMA_DIR = Path(__file__).parent


def get_schema(system: str):
    CHARACTER_SCHEMA = SCHEMA_DIR / f"{system}.yaml"
    if CHARACTER_SCHEMA.is_file():
        return load_schema(CHARACTER_SCHEMA)

    logger.debug("No character schema: %s", CHARACTER_SCHEMA)

    CHARACTER_SCHEMA = SCHEMA_DIR / f"{system}.json"
    if CHARACTER_SCHEMA.is_file():
        return load_schema(CHARACTER_SCHEMA)

    logger.debug("No character schema: %s", CHARACTER_SCHEMA)

    try:
        import importlib

        game_module = importlib.import_module(f"whathappened.sheets.schema.{system}")

        return game_module.CharacterSheet.model_json_schema()
    except:
        ...

    raise SchemaError("Missing schema")


def flatten_schema(schema: Dict[str, Any]):
    return schema


def load_schema(filename: Path) -> Dict[str, Any]:
    with open(filename, "r") as f:
        try:
            if filename.suffix == ".json":
                data = json.load(f)
                return data
            elif filename.suffix == ".yaml":
                data = yaml.safe_load(f)
                return data
        except Exception as e:
            logger.debug(e)
            raise SchemaError("Schema not saved in a known format")
    return {}


SchemaValidationError = Dict[str, str]


def validate(data: Dict, system: str) -> List[SchemaValidationError]:
    schema = get_schema(system)
    v = Draft7Validator(schema)
    return [
        {"path": "/".join(str(x) for x in e.path), "message": e.message}
        for e in v.iter_errors(data)
    ]


def build_boolean(schema: Dict[str, bool]) -> bool:
    logger.debug("build boolean: %s", schema["default"])
    return schema["default"]


def build_string(schema: Dict[str, str]) -> str:
    logger.debug("build string: %s", schema["default"])
    return schema["default"]


def build_integer(schema: Dict[str, int]) -> int:
    logger.debug("build integer: %s", schema["default"])
    return schema["default"]


def build_object(schema: Dict[str, Any], main_schema: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug("build object")
    output = {}
    for property, description in schema["properties"].items():
        output[property] = build_from_schema2(description, main_schema)
    return output


def build_array(schema: Dict[str, List[Any]]) -> List[Any]:
    logger.debug("build array")
    if "default" in schema:
        return schema["default"]
    return []


def get_sub(d: Dict[str, Any], path: List[str]) -> Dict:
    logger.debug("get_sub: %s", path)
    if len(path) == 1:
        return d[path[0]]

    p = path.pop(0)
    return get_sub(d[p], path)


def sub_schema(
    schema: Union[List, Dict], path: str
) -> Union[Dict, List, str, int, bool]:
    logger.debug("sub_schema: %s", path)
    parts = path.split("/")
    if parts[0] != "#":
        raise NotImplementedError(path)

    assert isinstance(schema, dict)

    return get_sub(schema, parts[1:])


def build_from_schema2(
    schema: Union[List, Dict[str, Any]], main_schema: Dict[str, Any]
) -> Union[Dict, List, str, int, bool]:
    if isinstance(schema, Dict):
        logger.debug("Handling a dictionary")
        if "$ref" in schema:
            sub = sub_schema(main_schema, schema["$ref"])

            assert isinstance(sub, Dict) or isinstance(sub, List)

            return build_from_schema2(sub, main_schema)
        if "const" in schema:
            return schema["const"]
        if schema.get("type") == "object" and isinstance(main_schema, dict):
            return build_object(schema, main_schema)
        if schema.get("type") == "string":
            return build_string(schema)
        if schema.get("type") == "integer":
            return build_integer(schema)
        if schema.get("type") == "boolean":
            return build_boolean(schema)
        if schema.get("type") == "array":
            return build_array(schema)
        if "default" in schema:
            return schema["default"]
        if "allOf" in schema:
            out = {}
            for entry in schema["allOf"]:
                out.update(build_from_schema2(entry, main_schema))
            return out
    elif isinstance(schema, List):
        logger.debug("Handling a list")
        raise NotImplementedError("Lists are not my strong suite.")

    return ""


def build_from_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    built = build_from_schema2(schema, schema)
    assert isinstance(built, MutableMapping)
    return built
