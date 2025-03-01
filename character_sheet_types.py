from typing import Any, Optional, Protocol, TextIO, TypedDict

from imgui_bundle import portable_file_dialogs as pfd  # type: ignore


class IntOrStrBonusType(TypedDict):
    name: str
    value: int | str


class IntBonusType(TypedDict):
    name: str
    value: int


class StatType(TypedDict):
    total: int  # used for exchanging the total value of a stat between parts of the app, never used when loading a character
    custom_mod: int  # either a base value for a stat (proficiency) or a manually added bonus


class AbilityType(StatType):
    forced_total_base_scores: list[IntBonusType]  # overrides from items (e.g. Headband of Intellect)
    base_score: int  # what number a player assigned to this ability when creating a character (point buy, rolls, etc.)
    base_score_bonuses: list[IntBonusType]  # ability score increase feats and similar
    mod_bonuses: list[IntBonusType]  # something that straight up increases your modifier


class ProficiencyType(StatType):
    bonuses: list[IntBonusType]


class IntStatType(StatType):
    bonuses: list[IntOrStrBonusType]


class ArmorType(IntBonusType):
    max_dex_bonus: None | int


class AcType(IntStatType):
    base: int
    armor: ArmorType


class SpeedType(IntStatType):
    base: int
    forced_bases: list[IntOrStrBonusType]


class RollableStatType(IntStatType):
    custom_advantage: bool
    custom_disadvantage: bool


class CharacterDataType(TypedDict):
    name: str
    abilities: dict[str, AbilityType]
    proficiency: ProficiencyType
    skills: dict[str, RollableStatType]
    ac: AcType
    speed: dict[str, SpeedType]


class MainWindowProtocol(Protocol):
    theme: str
    data: CharacterDataType
    open_file_dialog: Optional[pfd.open_file]
    character_file: TextIO

    def __call__(self) -> None: ...


def main_window_decorator(func: Any) -> MainWindowProtocol:
    return func
