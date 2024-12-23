from typing import List, TypedDict, Union


BaseValue = Union[int, str]


class SkillInfo(TypedDict, total=False):
    name: str
    value: int
    start_value: Union[int, str]
    specializations: bool
    subskills: List["SkillInfo"]


SKILLS: List[SkillInfo] = [
    {"name": "Accounting", "value": 5, "start_value": 5},
    {"name": "Anthropology", "value": 1, "start_value": 1},
    {"name": "Appraise", "value": 5, "start_value": 5},
    {"name": "Archaeology", "value": 1, "start_value": 1},
    {"name": "Art/Craft", "specializations": True, "value": 5, "start_value": 5},
    {"name": "Charm", "value": 15, "start_value": 15},
    {"name": "Climb", "value": 20, "start_value": 20},
    {"name": "Credit Rating", "value": 0, "start_value": 0},
    {"name": "Cthulhu Mythos", "value": 0, "start_value": 0},
    {"name": "Disguise", "value": 5, "start_value": 5},
    {"name": "Dodge", "value": 0, "start_value": "half DEX"},
    {"name": "Drive Auto", "value": 20, "start_value": 20},
    {"name": "Electrical Repair", "value": 10, "start_value": 10},
    {"name": "Fast Talk", "value": 5, "start_value": 5},
    {
        "name": "Fighting",
        "specializations": True,
        "value": 0,
        "start_value": 0,
        "subskills": [{"name": "Brawl", "value": 25, "start_value": 25}],
    },
    {
        "name": "Firearms",
        "specializations": True,
        "value": 0,
        "start_value": 0,
        "subskills": [
            {"name": "Handgun", "value": 20, "start_value": 20},
            {"name": "Rifle/Shotgun", "value": 25, "start_value": 25},
        ],
    },
    {"name": "First Aid", "value": 30, "start_value": 30},
    {"name": "History", "value": 5, "start_value": 5},
    {"name": "Intimidate", "value": 15, "start_value": 15},
    {"name": "Jump", "value": 20, "start_value": 20},
    {"name": "Language (Other)", "specializations": True, "value": 1, "start_value": 1},
    {"name": "Language (Own)", "value": 0, "start_value": "EDU"},
    {"name": "Law", "value": 5, "start_value": 5},
    {"name": "Library Use", "value": 20, "start_value": 20},
    {"name": "Listen", "value": 20, "start_value": 20},
    {"name": "Locksmith", "value": 1, "start_value": 1},
    {"name": "Mechanical Repair", "value": 10, "start_value": 10},
    {"name": "Medicine", "value": 1, "start_value": 1},
    {"name": "Natural World", "value": 10, "start_value": 10},
    {"name": "Navigate", "value": 10, "start_value": 10},
    {"name": "Occult", "value": 5, "start_value": 5},
    {"name": "Operate Heavy Machine", "value": 1, "start_value": 1},
    {"name": "Persuade", "value": 10, "start_value": 10},
    {"name": "Pilot", "specializations": True, "value": 1, "start_value": 1},
    {"name": "Psychology", "value": 10, "start_value": 10},
    {"name": "Psychoanalysis", "value": 1, "start_value": 1},
    {"name": "Ride", "value": 5, "start_value": 5},
    {"name": "Science", "specializations": True, "value": 1, "start_value": 1},
    {"name": "Sleight of Hand", "value": 10, "start_value": 10},
    {"name": "Spot Hidden", "value": 25, "start_value": 25},
    {"name": "Stealth", "value": 20, "start_value": 20},
    {"name": "Survival", "specializations": True, "value": 10, "start_value": 10},
    {"name": "Swim", "value": 20, "start_value": 20},
    {"name": "Throw", "value": 20, "start_value": 20},
    {"name": "Track", "value": 10, "start_value": 10},
]

MODERN_SKILLS: List[SkillInfo] = [
    {"name": "Computer Use", "value": 5, "start_value": 5},
    {"name": "Electronics", "value": 1, "start_value": 1},
]
