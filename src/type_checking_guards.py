from typing import Any, TypeGuard

from pydantic import TypeAdapter, ValidationError

import character_sheet_types


def isRepresentInt(value: Any) -> TypeGuard[int]:
    if isinstance(value, int):
        return True
    if value[0] in ("-", "+"):
        return value[1:].isdigit()
    return value.isdigit()


def isAbilityName(value: Any) -> TypeGuard[character_sheet_types.AbilityNameType]:
    if value in ["str", "dex", "con", "wis", "int", "cha"]:
        return True
    return False


def isRollableStatType(item: Any) -> TypeGuard[character_sheet_types.RollableStatType]:
    adapter = TypeAdapter(character_sheet_types.RollableStatType)
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False


def isListRollableStatType(item: Any) -> TypeGuard[list[character_sheet_types.RollableStatType]]:
    adapter = TypeAdapter(list[character_sheet_types.RollableStatType])
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False


def isListClassStatType(item: Any) -> TypeGuard[list[character_sheet_types.ClassDictType]]:
    adapter = TypeAdapter(list[character_sheet_types.ClassDictType])
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False


def isStaticStatType(item: Any) -> TypeGuard[character_sheet_types.StaticStatType]:
    adapter = TypeAdapter(character_sheet_types.StaticStatType)
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False


def isListStaticStatType(item: Any) -> TypeGuard[list[character_sheet_types.StaticStatType]]:
    adapter = TypeAdapter(list[character_sheet_types.StaticStatType])
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False


def isListIntBonusType(item: Any) -> TypeGuard[list[character_sheet_types.IntBonusType]]:
    adapter = TypeAdapter(list[character_sheet_types.IntBonusType])
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False


def isListIntOrStrBonusType(item: Any) -> TypeGuard[list[character_sheet_types.IntOrStrBonusType]]:
    adapter = TypeAdapter(list[character_sheet_types.IntOrStrBonusType])
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False
