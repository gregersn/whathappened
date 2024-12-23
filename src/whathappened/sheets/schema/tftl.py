from typing import Annotated, Literal, Optional
import yaml
from pydantic import BaseModel, ConfigDict, Field

from whathappened.sheets.schema.base import BaseSchema, Migration


def v006_to_007(data):
    data["meta"]["title"] = data["meta"]["Title"] or "Untitled"
    del data["meta"]["Title"]
    data["meta"]["creator"] = data["meta"]["Creator"]
    del data["meta"]["Creator"]
    data["meta"]["createdate"] = data["meta"]["CreateDate"]
    del data["meta"]["CreateDate"]
    data["meta"]["gamename"] = data["meta"]["GameName"]
    del data["meta"]["GameName"]
    data["meta"]["gameversion"] = data["meta"]["GameVersion"]
    del data["meta"]["GameVersion"]
    data["meta"]["gametype"] = data["meta"]["GameType"]
    del data["meta"]["GameType"]
    data["meta"]["disclaimer"] = data["meta"]["Disclaimer"]
    del data["meta"]["Disclaimer"]

    data["version"] = "0.0.7"
    return data


def v007_to_006(data):
    data["meta"]["Title"] = data["meta"]["title"]
    del data["meta"]["title"]
    data["meta"]["Creator"] = data["meta"]["creator"]
    del data["meta"]["creator"]
    data["meta"]["CreateDate"] = data["meta"]["createdate"]
    del data["meta"]["createdate"]
    data["meta"]["GameName"] = data["meta"]["gamename"]
    del data["meta"]["gamename"]
    data["meta"]["GameVersion"] = data["meta"]["gameversion"]
    del data["meta"]["gameversion"]
    data["meta"]["GameType"] = data["meta"]["gametype"]
    del data["meta"]["gametype"]
    data["meta"]["Disclaimer"] = data["meta"]["disclaimer"]
    del data["meta"]["disclaimer"]

    data["version"] = "0.0.6"
    return data


migrations = [
    Migration("0.0.1", "0.0.4"),
    Migration("0.0.4", "0.0.5"),
    Migration("0.0.6", "0.0.7", v006_to_007, v007_to_006),
]


class SheetInfo(BaseModel):
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    title: str = "New character"
    creator: str = "What happened? A TTRPG utility"
    createdate: Annotated[str, Field(title="CreateDate")] = ""
    gamename: Annotated[str, Field(title="GameName")] = "Tales From The Loop"
    gameversion: Annotated[str, Field(title="GameVersion")] = ""
    gametype: Annotated[str, Field(title="GameType")] = ""
    disclaimer: str = "We're not gonna take it!"


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
    meta: Annotated[SheetInfo, Field(default_factory=SheetInfo)]
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
