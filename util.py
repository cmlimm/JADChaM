# TODO: move to util.py or something
from typing import TypeGuard


def isRepresentInt(value: int | str) -> TypeGuard[int]:
    if isinstance(value, int):
        return True
    if value[0] in ("-", "+"):
        return value[1:].isdigit()
    return value.isdigit()


def isAbilityName(string: int | str) -> TypeGuard[str]:
    if string in ["str", "dex", "con", "wis", "int", "cha"]:
        return True
    return False


def isSpeedName(string: int | str) -> TypeGuard[str]:
    if string in ["walking", "climbing", "swimming", "flying"]:
        return True
    return False
