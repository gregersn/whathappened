"""Character sheet data for DoD."""

from typing import List, Literal
from typing_extensions import Annotated

import yaml

from pydantic import BaseModel, ConfigDict, Field

from whathappened.sheets.schema.base import BaseSheet, SheetInfo, Gametag


Yrke = Literal[
    "Bard",
    "Hantverkare",
    "Jägare",
    "Krigare",
    "Lärd",
    "Magiker",
    "Nasare",
    "Riddare",
    "Sjöfarare",
    "Tjuv",
]

Bonus = Literal["-", "+T4", "+T6"]
Alder = Literal["Ung", "Medelålders", "Gammal"]
Slakte = Literal["Människa", "Halvling", "Dvärg", "Alv", "Anka", "Vargfolk"]
BasEgenskap = Literal["STY", "FYS", "SMI", "INT", "PSY", "KAR"]


class Grundegenskaper(BaseModel):
    """Attributes."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    STY: Annotated[int, Field(le=18, ge=0, title="Styrke (STY)")] = 0
    FYS: Annotated[int, Field(le=18, ge=0, title="Fysik (FYS)")] = 0
    SMI: Annotated[int, Field(le=18, ge=0, title="Smidighet (SMI)")] = 0
    INT: Annotated[int, Field(le=18, ge=0, title="Intelligens (INT)")] = 0
    PSY: Annotated[int, Field(le=18, ge=0, title="Psyke (PSY)")] = 0
    KAR: Annotated[int, Field(le=18, ge=0, title="Karisma (KAR)")] = 0
    utmattad: bool = False
    krasslig: bool = False
    omtocknad: Annotated[bool, Field(title="Omtöcknad")] = False
    arg: bool = False
    radd: Annotated[bool, Field(title="Rädd")] = False
    uppgiven: bool = False


class Fardighet(BaseModel):
    """Skill."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    checked: Annotated[bool, Field(json_schema_extra={"hide_heading": True})] = False
    name: str = "namn"
    base: Annotated[
        BasEgenskap, Field(json_schema_extra={"filter": "parenthesize"})
    ] = "STY"
    value: int = 0


PrimaraFerdigheter: list[tuple[str, BasEgenskap]] = [
    ("Bestiologi", "INT"),
    ("Bluffa", "KAR"),
    ("Fingerfärdighet", "SMI"),
    ("Finna dolda ting", "INT"),
    ("Främmande språk", "INT"),
    ("Hantverk", "STY"),
    ("Hoppa & klättra", "SMI"),
    ("Jakt & fiske", "SMI"),
    ("Köpslå", "KAR"),
    ("Läkekonst", "INT"),
    ("Myter & legender", "INT"),
    ("Rida", "SMI"),
    ("Simma", "SMI"),
    ("Sjökunnighet", "INT"),
    ("Smyga", "SMI"),
    ("Undvika", "SMI"),
    ("Uppträda", "KAR"),
    ("Upptäcka fara", "INT"),
    ("Vildmarksvana", "INT"),
    ("Övertala", "KAR"),
]

VapenFardigheter: list[tuple[str, BasEgenskap]] = [
    ("Armborst", "SMI"),
    ("Hammare", "STY"),
    ("Kniv", "SMI"),
    ("Pilbåge", "SMI"),
    ("Slagsmål", "STY"),
    ("Slunga", "SMI"),
    ("Spjut", "STY"),
    ("Stav", "SMI"),
    ("Svärd", "STY"),
    ("Yxa", "STY"),
]


class Fardigheter(BaseModel):
    """Skills."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    primar: Annotated[
        List[Fardighet],
        Field(
            json_schema_extra={
                "constant": True,
                "widget": "table",
                "heading": False,
                "hide_title": True,
                "constant_fields": ["name", "base"],
            }
        ),
    ] = Field(
        default_factory=lambda: [
            Fardighet(name=name, base=base) for name, base in PrimaraFerdigheter
        ],
    )
    vapenfardigheter: Annotated[
        List[Fardighet],
        Field(
            json_schema_extra={
                "constant": True,
                "widget": "table",
                "constant_fields": ["name", "base"],
            },
            title="Vapenfärdigheter",
        ),
    ] = Field(
        default_factory=lambda: [
            Fardighet(name=name, base=base) for name, base in VapenFardigheter
        ],
    )

    sekundarafardigheter: Annotated[
        List[Fardighet],
        Field(
            json_schema_extra={"constant": False, "widget": "table"},
            title="Sekundära färdigheter",
        ),
    ] = Field(default_factory=lambda: [])


class Packning(BaseModel):
    """Inventory."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    barformoga: Annotated[int, Field(title="Bärformåga", ge=0, le=10)] = Field(
        default=0
    )
    items: Annotated[List[str], Field(json_schema_extra={"constant": True})] = Field(
        default_factory=lambda: ["-" for _ in range(10)]
    )
    minnessak: str = "-"
    smaasaker: Annotated[List[str], Field(title="Småsaker")] = []


