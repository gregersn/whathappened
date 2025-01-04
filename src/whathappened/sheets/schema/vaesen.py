"""Vaesen schema."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Literal, Optional, cast
from pydantic import BaseModel, ConfigDict, Field, JsonValue
import yaml

from whathappened.sheets.schema.base import BaseSchema


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

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    gamename: Literal["Vaesen"] = "Vaesen"
    title: str = "Unknown"


class Attributes(BaseModel):
    """Character attributes."""

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
    """Character skills."""

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
    """Armor data."""

    type: str
    protection: int
    agility: int


class Armors(str, Enum):
    """Armor types."""

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
    """Weapons data."""

    weapon: str = "Pocket lint"
    damage: int = 0
    range: str = "None"
    bonus: int = 0


class Equipment(BaseModel):
    """Equipment data."""

    description: str = "Pocket lint"
    bonus: int = 0


class PhysicalConditions(BaseModel):
    """Current physical conditions for the character."""

    exhausted: bool = False
    battered: bool = False
    wounded: bool = False
    broken: bool = False


class MentalConditions(BaseModel):
    """Current mental conditions for the character."""

    angry: bool = False
    frightened: bool = False
    hopeless: bool = False
    broken: bool = False


class Conditions(BaseModel):
    """A characters current conditions."""

    physical: PhysicalConditions = Field(
        title="Physical", default_factory=PhysicalConditions
    )
    mental: MentalConditions = Field(title="Mental", default_factory=MentalConditions)


class Miscellaneous(BaseModel):
    """Miscellaneous information about the character."""

    talents: Annotated[
        list[str],
        Field(
            description="Tricks, traits and abilities that can benefit you in various situations.",
        ),
    ] = []
    insights: Annotated[list[str], Field(title="Insights & defects")] = []
    advantages: Annotated[
        str, Field(description="What can help you on your current adventure?")
    ] = ""
    equipment: Annotated[
        list[Equipment],
        Field(
            json_schema_extra={"widget": "table", "header": True},
            description="All your things.",
        ),
    ] = []
    armor: Annotated[
        Armors,
        Field(
            title="Armor",
            json_schema_extra={"choice_values": cast(JsonValue, ArmorStats)},
        ),
    ] = Armors.NONE
    weapons: Annotated[
        list[Weapon],
        Field(
            json_schema_extra={
                "widget": "table",
                "header": True,
                "hide_title": True,
            },
        ),
    ] = []
    memento: Annotated[str, Field(description="Something that's a part of you.")] = ""


class Personality(BaseModel):
    """Information about character personality."""

    name: Annotated[str, Field(description="How should you be adressed?")] = ""
    age: Annotated[
        int,
        Field(
            description="Young: 17-25 years, middle-aged: 26-50 years, old: 51+ years."
        ),
    ] = 17
    archetype: Annotated[
        Archetype,
        Field(
            title="Archetype",
            description="The skeleton of your character.",
        ),
    ] = Archetype.ACADEMIC
    motivation: Annotated[
        str,
        Field(
            description="Why are you willing to risk your own life to track down and fight vaesen?",
        ),
    ] = ""
    trauma: Annotated[str, Field(description="What event gave you the Sight?")] = ""
    dark_secret: Annotated[
        str, Field(description="A problem you are ashamed of, and keep to yourself.")
    ] = ""
    relationships: Annotated[
        list[str],
        Field(
            title="Relationships",
            min_length=4,
            max_length=4,
            json_schema_extra={"constant": True},
            description="Your relationship to the other characters.",
        ),
    ] = ["PC 1", "PC 2", "PC 3", "PC 4"]

    description: Annotated[str, Field(json_schema_extra={"widget": "text"})] = ""
    portrait: Annotated[
        Optional[str], Field(json_schema_extra={"widget": "portrait"})
    ] = ""


class Characteristics(BaseModel):
    """All the characteristics of the character."""

    attributes: Annotated[
        Attributes,
        Field(
            title="Attributes",
            default_factory=Attributes,
            description="Each attribute has a value between 2 and 5 and determines the number of dice you roll when attempting things that depend on the attribute in question.",
        ),
    ] = Attributes()
    resources: Annotated[
        int,
        Field(
            description="How much capital you have at your disposal. 1 - destitude, 8 - filthy rich.",
        ),
    ] = 1
    conditions: Annotated[
        Conditions, Field(title="Conditions", default_factory=Conditions)
    ] = Conditions()
    skills: Annotated[
        Skills,
        Field(
            title="Skills",
            default_factory=Skills,
            description="Acquired knowledge, training and experience. Value between 0 and 5.",
        ),
    ] = Skills()
    experience: Annotated[
        int,
        Field(
            title="Experience",
            ge=0,
            le=20,
            json_schema_extra={"widget": "progress"},
        ),
    ] = 0


class Character(BaseModel):
    """Character information."""

    personalia: Annotated[
        Personality, Field(title="Personalia", default_factory=Personality)
    ] = Personality()
    miscellaneous: Annotated[
        Miscellaneous, Field(title="Miscellaneous", default_factory=Miscellaneous)
    ] = Miscellaneous()
    characteristics: Annotated[
        Characteristics,
        Field(title="Characteristics", default_factory=Characteristics),
    ] = Characteristics()


class Vaesen(BaseSchema):
    """Charactersheet for Vaesen."""

    system: Literal["vaesen"] = "vaesen"
    meta: SheetInfo = SheetInfo()
    character_sheet: Annotated[
        Character, Field(title="Vaesen", default_factory=Character)
    ]


CharacterSheet = Vaesen

if __name__ == "__main__":
    print(yaml.dump(Vaesen.model_json_schema()))
