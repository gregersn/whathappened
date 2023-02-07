from pathlib import Path
from typing import Dict


class Sheet:
    _filename: Path
    _schema: Path

    def save(self):
        raise NotImplementedError

    @classmethod
    def load(cls, data: Dict):
        raise NotImplementedError
