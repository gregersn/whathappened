"""Lasers and Feelings schema."""

from enum import Enum
from typing import Literal
import yaml

from pydantic import BaseModel, ConfigDict, Field

from whathappened.sheets.schema.base import BaseSheet, SheetInfo, Gametag


class CharacterStyle(str, Enum):
    """What style of character being played."""

    ALIEN = "Alien"
    DANGEROUS = "Dangerous"
    DROID = "Droid"
    HEROIC = "Heroic"
    HOTSHOT = "Hot-Shot"
    INTREPID = "Intrepid"
    SAVVY = "Savvy"


class CharacterRole(str, Enum):
    """The characters role."""

    DOCTOR = "Doctor"
    ENGINEER = "Engineer"
    ENVOY = "Envoy"
    EXPLORER = "Explorer"
    PILOT = "Pilot"
    SCIENTIST = "Scientist"
    SOLDIER = "Soldier"


class LasersAndFeelingsCharacter(BaseModel):
    """Character information."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    name: str = Field(title="Character name", default="Ace")
    style: CharacterStyle = Field(
        title="Character style", default=CharacterStyle.HEROIC
    )
    role: CharacterRole = Field(title="Character role", default=CharacterRole.SOLDIER)
    inventory: list[str] = Field(
        title="Inventory",
        default=["Consortium uniform", "Communicator", "Pistol"],
    )
    goal: str = Field(title="Character goal", default="Meet new aliens")
    stat: int = Field(
        ge=2,
        le=5,
        title="Lasers or feelings",
        default=4,
    )


class LasersAndFeelings(BaseSheet):
    """Character sheet."""

    system: Gametag = "landf"
    meta: SheetInfo = SheetInfo(gamename="Lasers and Feelings")

    character_sheet: LasersAndFeelingsCharacter = Field(
        default_factory=LasersAndFeelingsCharacter
    )


CharacterSheet = LasersAndFeelings

if __name__ == "__main__":
    print(yaml.dump(LasersAndFeelings.model_json_schema()))

    # print(LasersAndFeelings().model_dump_json())
