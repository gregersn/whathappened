from enum import Enum
from typing import List, Literal
from typing_extensions import Annotated

import yaml

import msgspec


class SheetInfo(msgspec.Struct):
    """Basic info about the sheet."""

    gamename: str = "Drakar och Demoner"
    title: str = "Unknown"


class Slakte(str, Enum):
    MANNISKA = "Människa"
    HALVLING = "Halvling"
    DVARG = "Dvärg"
    ALV = "Alv"
    ANKA = "Anka"
    VARGFOLK = "Vargfolk"


class Yrke(str, Enum):
    BARD = "Bard"
    HANTVERKARE = "Hantverkare"
    JAGARE = "Jägare"
    KRIGARE = "Krigare"
    LARD = "Lärd"
    MAGIKER = "Magiker"
    NASARE = "Masare"
    RIDDARE = "Riddare"
    SJOFARARE = "Sjöfarare"
    TJUV = "Tjuv"


Bonus = Literal["-", "+T4", "+T6"]
Alder = Literal["Ung", "Medelålders", "Gammal"]
BasAttribut = Literal["STY", "FYS", "SMI", "INT", "PSY", "KAR"]


class Attributer(msgspec.Struct, frozen=True):
    STY: Annotated[int, msgspec.Meta(le=18, ge=0, title="Styrke (STY)")] = 0
    FYS: Annotated[int, msgspec.Meta(le=18, ge=0, title="Fysik (FYS)")] = 0
    SMI: Annotated[int, msgspec.Meta(le=18, ge=0, title="Smidighet (SMI)")] = 0
    INT: Annotated[int, msgspec.Meta(le=18, ge=0, title="Intelligens (INT)")] = 0
    PSY: Annotated[int, msgspec.Meta(le=18, ge=0, title="Psyke (PSY)")] = 0
    KAR: Annotated[int, msgspec.Meta(le=18, ge=0, title="Karisma (KAR)")] = 0
    utmattad: bool = False
    krasslig: bool = False
    omtocknad: Annotated[bool, msgspec.Meta(title="Omtöcknad")] = False
    arg: bool = False
    radd: Annotated[bool, msgspec.Meta(title="Rädd")] = False
    uppgiven: bool = False


class Fardighet(msgspec.Struct, frozen=True):
    checked: Annotated[
        bool, msgspec.Meta(extra_json_schema=({"hide_heading": True}))
    ] = False
    name: str = "namn"
    base: BasAttribut = "STY"
    value: int = 0


PrimaraFerdigheter = [
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
    ("Vildmarksvana", "KAR"),
]

