"""Call of Cthulhu migration functions."""

from typing import Annotated, Literal, Optional, Union
from jsonschema import validate
from pydantic import BaseModel, ConfigDict, Field
import yaml

from whathappened.sheets.mechanics.coc7e import new_character
from whathappened.sheets.schema.base import BaseSchema
from whathappened.sheets.schema.build import get_schema
from whathappened.sheets.schema.utils import Migration


def v003_to_v004(data):
    data = data.copy()
    data["version"] = "0.0.4"
    for k, v in data["characteristics"].items():
        data["characteristics"][k] = int(v)

    for skill in data["skills"]:
        value = skill["value"]
        try:
            value = int(skill["value"], 10)
        except ValueError:
            value = None
        skill["value"] = value

        start_value = skill["start_value"]
        try:
            start_value = int(start_value, 10)
        except ValueError:
            pass

        skill["start_value"] = start_value

        if "subskills" in skill:
            for subskill in skill["subskills"]:
                subskill["value"] = int(subskill["value"], 10)

    for weapon in data["weapons"]:
        value = weapon["regular"]
        try:
            value = int(value, 10)
        except ValueError:
            value = 0
        weapon["regular"] = value

        value = weapon["ammo"]
        try:
            value = int(value, 10)
        except ValueError:
            pass
        weapon["ammo"] = value

        value = weapon["malf"]
        try:
            value = int(value, 10)
        except ValueError:
            pass
        weapon["malf"] = value

    return data


def v004_to_v003(data):
    data = data.copy()
    data["version"] = "0.0.3"
    for k, v in data["characteristics"].items():
        data["characteristics"][k] = str(v)

    for skill in data["skills"]:
        skill["value"] = str(skill["value"])
        if "subskills" in skill:
            for subskill in skill["subskills"]:
                subskill["value"] = str(subskill["value"])

    for weapon in data["weapons"]:
        value = weapon["regular"]
        weapon["regular"] = str(value)

        value = weapon["ammo"]
        weapon["ammo"] = str(value)

        weapon["malf"] = str(weapon["malf"])

    return data


def v002_to_v003(data):
    data = data.copy()
    data["system"] = "coc7e"
    data["version"] = "0.0.3"
    del data["meta"]["Version"]
    return data


def v003_to_v002(data):
    data = data.copy()
    del data["version"]
    del data["system"]
    data["meta"]["Version"] = "0.0.2"
    return data


def v001_to_002(data):
    data = data.copy()
    nc = new_character("Test Character", "Classic (1920's)")
    schema = get_schema("coc7e")
    validate(nc, schema=schema)

    start_values = {skill["name"]: str(skill["start_value"]) for skill in nc["skills"]}

    for skill in nc["skills"]:
        if "subskills" in skill and skill["subskills"]:
            for subskill in skill["subskills"]:
                start_values[": ".join((skill["name"], subskill["name"]))] = str(
                    subskill["start_value"]
                )

    outskills = []
    skill_index = {}

    for skill in data["skills"]:
        if skill["name"] in start_values:
            skill["start_value"] = start_values[skill["name"]]
        else:
            skill["start_value"] = "0"

        if "specializations" in skill:
            skill["specializations"] = (
                skill["specializations"] == "true"
                or skill["specializations"] == "True"
                or skill["specializations"] is True
            )

        if skill["name"] not in skill_index:
            skill_index[skill["name"]] = skill
            outskills.append(skill)

        if "subskills" in skill:
            for subskill in skill["subskills"]:
                fullskillname = ": ".join((skill["name"], subskill["name"]))
                if fullskillname in start_values:
                    subskill["start_value"] = start_values[fullskillname]
                else:
                    subskill["start_value"] = skill["start_value"]

    data["skills"] = outskills
    data["meta"]["Version"] = "0.0.2"

    return data


def v002_to_001(data):
    data = data.copy()
    data["meta"]["Version"] = "0.0.1"

    outskills = []
    for skill in data["skills"]:
        if "start_value" in skill:
            del skill["start_value"]

        if "subskills" in skill:
            for subskill in skill["subskills"]:
                del subskill["start_value"]
        if "specializations" in skill:
            skill["specializations"] = "true" if skill["specializations"] else "false"
        outskills.append(skill)

    data["skills"] = outskills
    return data


def v004_to_v005(data):
    data = data.copy()
    data["version"] = "0.0.5"
    return data


def v005_to_v004(data):
    data = data.copy()
    data["version"] = "0.0.4"
    return data


