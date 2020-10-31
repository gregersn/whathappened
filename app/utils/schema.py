import copy
from packaging.version import Version, parse


def up_or_down(from_version: Version, to_version: Version) -> int:
    if from_version == to_version:
        return 0

    if from_version > to_version:
        return -1

    if to_version > from_version:
        return 1

    raise Exception("Version comparison error")


def find_migration(version: Version, direction: int, migrations):
    for m in migrations:
        if direction > 0 and parse(m['from']) == version:
            return m

        if direction < 0 and parse(m['to']) == version:
            return m


def migrate(data, to_version, migrations=None):
    data = copy.deepcopy(data)
    from_version = parse(data['meta']['Version'])
    direction = up_or_down(from_version, parse(to_version))
    if direction == 0:
        return data

    migrator = find_migration(from_version, direction, migrations)

    if migrator is None:
        raise Exception("Migrator not found")

    if direction < 0:
        return migrator['down'](data)

    if direction > 0:
        return migrator['up'](data)
