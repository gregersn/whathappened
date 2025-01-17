"""Build sheets from schemas."""

from typing import Dict, List, MutableMapping, Optional, Union, Any
import logging
from pathlib import Path
import json
import yaml
import pydantic
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
from jsonschema.exceptions import SchemaError
from jsonschema.validators import Draft7Validator

from whathappened.core.sheets.schema.base import Gametag

CHARACTER_SCHEMA_DIR = Path(__file__).parent.parent / "schema"

assert CHARACTER_SCHEMA_DIR.is_dir(), CHARACTER_SCHEMA_DIR

logger = logging.getLogger(__name__)

SCHEMA_DIR = Path(__file__).parent


class UnsortedGenerateJsonSchema(GenerateJsonSchema):
    def sort(
        self, value: JsonSchemaValue, parent_key: Optional[str] = None
    ) -> JsonSchemaValue:
        return value


def get_schema(system: Gametag):
    """Get schema based on system name."""
    try:
        import importlib

        game_module = importlib.import_module(
            f"whathappened.core.sheets.schema.{system}"
        )

        if issubclass(game_module.CharacterSheet, pydantic.BaseModel):
            logger.debug("Getting character sheet from pydantic")
            return game_module.CharacterSheet.model_json_schema(
                mode="serialization", schema_generator=UnsortedGenerateJsonSchema
            )

    except ImportError:
        ...
    except AttributeError:
        ...

    CHARACTER_SCHEMA = SCHEMA_DIR / f"{system}.yaml"
    if CHARACTER_SCHEMA.is_file():
        logger.debug("Loading: %s", CHARACTER_SCHEMA)
        return load_schema(CHARACTER_SCHEMA)

    logger.debug("No character schema: %s", CHARACTER_SCHEMA)

    CHARACTER_SCHEMA = SCHEMA_DIR / f"{system}.json"
    if CHARACTER_SCHEMA.is_file():
        logger.debug("Loading: %s", CHARACTER_SCHEMA)
        return load_schema(CHARACTER_SCHEMA)

    logger.debug("No character schema: %s", CHARACTER_SCHEMA)

    raise SchemaError("Missing schema")


def flatten_schema(
    schema: Dict[str, Any], main_schema: Optional[Dict[str, Any]] = None
):
    """Resolve refs."""
    output: Dict[str, Any] = {}
    for key, value in schema.items():
        if key == "$ref":
            value = sub_schema(main_schema or schema, schema["$ref"])
            if isinstance(value, dict):
                value = flatten_schema(value, main_schema or schema)
                output = value | output
            else:
                raise NotImplementedError("WTF")
        elif isinstance(value, dict):
            output[key] = flatten_schema(value, main_schema or schema)
        else:
            output[key] = value
    return output


def load_schema(filename: Path) -> Dict[str, Any]:
    """Load schema from file."""
    with open(filename, "r", encoding="utf8") as f:
        try:
            if filename.suffix == ".json":
                data = json.load(f)
                return data
            if filename.suffix == ".yaml":
                data = yaml.safe_load(f)
                return data
        except Exception as e:
            logger.debug(e)
            raise SchemaError("Schema not saved in a known format") from e
    return {}


SchemaValidationError = Dict[str, str]


def validate(data: Dict, system: Gametag) -> List[SchemaValidationError]:
    """Validate a sheet against a system."""
    logger.debug("Getting schema")
    schema = get_schema(system)
    v = Draft7Validator(schema)
    return [
        {"path": "/".join(str(x) for x in e.path), "message": e.message}
        for e in v.iter_errors(data)
    ]


def build_boolean(schema: Dict[str, bool]) -> bool:
    """Build boolean."""
    logger.debug("build boolean: %s", schema["default"])
    return schema["default"]


def build_string(schema: Dict[str, str]) -> str:
    """Build string."""
    logger.debug("build string: %s", schema["default"])
    return schema["default"]


def build_integer(schema: Dict[str, int]) -> int:
    """Build integer."""
    logger.debug("build integer: %s", schema["default"])
    return schema["default"]


def build_object(schema: Dict[str, Any], main_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Build object."""
    logger.debug("build object")
    output = {}
    for prop, description in schema["properties"].items():
        output[prop] = build_from_schema_inner(description, main_schema)
    return output


def build_array(schema: Dict[str, List[Any]]) -> List[Any]:
    """Build array."""
    logger.debug("build array")
    if "default" in schema:
        return schema["default"]
    return []


def get_sub(d: Dict[str, Any], path: List[str]) -> Dict:
    """Get sub schema."""
    logger.debug("get_sub: %s", path)
    if len(path) == 1:
        return d[path[0]]

    p = path.pop(0)
    return get_sub(d[p], path)


def sub_schema(
    schema: Union[List, Dict], path: str
) -> Union[Dict, List, str, int, bool]:
    """Dive into sub schema."""
    logger.debug("sub_schema: %s", path)
    parts = path.split("/")
    if parts[0] != "#":
        raise NotImplementedError(path)

    assert isinstance(schema, dict)

    return get_sub(schema, parts[1:])


def build_from_schema_inner(
    schema: Union[List, Dict[str, Any]], main_schema: Dict[str, Any]
) -> Union[Dict, List, str, int, bool]:
    """Main loop of build_from_schema()"""
    if isinstance(schema, Dict):
        logger.debug("Handling a dictionary")
        if "default" in schema:
            return schema["default"]
        if "$ref" in schema:
            sub = sub_schema(main_schema, schema["$ref"])

            assert isinstance(sub, Dict) or isinstance(sub, List)

            return build_from_schema_inner(sub, main_schema)
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
        if "allOf" in schema:
            out = {}
            for entry in schema["allOf"]:
                all_of_data = build_from_schema_inner(entry, main_schema)
                assert isinstance(all_of_data, dict)
                out.update(all_of_data)
            return out
    elif isinstance(schema, List):
        logger.debug("Handling a list")
        raise NotImplementedError("Lists are not my strong suite.")

    return ""


def build_from_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Build a charactersheet from a schema."""
    built = build_from_schema_inner(schema, schema)
    assert isinstance(built, MutableMapping)
    return built
