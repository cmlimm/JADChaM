import random
import re
from math import trunc
from uuid import UUID

from fuzzysearch import find_near_matches  # type: ignore

from cs_types.components import Bonus
from cs_types.core import Description, MainWindowProtocol
from cs_types.guards import isRepresentFloat, isRepresentInt
from cs_types.stats import StaticStat
from settings import RE_VALUE


def find_id_by_name(name: str, static: MainWindowProtocol) -> str:
    try:
        UUID(name, version=4)
        return name
    except ValueError:
        ids = [element["id"] for key, element in static.data_refs.items() if element["name"] == name]
        
        id = ""
        if ids != []:
            id = ids[0]
        
        return id


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
        elif value == f"ability:{find_id_by_name("DEX", static)}":
            return min(static.data_refs.get(f"ability:{find_id_by_name("DEX", static)}", {"total": 0})["total"], max_dex_bonus) # type: ignore
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


def parse_description(description: Description, static: MainWindowProtocol) -> str:
    text = description["text"]
    for name, reference in description["references"].items():
        calc_static_stat(reference, static)
        text = re.sub(f"{{{name}}}", lambda x: str(reference["total"]), text)

    return text


# Abosolutely disgusting code, this can break anytime
def check_for_cycles(static: MainWindowProtocol, target_ref: str, bonus_ref: str | int, visited: list[str] = []) -> tuple[bool, list[str]]:
    if target_ref.startswith("initiative") or target_ref.startswith("armor_class") or target_ref.startswith("hp"):
        target_ref = target_ref.split(":")[0]

    if isRepresentInt(bonus_ref):
        return (False, visited)
    
    if target_ref == bonus_ref:
        return (True, [])

    if visited == []:
        visited = [bonus_ref] # type: ignore

    if bonus_ref != "proficiency" and not bonus_ref.startswith("ability:") and not bonus_ref.startswith("level:") and not bonus_ref.startswith("feature:"): # type: ignore
        # Even though cyclic references with current values of counters
        # do not lead to obvious cycles, we still need to check for them
        # because they lead to increasing the max value of the counter
        # when using the counter
        # EXAMPLE: initiative + misty step, perceprion + initiative, misty step + perception
        if bonus_ref.endswith(":current"): bonus_ref = bonus_ref[:-8] # type: ignore
        if bonus_ref.endswith(":max"): bonus_ref = bonus_ref[:-4] # type: ignore
        
        for bonus in static.data_refs[bonus_ref]["bonuses"]: # type: ignore
            value = bonus["value"] # type: ignore

            if isRepresentInt(value):
                continue
            
            if value.startswith("initiative") or value.startswith("armor_class") or value.startswith("hp"): # type: ignore
                value = value.split(":")[0] # type: ignore
            
            if value.endswith(":current"): value = value[:-8] # type: ignore
            if value.endswith(":max"): value = value[:-4] # type: ignore
            
            if value == target_ref: # type: ignore
                return (True, visited)
            
            if check_for_cycles(static, target_ref, value, visited)[0]: # type: ignore
                visited.append(str(value)) # type: ignore

                return (True, visited)
                    
    return (False, visited)


def fuzzy_search(text: str, line: str) -> bool:
    matches = find_near_matches(text.lower(), line.lower(), max_l_dist=1) # type: ignore
    if matches != []:
        return True

    return False


def calculate_roll(roll_mod: str, adv_disadv: int) -> int:
    roll = roll_mod
    mod = "0"
    if "+" in roll_mod:
        roll, mod = roll_mod.split("+")
    dice_count, dice_size = roll.split("d")

    roll_result = sum([random.randint(1, int(dice_size)) for _ in range(int(dice_count))])

    roll_result_2 = sum([random.randint(1, int(dice_size)) for _ in range(int(dice_count))])
    if adv_disadv == 1:
        roll_result = max(roll_result, roll_result_2)
    if adv_disadv == -1:
        roll_result = min(roll_result, roll_result_2)

    return roll_result + int(mod)


def calc_static_stat(stat: StaticStat, static: MainWindowProtocol) -> tuple[bool, int]:
    override_idx, override_value = find_max_override(stat["base_overrides"], static)
    bonus_total, _ = sum_bonuses(stat["bonuses"], static)

    is_override = False
    if override_value > stat["base"]:
        stat["total"] = override_value + bonus_total
        is_override = True
    else:
        stat["total"] = stat["base"] + bonus_total

    return (is_override, override_idx)