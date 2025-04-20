from typing import Any, TypeGuard

from pydantic import TypeAdapter, ValidationError

from cs_types import Ability, CharacterClass, RollableStat, StaticStat


def isRepresentInt(value: Any) -> TypeGuard[int]:
    if isinstance(value, int):
        return True
    if isinstance(value, str):
        if value != "" and value[0] in ("-", "+"):
            return value[1:].isdigit()
        return value.isdigit()
    return False


def isClassList(item: Any) -> TypeGuard[list[CharacterClass]]:
    adapter = TypeAdapter(list[CharacterClass])
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False
    

def isAbilityList(item: Any) -> TypeGuard[list[Ability]]:
    adapter = TypeAdapter(list[Ability])
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False
    
def isRollableStatList(item: Any) -> TypeGuard[list[RollableStat]]:
    adapter = TypeAdapter(list[RollableStat])
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False
    
def isStaticStatList(item: Any) -> TypeGuard[list[StaticStat]]:
    adapter = TypeAdapter(list[StaticStat])
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False