import re
import random


REGEX_DIE = re.compile(r'(?P<count>\d*)?d(?P<sides>\d+)')


def parse_rolls(command: str):
    match = re.match(REGEX_DIE, command)
    count = int(match.group('count'), 10) if match.group('count') else 1
    sides = int(match.group('sides'), 10)
    return {
        sides: count,
    }


def roll_die(sides: int) -> int:
    return random.randint(1, sides)


def roll(command: str) -> int:
    rolls = parse_rolls(command)
    total = 0
    for sides, count in rolls.items():
        for i in range(count):
            total += roll_die(sides)
    return total
