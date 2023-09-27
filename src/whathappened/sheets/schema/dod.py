from enum import Enum
from typing import List
from typing_extensions import Annotated

import yaml

from pydantic import BaseModel, Field


class SheetInfo(BaseModel):
    """Basic info about the sheet."""

    gamename: str
    title: str = "Unknown"


class DoDSlakte(str, Enum):
    MANNISKA = "Människa"


class DoDYrke(str, Enum):
    BARD = "Bard"


class DoDAttributer(BaseModel):
    ...


class DoDSkadebonus(BaseModel):
    ...


class DoDFardigheter(BaseModel):
    ...


class DoDPackning(BaseModel):
    barformoga: int = Field(title="Bärformåga")
    items: List[str] = list()
    minnessak: str
    smaasaker: List[str] = list()


class DoDPenger(BaseModel):
    guldmynt: int = 0
    silvermynt: int = 0
    kopparmynt: int = 0


class DrakarOchDemonerCharacter(BaseModel):
    namn: str
    slakte: Annotated[DoDSlakte, Field(title="Släkte")]
    alder: str = Field(title="Ålder")
    yrke: Annotated[DoDYrke, Field(title="Yrke")]
    svaghet: str
    utseende: str
    attributer: DoDAttributer
    skadebonus: DoDSkadebonus
    forflyttning: str
    formagor_og_besvarjelser: List[str]
    fardigheter: DoDFardigheter
    packning: DoDPackning
    penger: DoDPenger


class DrakarOchDemoner(BaseModel):
    """Character sheet."""

    system: str = Field("dod")
    meta: SheetInfo = Field(SheetInfo(gamename="Drakar och Demoner"))
    character_Sheet: DrakarOchDemonerCharacter = Field(title="Drakar och Demoner")


CharacterSheet = DrakarOchDemoner

if __name__ == "__main__":
    print(yaml.dump(DrakarOchDemoner.model_json_schema(), allow_unicode=True))
