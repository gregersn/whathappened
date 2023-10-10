from enum import Enum
import json
from typing_extensions import Annotated
import yaml

from pydantic import BaseModel, Field


class CharacterStyle(str, Enum):
    """What style of character being played."""

    ALIEN = "Alien"
    DROID = "Droid"
    DANGEROUS = "Dangerous"
    HEROIC = "Heroic"
    HOTSHOT = "Hot-Shot"
    INTREPID = "Intrepid"
    SAVVY = "Savvy"


class CharacterRole(str, Enum):
    """The characters role."""

    DOCTOR = "Doctor"
    ENVOY = "Envoy"
    ENGINEER = "Engineer"
    EXPLORER = "Explorer"
    PILOT = "Pilot"
    SCIENTIST = "Scientist"
    SOLDIER = "Soldier"


class SheetInfo(BaseModel, frozen=True):
    """Basic info about the sheet."""

    gamename: str = "Lasers and feelings"
    title: str = "Unknown"


class LasersAndFeelingsCharacter(BaseModel, frozen=True):
    """Character information."""

    name: str = Field(default="Ace", title="Character name")
    style: CharacterStyle = Field(CharacterStyle.HEROIC, title="Character style")
    role: CharacterRole = Field(CharacterRole.SOLDIER, title="Character role")
    inventory: list[str] = Field(
        title="Inventory",
        default_factory=lambda: ["Consortium uniform", "Communicator", "Pistol"],
    )
    goal: str = Field(title="Character goal", default="Meet new aliens")
    stat: int = Field(
        ge=2,
        le=5,
        title="Lasers or feelings",
        default=4,
    )


class LasersAndFeelings(BaseModel):
    """Character sheet."""

    system: str = Field(default="landf")
    meta: SheetInfo = SheetInfo()

    character_sheet: LasersAndFeelingsCharacter = Field(
        LasersAndFeelingsCharacter(), title="Lasers And Feelings"
    )


CharacterSheet = LasersAndFeelings

if __name__ == "__main__":
    print(
        json.dumps(LasersAndFeelings.model_json_schema(mode="serialization"), indent=4)
    )

    # print(LasersAndFeelings().model_dump_json())
