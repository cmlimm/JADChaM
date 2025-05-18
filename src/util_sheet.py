import re
from math import trunc
from typing import Any, Optional

from imgui_bundle import ImVec2, icons_fontawesome_6, imgui, imgui_md  # type: ignore

from cs_types import Bonus, BonusTo, Counter, Feature, MainWindowProtocol, NewBonus
from settings import STRIPED_NO_BORDERS_TABLE_FLAGS  # type: ignore
from settings import STRIPED_TABLE_FLAGS  # type: ignore
from settings import (  # type: ignore
    ADVANTAGE_ACTIVE_COLOR,
    DISADVANTAGE_ACTIVE_COLOR,
    DISADVANTAGE_COLOR,
    DISADVANTAGE_HOVER_COLOR,
    LIST_TYPE_TO_BONUS,
    MEDIUM_STRING_INPUT_WIDTH,
    OVERRIDE_COLOR,
    RE_VALUE,
    SHORT_STRING_INPUT_WIDTH,
    THREE_DIGIT_BUTTONS_INPUT_WIDTH,
    TWO_DIGIT_BUTTONS_INPUT_WIDTH,
)
from util_cs_types import (
    isAbilityList,
    isClassList,
    isFeature,
    isFeatureList,
    isRepresentFloat,
    isRepresentInt,
    isRollableStatList,
    isStaticStatList,
)
from util_imgui import draw_text_cell, end_table_nested


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


# Returns (total_bonus, (-1 if advantage, 0 if straight, 1 if advantage))
def sum_bonuses(bonus_list: list[Bonus], static: MainWindowProtocol, max_dex_bonus: int = 100) -> tuple[int, int]:
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


