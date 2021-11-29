from collections.abc import MutableMapping
from collections import ChainMap
from collections.abc import Mapping
import copy

from typing import Dict, Any


class ChainedSheet(ChainMap):
    submaps: Dict[str,  Any] = {}

    def __getitem__(self, key):
        val = super().__getitem__(key)
        if isinstance(val, MutableMapping):
            if key not in self.maps[0]:
                self.submaps[key] = {}
                self.maps[0][key] = ChainedSheet(self.submaps[key], val)
                return self.maps[0][key]

        return val

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        return super().__iter__()

    def __len__(self):
        raise NotImplementedError

    def _keytransform(self, key):
        raise NotImplementedError

    def to_dict(self):
        return self.maps[0]

    def changes(self):
        sheet = self.maps[0]
        d = {}
        for key in sheet:
            val = sheet[key]
            if isinstance(val, ChainedSheet):
                val = val.changes()
            d[key] = val
        return d
