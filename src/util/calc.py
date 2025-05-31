import re
from math import trunc

from cs_types import Bonus, MainWindowProtocol
from settings import RE_VALUE
from util.cs_types import isRepresentFloat, isRepresentInt


def get_bonus_value(value: str | int, static: MainWindowProtocol, max_dex_bonus: int = 100, return_delete: bool = True) -> int | float | str:
    if isRepresentInt(value):
        return int(value)
    elif isinstance(value, str):
        if value == "level:total":
            return static.data["level"]["total"]
        elif value == "proficiency":
            return static.data["proficiency"]["total"]
        elif value == "initiative":
            return static.data["initiative"]["total"]
        elif value == "armor_class":
            return static.data["armor_class"]["total"]
        elif value == "hp:current":
            return static.data["hp"]["current"]
        elif value == "hp:max":
            return static.data["hp"]["max_total"]
        elif value.startswith("ability") and value.endswith(":score"):
            return static.data_refs.get(value[:-6], {"total_base_score": 0})["total_base_score"] # type: ignore
        elif value == "advantage":
            return "advantage"
        elif value == "disadvantage":
            return "disadvantage"
        elif value == "ability:DEX":
            return min(static.data_refs.get("ability:DEX", {"total": 0})["total"], max_dex_bonus) # type: ignore
        elif value.startswith("counter") and value.endswith("max"):
            try:
                return static.data_refs[value[:-4]]["max"] # type: ignore
            except KeyError:
                return "delete"
        elif value.startswith("counter") and value.endswith("current"):
            try:
                return static.data_refs[value[:-8]]["current"] # type: ignore
            except KeyError:
                return "delete"
        else:
            # TODO: in release verison wrap everything with try-except
            return static.data_refs.get(value, {"total": 0})["total"] # type: ignore

    return 0


def sum_bonuses(bonus_list: list[Bonus], static: MainWindowProtocol, max_dex_bonus: int = 100) -> tuple[int, int]:
    """
    Returns (total_bonus, (-1 if advantage, 0 if straight, 1 if advantage))
    """

    total_bonus = 0
    advantage = False
    disadvantage = False

    for idx, bonus in enumerate(bonus_list):
        value = get_bonus_value(bonus["value"], static, max_dex_bonus)

        if value == "delete":
            del bonus_list[idx]
            continue

        if value == "advantage":
            advantage = True
        if value == "disadvantage":
            disadvantage = True
        elif isRepresentInt(value):
            mult = bonus["multiplier"]
            total_bonus += trunc(value * mult)

    if not advantage ^ disadvantage:
        roll = 0
    elif advantage:
        roll = 1
    else:
        roll = -1

    return (total_bonus, roll)


def find_max_override(override_list: list[Bonus], static: MainWindowProtocol) -> tuple[int, int]:
    max_idx = -1
    max_override = 0
    for idx, override in enumerate(override_list):
        override_value = trunc(get_bonus_value(override["value"], static) * override["multiplier"]) # type: ignore
        if override_value > max_override or max_idx == -1:
            max_idx = idx
            max_override = override_value

    return (max_idx, max_override)


def replace_value(match: re.Match[str], static: MainWindowProtocol) -> str:
    text = match.group(0).strip("{}")
    text_split = text.split(", mult=")
    value = text_split[0]
    multiplier = 1.0
    if len(text_split) == 2:
        multiplier_text = text_split[1]
        if isRepresentFloat(multiplier_text) or isRepresentInt(multiplier_text) :
            multiplier = float(multiplier_text)

    numerical_value = get_bonus_value(value, static)
    if numerical_value == "delete": numerical_value = "Error"

    if isRepresentInt(numerical_value):
        return str(trunc(int(numerical_value)*multiplier))
    else:
        return ""


def parse_text(text: str, static: MainWindowProtocol) -> str:
    return re.sub(RE_VALUE, lambda x: replace_value(x, static), text) # type: ignore