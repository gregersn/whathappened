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


Attribut = Annotated[int, msgspec.Meta(le=18)]
Bonus = Literal["-", "+T4", "+T6"]
Alder = Literal["Ung", "Medelålders", "Gammal"]
BasAttribut = Literal["STY", "FYS", "SMI", "INT", "PSY", "KAR"]


class Attributer(msgspec.Struct, frozen=True):
    STY: Attribut = 0
    FYS: Attribut = 0
    SMI: Attribut = 0
    INT: Attribut = 0
    PSY: Attribut = 0
    KAR: Attribut = 0

    utmattad: bool = False
    krasslig: bool = False
    omtocknad: bool = False
    arg: bool = False
    radd: bool = False
    uppgiven: bool = False


class Skadebonus(msgspec.Struct, frozen=True):
    sty: Bonus = "-"
    smi: Bonus = "-"


class Fardighet(msgspec.Struct, frozen=True):
    name: str = "namn"
    base: BasAttribut = "STY"
    checked: bool = False
    value: Attribut = 0


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
        msgspec.Meta(extra_json_schema={"constant": True, "widget": "table"}),
    ] = msgspec.field(
        default_factory=lambda: [
            Fardighet(name=name, base=base) for name, base in PrimaraFerdigheter
        ],
    )
    vapenfardigheter: Annotated[
        List[Fardighet],
        msgspec.Meta(extra_json_schema={"constant": True, "widget": "table"}),
    ] = msgspec.field(
        default_factory=lambda: [
            Fardighet(name=name, base=base) for name, base in VapenFardigheter
        ],
        name="Vapenfärdigheter",
    )

    sekundarafardigheter: Annotated[
        List[Fardighet],
        msgspec.Meta(extra_json_schema={"constant": False, "widget": "table"}),
    ] = msgspec.field(default_factory=lambda: [], name="Sekundära färdigheter")


class Packning(msgspec.Struct, frozen=True):
    barformoga: int = msgspec.field(default=0, name="Bärformåga")
    items: List[str] = []
    minnessak: str = "-"
    smaasaker: List[str] = []


class Penger(msgspec.Struct, frozen=True):
    guldmynt: int = 0
    silvermynt: int = 0
    kopparmynt: int = 0


class Rustning(msgspec.Struct, frozen=True):
    namn: str = "Ingen"
    skyddsvärde: int = 0
    smyga: bool = False
    undvika: bool = False
    hoppa_och_klatra: bool = False


class Hjalm(msgspec.Struct, frozen=True):
    namn: str = "Ingen"
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
    rustning: Rustning = msgspec.field(default_factory=Rustning)
    hjalm: Hjalm = msgspec.field(default_factory=Hjalm, name="Hjälm")
    til_hands: Annotated[
        List[Vapen],
        msgspec.Meta(extra_json_schema={"constant": True, "widget": "table"}),
    ] = msgspec.field(default_factory=lambda: [Vapen() for _ in range(3)])


class Viljepoang(msgspec.Struct, frozen=True):
    poang: int = msgspec.field(default=0, name="Poäng")
    anvanda: int = msgspec.field(default=0, name="Använda")


class Kroppspoang(Viljepoang, frozen=True):
    lyckade: int = 0
    misslyckade: int = 0


class DrakarOchDemonerCharacter(msgspec.Struct):
    namn: str = "Inget namn"
    slakte: Slakte = msgspec.field(default=Slakte.MANNISKA)
    alder: Alder = msgspec.field(default="Ung", name="Ålder")
    yrke: Annotated[Yrke, msgspec.field(name="Yrke")] = Yrke.BARD
    svaghet: str = "Odefinerad"
    utseende: str = "Odefinerad"
    attributer: Attributer = msgspec.field(default=Attributer())
    skadebonus: Skadebonus = msgspec.field(default=Skadebonus())
    forflyttning: int = 0
    formagor_og_besvarjelser: List[str] = msgspec.field(
        default=[], name="Förmågor & besvärjelser"
    )
    fardigheter: Fardigheter = msgspec.field(default=Fardigheter(), name="Färdigheter")
    packning: Packning = msgspec.field(default=Packning())
    penger: Penger = msgspec.field(default=Penger())
    vapen: Bevapning = msgspec.field(default=Bevapning())
    viljepoang: Viljepoang = msgspec.field(default=Viljepoang())
    kroppspoang: Kroppspoang = msgspec.field(default=Kroppspoang())


class DrakarOchDemoner(msgspec.Struct):
    """Character sheet."""

    system: str = "dod"
    meta: SheetInfo = msgspec.field(default_factory=SheetInfo)
    character_sheet: DrakarOchDemonerCharacter = msgspec.field(
        default_factory=DrakarOchDemonerCharacter
    )


CharacterSheet = DrakarOchDemoner

if __name__ == "__main__":
    print(yaml.dump(msgspec.json.schema(DrakarOchDemoner), allow_unicode=True))
