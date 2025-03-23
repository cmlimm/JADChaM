from typing import Any, Literal, Optional, Protocol, TypedDict

from imgui_bundle import imgui
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore


class IntOrStrBonusType(TypedDict):
    name: str
    value: int | str
    multiplier: float
    manual: bool


class IntBonusType(TypedDict):
    name: str
    value: int
    manual: bool


class StatType(TypedDict):
    total: int  # used for exchanging the total value of a stat between parts of the app, never used when loading a character
    custom_mod: int  # either a base value for a stat (proficiency) or a manually added bonus


class AbilityType(StatType):
    forced_total_base_scores: list[IntBonusType]  # overrides from items (e.g. Headband of Intellect)
    base_score: int  # what number a player assigned to this ability when creating a character (point buy, rolls, etc.)
    base_score_bonuses: list[IntBonusType]  # ability score increase feats and similar
    mod_bonuses: list[IntBonusType]  # something that straight up increases your modifier


type AbilityNameType = Literal["str", "dex", "con", "wis", "int", "cha"]


class AbilitiesDictType(TypedDict):
    str: AbilityType
    dex: AbilityType
    con: AbilityType
    wis: AbilityType
    int: AbilityType
    cha: AbilityType


class ProficiencyType(StatType):
    bonuses: list[IntBonusType]


class IntStatType(StatType):
    bonuses: list[IntOrStrBonusType]


class ArmorType(IntBonusType):
    max_dex_bonus: None | int


class AcType(IntStatType):
    base: int
    armor: ArmorType


type SpeedNameType = Literal["walking", "climbing", "swimming", "flying"]


class StaticStatType(IntStatType):
    base: int
    forced_bases: list[IntOrStrBonusType]


class SpeedDictType(TypedDict):
    walking: StaticStatType
    climbing: StaticStatType
    swimming: StaticStatType
    flying: StaticStatType


class RollableStatType(IntStatType):
    name: str
    custom_advantage: bool
    custom_disadvantage: bool
    custom_proficiency: bool


class SavesDictType(TypedDict):
    str: RollableStatType
    dex: RollableStatType
    con: RollableStatType
    wis: RollableStatType
    int: RollableStatType
    cha: RollableStatType


class PassivesDictType(TypedDict):
    perception: StaticStatType
    investigation: StaticStatType
    insight: StaticStatType


class ToolProficienciesListItemDictType(TypedDict):
    name: str
    source: str
    type: str
    manual: bool


class ToolProficiencySortingInEditModeDictType(TypedDict):
    sort_by: str
    sort_descending: bool


class ToolProficiencyDictType(TypedDict):
    sorting_in_edit_mode: ToolProficiencySortingInEditModeDictType
    proficiencies: list[ToolProficienciesListItemDictType]


class CharacterDataType(TypedDict):
    name: str
    abilities: AbilitiesDictType
    saves: SavesDictType
    passives: PassivesDictType
    proficiency: ProficiencyType
    initiative: RollableStatType
    skills: list[RollableStatType]
    ac: AcType
    speed: dict[str, StaticStatType]
    tool_proficiencies: ToolProficiencyDictType


class FontHolder:
    regular_font: imgui.ImFont
    bold_font: imgui.ImFont


class NewBonusDataType(TypedDict):
    new_bonus_name: str
    current_new_bonus_type_idx: int
    current_new_bonus_ability_idx: int
    new_bonus_numerical: int
    current_new_bonus_speed_idx: int
    current_new_bonus_mult_idx: int


class MainWindowProtocol(Protocol):
    theme: str
    regular_font: imgui.ImFont
    bold_font: imgui.ImFont
    data: CharacterDataType
    open_file_dialog: Optional[pfd.open_file]
    file_paths: list[str]
    skill_name: str
    skill_ability: int
    new_bonuses: dict[str, NewBonusDataType]
    tool_proficiency_name: str
    tool_proficiency_type: str
    tool_proficiency_source: str
    tool_proficiency_name_missing: bool

    def __call__(self, font_holder: FontHolder) -> None: ...


def main_window_decorator(func: Any) -> MainWindowProtocol:
    return func