class Pengar(BaseModel):
    """Money."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    guldmynt: int = 0
    silvermynt: int = 0
    kopparmynt: int = 0


class Rustning(BaseModel):
    """Armor."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    typ: str = "Ingen"
    skyddsvärde: int = 0
    smyga: bool = False
    undvika: bool = False
    hoppa_och_klattra: Annotated[bool, Field(title="Hoppa & klättra")] = False


class Hjalm(BaseModel):
    """Helmet."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    typ: str = "Ingen"
    skyddsvärde: int = 0
    upptäcka_fara: Annotated[bool, Field(title="Upptäcka fara")] = False
    avståndsattacker: bool = False


class Vapen(BaseModel):
    """Weapon."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    vapen: Annotated[str, Field(title="Vapen/sköld")] = "Obeväpnad"
    grepp: Literal["-", "1H", "2H"] = "-"
    räckvidd: str = "2"
    skada: str = "T6"
    brytvärde: str = "-"
    egenskaper: str = "Krossande"


class Bevapning(BaseModel):
    """Armory."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    rustning: Annotated[Rustning, Field(json_schema_extra={"subsection": True})] = (
        Field(default_factory=Rustning)
    )
    hjalm: Annotated[
        Hjalm, Field(title="Hjälm", json_schema_extra={"subsection": True})
    ] = Field(default_factory=Hjalm)
    till_hands: Annotated[
        List[Vapen],
        Field(
            title="Till hands",
            json_schema_extra={"constant": True, "widget": "table", "header": True},
        ),
    ] = Field(default_factory=lambda: [Vapen() for _ in range(3)])


class Viljepoang(BaseModel):
    """Willpower points."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    poang: Annotated[int, Field(title="Poäng", le=20)] = Field(default=0)
    anvanda: Annotated[
        int,
        Field(title="Använda", le=20, json_schema_extra=({"widget": "progress"})),
    ] = Field(default=0)


class Dodsslag(BaseModel):
    """Death rolls."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    lyckade: Annotated[
        int, Field(le=3, ge=0, json_schema_extra={"widget": "progress"})
    ] = 0
    misslyckade: Annotated[
        int, Field(le=3, ge=0, json_schema_extra={"widget": "progress"})
    ] = 0


class Kroppspoang(Viljepoang):
    """Hit points."""

    dodsslag: Annotated[Dodsslag, Field(title="Dödsslag")] = Field(default=Dodsslag())


class Personalia(BaseModel):
    """Personalia."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    namn: str = "Inget namn"
    slakte: Annotated[Slakte, Field(title="Släkte")] = Field(default="Människa")
    alder: Annotated[Alder, Field(title="Ålder")] = "Ung"
    yrke: Yrke = "Bard"
    svaghet: str = "Odefinerad"
    utseende: str = "Odefinerad"


class SekundaraEgenskaper(BaseModel):
    """Secondary skills."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    skadebonus_sty: Annotated[
        Bonus,
        Field(title="Skadebonus STY", json_schema_extra={"block": "inline"}),
    ] = "-"
    skadebonus_smi: Annotated[
        Bonus,
        Field(title="Skadebonus SMI", json_schema_extra={"block": "inline"}),
    ] = "-"
    forflyttning: Annotated[
        int, Field(json_schema_extra={"block": "inline"}, title="Förflyttning")
    ] = 0
    viljepoang: Annotated[
        Viljepoang,
        Field(title="Viljepoäng", json_schema_extra={"subsection": True}),
    ] = Field(default=Viljepoang())
    kroppspoang: Annotated[
        Kroppspoang,
        Field(title="Kroppspoäng", json_schema_extra={"subsection": True}),
    ] = Field(default=Kroppspoang())


class Character(BaseModel):
    """Character."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    personalia: Annotated[Personalia, Field(json_schema_extra={"columns": 2})] = Field(
        default=Personalia()
    )
    egenskaper: Annotated[Grundegenskaper, Field(json_schema_extra={"columns": 2})] = (
        Field(default=Grundegenskaper())
    )
    sekundara_egenskaper: Annotated[
        SekundaraEgenskaper, Field(title="Sekundära egenskaper")
    ] = Field(default=SekundaraEgenskaper())
    formagor_og_besvarjelser: List[str] = Field(
        default=[], alias="Förmågor & besvärjelser"
    )
    fardigheter: Annotated[
        Fardigheter,
        Field(title="Färdigheter", json_schema_extra={"columns": 2}),
    ] = Field(default=Fardigheter())
    packning: Packning = Field(default=Packning())
    pengar: Pengar = Field(default=Pengar())
    vapen: Annotated[Bevapning, Field(title="Beväpning")] = Field(default=Bevapning())


class DrakarOchDemoner(BaseSheet):
    """Character sheet."""

    system: Gametag = "dod"
    meta: SheetInfo = SheetInfo(gamename="Drakar och Demoner")

    character_sheet: Character = Field(default_factory=Character)


CharacterSheet = DrakarOchDemoner

if __name__ == "__main__":
    print(yaml.dump(DrakarOchDemoner.model_json_schema()))
