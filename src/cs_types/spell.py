from typing import TypedDict

from cs_types.components import Condition
from cs_types.stats import RollableStat


class SpellComponent(TypedDict):
    v: bool
    s: bool
    m: bool | str
    c: bool


class SpellRange(TypedDict):
    type: str
    amount: int


class SpellTime(TypedDict):
    type: str
    amount: int


class SpellDuration(TypedDict):
    type: str
    time: SpellTime


class DiceRoll(TypedDict):
    dice: int
    amount: int


class SpellDamage(TypedDict):
    roll: DiceRoll
    scaling_level: dict[int, DiceRoll]
    scaling_slot: dict[int, DiceRoll]


class Spell(TypedDict):
    id: str
    name: str
    description: str
    
    level: int
    school: str
    
    classes: list[str]
    subclasses: list[str]

    casting_time: list[SpellTime]
    duration: list[SpellDuration]
    concentration: bool
    
    range: list[SpellRange]
    area: list[str]
    
    components: SpellComponent
    ritual: bool

    to_hit: RollableStat
    damage: list[SpellDamage]
    damage_type: list[str]
    condition_inflicted: list[Condition]

    saving_throw: list[str]

    tags: list[str]