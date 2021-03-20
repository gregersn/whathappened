from .utils import half, fifth


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

            skill['value'] = int(skill['value'])
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
            weapon['regular'] = int(weapon['regular'])
            ammo = weapon['ammo']
            try:
                ammo = int(ammo, 10)
            except ValueError:
                pass
            weapon['ammo'] = ammo

            malf = weapon['malf']
            try:
                malf = int(malf, 10)
            except ValueError:
                pass
            weapon['malf'] = malf

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

    def convert_characteristics(characteristics):
        for k, v in characteristics.items():
            try:
                characteristics[k] = int(v, 10)
            except ValueError:
                print("WTF")
        return characteristics

    header = convert_header(investigator['Header'])
    personal_details = investigator['PersonalDetails']
    characteristics = convert_characteristics(investigator['Characteristics'])
    skills = convert_skills(investigator['Skills'])
    # talents = investigator['Talents']  # Not used
    weapons = convert_weapons(investigator['Weapons'])
    combat = convert_combat(investigator['Combat'])
    backstory = investigator['Backstory']
    possessions = convert_possessions(investigator['Possessions'])
    cash = investigator['Cash']
    assets = investigator['Assets']

    return {
        'version': '0.0.4',
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
