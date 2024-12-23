"""Vaesen Headquarters sheet."""

from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field
import yaml

from whathappened.sheets.schema.base import BaseSchema, Migration


def v004_to_v005(data):
    data["character_sheet"]["information"]["picture"] = None
    data["version"] = "0.0.5"
    return data


def v005_to_v004(data):
    del data["character_sheet"]["information"]["picture"]
    data["version"] = "0.0.4"
    return data


migrations = [
    Migration("0.0.4", "0.0.5", v004_to_v005, v005_to_v004),
]


class SheetInfo(BaseModel):
    """Basic information about the character sheet."""

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

    function: str = "No function"
    asset: str = "No asset"


class Upgrades(BaseModel):
    """Upgrades to headquarters."""

    facilities: list[Upgrade] = Field(
        default=[], json_schema_extra={"widget": "table", "header": True}
    )
    discovered_facilities: list[Upgrade] = Field(
        default=[], json_schema_extra={"widget": "table", "header": True}
    )
    contacts: list[Upgrade] = Field(
        default=[], json_schema_extra={"widget": "table", "header": True}
    )
    personell: list[Upgrade] = Field(
        default=[], json_schema_extra={"widget": "table", "header": True}
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
