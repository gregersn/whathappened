from typing import Annotated, Literal, Optional
import yaml
from pydantic import BaseModel, ConfigDict, Field

from whathappened.sheets.schema.base import BaseSchema, Migration


def v001_to_004(data):
    data = data.copy()
    data["version"] = "0.0.4"
    return data


def v004_to_001(data):
    data = data.copy()
    data["version"] = "0.0.1"
    return data


migrations = [Migration("0.0.1", "0.0.4", v001_to_004, v004_to_001)]


class Meta(BaseModel):
    Title: str = "New character"
    Creator: str = "What happened? A TTRPG utility"
    CreateDate: Annotated[str, Field(title="CreateDate")] = ""
    GameName: Annotated[str, Field(title="GameName")] = "Tales From The Loop"
    GameVersion: Annotated[str, Field(title="GameVersion")] = ""
    GameType: Annotated[str, Field(title="GameType")] = ""
    Disclaimer: str = "We're not gonna take it!"


class Pride(BaseModel):
    description: str = "Unknown"
    used: bool = False


class Personalia(BaseModel):
    name: str = Field(default="Unknown", description="How should you be adressed?")
    type: str = Field(default="Unknown")
    age: str = Field(default="Unknown")
    luck_points: int = Field(default=0, ge=0, le=5)
    drive: str = Field(default="Unknown")
    anchor: str = Field(default="Unknown")
    problem: str = Field(default="Unknown")
    pride: Pride = Field(default_factory=Pride)
    description: str = Field(default="Unknown")
    favorite_song: str = Field(default="Unknown")
    portrait: Optional[str] = ""


class Relationships(BaseModel):
    kids: list[str] = ["Unknown"]
    npcs: list[str] = ["Unknown"]


class Item(BaseModel):
    name: str = "Pocket lint"
    bonus: Annotated[Optional[int], Field(default=1, ge=1, le=3)] = 1


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


class Conditions(BaseModel):
    Upset: bool = False
    Scared: bool = False
    Exhausted: bool = False
    Injured: bool = False
    Broken: bool = False


class TalesFromTheLoop(BaseSchema):
    """Tales from the Loop sheet."""

    model_config = ConfigDict(
        frozen=True, json_schema_serialization_defaults_required=True
    )

    system: Annotated[Literal["tftl"], Field(frozen=True)] = "tftl"
    meta: Annotated[Meta, Field(default_factory=Meta)]
    personalia: Annotated[Personalia, Field(default_factory=Personalia)]
    relationships: Annotated[Relationships, Field(default_factory=Relationships)]
    items: Annotated[list[Item], Field(default_factory=lambda: [Item()])]
    hideout: str = "Tree hut"
    notes: str = ""
    attributes: Attributes = Attributes()
    conditions: Conditions = Conditions()
    skills: Skills = Skills()
    experience: Annotated[int, Field(ge=0, le=10)] = 0


CharacterSheet = TalesFromTheLoop

if __name__ == "__main__":
    print(yaml.dump(TalesFromTheLoop.model_json_schema()))
