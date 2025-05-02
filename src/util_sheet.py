import re
from math import trunc
from typing import Any

from imgui_bundle import ImVec2, icons_fontawesome_6, imgui  # type: ignore

from cs_types import Bonus, BonusTo, Feature, MainWindowProtocol, NewBonus
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
    isRepresentFloat,
    isRepresentInt,
    isRollableStatList,
    isStaticStatList,
)
from util_gui import draw_text_cell, end_table_nested


def get_bonus_value(value: str | int, static: MainWindowProtocol, max_dex_bonus: int = 100) -> int | float | str:
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
            return static.data["hp"]["max_total"]
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
        else:
            return static.data_refs.get(value, {"total": 0})["total"] # type: ignore
    
    return 0


# Returns (total_bonus, (-1 if advantage, 0 if straight, 1 if advantage))
def sum_bonuses(bonus_list: list[Bonus], static: MainWindowProtocol, max_dex_bonus: int = 100) -> tuple[int, int]:
    total_bonus = 0
    advantage = False
    disadvantage = False

    for bonus in bonus_list:
        value = get_bonus_value(bonus["value"], static, max_dex_bonus)

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
    if imgui.begin_menu(f"{menu_name}##{menu_id}"):
        for bonus_type in types:
            # Numerical
            if bonus_type == "Numerical" and imgui.menu_item_simple(f"Numerical##{menu_id}"):
                new_bonus["new_bonus_type"] = "Numerical Bonus"
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
            elif bonus_type == "HP" and imgui.menu_item_simple(f"HP##{menu_id}"):
                new_bonus["new_bonus_type"] = f"HP"
                new_bonus["new_bonus_value"] = f"hp"
                            
        imgui.end_menu()
    imgui.pop_item_flag()


