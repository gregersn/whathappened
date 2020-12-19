import logging
import json
import jinja2
import math
import time
from typing import Literal
import os

from ..core import register_game
from ..schema import validate

logger = logging.getLogger(__name__)

schema_file = os.path.join(os.path.dirname(__file__), '../schema/coc7e.json')

# This is not pretty
GameType = Literal["Classic (1920's)", "Modern"]
GameTypes = ["Classic (1920's)", "Modern"]

from .mechanics import CoCMechanics
from .forms import CreateForm

CHARACTER_TEMPLATE = 'character/coc7e/blank_character.json.jinja'

from .routes import view


def new_character(title, gametype: GameType):
    templateloader = jinja2 \
                     .FileSystemLoader(searchpath="./app/character/templates/")
    templateenv = jinja2.Environment(loader=templateloader)
    template = templateenv.get_template(CHARACTER_TEMPLATE)
    gtype = gametype
    return json.loads(template.render(title=title,
                                      timestamp=time.time(),
                                      type=gtype))


def convert_from_dholes(indata):
    investigator = indata

    if 'Investigator' in indata:
        investigator = indata['Investigator']

    def convert_header(header):
        del header['Version']
        return header

    def convert_skills(skills):
        inskills = skills['Skill']
        outskills = []

        skill_index = {}
        subskills = []

        for skill in inskills:
            skill.pop('fifth', None)
            skill.pop('half', None)

            skill['start_value'] = skill['value']

            if 'occupation' in skill:
                skill['occupation'] = skill['occupation'] == "true"

            if 'subskill' in skill:
                if skill['subskill'] == 'None':
                    del skill['subskill']
                else:
                    subskills.append(skill)
                    continue

            if skill['name'] not in skill_index:
                skill_index[skill['name']] = skill
                outskills.append(skill)

        for subskill in subskills:
            if subskill['name'] not in skill_index:
                if subskill['name'] == "Language (Own)":
                    del subskill['subskill']
                    outskills.append(subskill)
                    skill_index[subskill['name']] = subskill
                    continue
                else:
                    parent_skill = {
                        'name': subskill['name'],
                        'value': subskill['value'],
                        'start_value': subskill['value'],
                        'subskills': [
                            {
                                'name': subskill['subskill'],
                                'value': subskill['value'],
                                'start_value': subskill['value']
                            }
                        ]
                    }
                    outskills.append(parent_skill)
                    skill_index[parent_skill['name']] = parent_skill

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

    header = convert_header(investigator['Header'])
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
        'version': '0.0.3',
        'system': 'coc7e',
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
    if type(value) == str:
        value = int(value, 10)
    return str(math.floor(value / 2))


def fifth(value):
    if type(value) == str:
        value = int(value, 10)
    return str(math.floor(value / 5))


def convert_to_dholes(indata):
    def convert_skills(skills):
        outskills = []
        for skill in skills:
            skill['half'] = half(skill['value'])
            skill['fifth'] = fifth(skill['value'])
            if 'occupation' in skill:
                skill['occupation'] = ("true" if skill['occupation']
                                       else "false")

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


register_game('coc7e', 'Call of Cthulhu TM', CoCMechanics)
