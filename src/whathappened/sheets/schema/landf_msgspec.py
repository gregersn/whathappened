from enum import Enum
from typing_extensions import Annotated
import yaml

import msgspec


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


class SheetInfo(msgspec.Struct):
    """Basic info about the sheet."""

    gamename: str = ""
    title: str = "Unknown"


class LasersAndFeelingsCharacter(msgspec.Struct):
    """Character information."""

    name: str = msgspec.field(name="Character name", default="Ace")
    style: Annotated[
        CharacterStyle, msgspec.field(name="Character style")
    ] = CharacterStyle.HEROIC
    role: Annotated[
        CharacterRole, msgspec.field(name="Character role")
    ] = CharacterRole.SOLDIER
    inventory: list[str] = msgspec.field(
        default_factory=lambda: ["Consortium uniform", "Communicator", "Pistol"],
        name="Inventory",
    )
    goal: str = msgspec.field(default="Meet new aliens", name="Character goal")
    stat: Annotated[int, msgspec.Meta(ge=2, le=5)] = msgspec.field(
        default=4, name="Lasers or feelings"
    )


class LasersAndFeelings(msgspec.Struct):
    """Character sheet."""

    system: str = msgspec.field(default="landf")
    meta: SheetInfo = msgspec.field(
        default_factory=lambda: SheetInfo(gamename="Lasers and feelings")
    )
    character_sheet: LasersAndFeelingsCharacter = msgspec.field(
        default_factory=lambda: LasersAndFeelingsCharacter(), name="Lasers And Feelings"
    )


CharacterSheet = LasersAndFeelings

if __name__ == "__main__":
    print(yaml.dump(msgspec.json.schema(LasersAndFeelings)))

    # print(LasersAndFeelings().model_dump_json())
