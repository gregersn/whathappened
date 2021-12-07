from collections import ChainMap, UserList
from collections.abc import Mapping
import copy

from typing import Dict, Any, MutableSequence, MutableMapping


class ChangedList(UserList):
    def __init__(self, initlist=None):
        super().__init__(initlist=initlist)
        self.original = self.data.copy()

    @property
    def changed(self):
        if self.original != self.data:
            return True
        return False


class ChainedSheet(ChainMap):
    submaps: Dict[Any,  Any] = {}

    def __init__(self, *maps: MutableMapping[Any, Any]):
        self.maps = list(maps) or [{}]          # always at least one map

    def _subsearch(self, key: Any) -> Any:
        for mapping in self.maps[1:]:
            if key in mapping:
                return mapping[key]

    def __getitem__(self, key: Any) -> Any:
        submaps = [mapping for mapping in self.maps if key in mapping]
        val = super().__getitem__(key)
        if isinstance(val, MutableMapping):
            if key not in self.maps[0]:
                self.submaps[key] = {}
                self.maps[0][key] = ChainedSheet(self.submaps[key], val)
            elif not isinstance(val, ChainMap):
                v = self._subsearch(key)
                if v is not None and not isinstance(v, ChainMap):
                    if key not in self.submaps:
                        self.submaps[key] = val
                    self.maps[0][key] = ChainedSheet(self.submaps[key], v)
            return self.maps[0][key]

        if isinstance(val, MutableSequence):
            if key not in self.maps[0]:
                self.maps[0][key] = ChangedList(val)
                return self.maps[0][key]

        return val

    def __setitem__(self, key: Any, value: Any):
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
            if val == {}:
                continue

            if isinstance(val, ChangedList):
                if val.changed:
                    val = val.data
                else:
                    continue

            # if val == self.maps[1][key]:
            #    continue

            d[key] = val
        return d
