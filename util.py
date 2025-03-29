# TODO: move to util.py or something
from typing import Any, TypeGuard

from pydantic import TypeAdapter, ValidationError

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


def isPassiveName(string: int | str) -> TypeGuard[character_sheet_types.PassiveNameType]:
    if string in ["perception", "investigation", "insight"]:
        return True
    return False


def isRollableStatType(dictionary: Any | Any) -> TypeGuard[character_sheet_types.RollableStatType]:
    rollable_stat_adapter = TypeAdapter(character_sheet_types.RollableStatType)
    try:
        rollable_stat_adapter.validate_python(dictionary)
        return True
    except ValidationError:
        return False


def isStaticStatType(dictionary: Any | Any) -> TypeGuard[character_sheet_types.StaticStatType]:
    static_stat_adapter = TypeAdapter(character_sheet_types.StaticStatType)
    try:
        static_stat_adapter.validate_python(dictionary)
        return True
    except ValidationError:
        return False


def isListIntBonusType(dictionary: Any | Any) -> TypeGuard[list[character_sheet_types.IntBonusType]]:
    static_stat_adapter = TypeAdapter(list[character_sheet_types.IntBonusType])
    try:
        static_stat_adapter.validate_python(dictionary)
        return True
    except ValidationError:
        return False


def isListIntOrStrBonusType(dictionary: Any | Any) -> TypeGuard[list[character_sheet_types.IntOrStrBonusType]]:
    static_stat_adapter = TypeAdapter(list[character_sheet_types.IntOrStrBonusType])
    try:
        static_stat_adapter.validate_python(dictionary)
        return True
    except ValidationError:
        return False