def draw_entities_menu(menu_name: str, menu_id: str, types: list[str], 
                       new_bonus: NewBonus, static: MainWindowProtocol):
    imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
    imgui.push_item_flag(imgui.ItemFlags_.auto_close_popups, False) # type: ignore

    if menu_name == "":
        menu_name = "Choose Bonus"

    if imgui.begin_menu(f"{menu_name}##{menu_id}"):
        for bonus_type in types:
            # Numerical
            if bonus_type == "Numerical" and imgui.menu_item_simple(f"Numerical##{menu_id}"):
                new_bonus["new_bonus_type"] = "Numerical"
                new_bonus["new_bonus_value"] = 0
            # Class Level
            elif bonus_type == "Level" and imgui.begin_menu(f"Level##{menu_id}"):
                if imgui.menu_item_simple("Total"):
                    new_bonus["new_bonus_type"] = f"Level, Total"
                    new_bonus["new_bonus_value"] = f"level:total"
                for class_item in static.data["level"]["classes"]:
                    class_name = class_item["name"]
                    if not class_name.startswith("no_display") and imgui.menu_item_simple(f"{class_name}##{menu_id}"):
                        new_bonus["new_bonus_type"] = f"Level, {class_name}"
                        new_bonus["new_bonus_value"] = f"level:{class_name}"
                imgui.end_menu()
            # Advantage and Disadvantage
            elif bonus_type == "Advantage" and imgui.menu_item_simple(f"Advantage##{menu_id}"):
                new_bonus["new_bonus_type"] = "Advantage"
                new_bonus["new_bonus_value"] = "advantage"
            elif bonus_type == "Disadvantage" and imgui.menu_item_simple(f"Disadvantage##{menu_id}"):
                new_bonus["new_bonus_type"] = "Disadvantage"
                new_bonus["new_bonus_value"] = "disadvantage"
            # Ability
            elif bonus_type == "Ability" and imgui.begin_menu(f"Ability##{menu_id}"):
                for ability in static.data["abilities"]:
                    ability_name = ability["name"]
                    if not ability_name.startswith("no_display") and imgui.begin_menu(f"{ability_name}##{menu_id}"):
                        if imgui.menu_item_simple(f"Modifier##{menu_id}"):
                            new_bonus["new_bonus_type"] = f"Ability Modifier, {ability_name}"
                            new_bonus["new_bonus_value"] = f"ability:{ability_name}"
                        if imgui.menu_item_simple(f"Score##{menu_id}"):
                            new_bonus["new_bonus_type"] = f"Ability Score, {ability_name}"
                            new_bonus["new_bonus_value"] = f"ability:{ability_name}:score"
                        imgui.end_menu()
                imgui.end_menu()
            # Saving Throw
            elif bonus_type == "Saving Throw" and imgui.begin_menu(f"Save##{menu_id}"):
                for save in static.data["saves"]:
                    save_name = save["name"]
                    if not save_name.startswith("no_display") and imgui.menu_item_simple(save_name):
                        new_bonus["new_bonus_type"] = f"Saving Throw, {save_name}"
                        new_bonus["new_bonus_value"] = f"save:{save_name}"
                imgui.end_menu()
            # Skill
            elif bonus_type == "Skill" and imgui.begin_menu(f"Skill##{menu_id}"):
                for skill in static.data["skills"]:
                    skill_name = skill["name"]
                    if not skill_name.startswith("no_display") and imgui.menu_item_simple(skill_name):
                        new_bonus["new_bonus_type"] = f"Skill, {skill_name}"
                        new_bonus["new_bonus_value"] = f"skill:{skill_name}"
                imgui.end_menu()
            # Proficiency
            elif bonus_type == "Proficiency" and imgui.menu_item_simple(f"Proficiency##{menu_id}"):
                new_bonus["new_bonus_type"] = f"Proficiency"
                new_bonus["new_bonus_value"] = f"proficiency"
            # Speed
            elif bonus_type == "Speed" and imgui.begin_menu(f"Speed##{menu_id}"):
                for speed in static.data["speed"]:
                    speed_name = speed["name"]
                    if not speed_name.startswith("no_display") and imgui.menu_item_simple(speed_name):
                        new_bonus["new_bonus_type"] = f"Speed, {speed_name}"
                        new_bonus["new_bonus_value"] = f"speed:{speed_name}"
                imgui.end_menu()
            # Passive Skill
            elif bonus_type == "Passive Skill" and imgui.begin_menu(f"Passive Skill##{menu_id}"):
                for passive in static.data["passive_skill"]:
                    passive_name = passive["name"]
                    if not passive_name.startswith("no_display") and imgui.menu_item_simple(passive_name):
                        new_bonus["new_bonus_type"] = f"Passive Skill, {passive_name}"
                        new_bonus["new_bonus_value"] = f"passive:{passive_name}"
                imgui.end_menu()
            # Sense
            elif bonus_type == "Sense" and imgui.begin_menu(f"Sense##{menu_id}"):
                for sense in static.data["sense"]:
                    sense_name = sense["name"]
                    if not sense_name.startswith("no_display") and imgui.menu_item_simple(sense_name):
                        new_bonus["new_bonus_type"] = f"Sense, {sense_name}"
                        new_bonus["new_bonus_value"] = f"sense:{sense_name}"
                imgui.end_menu()
            # Initiative
            elif bonus_type == "Initiative" and imgui.menu_item_simple(f"Initiative##{menu_id}"):
                new_bonus["new_bonus_type"] = f"Initiative"
                new_bonus["new_bonus_value"] = f"initiative"
            # Armor Class
            elif bonus_type == "Armor Class" and imgui.menu_item_simple(f"Armor Class##{menu_id}"):
                new_bonus["new_bonus_type"] = f"Armor Class"
                new_bonus["new_bonus_value"] = f"armor_class"
            # HP
            elif bonus_type == "HP" and imgui.begin_menu(f"HP##{menu_id}"):
                if imgui.menu_item_simple(f"Max##{menu_id}"):
                    new_bonus["new_bonus_type"] = f"HP Max"
                    new_bonus["new_bonus_value"] = f"hp:max"
                if imgui.menu_item_simple(f"Current##{menu_id}"):
                    new_bonus["new_bonus_type"] = f"HP Current"
                    new_bonus["new_bonus_value"] = f"hp:current"
                imgui.end_menu() 
            # Counter
            elif bonus_type == "Counter" and imgui.begin_menu(f"Counter##{menu_id}"):
                for feature in static.data["features"]:
                    if feature["counters"] != [] and imgui.begin_menu(f"{feature["name"]}##counters_{menu_id}"):
                        for counter in feature["counters"]:
                            if imgui.begin_menu(f"{counter["name"]}##counter_menu_{menu_id}"):
                                if imgui.menu_item_simple(f"Max##{menu_id}"):
                                    new_bonus["new_bonus_type"] = f"{counter["name"]} ({feature["name"]}) Max"
                                    new_bonus["new_bonus_value"] = f"counter:{feature["name"]}:{counter["name"]}:max"
                                if imgui.menu_item_simple(f"Current##{menu_id}"):
                                    new_bonus["new_bonus_type"] = f"{counter["name"]} ({feature["name"]}) Current"
                                    new_bonus["new_bonus_value"] = f"counter:{feature["name"]}:{counter["name"]}:current"
                                imgui.end_menu() 
                        imgui.end_menu() 
                imgui.end_menu() 
        imgui.end_menu()
    imgui.pop_item_flag()


