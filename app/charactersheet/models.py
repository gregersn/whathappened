import json
from functools import reduce
from jsoncomment import JsonComment
from datetime import datetime
import base64
import io
from PIL import Image

from app import db


def fix_image(imagedata: str) -> str:
    imagetype, imagedata = imagedata.split(',')
    decoded = base64.b64decode(imagedata)
    buf = io.BytesIO(decoded)
    img = Image.open(buf)
    img.thumbnail((192, 192))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')


class Character(db.Model):
    __tablename__ = 'charactersheet'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))

    def __repr__(self):
        return '<Character {}>'.format(self.title)

    def __init__(self, *args, **kwargs):
        super(Character, self).__init__(*args, **kwargs)
        self.data = None

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': JsonComment(json).loads(self.body),
            'timestamp': self.timestamp,
            'user_id': self.user_id
        }

    def get_sheet(self):
        return JsonComment(json).loads(self.body)

    def check_data(self):
        if not hasattr(self, 'data') or self.data is None:
            self.data = JsonComment(json).loads(self.body)

    def attribute(self, *args):
        self.check_data()

        path = args[0]

        val = reduce(lambda x, y: x.get(y, None) if x is not None else None,
                     path.split("."),
                     self.data)

        return val

    def set_attribute(self, attribute):
        """Set a specific attribute."""
        self.check_data()

        if attribute.get('type', None) == 'skill':
            print("Set a skill")
            path, skill = attribute['field'].split('#')
            subfield = attribute.get('subfield', None)
            value = attribute.get('value')
            skills = reduce(lambda x, y: x[y], path.split("."),
                            self.data)
            for s in skills:
                if s['name'] == skill:
                    if (subfield is not None
                            and subfield != s.get('subskill', 'None')):
                        continue
                    print("Setting value")
                    s['value'] = value

        elif attribute.get('type', None) == 'skillcheck':
            print("Check a skill")
            path, skill = attribute['field'].split('#')
            subfield = attribute.get('subfield', None)
            check = attribute.get('value', False)
            skills = reduce(lambda x, y: x[y], path.split("."), self.data)
            for s in skills:
                if s['name'] == skill:
                    if (subfield is not None
                            and subfield != s.get('subskill', 'None')):
                        continue
                    s['checked'] = check

        elif attribute.get('type', None) == 'occupationcheck':
            print("Mark occupation skill")
            path, skill = attribute['field'].split('#')
            subfield = attribute.get('subfield', None)
            check = attribute.get('value', False)
            skills = reduce(lambda x, y: x[y], path.split("."), self.data)
            for s in skills:
                if s['name'] == skill:
                    if (subfield is not None
                            and subfield != s.get('subskill', 'None')):
                        continue
                    s['occupation'] = check
        
        elif attribute.get('type', None) == 'portrait':
            print("Set portrait")
            data = attribute.get('value', None)
            self.set_portrait(data)
        else:
            print("Set some other attribute")
            s = reduce(lambda x, y: x[y], attribute['field'].split(".")[:-1],
                       self.data)
            s[attribute['field'].split(".")[-1]] = attribute['value']

    def store_data(self):
        """Put loaded data back into JSON."""
        self.check_data()
        self.body = json.dumps(self.data)

    def skill(self, skillpath, subskill=None):
        """Return a single skill, or something."""
        self.check_data()
        path, skill = skillpath.split('#')

        skills = self.skills()

        for s in skills:
            if s['name'] == skill:
                if subskill is not None and subskill != s.get('subskill',
                                                              'None'):
                    print("Wrong subskill", skill, repr(subskill))
                    continue
                return s

        print("Did not find", skill, subskill)
        return 0

    def skills(self, *args):
        """Return a list of skills."""
        self.check_data()
        return self.data['skills']

    def add_skill(self, skillname, value="1"):
        self.check_data()
        self.data['skills'].append({"name": skillname, "value": str(value)})
        if isinstance(self.data['skills'], list):
            self.data['skills'].sort(key=lambda x: x['name'])

    def get_portrait(self):
        self.check_data()
        return self.data['personalia']['Portrait']

    def set_portrait(self, data):
        self.check_data()
        self.data['personalia']['Portrait'] = fix_image(data)
        return self.get_portrait()