def draw_target_menu(menu_name: str, menu_id: str, static: MainWindowProtocol):
    imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
    imgui.push_item_flag(imgui.ItemFlags_.auto_close_popups, False) # type: ignore
    if imgui.begin_menu(f"{menu_name}##{menu_id}"):
        # Ability
        if imgui.begin_menu(f"Ability##{menu_id}"):
            for ability in static.data["abilities"]:
                ability_name = ability["name"]
                if not ability_name.startswith("no_display") and imgui.begin_menu(f"{ability_name}##{menu_id}"):
                    if imgui.menu_item_simple(f"Modifier##{menu_id}"):
                        static.states["target_name"] = f"Ability Modifier, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability_name}:modifier_bonuses"
                    if imgui.menu_item_simple(f"Base Score##{menu_id}"):
                        static.states["target_name"] = f"Ability Base Score, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability_name}:base_score_bonuses"
                    if imgui.menu_item_simple(f"Base Score Override##{menu_id}"):
                        static.states["target_name"] = f"Ability Base Score Override, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability_name}:base_score_overrides"
                    imgui.end_menu()
            imgui.end_menu()
        # Saving Throw
        if imgui.begin_menu(f"Save##{menu_id}"):
            for save in static.data["saves"]:
                save_name = save["name"]
                if not save_name.startswith("no_display") and imgui.menu_item_simple(save_name):
                    static.states["target_name"] = f"Saving Throw, {save_name}"
                    static.states["target_ref"] = f"save:{save_name}:bonuses"
            imgui.end_menu()
        # Skill
        if imgui.begin_menu(f"Skill##{menu_id}"):
            for skill in static.data["skills"]:
                skill_name = skill["name"]
                if not skill_name.startswith("no_display") and imgui.menu_item_simple(skill_name):
                    static.states["target_name"] = f"Skill, {skill_name}"
                    static.states["target_ref"] = f"skill:{skill_name}:bonuses"
            imgui.end_menu()
        # Speed
        if imgui.begin_menu(f"Speed##{menu_id}"):
            for speed in static.data["speed"]:
                speed_name = speed["name"]
                if not speed_name.startswith("no_display") and imgui.begin_menu(f"{speed_name}##{menu_id}"):
                    if imgui.menu_item_simple("Bonus"):
                        static.states["target_name"] = f"Speed, {speed_name}"
                        static.states["target_ref"] = f"speed:{speed_name}:bonuses"
                    if imgui.menu_item_simple("Override"):
                        static.states["target_name"] = f"Speed Base Override, {speed_name}"
                        static.states["target_ref"] = f"speed:{speed_name}:base_overrides"
                    imgui.end_menu()
            imgui.end_menu()
        # Passive Skill
        if imgui.begin_menu(f"Passive Skill##{menu_id}"):
            for passive in static.data["passive_skill"]:
                passive_name = passive["name"]
                if not passive_name.startswith("no_display") and imgui.begin_menu(f"{passive_name}##{menu_id}"):
                    if imgui.menu_item_simple("Bonus"):
                        static.states["target_name"] = f"Passive Skill, {passive_name}"
                        static.states["target_ref"] = f"passive:{passive_name}:bonuses"
                    if imgui.menu_item_simple("Override"):
                        static.states["target_name"] = f"Passive Skill Base Override, {passive_name}"
                        static.states["target_ref"] = f"passive:{passive_name}:base_overrides"
                    imgui.end_menu()
            imgui.end_menu()
        # Sense
        if imgui.begin_menu(f"Sense##{menu_id}"):
            for sense in static.data["sense"]:
                sense_name = sense["name"]
                if not sense_name.startswith("no_display") and imgui.begin_menu(f"{sense_name}##{menu_id}"):
                    if imgui.menu_item_simple("Bonus"):
                        static.states["target_name"] = f"Sense, {sense_name}"
                        static.states["target_ref"] = f"sense:{sense_name}:bonuses"
                    if imgui.menu_item_simple("Override"):
                        static.states["target_name"] = f"Sense Base Override, {sense_name}"
                        static.states["target_ref"] = f"sense:{sense_name}:base_overrides"
                    imgui.end_menu()
            imgui.end_menu()
        # Initiative
        if imgui.menu_item_simple(f"Initiative##{menu_id}"):
            static.states["target_name"] = f"Initiative"
            static.states["target_ref"] = f"initiative:bonuses"
        # Armor Class
        if imgui.menu_item_simple(f"Armor Class##{menu_id}"):
            static.states["target_name"] = f"Armor Class"
            static.states["target_ref"] = f"armor_class:bonuses"
        # HP
        if imgui.menu_item_simple(f"HP##{menu_id}"):
            static.states["target_name"] = f"HP"
            static.states["target_ref"] = f"hp:bonuses"
                            
        imgui.end_menu()
    imgui.pop_item_flag()