def draw_add_bonus(bonus_id: str, bonus_list: list[Bonus], 
                   list_type: str, static: MainWindowProtocol,
                   numerical_step: int = 1,
                   is_feature_bonus: bool = False, add_manual_text : bool = True) -> None:
    if not bonus_id in static.states["new_bonuses"]:
        static.states["new_bonuses"][bonus_id] = {
            "new_bonus_type": "",
            "new_bonus_value": "",
            "new_bonus_mult": 1.0
        }
    new_bonus = static.states["new_bonuses"][bonus_id]

    bonus_types = LIST_TYPE_TO_BONUS[list_type]

    # Choose bonus type
    draw_entities_menu(static.states["new_bonuses"][bonus_id]["new_bonus_type"], bonus_id, bonus_types, new_bonus, static)

    # If `Numerical` draw int button, else draw multiplier button
    if new_bonus["new_bonus_type"] == "Numerical":
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        _, new_bonus["new_bonus_value"] = imgui.input_int(
            f"##new_bonus_value_{bonus_id}",
            new_bonus["new_bonus_value"], # type: ignore
            numerical_step)
    elif new_bonus["new_bonus_type"] == "Advantage" or new_bonus["new_bonus_type"] == "Disadvantage":
        pass
    elif new_bonus["new_bonus_type"] != "":
        imgui.text("Multiplier"); imgui.same_line()
        imgui.push_item_width(THREE_DIGIT_BUTTONS_INPUT_WIDTH)
        _, new_bonus["new_bonus_mult"] = imgui.input_float(
            f"##new_bonus_mult_{bonus_id}",
            new_bonus["new_bonus_mult"],
            0.5, format="%.1f")
    
    if not is_feature_bonus:
        if new_bonus["new_bonus_type"] != "" and not (new_bonus["new_bonus_type"] == "Advantage" or new_bonus["new_bonus_type"] == "Disadvantage"):
            imgui.same_line()

        if new_bonus["new_bonus_type"] != "" and imgui.button(f"Add Bonus##{bonus_id}_new_bonus"):
            bonus_list.append({
                "name": f"{new_bonus["new_bonus_type"]}{" (Manual)" if add_manual_text else ""}",
                "value": new_bonus["new_bonus_value"],
                "multiplier": new_bonus["new_bonus_mult"],
                "manual": True
            })

            static.states["new_bonuses"][bonus_id] = {
                "new_bonus_type": "",
                "new_bonus_value": "",
                "new_bonus_mult": 1.0
            }


def draw_bonuses(list_id: str, bonus_list: list[Bonus], static: MainWindowProtocol) -> None:
    if bonus_list != [] and imgui.begin_table(f"bonuses##{list_id}", 4, flags=STRIPED_NO_BORDERS_TABLE_FLAGS): # type: ignore
        for idx, bonus in enumerate(bonus_list):
            name, value, mult, manual = bonus["name"], bonus["value"], bonus["multiplier"], bonus["manual"]
            
            draw_text_cell("    ")
            imgui.table_next_column(); imgui.align_text_to_frame_padding()
            imgui.text(name)

            if value == "advantage":
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text_colored(ADVANTAGE_ACTIVE_COLOR, "Advantage")
            elif value == "disadvantage":
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text_colored(DISADVANTAGE_ACTIVE_COLOR, "Disadvantage")
            else:
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(f"{get_bonus_value(value, static)}{" x" + str(mult) if mult != 1.0 else ""}")

            if manual:
                imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                imgui.table_next_column()
                if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                    del bonus_list[idx]
                imgui.pop_style_color(3)
        end_table_nested()


