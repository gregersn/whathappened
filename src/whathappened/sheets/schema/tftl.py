"""Tales from the Loop schema."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Optional
from pydantic import BaseModel, Field
import yaml

from whathappened.sheets.schema.base import BaseSheet, SheetInfo, Gametag


class Archetype(str, Enum):
    """Character archetype"""

    ACADEMIC = "Academic"
    DOCTOR = "Doctor"
    HUNTER = "Hunter"
    OCCULTIST = "Occultist"
    OFFICER = "Officer"
    PRIEST = "Priest"
    PRIVATE_DETECTIVE = "Private detective"
    SERVANT = "Servant"
    VAGABOND = "Vagabond"
    WRITER = "Writer"


class Attributes(BaseModel):
    physique: int = Field(
        ge=2, le=5, default=2, description="How big and strong you are."
    )
    precision: int = Field(
        ge=2, le=5, default=2, description="Coordination and motor skills."
    )
    logic: int = Field(ge=2, le=5, default=2, description="Intellectual capacity.")
    empathy: int = Field(
        ge=2, le=5, default=2, description="Your ability to understand other people."
    )


class Skills(BaseModel):
    agility: int = Field(ge=0, le=5, default=0, title="Agility (Physique)")
    close_combat: int = Field(ge=0, le=5, default=0, title="Close combat (Physique)")
    force: int = Field(ge=0, le=5, default=0, title="Force (Physique)")

    medicine: int = Field(ge=0, le=5, default=0, title="Medicine (Precision)")
    ranged_combat: int = Field(ge=0, le=5, default=0, title="Ranged combat (Precision)")
    stealth: int = Field(ge=0, le=5, default=0, title="Stealth (Precision)")

    investigation: int = Field(ge=0, le=5, default=0, title="Investigation (Logic)")
    learning: int = Field(ge=0, le=5, default=0, title="Learning (Logic)")
    vigilance: int = Field(ge=0, le=5, default=0, title="Vigilance (Logic)")

    inspiration: int = Field(ge=0, le=5, default=0, title="Inspiration (Empathy)")
    manipulation: int = Field(ge=0, le=5, default=0, title="Manipulation (Empathy)")
    observation: int = Field(ge=0, le=5, default=0, title="Observation (Empathy)")


@dataclass
class Armor:
    type: str
    protection: int
    agility: int


class Armors(str, Enum):
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


ArmorStats: dict[str, str] = {
    "none": "(none), protection: 0, agility: 0",
    "light": "Light, protection: 2, agility: -1",
    "medium": "Medium, protection: 4, agility: -2",
    "heavy": "Heavy, protection: 6, agility: -3",
}


class Weapon(BaseModel):
    weapon: str = "Pocket lint"
    damage: int = 0
    range: str = "None"
    bonus: int = 0


class Equipment(BaseModel):
    description: str = "Pocket lint"
    bonus: int = 0


class PhysicalConditions(BaseModel):
    exhausted: bool = False
    battered: bool = False
    wounded: bool = False
    broken: bool = False


class MentalConditions(BaseModel):
    angry: bool = False
    frightened: bool = False
    hopeless: bool = False
    broken: bool = False


class Conditions(BaseModel):
    physical: PhysicalConditions = Field(
        title="Physical", default_factory=PhysicalConditions
    )
    mental: MentalConditions = Field(title="Mental", default_factory=MentalConditions)


class Miscellaneous(BaseModel):
    talents: list[str] = Field(
        [],
        description="Tricks, traits and abilities that can benefit you in various situations.",
    )
    insights: list[str] = Field(title="Insights & defects", default=[])
    advantages: str = Field(
        "", description="What can help you on your current adventure?"
    )
    equipment: list[Equipment] = Field(
        default=[],
        json_schema_extra={"widget": "table", "header": True},
        description="All your things.",
    )
    armor: Armors = Field(
        title="Armor",
        default=Armors.NONE,
        json_schema_extra={"choice_values": ArmorStats},
    )
    weapons: list[Weapon] = Field(
        default_factory=lambda: [],
        json_schema_extra={
            "widget": "table",
            "header": True,
            "hide_title": True,
        },
    )
    memento: str = Field("", description="Something that's a part of you.")


class Pride(BaseModel):
    description: str = "Unkown"
    used: bool = False


class Personality(BaseModel):
    name: str = Field("Unknown", description="How should you be adressed?")
    type: str = Field("Unknown")
    age: str = Field("Unknown")
    luck_points: int = Field(0, ge=0, le=5)
    drive: str = Field("Unknown")
    anchor: str = Field("Unknown")
    problem: str = Field("Unknown")
    pride: Pride = Field(default_factory=Pride)
    description: str = Field("Unknown")
    favorite_song: str = Field("Unknown")
    portrait: Optional[str] = None


class Characteristics(BaseModel):
    attributes: Attributes = Field(
        title="Attributes",
        default_factory=Attributes,
        description="Each attribute has a value between 2 and 5 and determines the number of dice you roll when attempting things that depend on the attribute in question.",
    )
    resources: int = Field(
        default=1,
        description="How much capital you have at your disposal. 1 - destitude, 8 - filthy rich.",
    )
    conditions: Conditions = Field(title="Conditions", default_factory=Conditions)
    skills: Skills = Field(
        title="Skills",
        default_factory=Skills,
        description="Acquired knowledge, training and experience. Value between 0 and 5.",
    )
    experience: int = Field(
        title="Experience",
        ge=0,
        le=20,
        default=0,
        json_schema_extra={"widget": "progress"},
    )


class Relationships(BaseModel):
    kids: list[str] = Field(default=["Unknown"])
    npcs: list[str] = Field(default=["Unknown"])


class Condition(BaseModel):
    Upset: bool = False
    Scared: bool = False
    Exhausted: bool = False
    Injured: bool = False
    Broken: bool = False


class Item(BaseModel):
    name: str = "Pocket lint"
    bonus: int = Field(default=1, ge=1, le=3)


class Attributes(BaseModel):
    Body: Annotated[int, Field(ge=1, le=5)] = 1
    Tech: Annotated[int, Field(ge=1, le=5)] = 1
    Heart: Annotated[int, Field(ge=1, le=5)] = 1
    Mind: Annotated[int, Field(ge=1, le=5)] = 1


class Skills(BaseModel):
    Sneak: Annotated[int, Field(alias="Sneak (Body)", ge=0, le=5)] = 0
    Force: Annotated[int, Field(alias="Force (Body)", ge=0, le=5)] = 0
    Move: Annotated[int, Field(alias="Move (Body)", ge=0, le=5)] = 0
    Tinker: Annotated[int, Field(alias="Tinker (Tech)", ge=0, le=5)] = 0
    Program: Annotated[int, Field(alias="Program (Tech)", ge=0, le=5)] = 0
    Calculate: Annotated[int, Field(alias="Calculate (Tech)", ge=0, le=5)] = 0
    Contact: Annotated[int, Field(alias="Contact (Heart)", ge=0, le=5)] = 0
    Charm: Annotated[int, Field(alias="Charm (Heart)", ge=0, le=5)] = 0
    Lead: Annotated[int, Field(alias="Lead (Heart)", ge=0, le=5)] = 0
    Investigate: Annotated[int, Field(alias="Investigate (Mind)", ge=0, le=5)] = 0
    Comprehend: Annotated[int, Field(alias="Comprehend (Mind)", ge=0, le=5)] = 0
    Empathize: Annotated[int, Field(alias="Empathize (Mind)", ge=0, le=5)] = 0


class Character(BaseModel):
    """Character information."""

    personalia: Personality = Field(title="Personalia", default_factory=Personality)
    relationships: Relationships = Field(
        default_factory=Relationships, serialization_alias="relationships"
    )
    items: list[Item] = Field(default_factory=lambda: [Item()])
    hideout: str = "Tree hut"
    notes: str = ""
    attributes: Attributes = Attributes()
    conditions: Conditions = Field(default_factory=Conditions)
    skills: Skills = Skills()
    experience: int = Field(0, ge=0, le=10)


class TalesFromTheLoop(BaseSheet):
    """Charactersheet for Tales from the Loop."""

    system: Gametag = "tftl"
    meta: SheetInfo = SheetInfo(gamename="Tales from the Loop")
    character_sheet: Character = Field(
        title="Tales from the Loop", default_factory=Character
    )


CharacterSheet = TalesFromTheLoop

if __name__ == "__main__":
    print(yaml.dump(TalesFromTheLoop.model_json_schema()))
