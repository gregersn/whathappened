from typing import Annotated, Literal, Optional
import yaml
from pydantic import BaseModel, ConfigDict, Field

from whathappened.core.sheets.schema.base import BaseSchema, Migration


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


v007_to_v008_skillnames = (
    ("Calculate (Tech)", "calculate"),
    ("Charm (Heart)", "charm"),
    ("Comprehend (Mind)", "comprehend"),
    ("Contact (Heart)", "contact"),
    ("Empathize (Mind)", "empathize"),
    ("Force (Body)", "force"),
    ("Investigate (Mind)", "investigate"),
    ("Lead (Heart)", "lead"),
    ("Move (Body)", "move"),
    ("Program (Tech)", "program"),
    ("Sneak (Body)", "sneak"),
    ("Tinker (Tech)", "tinker"),
)


def v007_to_v008(data):
    keys_to_move = (
        "attributes",
        "conditions",
        "experience",
        "hideout",
        "items",
        "notes",
        "personalia",
        "relationships",
        "skills",
    )
    data["character_sheet"] = {}
    for key in keys_to_move:
        data["character_sheet"][key] = data[key]
        del data[key]

    for container in ("attributes", "conditions"):
        for_deletion = []
        for key, value in dict(data["character_sheet"][container]).items():
            data["character_sheet"][container][key.lower()] = value
            for_deletion.append(key)

        for key in for_deletion:
            del data["character_sheet"][container][key]

    for old, new in v007_to_v008_skillnames:
        data["character_sheet"]["skills"][new] = data["character_sheet"]["skills"].pop(
            old
        )

    data["version"] = "0.0.8"
    return data


def v008_to_v007(data):
    keys_to_move = (
        "attributes",
        "conditions",
        "experience",
        "hideout",
        "items",
        "notes",
        "personalia",
        "relationships",
        "skills",
    )

    for container in ("attributes", "conditions"):
        for_deletion = []
        for key, value in dict(data["character_sheet"][container]).items():
            data["character_sheet"][container][key.capitalize()] = value
            for_deletion.append(key)

        for key in for_deletion:
            del data["character_sheet"][container][key]

    for old, new in v007_to_v008_skillnames:
        data["character_sheet"]["skills"][old] = data["character_sheet"]["skills"].pop(
            new
        )

    for key in keys_to_move:
        data[key] = data["character_sheet"][key]
        del data["character_sheet"][key]
    del data["character_sheet"]
    data["version"] = "0.0.7"
    return data


migrations = [
    Migration("0.0.1", "0.0.4"),
    Migration("0.0.4", "0.0.5"),
    Migration("0.0.6", "0.0.7", v006_to_007, v007_to_006),
    Migration("0.0.7", "0.0.8", v007_to_v008, v008_to_v007),
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
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    body: Annotated[int, Field(ge=1, le=5)] = 1
    tech: Annotated[int, Field(ge=1, le=5)] = 1
    heart: Annotated[int, Field(ge=1, le=5)] = 1
    mind: Annotated[int, Field(ge=1, le=5)] = 1


class Skills(BaseModel):
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    sneak: Annotated[int, Field(title="Sneak (Body)", ge=0, le=5)] = 0
    force: Annotated[int, Field(title="Force (Body)", ge=0, le=5)] = 0
    move: Annotated[int, Field(title="Move (Body)", ge=0, le=5)] = 0
    tinker: Annotated[int, Field(title="Tinker (Tech)", ge=0, le=5)] = 0
    program: Annotated[int, Field(title="Program (Tech)", ge=0, le=5)] = 0
    calculate: Annotated[int, Field(title="Calculate (Tech)", ge=0, le=5)] = 0
    contact: Annotated[int, Field(title="Contact (Heart)", ge=0, le=5)] = 0
    charm: Annotated[int, Field(title="Charm (Heart)", ge=0, le=5)] = 0
    lead: Annotated[int, Field(title="Lead (Heart)", ge=0, le=5)] = 0
    investigate: Annotated[int, Field(title="Investigate (Mind)", ge=0, le=5)] = 0
    comprehend: Annotated[int, Field(title="Comprehend (Mind)", ge=0, le=5)] = 0
    empathize: Annotated[int, Field(title="Empathize (Mind)", ge=0, le=5)] = 0


class Conditions(BaseModel):
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    upset: bool = False
    scared: bool = False
    exhausted: bool = False
    injured: bool = False
    broken: bool = False


class TalesFromTheLoopSheet(BaseModel):
    personalia: Annotated[Personalia, Field(default_factory=Personalia)]
    relationships: Annotated[Relationships, Field(default_factory=Relationships)]
    items: Annotated[list[Item], Field(default_factory=lambda: [Item()])]
    hideout: str = "Tree hut"
    notes: str = ""
    attributes: Attributes = Attributes()
    conditions: Conditions = Conditions()
    skills: Skills = Skills()
    experience: Annotated[int, Field(ge=0, le=10)] = 0


class TalesFromTheLoop(BaseSchema):
    """Tales from the Loop sheet."""

    model_config = ConfigDict(
        frozen=True, json_schema_serialization_defaults_required=True
    )

    system: Annotated[Literal["tftl"], Field(frozen=True)] = "tftl"
    meta: Annotated[SheetInfo, Field(default_factory=SheetInfo)]

    character_sheet: TalesFromTheLoopSheet = Field(
        title="Tales from the Loop", default_factory=TalesFromTheLoopSheet
    )


CharacterSheet = TalesFromTheLoop

if __name__ == "__main__":
    print(yaml.dump(TalesFromTheLoop.model_json_schema()))
