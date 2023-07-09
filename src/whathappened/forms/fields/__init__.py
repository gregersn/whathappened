import json
import yaml
from wtforms.fields.simple import TextAreaField
from .alchemy import QuerySelectField, QuerySelectMultipleField  # noqa


class JsonField(TextAreaField):
    def _value(self):
        return self.data or {}

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])
            except ValueError as exc:
                raise ValueError("This field is not valid JSON") from exc
        else:
            self.data = None

    def pre_validate(self, form):
        super().pre_validate(form)
        if self.data:
            try:
                json.dumps(self.data)
            except TypeError:
                raise ValueError("Invalid JSON")


class YamlField(TextAreaField):
    def _value(self):
        return yaml.dump(self.data, indent=4) if self.data else ""

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = yaml.load(valuelist[0], yaml.SafeLoader)
            except ValueError:
                raise ValueError("This field is not valid YAML")
        else:
            self.data = None

    def pre_validate(self, form):
        super().pre_validate(form)
        if self.data:
            try:
                yaml.dump(self.data)
            except TypeError:
                raise ValueError("Invalid YAML")
