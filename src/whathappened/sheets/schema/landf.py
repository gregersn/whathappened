from enum import Enum
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


class SheetInfo(BaseModel):
    """Basic info about the sheet."""

    gamename: str = ""
    title: str = "Unknown"


class LasersAndFeelingsCharacter(BaseModel):
    """Character information."""

    name: str = Field(title="Character name", default="Ace")
    style: Annotated[
        CharacterStyle, Field(title="Character style")
    ] = CharacterStyle.HEROIC
    role: Annotated[
        CharacterRole, Field(title="Character role")
    ] = CharacterRole.SOLDIER
    inventory: list[str] = Field(
        ["Consortium uniform", "Communicator", "Pistol"], title="Inventory"
    )
    goal: str = Field("Meet new aliens", title="Character goal")
    stat: int = Field(4, title="Lasers or feelings", ge=2, le=5)


class LasersAndFeelings(BaseModel):
    """Character sheet."""

    system: str = Field("landf")
    meta: SheetInfo = Field(SheetInfo(gamename="Lasers and feelings"))
    character_sheet: LasersAndFeelingsCharacter = Field(
        LasersAndFeelingsCharacter(), title="Lasers And Feelings"
    )


CharacterSheet = LasersAndFeelings

if __name__ == "__main__":
    print(
        yaml.dump(LasersAndFeelings.model_json_schema(mode="serialization"), indent=2)
    )

    print(LasersAndFeelings().model_dump_json())
