"""Call of Cthulhu schema definition."""

from typing import Annotated, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field
import yaml

from whathappened.sheets.schema.base import BaseSchema
from whathappened.sheets.schema.coc7e.skills import SKILLS


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
    injuries: Optional[str]
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
                "skills",
            ]
        },
    )

    system: Annotated[Literal["coc7e"], Field(frozen=True)] = "coc7e"
    meta: Annotated[Meta, Field()]
    personalia: Annotated[Personalia, Field()]
    characteristics: Annotated[Characteristics, Field()]
    skills: Annotated[
        list[Skill],
        Field(
            json_schema_extra={"unique_items": True},
        ),
    ] = Field(
        default_factory=lambda: [
            Skill(
                name=skill.get("name", "Unknown"),
                start_value=skill.get("start_value", 0),
                value=skill.get("value", 0),
                specializations=skill.get("specializations", False),
                checked=False,
                occupation=False,
            )
            for skill in SKILLS
        ]
    )
    weapons: Annotated[list[Weapon], Field(default=[])]
    combat: Annotated[Combat, Field()]
    backstory: Backstory
    possessions: Optional[list[str]]
    cash: Cash
    assets: Optional[str] = None


if __name__ == "__main__":
    print(yaml.dump(CallofCthulhu7e.model_json_schema()))
