from typing import Literal, TypedDict


class Bonus(TypedDict):
    name: str
    value: str | int
    multiplier: float
    manual: bool


class TextData(TypedDict):
    name: str
    type: str
    source: str
    manual: bool


class TextDataWithIdx(TextData):
    name_idx: int
    type_idx: int


class Condition(TypedDict):
    name: str
    description: str
    enabled: bool
    custom: bool


class BonusTo(TypedDict):
    name: str
    target: str
    bonus: Bonus
    manual: bool


class Counter(TypedDict):
    id: str
    name: str
    parent: str
    current: int
    max: int
    display_type: Literal["Checkboxes", "+- Buttons"]
    bonuses: list[Bonus]
    min: int
    manual: bool