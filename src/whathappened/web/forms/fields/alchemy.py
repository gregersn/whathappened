"""
Copyright (c) 2012, Konsta Vesterinen

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* The names of the contributors may not be used to endorse or promote products
  derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import operator
import warnings

from typing import Any, Optional
from wtforms import widgets
from wtforms.fields import SelectFieldBase
from wtforms.validators import ValidationError

from sqlalchemy.orm.util import identity_key


class QuerySelectField(SelectFieldBase):
    """
    Will display a select drop-down field to choose between ORM results in a
    sqlalchemy `Query`.  The `data` property actually will store/keep an ORM
    model instance, not the ID. Submitting a choice which is not in the query
    will result in a validation error.
    This field only works for queries on models whose primary key column(s)
    have a consistent string representation. This means it mostly only works
    for those composed of string, unicode, and integer types. For the most
    part, the primary keys will be auto-detected from the model, alternately
    pass a one-argument callable to `get_pk` which can return a unique
    comparable key.
    The `query` property on the field can be set from within a view to assign
    a query per-instance to the field. If the property is not set, the
    `query_factory` callable passed to the field constructor will be called to
    obtain a query.
    Specify `get_label` to customize the label associated with each option. If
    a string, this is the name of an attribute on the model object to use as
    the label text. If a one-argument callable, this callable will be passed
    model instance and expected to return the label text. Otherwise, the model
    object's `__str__` or `__unicode__` will be used.
    If `allow_blank` is set to `True`, then a blank choice will be added to the
    top of the list. Selecting this choice will result in the `data` property
    being `None`. The label for this blank choice can be set by specifying the
    `blank_text` parameter.
    """

    widget = widgets.Select()
    _formdata: Optional[set]
    _data: Any

    def __init__(
        self,
        label=None,
        validators=None,
        query_factory=None,
        get_pk=None,
        get_label=None,
        allow_blank=False,
        blank_text="",
        **kwargs,
    ):
        super().__init__(label, validators, **kwargs)
        self.query_factory = query_factory

        if get_pk is None:
            self.get_pk = get_pk_from_identity
        else:
            self.get_pk = get_pk

        if get_label is None:
            self.get_label = lambda x: x
        elif isinstance(get_label, (str,)):
            self.get_label = operator.attrgetter(get_label)
        else:
            self.get_label = get_label

        self.allow_blank = allow_blank
        self.blank_text = blank_text
        self.query = None
        self._object_list = None

    def _get_data(self):
        if self._formdata is not None:
            for pk, obj in self._get_object_list():
                if pk == self._formdata:
                    self._set_data(obj)
                    break
        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def _get_object_list(self):
        if self._object_list is None:
            query = (
                self.query
                if self.query is not None
                else self.query_factory()
                if self.query_factory
                else []
            )
            get_pk = self.get_pk
            self._object_list = list((str(get_pk(obj)), obj) for obj in query)
        return self._object_list

    def iter_choices(self):
        if self.allow_blank:
            yield ("__None", self.blank_text, self.data is None, {})

        for pk, obj in self._get_object_list():
            yield (pk, self.get_label(obj), obj == self.data, {})

    def iter_groups(self):
        raise NotImplementedError()

    def process_formdata(self, valuelist):
        if valuelist:
            if self.allow_blank and valuelist[0] == "__None":
                self.data = None
            else:
                self._data = None
                self._formdata = valuelist[0]

    def pre_validate(self, form):
        data = self.data
        if data is not None:
            for _, obj in self._get_object_list():
                if data == obj:
                    break
            else:
                raise ValidationError(self.gettext("Not a valid choice"))
        elif self._formdata or not self.allow_blank:
            raise ValidationError(self.gettext("Not a valid choice"))


class QuerySelectMultipleField(QuerySelectField):
    """
    Very similar to QuerySelectField with the difference that this will
    display a multiple select. The data property will hold a list with ORM
    model instances and will be an empty list when no value is selected.
    If any of the items in the data list or submitted form data cannot be
    found in the query, this will result in a validation error.
    """

    widget = widgets.Select(multiple=True)

    def __init__(self, label=None, validators=None, default=None, **kwargs):
        if default is None:
            default = []
        super().__init__(label, validators, default=default, **kwargs)
        if kwargs.get("allow_blank", False):
            warnings.warn(
                "allow_blank=True does not do anything for QuerySelectMultipleField."
            )
        self._invalid_formdata = False

    def _get_data(self):
        formdata = self._formdata
        if formdata is not None:
            data = []
            for pk, obj in self._get_object_list():
                if not formdata:
                    break

                if pk in formdata:
                    formdata.remove(pk)
                    data.append(obj)
            if formdata:
                self._invalid_formdata = True
            self._set_data(data)
        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def iter_choices(self):
        for pk, obj in self._get_object_list():
            yield (pk, self.get_label(obj), obj in self.data, {})

    def iter_groups(self):
        raise NotImplementedError()

    def process_formdata(self, valuelist):
        self._formdata = set(valuelist)

    def pre_validate(self, form):
        if self._invalid_formdata:
            raise ValidationError(self.gettext("Not a valid choice"))

        if self.data:
            obj_list = list(x[1] for x in self._get_object_list())
            for v in self.data:
                if v not in obj_list:
                    raise ValidationError(self.gettext("Not a valid choice"))


def get_pk_from_identity(obj):
    """Get primary key from identity."""
    _, key = identity_key(instance=obj)[0:2]
    return ":".join(str(x) for x in key)