def draw_overrides(list_id: str, override_list: list[Bonus], override_idx: int, is_override: bool, static: MainWindowProtocol) -> None:
    if override_list != [] and imgui.begin_table(f"overrides##{list_id}", 4, flags=STRIPED_NO_BORDERS_TABLE_FLAGS): # type: ignore
        for idx, override in enumerate(override_list):
            name, value, mult, manual = override["name"], override["value"], override["multiplier"], override["manual"]
            
            draw_text_cell("    ")
            imgui.table_next_column(); imgui.align_text_to_frame_padding()
            if is_override and idx == override_idx:
                imgui.text_colored(OVERRIDE_COLOR, name)
            else:
                imgui.text_disabled(name)

            imgui.table_next_column(); imgui.align_text_to_frame_padding()
            value_text = f"{get_bonus_value(value, static)}{" x" + str(mult) if mult != 1.0 else ""}"
            if is_override and idx == override_idx:
                imgui.text_colored(OVERRIDE_COLOR, value_text)
            else:
                imgui.text_disabled(value_text)

            if manual:
                imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                imgui.table_next_column()
                if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                    del override_list[idx]
                imgui.pop_style_color(3)
        end_table_nested()


def delete_feature_bonus(feature: Feature, bonus: BonusTo, static: MainWindowProtocol):
    delete_target = static.bonus_list_refs[bonus["target"]]
    delete_idx = delete_target.index(bonus["bonus"])
    del delete_target[delete_idx]

    idx = feature["bonuses"].index(bonus)
    del feature["bonuses"][idx]


def delete_item_from_list(item: Any, item_idx: int, editable_list: list[Any], 
                          cache_prefix: str, static: MainWindowProtocol):
    if item["manual"]:
        if isFeature(item):
            for bonus in item["bonuses"]:
                delete_feature_bonus(item, bonus, static)
            for counter in item["counters"]:
                # if counters in the feature are added somewhere as a bonus, they will be deleted
                # from bonuses automatically when the program cannot find a reference, 
                # see `get_bonus_value` and `sum_bonuses`
                del static.data_refs[f"counter:{item["name"]}:{counter["name"]}"]
        del editable_list[item_idx]
        del static.data_refs[f"{cache_prefix}:{item["name"]}"]


def add_item_to_list(item_name: str, editable_list: list[Any], cache_prefix: str, 
                     static: MainWindowProtocol, tag: str = ""):
    if item_name != "":
        if isClassList(editable_list):
            editable_list.append({
                "name": item_name,
                "subclass": "",
                "total": 0,
                "level": 0,
                "dice": 6,
                "manual": True
            })
        if isAbilityList(editable_list):
            editable_list.append({
                "name": item_name,
                "total": 0,
                "total_base_score": 0,
                "base_score_overrides": [],
                "base_score_bonuses": [],
                "base_score": 10,
                "modifier_bonuses": [],
                "manual": True
            })
            static.bonus_list_refs[f"{cache_prefix}:{item_name}:base_score_bonuses"] = editable_list[-1]["base_score_bonuses"]
            static.bonus_list_refs[f"{cache_prefix}:{item_name}:base_score_overrides"] = editable_list[-1]["base_score_overrides"]
            static.bonus_list_refs[f"{cache_prefix}:{item_name}:modifier_bonuses"] = editable_list[-1]["modifier_bonuses"]
        if isRollableStatList(editable_list):
            editable_list.append({
                "name": item_name,
                "total": 0,
                "bonuses": [
                    {
                        "name": "Manual",
                        "value": 0,
                        "multiplier": 1.0,
                        "manual": False
                    }
                ],
                "manual_advantage": False,
                "manual_disadvantage": False,
                "manual": True
            })
            static.bonus_list_refs[f"{cache_prefix}:{item_name}:bonuses"] = editable_list[-1]["bonuses"]
        if isStaticStatList(editable_list):
            editable_list.append({
                "name": item_name,
                "total": 0,
                "base": 0,
                "base_overrides": [],
                "bonuses": [],
                "manual": True
            })
            static.bonus_list_refs[f"{cache_prefix}:{item_name}:bonuses"] = editable_list[-1]["bonuses"]
            static.bonus_list_refs[f"{cache_prefix}:{item_name}:base_overrides"] = editable_list[-1]["base_overrides"]
        if isFeatureList(editable_list):
            tags = []
            if tag != "All Features":
                tags = [tag]
            editable_list.append({
                "name": item_name,
                "description": "",
                "tags": tags,
                "bonuses": [],
                "counters": [],
                "manual": True
            })
        static.data_refs[f"{cache_prefix}:{item_name}"] = editable_list[-1]