VapenFardigheter = [
    ("Armbrost", "SMI"),
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


class Fardigheter(msgspec.Struct, frozen=True):
    primar: Annotated[
        List[Fardighet],
        msgspec.Meta(
            extra_json_schema={"constant": True, "widget": "table", "heading": False}
        ),
    ] = msgspec.field(
        default_factory=lambda: [
            Fardighet(name=name, base=base) for name, base in PrimaraFerdigheter
        ],
    )
    vapenfardigheter: Annotated[
        List[Fardighet],
        msgspec.Meta(
            extra_json_schema={"constant": True, "widget": "table"},
            title="Vapenfärdigheter",
        ),
    ] = msgspec.field(
        default_factory=lambda: [
            Fardighet(name=name, base=base) for name, base in VapenFardigheter
        ],
    )

    sekundarafardigheter: Annotated[
        List[Fardighet],
        msgspec.Meta(
            extra_json_schema={"constant": False, "widget": "table"},
            title="Sekundära färdigheter",
        ),
    ] = msgspec.field(default_factory=lambda: [])


class Packning(msgspec.Struct, frozen=True):
    barformoga: Annotated[
        int, msgspec.Meta(title="Bärformåga", ge=0, le=10)
    ] = msgspec.field(default=0)
    items: Annotated[
        List[str], msgspec.Meta(extra_json_schema={"constant": True})
    ] = msgspec.field(default_factory=lambda: ["-" for _ in range(10)])
    minnessak: str = "-"
    smaasaker: List[str] = []


class Penger(msgspec.Struct, frozen=True):
    guldmynt: int = 0
    silvermynt: int = 0
    kopparmynt: int = 0


class Rustning(msgspec.Struct, frozen=True):
    typ: str = "Ingen"
    skyddsvärde: int = 0
    smyga: bool = False
    undvika: bool = False
    hoppa_och_klatra: bool = False


class Hjalm(msgspec.Struct, frozen=True):
    typ: str = "Ingen"
    skyddsvärde: int = 0
    upptäcka_fara: bool = False
    avståndsattacker: bool = False


class Vapen(msgspec.Struct, frozen=True):
    vapen: str = "Obeväpnad"
    grepp: Literal["-", "1H", "2H"] = "-"
    räckvidd: str = "2"
    skada: str = "T6"
    brytvärde: str = "-"
    egenskaper: str = "Krossande"


class Bevapning(msgspec.Struct, frozen=True):
    rustning: Annotated[
        Rustning, msgspec.Meta(extra_json_schema={"subsection": True})
    ] = msgspec.field(default_factory=Rustning)
    hjalm: Annotated[
        Hjalm, msgspec.Meta(title="Hjälm", extra_json_schema={"subsection": True})
    ] = msgspec.field(default_factory=Hjalm)
    til_hands: Annotated[
        List[Vapen],
        msgspec.Meta(
            extra_json_schema={"constant": True, "widget": "table", "header": True}
        ),
    ] = msgspec.field(default_factory=lambda: [Vapen() for _ in range(3)])


class Viljepoang(msgspec.Struct, frozen=True):
    poang: Annotated[int, msgspec.Meta(title="Poäng", le=20)] = msgspec.field(default=0)
    anvanda: Annotated[
        int,
        msgspec.Meta(
            title="Använda", le=20, extra_json_schema=({"widget": "progress"})
        ),
    ] = msgspec.field(default=0)


class Dodsrull(msgspec.Struct, frozen=True):
    lyckade: Annotated[
        int, msgspec.Meta(le=3, ge=0, extra_json_schema=({"widget": "progress"}))
    ] = 0
    misslyckade: Annotated[
        int, msgspec.Meta(le=3, ge=0, extra_json_schema=({"widget": "progress"}))
    ] = 0


class Kroppspoang(Viljepoang, frozen=True):
    dodsrull: Dodsrull = msgspec.field(default=Dodsrull())


class Personalia(msgspec.Struct, frozen=True):
    namn: str = "Inget namn"
    slakte: Annotated[Slakte, msgspec.Meta(title="Släkte")] = msgspec.field(
        default=Slakte.MANNISKA
    )
    alder: Annotated[Alder, msgspec.Meta(title="Ålder")] = "Ung"
    yrke: Yrke = Yrke.BARD
    svaghet: str = "Odefinerad"
    utseende: str = "Odefinerad"


class AvledadeAttributer(msgspec.Struct, frozen=True):
    skadebonus_sty: Annotated[
        Bonus,
        msgspec.Meta(title="Skadebonus STY", extra_json_schema={"block": "inline"}),
    ] = "-"
    skadebonus_smi: Annotated[
        Bonus,
        msgspec.Meta(title="Skadebonus SMI", extra_json_schema={"block": "inline"}),
    ] = "-"
    forflyttning: Annotated[
        int, msgspec.Meta(extra_json_schema={"block": "inline"}, title="Förflyttning")
    ] = 0
    viljepoang: Annotated[
        Viljepoang,
        msgspec.Meta(title="Viljepoäng", extra_json_schema={"subsection": True}),
    ] = msgspec.field(default=Viljepoang())
    kroppspoang: Annotated[
        Kroppspoang,
        msgspec.Meta(title="Kroppspoäng", extra_json_schema={"subsection": True}),
    ] = msgspec.field(default=Kroppspoang())


class Character(msgspec.Struct):
    personalia: Annotated[
        Personalia, msgspec.Meta(extra_json_schema=({"columns": 2}))
    ] = msgspec.field(default=Personalia())
    attributer: Annotated[
        Attributer, msgspec.Meta(extra_json_schema=({"columns": 2}))
    ] = msgspec.field(default=Attributer())
    avledade_attributer: Annotated[
        AvledadeAttributer, msgspec.Meta(title="Avledade attributer")
    ] = msgspec.field(default=AvledadeAttributer())
    formagor_og_besvarjelser: List[str] = msgspec.field(
        default=[], name="Förmågor & besvärjelser"
    )
    fardigheter: Annotated[
        Fardigheter,
        msgspec.Meta(title="Färdigheter", extra_json_schema=({"columns": 2})),
    ] = msgspec.field(default=Fardigheter())
    packning: Packning = msgspec.field(default=Packning())
    penger: Penger = msgspec.field(default=Penger())
    vapen: Annotated[Bevapning, msgspec.Meta(title="Beväpning")] = msgspec.field(
        default=Bevapning()
    )


class DrakarOchDemoner(msgspec.Struct):
    """Character sheet."""

    system: str = "dod"
    meta: SheetInfo = msgspec.field(default_factory=SheetInfo)
    character_sheet: Character = msgspec.field(default_factory=Character)


CharacterSheet = DrakarOchDemoner

if __name__ == "__main__":
    print(yaml.dump(msgspec.json.schema(DrakarOchDemoner), allow_unicode=True))
