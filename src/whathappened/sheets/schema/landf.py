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


class SheetInfo(msgspec.Struct, frozen=True):
    """Basic info about the sheet."""

    gamename: str = "Lasers and feelings"
    title: str = "Unknown"


class LasersAndFeelingsCharacter(msgspec.Struct, frozen=True):
    """Character information."""

    name: Annotated[str, msgspec.Meta(title="Character name")] = msgspec.field(
        default="Ace"
    )
    style: Annotated[
        CharacterStyle, msgspec.Meta(title="Character style")
    ] = CharacterStyle.HEROIC
    role: Annotated[
        CharacterRole, msgspec.Meta(title="Character role")
    ] = CharacterRole.SOLDIER
    inventory: Annotated[list[str], msgspec.Meta(title="Inventory")] = msgspec.field(
        default_factory=lambda: ["Consortium uniform", "Communicator", "Pistol"],
    )
    goal: Annotated[str, msgspec.Meta(title="Character goal")] = msgspec.field(
        default="Meet new aliens"
    )
    stat: Annotated[
        int, msgspec.Meta(ge=2, le=5, title="Lasers or feelings")
    ] = msgspec.field(
        default=4,
    )


class LasersAndFeelings(msgspec.Struct):
    """Character sheet."""

    system: str = msgspec.field(default="landf")
    meta: SheetInfo = SheetInfo()

    character_sheet: Annotated[
        LasersAndFeelingsCharacter, msgspec.Meta(title="Lasers And Feelings")
    ] = LasersAndFeelingsCharacter()


CharacterSheet = LasersAndFeelings

if __name__ == "__main__":
    print(yaml.dump(msgspec.json.schema(LasersAndFeelings)))

    # print(LasersAndFeelings().model_dump_json())
