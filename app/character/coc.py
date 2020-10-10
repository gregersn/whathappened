import json
from jsoncomment import JsonComment
import jinja2
import math
import time
from typing import Literal


GameTypes = ["Classic (1920's)", "Modern"]
GameType = Literal["Classic (1920's)", "Modern"]


schema = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "properties": {
        "meta": {
            "type": "object",
            "properties": {
                "Title": {"type": "string"},
                "Creator": {"type": "string"},
                "CreateDate": {"type": "string"},
                "GameName": {"type": "string"},
                "GameVersion": {"type": "string"},
                "GameType": {
                    "type": "string",
                    "enum": GameTypes
                },
                "Disclaimer": {"type": "string"},
                "Version": {"type": "string", "value": "0.0.1"}
            }
        },
        "personalia": {
            "type": "object",
            "properties": {
                "Name": {"type": "string"},
                "Occupation": {"type": "string"},
                "Gender": {"type": "string"},
                "Age": {"type": "string"},
                "Birthplace": {"type": "string"},
                "Residence": {"type": "string"}
            }
        },
        "characteristics": {
            "type": "object",
            "properties": {
                "STR": {"type": "string"},
                "DEX": {"type": "string"},
                "INT": {"type": "string"},
                "CON": {"type": "string"},
                "APP": {"type": "string"},
                "POW": {"type": "string"},
                "SIZ": {"type": "string"},
                "EDU": {"type": "string"},
                "Move": {"type": "string"},
                "Luck": {"type": "string"},
                "LuckMax": {"type": "string"},
                "Sanity": {"type": "string"},
                "SanityStart": {"type": "string"},
                "SanityMax": {"type": "string"},
                "MagicPts": {"type": "string"},
                "MagicPtsMax": {"type": "string"},
                "HitPts": {"type": "string"},
                "HitPtsMax": {"type": "string"},
            }
        },
        "skills": {
            "type": "array",
            "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "value": {"type": "string"}
                    }
            }
        },
        "weapons": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "regular": {"type": "string"},
                    "damage": {"type": "string"},
                    "range": {"type": "string"},
                    "attacks": {"type": "string"},
                    "ammo": {"type": "string"},
                    "malf": {"type": "string"}
                }
            }
        },
        "combat": {
            "type": "object",
            "properties": {
                "DamageBonus": {"type": "string"},
                "Build": {"type": "string"},
                "Dodge": {"type": "string"}
            }
        },
        "backstory": {
            "type": "object",
            "properties": {
                "description": {
                    "anyOf": [{"type": "string"}, {"type": "null"}]
                },
                "traits": {
                    "anyOf": [{"type": "string"}, {"type": "null"}]
                },
                "ideology": {
                    "anyOf": [{"type": "string"}, {"type": "null"}]
                },
                "injurues": {
                    "anyOf": [{"type": "string"}, {"type": "null"}]
                },
                "people": {
                    "anyOf": [{"type": "string"}, {"type": "null"}]
                },
                "phobias": {
                    "anyOf": [{"type": "string"}, {"type": "null"}]
                },
                "locations": {
                    "anyOf": [{"type": "string"}, {"type": "null"}]
                },
                "tomes": {
                    "anyOf": [{"type": "string"}, {"type": "null"}]
                },
                "possessions": {
                    "anyOf": [{"type": "string"}, {"type": "null"}]
                },
                "encounters": {
                    "anyOf": [{"type": "string"}, {"type": "null"}]
                }
            }
        },
        "possessions": {
            "anyOf": [{"type": "array"}, {"type": "null"}]
        },
        "cash": {
            "type": "object",
            "properties": {
                "spending": {"type": "string"},
                "cash": {"type": "string"},
                "assets": {"type": "string"}
            }
        },
        "assets": {
            "anyOf": [{"type": "object"}, {"type": "null"}]
        }
    }
}


def new_character(title, gametype: GameType):
    templateloader = jinja2.FileSystemLoader(searchpath="./app/character/templates/")
    templateenv = jinja2.Environment(loader=templateloader)
    template = templateenv.get_template('character/blank_character.json.jinja')
    gtype = gametype
    return JsonComment(json).loads(template.render(title=title,
                                   timestamp=time.time(),
                                   type=gtype))


def convert_from_dholes(indata):
    investigator = indata

    if 'Investigator' in indata:
        investigator = indata['Investigator']

    def convert_skills(skills):
        inskills = skills['Skill']
        outskills = []

        for skill in inskills:
            skill.pop('fifth', None)
            skill.pop('half', None)
            outskills.append(skill)

        return outskills

    def convert_weapons(weapons):
        inweapons = weapons['weapon']
        if not isinstance(inweapons, list):
            inweapons = [inweapons, ]
        outweapons = []
        for weapon in inweapons:
            weapon.pop('hard', None)
            weapon.pop('extreme', None)
            outweapons.append(weapon)
        return outweapons

    def convert_possessions(possessions):
        outpossessions = []
        if possessions is not None:
            inpossessions = possessions['item']
            for item in inpossessions:
                outpossessions.append(item['description'])

        return outpossessions

    def convert_combat(combat):
        return {
            'DamageBonus': combat['DamageBonus'],
            'Build': combat['Build'],
            'Dodge': combat['Dodge']['value']
        }

    header = investigator['Header']
    personal_details = investigator['PersonalDetails']
    characteristics = investigator['Characteristics']
    skills = convert_skills(investigator['Skills'])
    # talents = investigator['Talents']  # Not used
    weapons = convert_weapons(investigator['Weapons'])
    combat = convert_combat(investigator['Combat'])
    backstory = investigator['Backstory']
    possessions = convert_possessions(investigator['Possessions'])
    cash = investigator['Cash']
    assets = investigator['Assets']

    return {
        'meta': header,
        'personalia': personal_details,
        'characteristics': characteristics,
        'skills': skills,
        'weapons': weapons,
        'combat': combat,
        'backstory': backstory,
        'possessions': possessions,
        'cash': cash,
        'assets': assets
    }


def half(value):
    return str(math.floor(int(value, 10) / 2))


def fifth(value):
    return str(math.floor(int(value, 10) / 5))


def convert_to_dholes(indata):
    def convert_skills(skills):
        outskills = []
        for skill in skills:
            skill['half'] = half(skill['value'])
            skill['fifth'] = fifth(skill['value'])

            outskills.append(
                skill
            )

        return {
                'Skill': skills
        }

    def convert_weapons(weapons):
        outweapons = []
        for weapon in weapons:
            weapon['hard'] = half(weapon['regular'])
            weapon['extreme'] = fifth(weapon['regular'])
            outweapons.append(weapon)
        return {'weapon': outweapons}

    def convert_possessions(possessions):
        outpossessions = []
        for possession in possessions:
            outpossessions.append(
                {'description': possession}
            )
        return {'item': outpossessions}

    def convert_combat(combat):
        return {
            'DamageBonus': combat['DamageBonus'],
            'Build': combat['Build'],
            'Dodge': {
                'value': combat['Dodge'],
                'half': half(combat['Dodge']),
                'fifth': fifth(combat['Dodge'])
            }
        }

    return {
        'Investigator': {
            'Header': indata['meta'],
            'PersonalDetails': indata['personalia'],
            'Characteristics': indata['characteristics'],
            'Skills': convert_skills(indata['skills']),
            'Talents': None,
            'Weapons': convert_weapons(indata['weapons']),
            'Combat': convert_combat(indata['combat']),
            'Backstory': indata['backstory'],
            'Possessions': convert_possessions(indata['possessions']),
            'Cash': indata['cash'],
            'Assets': indata['assets']
        }
    }
