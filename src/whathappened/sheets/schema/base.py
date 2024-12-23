from dataclasses import dataclass
from typing import Callable, Literal, Optional
from typing_extensions import Annotated

from pydantic import BaseModel, ConfigDict, Field

CURRENT_SCHEMA_VERSION_TYPE = Literal["0.0.5"]
CURRENT_SCHEMA_VERSION = "0.0.5"


@dataclass
class Migration:
    """Migration info."""

    from_version: str
    to: str
    up: Optional[Callable] = None
    down: Optional[Callable] = None


Gametag = Literal["landf", "tftl", "coc7e", "dod", "vaesen", "vaesenhq"]


def v000_to_004(data):
    data["version"] = "0.0.4"
    return data


def v004_to_000(data):
    del data["version"]
    return data


def v004_to_005(data):
    data["version"] = "0.0.5"
    data["character_sheet"]["personalia"]["portrait"] = None
    return data


def v005_to_004(data):
    data["version"] = "0.0.4"
    del data["character_sheet"]["personalia"]["portrait"]
    return data


migrations: list[Migration] = [
    Migration("0.0.0", "0.0.4", v000_to_004, v004_to_000),
    Migration("0.0.4", "0.0.5", v004_to_005, v005_to_004),
]


class BaseSchema(BaseModel):
    """Base Character schema."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    version: str = CURRENT_SCHEMA_VERSION
