from typing import Any, Optional, Protocol, TextIO, TypedDict

from imgui_bundle import portable_file_dialogs as pfd  # type: ignore


class IntOrAbilityBonusType(TypedDict):
    name: str
    value: int | str


class IntBonusType(TypedDict):
    name: str
    value: int


class StatType(TypedDict):
    total: int
    custom_mod: int


class AbilityType(StatType):
    forced_total: list[IntBonusType]
    base_score: int
    base_score_bonuses: list[IntBonusType]
    mod_bonuses: list[IntBonusType]


class ProficiencyType(StatType):
    bonuses: list[IntBonusType]


class IntStatType(StatType):
    bonuses: list[IntOrAbilityBonusType]


class RollableStatType(IntStatType):
    custom_advantage: bool
    custom_disadvantage: bool


class CharacterDataType(TypedDict):
    name: str
    abilities: dict[str, AbilityType]
    proficiency: ProficiencyType
    skills: dict[str, RollableStatType]
    ac: IntStatType
    speed: IntStatType


class MainWindowProtocol(Protocol):
    theme: str
    data: CharacterDataType
    open_file_dialog: Optional[pfd.open_file]
    character_file: TextIO

    def __call__(self) -> None: ...


def main_window_decorator(func: Any) -> MainWindowProtocol:
    return func