def draw_add_bonus(bonus_id: str, bonus_list: list[Bonus], 
                   list_type: str, static: MainWindowProtocol,
                   numerical_step: int = 1,
                   is_feature_bonus: bool = False) -> None:
    if not bonus_id in static.states["new_bonuses"]:
        static.states["new_bonuses"][bonus_id] = {
            "new_bonus_name": "",
            "new_bonus_type": "",
            "new_bonus_value": "",
            "new_bonus_mult": 1.0
        }
    new_bonus = static.states["new_bonuses"][bonus_id]

    bonus_types = LIST_TYPE_TO_BONUS[list_type]

    # Choose bonus type
    draw_entities_menu("Bonus Type", bonus_id, bonus_types, new_bonus, static)

    if new_bonus["new_bonus_type"] != "":
        imgui.text(new_bonus["new_bonus_type"])
    else:
        imgui.text("Choose bonus type")

    if not is_feature_bonus:
        _, new_bonus["new_bonus_name"] = imgui.input_text_with_hint(
            f"##new_bonus_name_{bonus_id}", 
            "Name",
            new_bonus["new_bonus_name"],
            128); imgui.same_line()

    # If `Numerical` draw int button, else draw multiplier button
    if new_bonus["new_bonus_type"] == "Numerical Bonus":
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
            0.5)
    
    if not is_feature_bonus:
        imgui.same_line()

        if imgui.button(f"Add##{bonus_id}_new_bonus") and new_bonus["new_bonus_type"] != "":
            bonus_list.append({
                "name": new_bonus["new_bonus_name"],
                "value": new_bonus["new_bonus_value"],
                "multiplier": new_bonus["new_bonus_mult"],
                "manual": True
            })

            static.states["new_bonuses"][bonus_id] = {
                "new_bonus_name": "",
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


def draw_edit_list_popup(editable_list: list[Any], cache_prefix: str, popup_name: str, static: MainWindowProtocol):
    center = imgui.get_main_viewport().get_center()
    imgui.set_next_window_pos(center, imgui.Cond_.appearing.value, ImVec2(0.5, 0.5))

    if imgui.begin_popup_modal(popup_name, None, imgui.WindowFlags_.always_auto_resize.value)[0]:
        imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
        _, static.states["new_item_name"] = imgui.input_text_with_hint(
            "##new_item", 
            "Name", 
            static.states["new_item_name"],
            128); imgui.same_line()

        if imgui.button("Add##new_item"):
            if static.states["new_item_name"] != "":
                if isClassList(editable_list):
                    editable_list.append({
                        "name": static.states["new_item_name"],
                        "subclass": "",
                        "total": 0,
                        "level": 0,
                        "dice": 6,
                        "manual": True
                    })
                if isAbilityList(editable_list):
                    editable_list.append({
                        "name": static.states["new_item_name"],
                        "total": 0,
                        "total_base_score": 0,
                        "base_score_overrides": [],
                        "base_score_bonuses": [],
                        "base_score": 10,
                        "modifier_bonuses": [],
                        "manual": True
                    })
                if isRollableStatList(editable_list):
                    editable_list.append({
                        "name": static.states["new_item_name"],
                        "total": 0,
                        "bonuses": [],
                        "manual_advantage": False,
                        "manual_disadvantage": False,
                        "manual": True
                    })
                if isStaticStatList(editable_list):
                    editable_list.append({
                        "name": static.states["new_item_name"],
                        "total": 0,
                        "base": 0,
                        "base_overrides": [],
                        "bonuses": [],
                        "manual": True
                    })
                static.data_refs[f"{cache_prefix}:{static.states["new_item_name"]}"] = editable_list[-1]
                static.states["new_item_name"] = ""

        imgui.spacing()

        if imgui.begin_table("edit_list_display", 2, flags=STRIPED_TABLE_FLAGS):  # type: ignore
            imgui.table_setup_column("Name")
            imgui.table_setup_column("##delete")
            imgui.table_headers_row()

            for idx, item in enumerate(editable_list):
                if not item["name"].startswith("no_display"):
                    draw_text_cell(item["name"]); imgui.table_next_column()
                    if item["manual"]:
                        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                        if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                            del editable_list[idx]
                            del static.data_refs[f"{cache_prefix}:{item["name"]}"]
                        imgui.pop_style_color(3)

            end_table_nested()

        imgui.spacing()

        if imgui.button("Close", ImVec2(120, 0)):
            imgui.close_current_popup()
        imgui.end_popup()


def draw_edit_feature(feature: Feature, static: MainWindowProtocol) -> None:
    center = imgui.get_main_viewport().get_center()
    imgui.set_next_window_pos(center, imgui.Cond_.appearing.value, ImVec2(0.5, 0.5))
    window_size = imgui.get_main_viewport().size
    
    popup_name = f"Edit {feature["name"]}##popup"
    if imgui.begin_popup_modal(popup_name, None)[0]:
        imgui.set_cursor_pos_x(window_size.x/2)
        imgui.dummy(ImVec2(0, 0))

        imgui.align_text_to_frame_padding()
        imgui.text("Name"); imgui.same_line()
        imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
        _, static.states["feat_name"] = imgui.input_text(f"##{feature["name"]}_feature_name", static.states["feat_name"], 128)
        imgui.pop_item_width()

        imgui.text("Description")
        _, feature["description"] = imgui.input_text_multiline(f"##{feature["name"]}_feature_description", feature["description"], ImVec2(-1, imgui.get_text_line_height() * 10), 128)
        
        imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
        _, static.states["new_tag"] = imgui.input_text_with_hint("##new_tag", "Tag", static.states["new_tag"], 128)
        imgui.pop_item_width(); imgui.same_line()
        if imgui.button(f"Add##add_tag"):
            feature["tags"].append(static.states["new_tag"])
            static.states["new_tag"] = ""
        imgui.same_line()
        
        for idx, tag in enumerate(feature["tags"]):
            imgui.same_line(); imgui.align_text_to_frame_padding()
            imgui.text(f"{tag}"); imgui.same_line()

            imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
            imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
            imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{tag}_{idx}"):
                del feature["tags"][idx]
            imgui.pop_style_color(3)
        
        draw_target_menu("Target", f"{feature["name"]}_target", static)
        
        new_bonus = None
        if static.states["target_name"] != "":
            bonus_idx = len(feature["bonuses"]) + 1
            bonus_id = f"{feature["name"]}_bonus_{bonus_idx}"
            if not bonus_id in static.states["new_bonuses"]:
                static.states["new_bonuses"][bonus_id] = {
                    "new_bonus_name": "",
                    "new_bonus_type": "",
                    "new_bonus_value": "",
                    "new_bonus_mult": 1.0
                }
            new_bonus = static.states["new_bonuses"][bonus_id]

            draw_add_bonus(bonus_id, 
                           static.bonus_list_refs[static.states["target_ref"]],
                           "hp", static, is_feature_bonus=True)

        if imgui.button(f"Add##{feature["name"]}_new_bonus_to"):
            if new_bonus:
                bonus_mult = new_bonus["new_bonus_mult"]
                bonus_name = f"{new_bonus["new_bonus_type"]}{" x" + str(bonus_mult) if bonus_mult != 1.0 else ""} ({feature["name"]})"

                target_bonus: Bonus = {
                    "name": bonus_name,
                    "value": new_bonus["new_bonus_value"],
                    "multiplier": new_bonus["new_bonus_mult"],
                    "manual": False
                }

                feature_bonus: BonusTo = {
                    "name": static.states["target_name"],
                    "target": static.states["target_ref"],
                    "bonus": target_bonus,
                    "manual": True
                }

                static.bonus_list_refs[static.states["target_ref"]].append(target_bonus)
                feature["bonuses"].append(feature_bonus)

                static.states["target_name"] = ""
                static.states["target_ref"] = ""

                del static.states["new_bonuses"][bonus_id] # type: ignore

        if imgui.begin_table("feature_bonuses", 3, flags=STRIPED_TABLE_FLAGS): # type: ignore
            for idx, feature_bonus in enumerate(feature["bonuses"]):
                imgui.table_next_row(); imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(feature_bonus["name"])

                imgui.table_next_column()
                imgui.text(f"{feature_bonus["bonus"]["name"].replace(f" ({feature["name"]})", "")}")

                imgui.table_next_column()
                if feature_bonus["manual"]:
                    imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                    imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                    imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                    if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##feature_bonus_{idx}"):
                        delete_target = static.bonus_list_refs[feature_bonus["target"]]
                        delete_idx = delete_target.index(feature_bonus["bonus"])
                        del delete_target[delete_idx]

                        del feature["bonuses"][idx]
                    imgui.pop_style_color(3)

            end_table_nested()

        imgui.spacing()

        if imgui.button("Close", ImVec2(120, 0)):
            imgui.close_current_popup()
            if static.states["feat_name"] != "":
                feature["name"] = static.states["feat_name"]
            static.states["feat_name"] = ""

            static.states["target_name"] = ""
            static.states["target_ref"] = ""

            if new_bonus:
                del static.states["new_bonuses"][bonus_id] # type: ignore
        imgui.end_popup()