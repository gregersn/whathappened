"""Vaesen Headquarters sheet."""

from typing import Annotated, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
import yaml

from whathappened.core.sheets.schema.base import BaseSchema, Migration


def v004_to_v005(data):
    data["character_sheet"]["information"]["picture"] = None
    data["version"] = "0.0.5"
    return data


def v005_to_v004(data):
    del data["character_sheet"]["information"]["picture"]
    data["version"] = "0.0.4"
    return data


def v008_to_v009(data):
    data["version"] = "0.0.9"

    upgrades = ["contacts", "discovered_facilities", "facilities", "personell"]

    for upgrade in upgrades:
        for added in data["character_sheet"]["upgrades"][upgrade]:
            if "title" not in added:
                added["title"] = "No title"

    return data


def v009_to_v008(data):
    data["version"] = "0.0.8"

    upgrades = ["contacts", "discovered_facilities", "facilities", "personell"]

    for upgrade in upgrades:
        for added in data["character_sheet"]["upgrades"][upgrade]:
            if "title" in added:
                del added["title"]
    return data


migrations = [
    Migration("0.0.4", "0.0.5", v004_to_v005, v005_to_v004),
    Migration("0.0.8", "0.0.9", v008_to_v009, v009_to_v008),
]


class SheetInfo(BaseModel):
    """Basic information about the character sheet."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    gamename: Literal["Vaesen"] = "Vaesen"
    title: str = "Unknown"


class Information(BaseModel):
    """Basic information about headquarters."""

    name: str = "Unknown"
    type_of_building: str = "Unknown"
    location: str = "Somewhere"
    development_points: int = 0
    picture: Annotated[
        Optional[str], Field(json_schema_extra={"widget": "portrait"})
    ] = ""


class Upgrade(BaseModel):
    """Information about an upgrade."""

    title: str = "No title"
    function: str = "No function"
    asset: str = "No asset"


class Upgrades(BaseModel):
    """Upgrades to headquarters."""

    facilities: list[Upgrade] = Field(
        default=[], json_schema_extra={"widget": "table", "header": False}
    )
    discovered_facilities: list[Upgrade] = Field(
        default=[], json_schema_extra={"widget": "table", "header": False}
    )
    contacts: list[Upgrade] = Field(
        default=[], json_schema_extra={"widget": "table", "header": False}
    )
    personell: list[Upgrade] = Field(
        default=[], json_schema_extra={"widget": "table", "header": False}
    )


class Headquarters(BaseModel):
    """Headquarters."""

    information: Information = Field(title="Information", default_factory=Information)
    upgrades: Upgrades = Field(title="Upgrades", default_factory=Upgrades)


class Vaesen(BaseSchema):
    """Charactersheet for Vaesen."""

    system: Literal["vaesenhq"] = "vaesenhq"
    meta: SheetInfo = SheetInfo()
    character_sheet: Headquarters = Field(
        title="Vaesen Headquarters", default_factory=Headquarters
    )


CharacterSheet = Vaesen

if __name__ == "__main__":
    print(yaml.dump(Vaesen.model_json_schema()))
