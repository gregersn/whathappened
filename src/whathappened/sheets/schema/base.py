from dataclasses import dataclass
from typing import Callable, Literal, Optional
from typing_extensions import Annotated

from pydantic import BaseModel, ConfigDict, Field

CURRENT_SCHEMA_VERSION_TYPE = Literal["0.0.4"]
CURRENT_SCHEMA_VERSION = "0.0.4"


@dataclass
class Migration:
    """Migration info."""

    from_version: str
    to: str
    up: Optional[Callable] = None
    down: Optional[Callable] = None


Gametag = Literal["landf", "tftl", "coc7e", "dod", "vaesen", "vaesenhq"]


def v000_to_004(data):
    data = data.copy()
    data["version"] = "0.0.4"
    return data


def v004_to_000(data):
    data = data.copy()
    del data["version"]
    return data


migrations: list[Migration] = [Migration("0.0.0", "0.0.4", v000_to_004, v004_to_000)]


class BaseSchema(BaseModel):
    """Base Character schema."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    version: str = CURRENT_SCHEMA_VERSION
