"""Vaesen schema."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field
import yaml


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


class SheetInfo(BaseModel):
    """Basic information about the character sheet."""

    gamename: Literal["Vaesen"] = "Vaesen"
    title: str = "Unknown"


class Attributes(BaseModel):
    physique: int = Field(ge=2, le=5, default=2)
    precision: int = Field(ge=2, le=5, default=2)
    logic: int = Field(ge=2, le=5, default=2)
    empathy: int = Field(ge=2, le=5, default=2)


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
    talents: list[str] = []
    insights: list[str] = Field(title="Insights & defects", default=[])
    advantages: str = ""
    equipment: list[Equipment] = Field(
        default=[], json_schema_extra={"widget": "table", "header": True}
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
    memento: str = ""


class Personality(BaseModel):
    name: str = ""
    age: int = 17
    archetype: Archetype = Field(title="Archetype", default=Archetype.ACADEMIC)
    motivation: str = ""
    trauma: str = ""
    dark_secret: str = ""
    relationships: list[str] = Field(
        title="Relationships",
        default=["PC 1", "PC 2", "PC 3", "PC 4"],
        min_length=4,
        max_length=4,
        json_schema_extra={"constant": True},
    )
    description: str = ""


class Characteristics(BaseModel):
    attributes: Attributes = Field(title="Attributes", default_factory=Attributes)
    resources: int = 1
    conditions: Conditions = Field(title="Conditions", default_factory=Conditions)
    skills: Skills = Field(title="Skills", default_factory=Skills)
    experience: int = Field(
        title="Experience",
        ge=0,
        le=10,
        default=0,
        json_schema_extra={"widget": "progress"},
    )


class Character(BaseModel):
    """Character information."""

    personalia: Personality = Field(title="Personalia", default_factory=Personality)
    miscellaneous: Miscellaneous = Field(
        title="Miscellaneous", default_factory=Miscellaneous
    )
    characteristics: Characteristics = Field(
        title="Characteristics", default_factory=Characteristics
    )


class Vaesen(BaseModel):
    """Charactersheet for Vaesen."""

    system: Literal["vaesen"] = "vaesen"
    meta: SheetInfo = SheetInfo()
    character_sheet: Character = Field(title="Vaesen", default_factory=Character)


CharacterSheet = Vaesen

if __name__ == "__main__":
    print(yaml.dump(Vaesen.model_json_schema()))
