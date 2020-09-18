import math


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