migrations = [
    Migration("0.0.1", "0.0.2", v001_to_002, v002_to_001),
    Migration("0.0.2", "0.0.3", v002_to_v003, v003_to_v002),
    Migration("0.0.3", "0.0.4", v003_to_v004, v004_to_v003),
    Migration("0.0.4", "0.0.5"),
]


class Meta(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "required": ["Title", "GameName", "GameVersion", "GameType"]
        },
    )

    Title: str
    Creator: str
    CreateDate: Annotated[str, Field(title="CreateDate")]
    GameName: Annotated[
        Literal["Call of Cthulhu TM"], Field(title="GameName", frozen=True)
    ]
    GameVersion: Annotated[
        Literal["7th Edition"], Field(title="GameVersion", frozen=True)
    ]
    GameType: Annotated[Literal["Classic (1920's)", "Modern"], Field(title="GameType")]
    Disclaimer: str


class Personalia(BaseModel):
    model_config = ConfigDict(extra="ignore", json_schema_extra={"required": []})

    Name: str
    Occupation: str
    Gender: str
    Age: str
    Birthplace: str
    Residence: str
    Portrait: Optional[str]


class Characteristics(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "required": [
                "STR",
                "DEX",
                "INT",
                "CON",
                "APP",
                "POW",
                "SIZ",
                "EDU",
                "Move",
                "Luck",
                "Sanity",
                "SanityMax",
                "MagicPts",
                "MagicPtsMax",
                "HitPts",
                "HitPtsMax",
            ]
        },
    )

    STR: int
    DEX: int
    INT: int
    CON: int
    APP: int
    POW: int
    SIZ: int
    EDU: int
    Move: int
    Luck: int
    LuckMax: int
    Sanity: int
    SanityStart: int
    SanityMax: int
    MagicPts: int
    MagicPtsMax: int
    HitPts: int
    HitPtsMax: int


class Skill(BaseModel):
    model_config = ConfigDict(
        extra="ignore", json_schema_extra={"required": ["name", "value", "start_value"]}
    )

    checked: bool
    name: str
    occupation: bool
    start_value: Union[str, int]
    value: Optional[int]
    specializations: Annotated[bool, Field(frozen=True)]
    subskills: Annotated[
        Optional[list["Skill"]], Field(json_schema_extra={"unique_items": True})
    ] = None

    # TODO: Add a conditional for subskills based on specializations.
    # Use a custom validator function.


class Weapon(BaseModel):
    model_config = ConfigDict(
        json_schema_serialization_defaults_required=True, extra="ignore"
    )

    name: str
    regular: Optional[int] = None
    damage: str
    range: str
    attacks: Union[int, str]
    ammo: Union[Literal["-"], int] = "-"
    malf: Union[Literal["-"], int] = "-"


class Combat(BaseModel):
    model_config = ConfigDict(
        json_schema_serialization_defaults_required=True, extra="ignore"
    )

    DamageBonus: Union[str, int]
    Build: Union[str, int]
    Dodge: Union[str, int]


class Backstory(BaseModel):
    model_config = ConfigDict(extra="ignore", json_schema_extra={"required": []})

    description: Optional[str]
    traits: Optional[str]
    ideology: Optional[str]
    injurues: Optional[str]  # TODO: Fix typo
    people: Optional[str]
    phobias: Optional[str]
    locations: Optional[str]
    tomes: Optional[str]
    possessions: Optional[str]
    encounters: Optional[str]


class Cash(BaseModel):
    model_config = ConfigDict(extra="ignore", json_schema_extra={"required": []})
    spending: Union[str, int]
    cash: Union[str, int]
    assets: Union[str, int]


class CallofCthulhu7e(BaseSchema):
    """Call of Cthulhu 7e sheet."""

    model_config = ConfigDict(
        frozen=True,
        extra="ignore",
        json_schema_extra={
            "required": [
                "version",
                "system",
                "meta",
                "personalia",
                "characteristics",
            ]
        },
    )

    system: Annotated[Literal["coc7e"], Field(frozen=True)] = "coc7e"
    meta: Annotated[Meta, Field()]
    personalia: Annotated[Personalia, Field()]
    characteristics: Annotated[Characteristics, Field()]
    skills: Annotated[
        list[Skill], Field(default=[], json_schema_extra={"unique_items": True})
    ]
    weapons: Annotated[list[Weapon], Field(default=[])]
    combat: Annotated[Combat, Field()]
    backstory: Backstory
    possessions: Optional[list[str]]
    cash: Cash
    assets: Optional[str] = None


CharacterSheet = CallofCthulhu7e

if __name__ == "__main__":
    print(yaml.dump(CallofCthulhu7e.model_json_schema()))
