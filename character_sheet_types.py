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
    manual_mod: int


class AbilityType(StatType):
    base_score: int
    base_score_bonuses: list[IntBonusType]
    mod_bonuses: list[IntBonusType]


class ProficiencyType(StatType):
    bonuses: list[IntBonusType]


class MiscStatType(StatType):
    bonuses: list[IntOrAbilityBonusType]

class CharacterDataType(TypedDict):
    name: str
    abilities: dict[str, AbilityType]
    proficiency: ProficiencyType
    initiative: MiscStatType
    ac: MiscStatType
    speed: MiscStatType


class MainWindowProtocol(Protocol):
    theme: str
    data: CharacterDataType
    open_file_dialog: Optional[pfd.open_file]
    character_file: TextIO

    def __call__(self) -> None: ...


def main_window_decorator(func: Any) -> MainWindowProtocol:
    return func