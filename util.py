# TODO: move to util.py or something
from typing import TypeGuard

import character_sheet_types


def isRepresentInt(value: int | str) -> TypeGuard[int]:
    if isinstance(value, int):
        return True
    if value[0] in ("-", "+"):
        return value[1:].isdigit()
    return value.isdigit()


def isAbilityName(string: int | str) -> TypeGuard[character_sheet_types.AbilityNameType]:
    if string in ["str", "dex", "con", "wis", "int", "cha"]:
        return True
    return False


def isSpeedName(string: int | str) -> TypeGuard[character_sheet_types.SpeedNameType]:
    if string in ["walking", "climbing", "swimming", "flying"]:
        return True
    return False
