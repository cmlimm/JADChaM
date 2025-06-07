from cs_types.stats import RollableStat
from typing import Optional, TypedDict


class SpellComponent(TypedDict):
    v: bool
    s: bool
    m: bool | str


class SpellRange(TypedDict):
    type: str
    amount: Optional[int]


class SpellTime(TypedDict):
    type: str
    amount: Optional[int]


class SpellDuration(TypedDict):
    type: str
    time: Optional[SpellTime]


class DiceRoll(TypedDict):
    dice: int
    amount: int


class SpellDamage(TypedDict):
    type: str
    roll: DiceRoll
    scaling: dict[int, DiceRoll]


class Spell(TypedDict, total=False):
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

    to_hit: Optional[RollableStat]
    damage_inflicted: Optional[list[SpellDamage]]
    condition_inflicted: Optional[list[str]]

    saving_throw: Optional[list[str]]

    tags: list[str]