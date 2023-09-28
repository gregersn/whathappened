from enum import Enum
from typing import List
from typing_extensions import Annotated

import yaml

from pydantic import BaseModel, Field


class SheetInfo(BaseModel):
    """Basic info about the sheet."""

    gamename: str = "Drakar och Demoner"
    title: str = "Unknown"


class DoDSlakte(str, Enum):
    MANNISKA = "Människa"
    HALVLING = "Halvling"
    DVARG = "Dvärg"
    ALV = "Alv"
    ANKA = "Anka"
    VARGFOLK = "Vargfolk"


class DoDYrke(str, Enum):
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


class DoDAttributer(BaseModel):
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


class DoDSkadebonus(BaseModel):
    sty: str = Field("", title="Styrke")
    smi: str = Field("", title="Smidighet")


class DoDFardigheter(BaseModel):
    ...


class DoDPackning(BaseModel):
    barformoga: int = Field(0, title="Bärformåga")
    items: List[str] = []
    minnessak: str = ""
    smaasaker: List[str] = []


class DoDPenger(BaseModel):
    guldmynt: int = 0
    silvermynt: int = 0
    kopparmynt: int = 0


class DrakarOchDemonerCharacter(BaseModel):
    namn: str = ""
    slakte: Annotated[DoDSlakte, Field(title="Släkte")] = DoDSlakte.MANNISKA
    alder: str = Field("", title="Ålder")
    yrke: Annotated[DoDYrke, Field(title="Yrke")] = DoDYrke.BARD
    svaghet: str = ""
    utseende: str = ""
    attributer: DoDAttributer = Field(default_factory=DoDAttributer)
    skadebonus: DoDSkadebonus = Field(default_factory=DoDSkadebonus)
    forflyttning: str = ""
    formagor_og_besvarjelser: List[str] = list()
    fardigheter: DoDFardigheter = Field(default_factory=DoDFardigheter)
    packning: DoDPackning = Field(default_factory=DoDPackning)
    penger: DoDPenger = Field(default_factory=DoDPenger)


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
