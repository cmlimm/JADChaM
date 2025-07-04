from typing import TypedDict

from cs_types.components import Bonus


class RollableStat(TypedDict):
    id: str
    name: str
    total: int
    bonuses: list[Bonus]
    manual_advantage: bool
    manual_disadvantage: bool
    manual: bool


class StaticStat(TypedDict):
    id: str
    name: str
    total: int
    base: int
    base_overrides: list[Bonus]
    bonuses: list[Bonus]
    manual: bool