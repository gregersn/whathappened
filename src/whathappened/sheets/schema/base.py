import typing
from pydantic import BaseModel, ConfigDict

Gametag = typing.Literal["landf", "tftl", "coc7e", "dod", "vaesen"]
SYSTEMS: list[str] = list(typing.get_args(Gametag))

try:
    from whathappened._version import __version__
except ModuleNotFoundError:
    __version__ = "unknown"


class SheetInfo(BaseModel):
    model_config = ConfigDict(
        json_schema_serialization_defaults_required=True, extra="ignore"
    )

    gamename: str
    title: str = "Unknown"


class BaseSheet(BaseModel):
    """Basic info about the sheet."""

    model_config = ConfigDict(
        json_schema_serialization_defaults_required=True, extra="ignore"
    )

    system: Gametag
    version: str = __version__

    meta: SheetInfo
