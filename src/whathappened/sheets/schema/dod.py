from enum import Enum
from typing import List
from typing_extensions import Annotated

import yaml

from pydantic import BaseModel, Field


class SheetInfo(BaseModel):
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


class Attributer(BaseModel):
    STY: int = 0
    FYS: int = 0
    SMI: int = 0
    INT: int = 0
    PSY: int = 0
    KAR: int = 0

    utmattad: bool = False
    krasslig: bool = False
    omtocknad: bool = False
    arg: bool = False
    radd: bool = False
    uppgiven: bool = False


class Skadebonus(BaseModel):
    sty: str = Field("", title="Styrke")
    smi: str = Field("", title="Smidighet")


class Fardighet(BaseModel):
    checked: bool = False
    value: int = 0
    name: str
    base: str


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
    ("Undivka", "SMI"),
    ("Uppträda", "KAR"),
    ("Upptäcka fara", "INT"),
    ("Vildmakrsvana", "KAR"),
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


class Fardigheter(BaseModel):
    primar: List[Fardighet] = Field(
        [Fardighet(name=name, base=base) for name, base in PrimaraFerdigheter]
    )
    vapenfardigheter: List[Fardighet] = Field(
        [Fardighet(name=name, base=base) for name, base in VapenFardigheter],
        title="Vapenfärdigheter",
    )

    sekundarafardigheter: List[Fardighet] = Field([], title="Sekundära färdigheter")


class Packning(BaseModel):
    barformoga: int = Field(0, title="Bärformåga")
    items: List[str] = []
    minnessak: str = ""
    smaasaker: List[str] = []


class Penger(BaseModel):
    guldmynt: int = 0
    silvermynt: int = 0
    kopparmynt: int = 0


class Rustning(BaseModel):
    skyddsvärde: int = 0
    smyga: bool = False
    undvika: bool = False
    hoppa_och_klatra: bool = False


class Hjalm(BaseModel):
    skyddsvärde: int = 0
    upptäcka_fara: bool = False
    avståndsattacker: bool = False


class Vapen(BaseModel):
    vapen: str = ""
    grepp: str = ""
    räckvidd: str = ""
    skada: str = ""
    brytvärde: str = ""
    egenskaper: str = ""


class Bevapning(BaseModel):
    rustning: Rustning = Field(default_factory=Rustning)
    hjalm: Hjalm = Field(default_factory=Hjalm, title="Hjälm")
    til_hands: List[Vapen] = Field(default=[Vapen() for _ in range(3)])


class Viljepoang(BaseModel):
    poeng: int = 0
    brukt: int = 0


class Kroppspoang(Viljepoang):
    lyckade: int = 0
    misslyckade: int = 0


class DrakarOchDemonerCharacter(BaseModel):
    namn: str = ""
    slakte: Annotated[Slakte, Field(title="Släkte")] = Slakte.MANNISKA
    alder: str = Field("", title="Ålder")
    yrke: Annotated[Yrke, Field(title="Yrke")] = Yrke.BARD
    svaghet: str = ""
    utseende: str = ""
    attributer: Attributer = Field(default_factory=Attributer)
    skadebonus: Skadebonus = Field(default_factory=Skadebonus)
    forflyttning: int = 0
    formagor_og_besvarjelser: List[str] = Field([], title="Förmågor & besvärjelser")
    fardigheter: Fardigheter = Field(default_factory=Fardigheter, title="Färdigheter")
    packning: Packning = Field(default_factory=Packning)
    penger: Penger = Field(default_factory=Penger)
    vapen: Bevapning = Field(default_factory=Bevapning)
    viljepoang: Viljepoang = Field(default_factory=Viljepoang)
    kroppspoang: Kroppspoang = Field(default_factory=Kroppspoang)


class DrakarOchDemoner(BaseModel):
    """Character sheet."""

    system: str = "dod"
    meta: SheetInfo = Field(default_factory=SheetInfo)
    character_sheet: DrakarOchDemonerCharacter = Field(
        default_factory=DrakarOchDemonerCharacter
    )


CharacterSheet = DrakarOchDemoner

if __name__ == "__main__":
    print(yaml.dump(DrakarOchDemoner.model_json_schema(), allow_unicode=True))
