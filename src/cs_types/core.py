from typing import Any, Literal, Optional, TypedDict

from imgui_bundle import imgui
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

from cs_types.components import Bonus, BonusTo, Condition, Counter, TextData
from cs_types.spell import Spell
from cs_types.stats import RollableStat, StaticStat  # type: ignore

StatTypes = Literal["static", "rollable"]


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


class Exhaustion(TypedDict):
    total: int
    description: str


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
    exhaustion: Exhaustion

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

    spells: list[Spell]

    # attacks: list[Attack]
    # counters: list[IntegerValue]


class NewBonus(TypedDict):
    new_bonus_type: str
    new_bonus_value: int | str
    new_bonus_mult: float


class SearchData(TypedDict):
    search_text: str
    search_results: list[Any]


class Roll(TypedDict):
    roll_str: str
    roll_type: str
    roll_result: int


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

    cyclic_bonus: bool
    cyclic_bonus_path: list[str]

    # A temporary storage for the new feature name
    # Used when opening a feature popup to be able to change 
    # the name of the feature without the popup closing,
    # otherwise the popup name changes with the feature name.
    feat_name: str

    search_data: dict[str, SearchData]
    
    roll_list: list[Roll]
    roll_popup_opened: dict[str, bool]
    roll_color_frames_count: int
    roll_popup_color: list[int]


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
    are_windows_loaded: bool

    loaded_spells: list[Spell]

    data_refs: dict[str, CharacterClass | Ability | RollableStat | StaticStat | ArmorClass | Hp | Proficiency | Feature | Counter]
    bonus_list_refs: dict[str, list[Bonus]]

    def __call__(self, font_holder: FontHolder) -> None: ...


def main_window_decorator(func: Any) -> MainWindowProtocol:
    return func
