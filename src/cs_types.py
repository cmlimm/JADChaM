from typing import Any, Literal, Optional, TypedDict

from imgui_bundle import imgui
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore


class ListTypeToBonus(TypedDict):
    all: list[str]
    all_no_advantage: list[str]
    base_score: list[str]
    armor_class: list[str]
    speed: list[str]
    passive: list[str]
    sense: list[str]
    rollable: list[str]


class FontHolder:
    regular_font: imgui.ImFont
    bold_font: imgui.ImFont


class Bonus(TypedDict):
    name: str
    value: str | int
    multiplier: float
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


class CharacterClass(TypedDict):
    name: str
    subclass: str
    total: int
    level: int
    dice: int
    spell_save_enabled: bool
    spell_save: StaticStat
    manual: bool


class Level(TypedDict):
    name: str
    total: int
    classes: list[CharacterClass]


class Hp(TypedDict):
    name: str
    current: int
    max_total: int
    max_base: int
    temp: int
    bonuses: list[Bonus]


class Proficiency(TypedDict):
    name: str
    total: int


class Armor(TypedDict):
    name: str
    armor_class: int
    max_dex_bonus: int


class ArmorClass(TypedDict):
    name: str
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


class TextData(TypedDict):
    name: str
    type: str
    source: str
    manual: bool


class Condition(TypedDict):
    name: str
    description: str
    enabled: bool
    custom: bool


# class Property(TypedDict):
#     name: str
#     description: str


# class Reference(TypedDict):
#     name: str
#     ref: str
#     manual: bool


# class CounterReference(Reference):
#     amount: int


# class Damage(TypedDict):
#     name: str
#     total: int
#     dice_count: list[IntegerValue]
#     manual: bool


# class Attack(TypedDict):
#     name: str
#     description: str
#     properties: list[Property]
#     tags: list[str]

#     action: str

#     to_hit: IntegerValue
#     damage: list[Damage]
#     difficulty_class: list[IntegerValue]
#     range: IntegerValue
#     long_range: IntegerValue
#     area_of_effect: IntegerValue

#     uses: list[CounterReference]


class BonusTo(TypedDict):
    name: str
    target: str
    bonus: Bonus
    manual: bool


class Counter(TypedDict):
    name: str
    parent: str
    current: int
    max: int
    display_type: Literal["Checkboxes", "+- Buttons"] 
    bonuses: list[Bonus]
    min: int
    manual: bool


class Feature(TypedDict):
    name: str
    description: str
    tags: list[str]
    bonuses: list[BonusTo]
    counters: list[Counter]
    damage_effects: list[TextData]
    proficiencies: list[TextData]
    manual: bool


class CharacterData(TypedDict):
    name: str
    image_path: str
    level: Level
    hp: Hp
    damage_effects: list[TextData]
    default_conditions: list[Condition]
    custom_conditions: list[Condition]

    proficiency: Proficiency
    initiative: RollableStat
    armor_class: ArmorClass

    abilities: list[Ability]
    saves: list[RollableStat]
    skills: list[RollableStat]

    speed: list[StaticStat]
    passive_skill: list[StaticStat]
    sense: list[StaticStat]

    training: list[TextData]

    features: list[Feature]
    feature_windows: list[str]

    # attacks: list[Attack]
    # counters: list[IntegerValue]


class NewBonus(TypedDict):
    new_bonus_type: str
    new_bonus_value: int | str
    new_bonus_mult: float

class States(TypedDict):
    hp_dice_idx: int
    ability_bonus_type_idx: int
    static_bonus_type_idx: int
    counter_display_type_idx: int
    text_table_type_idx: int
    
    hp_add: str
    
    new_item_name: str
    new_training: TextData
    new_tag: str
    new_bonuses: dict[str, NewBonus]
    new_window_name: str
    new_condition_name: str
    new_condition_description: str

    target_name: str
    target_ref: str

    counter_edit: Counter

    new_text_item_popups_opened: dict[str, bool]

    # A temporary storage for the new feature name
    # Used when opening a feature popup to be able to change 
    # the name of the feature without the popup closing,
    # otherwise the popup name changes with the feature name.
    feat_name: str
    

class MainWindowProtocol():
    regular_font: imgui.ImFont
    bold_font: imgui.ImFont
    theme: str
    states: States

    open_file_dialog: Optional[pfd.open_file]
    file_path: list[str]

    open_image_dialog: Optional[pfd.open_file]
    
    data: CharacterData
    is_character_loaded: bool

    data_refs: dict[str, CharacterClass | Ability | RollableStat | StaticStat | ArmorClass | Hp | Proficiency | Feature | Counter]
    bonus_list_refs: dict[str, list[Bonus]]

    def __call__(self, font_holder: FontHolder) -> None: ...


def main_window_decorator(func: Any) -> MainWindowProtocol:
    return func
