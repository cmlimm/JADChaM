from typing import Any, TypeGuard

from pydantic import TypeAdapter, ValidationError

from cs_types.core import Ability, CharacterClass, Feature
from cs_types.stats import RollableStat, StaticStat


def isRepresentInt(value: Any) -> TypeGuard[int]:
    try:
        int(value)
        return True
    except ValueError:
        return False


def isRepresentFloat(value: Any) -> TypeGuard[float]:
    try:
        float(value)
        return True
    except ValueError:
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
    

def isFeatureList(item: Any) -> TypeGuard[list[Feature]]:
    adapter = TypeAdapter(list[Feature])
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False
    
def isFeature(item: Any) -> TypeGuard[Feature]:
    adapter = TypeAdapter(Feature)
    try:
        adapter.validate_python(item)
        return True
    except ValidationError:
        return False