def draw_list_item_context_menu(menu_id: str, item: Any, item_idx: int, editable_list: list[Any], 
                                cache_prefix: str, static: MainWindowProtocol, draw_delete: bool = True):
    if imgui.begin_popup_context_item(menu_id):
        if draw_delete and imgui.button(f"Delete {item["name"]}"):
            delete_item_from_list(item, item_idx, editable_list, cache_prefix, static)
        if imgui.button(f"New Item"):
            imgui.open_popup("New item name")
        if imgui.begin_popup("New item name"):
            imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
            _, static.states["new_item_name"] = imgui.input_text_with_hint(
                "##new_item", 
                "Name", 
                static.states["new_item_name"],
                128); imgui.same_line()
            imgui.pop_item_width()
            if imgui.button("Add##new_list_item"):
                add_item_to_list(static.states["new_item_name"], editable_list, cache_prefix, static)
                static.states["new_item_name"] = ""
            imgui.end_popup()
        imgui.end_popup()


def draw_counter(counter: Counter, static: MainWindowProtocol) -> None:
    counter["max"], _ = sum_bonuses(counter["bonuses"], static)
    if counter["max"] < counter["min"]: counter["max"] = counter["min"]
    
    imgui.align_text_to_frame_padding()
    if counter["display_type"] == "+- Buttons":
        imgui.text(f"{counter["name"]} ({counter["max"]})"); imgui.same_line()
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        _, counter["current"] = imgui.input_int(f"##{counter["name"]}_counter", counter["current"])
        if counter["current"] > counter["max"]:
            counter["current"] = counter["max"]
        if counter["current"] < 0:
            counter["current"] = 0
    elif counter["display_type"] == "Checkboxes":
        imgui.text(f"{counter["name"]}"); imgui.same_line()
        counter_states: list[bool] = []
        true_counter = counter["current"]
        for _ in range(counter["max"]):
            if true_counter != 0:
                counter_states.append(True)
                true_counter -= 1
            else:
                counter_states.append(False)
        for idx, _ in enumerate(counter_states):
            _, counter_states[idx] = imgui.checkbox(f"##{counter["name"]}_{idx}_checkbox", counter_states[idx])
            imgui.same_line()
        imgui.dummy(ImVec2(0, 0))
        counter["current"] = sum([int(state) for state in counter_states])

def draw_edit_counter(counter_list: list[Counter], parent_name: str, static: MainWindowProtocol, 
                      counter: Optional[Counter] = None) -> None:
    if not counter:
        popup_name = "Edit Counter##popup"
    else:
        popup_name = f"Edit Counter##{counter["name"]}_popup"
    if imgui.begin_popup(popup_name):
        draw_add_button = False
        if not counter:
            counter = static.states["counter_edit"]
            draw_add_button = True

        counter["parent"] = parent_name
        
        imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
        _, counter["name"] = imgui.input_text_with_hint("##new_counter_name", "Name", 
                                                        counter["name"], 128)
        imgui.pop_item_width()
        
        imgui.align_text_to_frame_padding()
        imgui.text("Display Type"); imgui.same_line()
        items = ["+- Buttons", "Checkboxes"]
        static.states["counter_display_type_idx"] = 0 if counter["display_type"] == "+- Buttons" else 1
        imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
        _, static.states["counter_display_type_idx"] = imgui.combo(f"##counter_select_display_type", 
                                                                    static.states["counter_display_type_idx"], 
                                                                    items, len(items))
        counter["display_type"] = items[static.states["counter_display_type_idx"]] # type: ignore
        imgui.pop_item_width()

        imgui.align_text_to_frame_padding()
        imgui.text("Minimum"); imgui.same_line()
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        _, counter["min"] = imgui.input_int("##new_counter_minimum", counter["min"], 1)
        imgui.pop_item_width()

        if counter["bonuses"] != []:
            imgui.separator_text(f"Bonuses")
            draw_bonuses("counter_bonus_list", counter["bonuses"], static)

        imgui.separator_text(f"New bonus")
        draw_add_bonus(f"counter_new_bonus", counter["bonuses"], "hp", static, add_manual_text=False)
        
        if draw_add_button and imgui.button("Add Counter") and counter["name"] != "":
            counter["max"], _ = sum_bonuses(counter["bonuses"], static)
            counter["current"] = counter["max"]
            counter_list.append(counter)
            static.data_refs[f"counter:{parent_name}:{counter["name"]}"] = counter_list[-1]
            static.states["counter_edit"] = {
                "name": "",
                "parent": "",
                "current": 0,
                "max": 0,
                "display_type": "+- Buttons",
                "bonuses": [],
                "min": 0,
                "manual": True
            }
        
        imgui.end_popup()