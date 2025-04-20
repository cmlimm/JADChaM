from typing import Any, Optional, Protocol, TypedDict

from imgui_bundle import imgui
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore


class FontHolder:
    regular_font: imgui.ImFont
    bold_font: imgui.ImFont


class Bonus(TypedDict):
    name: str
    value: str | int
    multiplier: float
    manual: bool


class CharacterClass(TypedDict):
    name: str
    total: int
    level: int
    dice: int
    manual: bool


class Level(TypedDict):
    total: int
    classes: list[CharacterClass]


class Hp(TypedDict):
    current: int
    max_total: int
    max_base: int
    temp: int
    max_hp_bonuses: list[Bonus]


class Proficiency(TypedDict):
    total: int


class Armor(TypedDict):
    name: str
    armor_class: int
    max_dex_bonus: int


class ArmorClass(TypedDict):
    total: int
    base: int
    armor: Armor
    bonuses: list[Bonus]


class Ability(TypedDict):
    name: str
    total: int
    total_base_score: int

    base_score_overrides: list[Bonus]
    base_score_bonuses: list[Bonus]
    base_score: int

    modifier_bonuses: list[Bonus]
    manual: bool


class RollableStat(TypedDict):
    name: str
    total: int
    bonuses: list[Bonus]
    manual_advantage: bool
    manual_disadvantage: bool
    manual: bool


class StaticStat(TypedDict):
    name: str
    total: int
    base: int
    base_overrides: list[Bonus]
    bonuses: list[Bonus]
    manual: bool


class Training(TypedDict):
    name: str
    type: str
    source: str
    manual: bool


class CharacterData(TypedDict):
    name: str
    image_path: str
    level: Level
    hp: Hp
    proficiency: Proficiency
    initiative: RollableStat
    armor_class: ArmorClass

    abilities: list[Ability]
    saves: list[RollableStat]
    skills: list[RollableStat]

    speed: list[StaticStat]
    passive_skill: list[StaticStat]
    sense: list[StaticStat]

    training: list[Training]


class NewBonus(TypedDict):
    new_bonus_name: str
    new_bonus_type: str
    new_bonus_value: int | str
    new_bonus_mult: float


class States(TypedDict):
    hp_dice_idx: int

    new_item_name: str

    hp_add: str

    new_bonuses: dict[str, NewBonus]
    new_training: Training
    

class MainWindowProtocol(Protocol):
    regular_font: imgui.ImFont
    bold_font: imgui.ImFont
    theme: str
    states: States

    open_file_dialog: Optional[pfd.open_file]
    file_path: list[str]

    open_image_dialog: Optional[pfd.open_file]
    
    data: CharacterData
    is_character_loaded: bool

    data_refs: dict[str, CharacterClass | Ability | RollableStat | StaticStat]

    def __call__(self, font_holder: FontHolder) -> None: ...


def main_window_decorator(func: Any) -> MainWindowProtocol:
    return func
