import math

def convert_from_dholes(indata):
    investigator = indata['Investigator']

    def convert_skills(skills):
        inskills = skills['Skill']
        outskills = []

        for skill in inskills:
            outskills.append(skill)

        return outskills
    
    def convert_weapons(weapons):
        inweapons = weapons['weapon']
        outweapons = []
        for weapon in inweapons:
            outweapons.append(weapon)
        return outweapons

    def convert_possessions(possessions):
        inpossessions = possessions['item']
        outpossessions = []
        for item in inpossessions:
            outpossessions.append(item['description'])

        return outpossessions

    header = investigator['Header']
    personal_details = investigator['PersonalDetails']
    characteristics = investigator['Characteristics']
    skills = convert_skills(investigator['Skills'])
    talents = investigator['Talents']
    weapons = convert_weapons(investigator['Weapons'])
    combat = investigator['Combat']
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


def convert_to_dholes(indata):
    def convert_skills(skills):
        outskills = []
        for skill in skills:
            skill['half'] = str(math.floor(int(skill['value'], 10) / 2))
            skill['fifth'] = str(math.floor(int(skill['value'], 10) / 5))

            outskills.append(
                skill
            )

        return {
                'Skill': skills
        }

    def convert_weapons(weapons):
        outweapons = []
        for weapon in weapons:
            outweapons.append(weapon)
        return {'weapon': outweapons}

    def convert_possessions(possessions):
        outpossessions = []
        for possession in possessions:
            outpossessions.append(
                {'description': possession}
            )
        return {'item': outpossessions}

    return {
        'Investigator': {
            'Header': indata['meta'],
            'PersonalDetails': indata['personalia'],
            'Characteristics': indata['characteristics'],
            'Skills': convert_skills(indata['skills']),
            'Talents': None,
            'Weapons': convert_weapons(indata['weapons']),
            'Combat': indata['combat'],
            'Backstory': indata['backstory'],
            'Possessions': convert_possessions(indata['possessions']),
            'Cash': indata['cash'],
            'Assets': indata['assets']
        }
    }

