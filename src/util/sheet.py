import itertools
import random
from typing import Any, Callable, Optional

from imgui_bundle import ImColor, ImVec2, icons_fontawesome_6, imgui
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

from cs_types.components import Bonus, BonusTo, Counter, TextData
from cs_types.core import Feature, MainWindowProtocol, NewBonus, Roll, StatTypes
from cs_types.guards import (
    isAbilityList,
    isClassList,
    isFeature,
    isFeatureList,
    isRollableStatList,
    isStaticStatList,
)
from settings import STRIPED_NO_BORDERS_TABLE_FLAGS  # type: ignore
from settings import STRIPED_TABLE_FLAGS  # type: ignore
from settings import (  # type: ignore
    ADVANTAGE_ACTIVE_COLOR,
    DISADVANTAGE_ACTIVE_COLOR,
    DISADVANTAGE_COLOR,
    INVISIBLE_TABLE_FLAGS,
    LARGE_STRING_INPUT_WIDTH,
    LIST_TYPE_TO_BONUS,
    MAGICAL_WORD_WRAP_NUMBER_TABLE,
    MEDIUM_STRING_INPUT_WIDTH,
    OVERRIDE_COLOR,
    SHORT_STRING_INPUT_WIDTH,
    THREE_DIGIT_BUTTONS_INPUT_WIDTH,
    TWO_DIGIT_BUTTONS_INPUT_WIDTH,
)
from util.calc import (
    calculate_roll,
    check_for_cycles,
    fuzzy_search,
    get_bonus_value,
    sum_bonuses,
)
from util.core import open_image
from util.custom_imgui import ColorButton, draw_text_cell, end_table_nested, help_marker


def draw_exhaustion_penalty(stat_type: StatTypes, static: MainWindowProtocol) -> None:
    if static.data["exhaustion"]["total"] != 0 and static.data["exhaustion"]["total"] != 6:
        mult = 0
        if stat_type == "rollable":
            mult = 2
        elif stat_type == "static":
            mult = 5
        
        penalty = static.data["exhaustion"]["total"] * mult
        imgui.same_line()
        imgui.text_colored(DISADVANTAGE_COLOR, f"-{penalty}"); imgui.same_line()
        help_marker(static.data["exhaustion"]["description"])
    elif static.data["exhaustion"]["total"] == 6:
        imgui.same_line()
        imgui.text_colored(DISADVANTAGE_COLOR, "Dead"); imgui.same_line()
        help_marker(static.data["exhaustion"]["description"])


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
            # Spell Save
            elif bonus_type == "Spell Save"  and imgui.begin_menu(f"Spell Save##{menu_id}"):
                for class_item in static.data["level"]["classes"]:
                    class_name = class_item["name"]
                    if not class_name.startswith("no_display") and class_item["spell_save_enabled"] and imgui.menu_item_simple(f"{class_name}##{menu_id}"):
                        new_bonus["new_bonus_type"] = f"Spell Save, {class_name}"
                        new_bonus["new_bonus_value"] = f"spell_save:{class_name}"
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


def draw_add_bonus(bonus_id: str, 
                   target_ref: str,
                   bonus_list: list[Bonus],
                   bonus_types: list[str], static: MainWindowProtocol,
                   numerical_step: int = 1,
                   is_feature_bonus: bool = False, add_manual_text : bool = True) -> None:
    if not bonus_id in static.states["new_bonuses"]:
        static.states["new_bonuses"][bonus_id] = {
            "new_bonus_type": "",
            "new_bonus_value": "",
            "new_bonus_mult": 1.0
        }
    new_bonus = static.states["new_bonuses"][bonus_id]

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
            static.states["cyclic_bonus"], static.states["cyclic_bonus_path"] = check_for_cycles(static, 
                                                                                                 target_ref, 
                                                                                                 new_bonus["new_bonus_value"])
            
            if static.states["cyclic_bonus"]:
                imgui.open_popup("Cyclic Bonus Path")
            else:
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

    if static.states["cyclic_bonus"]:
        center = imgui.get_main_viewport().get_center()
        imgui.set_next_window_pos(center, imgui.Cond_.appearing.value, ImVec2(0.5, 0.5))
        
        if imgui.begin_popup_modal("Cyclic Bonus Path", None, imgui.WindowFlags_.always_auto_resize.value)[0]:
            imgui.text_colored(DISADVANTAGE_ACTIVE_COLOR, 
                               f"{' > '.join([target_ref] + static.states['cyclic_bonus_path'] + [target_ref])}")
        
            if imgui.button("Close", ImVec2(120, 0)):
                static.states["cyclic_bonus"] = False
                static.states["cyclic_bonus_path"] = []

                imgui.close_current_popup()
            imgui.end_popup()
                


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
                with ColorButton("bad"):
                    imgui.table_next_column()
                    if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                        del bonus_list[idx]
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
                with ColorButton("bad"):
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
                "spell_save_enabled": False,
                "spell_save": {
                    "name": f"Spell Save {item_name}",
                    "total": 0,
                    "base": 12,
                    "base_overrides": [],
                    "bonuses": [],
                    "manual": False
                },
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
                "damage_effects": [],
                "proficiencies": [],
                "manual": True
            })
        static.data_refs[f"{cache_prefix}:{item_name}"] = editable_list[-1]


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
            for damage_effect in item["damage_effects"]:
                idx_delete = static.data["damage_effects"].index(damage_effect)
                del static.data["damage_effects"][idx_delete]
            for proficiency in item["proficiencies"]:
                idx_delete = static.data["training"].index(proficiency)
                del static.data["training"][idx_delete]
        del editable_list[item_idx]
        del static.data_refs[f"{cache_prefix}:{item["name"]}"]


def draw_edit_list_popup(editable_list: list[Any], cache_prefix: str, 
                         popup_name: str, static: MainWindowProtocol, tag: str = ""):
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
            add_item_to_list(static.states["new_item_name"], editable_list, cache_prefix, static, tag)
            static.states["new_item_name"] = ""

        imgui.spacing()

        if imgui.begin_table("edit_list_display", 2, flags=STRIPED_TABLE_FLAGS):  # type: ignore
            imgui.table_setup_column("Name")
            imgui.table_setup_column("##delete")
            imgui.table_headers_row()

            for idx, item in enumerate(editable_list):
                if item["name"] != "no_display":
                    draw_text_cell(item["name"]); imgui.table_next_column()
                    if item["manual"]:
                        with ColorButton("bad"):
                            if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                                delete_item_from_list(item, idx, editable_list, cache_prefix, static)

            end_table_nested()

        imgui.spacing()

        if imgui.button("Close", ImVec2(120, 0)):
            imgui.close_current_popup()
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
        draw_add_bonus(f"counter_new_bonus", 
                       f"counter:{parent_name}:{counter["name"]}", 
                       counter["bonuses"], 
                       LIST_TYPE_TO_BONUS["all_no_advantage"], 
                       static, 
                       add_manual_text=False)
        
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


def draw_new_text_item_popup(table_name: str, default_types: list[str], target_lists: list[list[TextData]], 
                             static: MainWindowProtocol, source: str = "", manual: bool = True) -> None:
    if imgui.begin_popup(f"New Text Table Item Popup##{table_name}"):
        imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
        _, static.states["new_training"]["name"] = imgui.input_text_with_hint(
            "##new_training_name", "Name", static.states["new_training"]["name"], 128)
        imgui.pop_item_width()
        
        types = default_types + ["Other"]
        imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
        _, static.states["text_table_type_idx"] = imgui.combo(f"##{table_name}_select_type", 
                                                            static.states["text_table_type_idx"], 
                                                            types, len(types))
        imgui.pop_item_width()

        if static.states["text_table_type_idx"] == len(types) - 1:
            imgui.same_line()
            imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
            if static.states["new_training"]["type"] in types:
                static.states["new_training"]["type"] = ""
            _, static.states["new_training"]["type"] = imgui.input_text_with_hint(
                "##new_training_type", "Type (optional)", static.states["new_training"]["type"], 128)
            imgui.pop_item_width()
        else:
            static.states["new_training"]["type"] = types[static.states["text_table_type_idx"]]
        
        if source == "":
            imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
            _, static.states["new_training"]["source"] = imgui.input_text_with_hint(
                "##new_training_source", "Source (optional)", static.states["new_training"]["source"], 128)
            imgui.pop_item_width()
        
        if imgui.button("Add##add_new_training") and static.states["new_training"]["name"] != "":
            if static.states["new_training"]["type"] == "":
                static.states["new_training"]["type"] = "Other"

            for target_list in target_lists:
                target_list.append({
                    "name": static.states["new_training"]["name"],
                    "type": static.states["new_training"]["type"],
                    "source": static.states["new_training"]["source"] if source == "" else source,
                    "manual": manual
                })

            static.states["new_training"] = {
                "name": "",
                "type": "",
                "source": "",
                "manual": True
            }
        imgui.end_popup()
    # The reason why we do not need `elif` here with a check for opened popup is because
    # we can reset the data as much as we want (every frame when the popup is closed).
    # We only need to store the temporary data for the new item while the popup is opened.
    else:
        static.states["text_table_type_idx"] = 0
        static.states["new_training"] = {
            "name": "",
            "type": "",
            "source": "",
            "manual": True
        }

def draw_text_table(table_name: str, data: list[TextData], default_types: list[str], 
                    static: MainWindowProtocol) -> None:
    if imgui.begin_table(F"{table_name}_text_table", 2, flags=STRIPED_TABLE_FLAGS):  # type: ignore
        width = imgui.get_window_width()
        for item_type, item_list in itertools.groupby(sorted(data,  key=lambda x: x["type"]), key=lambda x: x["type"]):
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text(item_type)
            
            # Sort so that the order of the types is always the same regargdless of the order
            # proficiencies were added
            items = list(item_list)
            items.sort(key=lambda x: x["name"])
            imgui.table_next_column()
            imgui.push_text_wrap_pos(imgui.get_cursor_pos()[0] + width - MAGICAL_WORD_WRAP_NUMBER_TABLE)
            imgui.text(", ".join([item["name"] for item in items]))
            imgui.pop_text_wrap_pos()
        end_table_nested()

    center = imgui.get_main_viewport().get_center()
    imgui.set_next_window_pos(center, imgui.Cond_.appearing.value, ImVec2(0.5, 0.5))

    popup_name = f"Edit {table_name}"
    if imgui.begin_popup_modal(popup_name, None, imgui.WindowFlags_.always_auto_resize.value)[0]:
        if imgui.button(f"New Item##{table_name}"):
            imgui.open_popup(f"New Text Table Item Popup##{table_name}")
        draw_new_text_item_popup(table_name, default_types, [data], static)

        if imgui.begin_table("training_edit_list", 2, flags=STRIPED_TABLE_FLAGS):  # type: ignore
            for item_type, item_list in itertools.groupby(sorted(data, key=lambda x: x["type"]), key=lambda x: x["type"]):
                draw_text_cell(item_type); imgui.table_next_column()
                
                # Sort so that the order of the types is always the same regargdless of the order
                # proficiencies were added
                items = list(item_list)
                items.sort(key=lambda x: x["name"])

                if imgui.begin_table("training_of_type", 3, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
                    for item in items:
                        draw_text_cell(item["name"]); imgui.table_next_column(); imgui.align_text_to_frame_padding()
                        imgui.text(item["source"]); imgui.table_next_column()

                        if item["manual"]:
                            with ColorButton("bad"):
                                if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{item_type}_{item["name"]}"):
                                    delete_idx = data.index(item)
                                    del data[delete_idx]
                    end_table_nested()
            end_table_nested()
        
        imgui.spacing()
        if imgui.button("Close", ImVec2(120, 0)):
            static.states["new_training"] = {
                "name": "",
                "type": "",
                "source": "",
                "manual": True
            }
            imgui.close_current_popup()
        imgui.end_popup()


def draw_open_image_button(static: MainWindowProtocol) -> None:
    if not hasattr(static, "open_image_dialog"):
        static.open_image_dialog = None

    if imgui.button(f"{icons_fontawesome_6.ICON_FA_IMAGE}##open_image"):
        static.open_image_dialog = pfd.open_file("Select file", filters=["Image Files", "*.png *.jpg *.jpeg *.bmp"])

    open_image(static)


def draw_search_popup(search_id: str, search_list: list[Any],
                      search_key: str, tooltip_key: str,
                      target_list: list[Any], static: MainWindowProtocol,
                      callback_on_add: Optional[Callable[..., Any]]=None) -> None:
    """
    When opening a search popup, make sure to set up search data:

    ```
    if not static.states["search_data"].get("spells", False):
        static.states["search_data"]["spells"] = {
            "search_window_opened": True,
            "search_text": "",
            "search_results": []
        }
    ```
    """
    if imgui.begin_popup(f"search_{search_id}"):
        imgui.push_item_width(LARGE_STRING_INPUT_WIDTH)
        changed, static.states["search_data"][search_id]["search_text"] = imgui.input_text_with_hint(f"##search_{search_id}",
                                                                                                     "Search",
                                                                                                     static.states["search_data"][search_id]["search_text"],
                                                                                                     128)
        imgui.pop_item_width()

        if changed and static.states["search_data"][search_id]["search_text"] != "":
            static.states["search_data"][search_id]["search_results"] = list(filter(lambda x: fuzzy_search(static.states["search_data"][search_id]["search_text"],
                                                                                                           x[search_key]), search_list))

        
        # TODO: the search results are always one line. Use Clipper to clip the results table
        outer_size = ImVec2(0.0, imgui.get_text_line_height_with_spacing()*10)
        if static.states["search_data"][search_id]["search_results"] != [] and imgui.begin_table(f"search_results_{search_id}", 1, flags=STRIPED_TABLE_FLAGS | imgui.TableFlags_.scroll_y, outer_size=outer_size): # type: ignore
            for result in static.states["search_data"][search_id]["search_results"]:
                imgui.table_next_row(); imgui.table_next_column()
                imgui.set_next_item_allow_overlap()
                imgui.selectable(result[search_key], False, imgui.SelectableFlags_.span_all_columns) # type: ignore
                if imgui.is_item_hovered():
                    help_marker(result[tooltip_key], with_question_mark=False)
                    imgui.set_mouse_cursor(imgui.MouseCursor_.hand) # type: ignore
                    if imgui.is_mouse_clicked(imgui.MouseButton_.left): # type: ignore
                        target_list.append(result)
                        if callback_on_add:
                            callback_on_add()
                imgui.same_line()
            imgui.end_table()

        imgui.end_popup()
    elif static.states["search_data"].get(search_id, False):
        static.states["search_data"][search_id]["search_text"] = ""
        static.states["search_data"][search_id]["search_results"] = []


def draw_roll_menu(menu_id: str, roll_str: str, mod_str: str, roll_type: str, adv_disadv: int, static: MainWindowProtocol, button_result: bool=False) -> None:
    open_popup = False

    if button_result:
        imgui.open_popup(menu_id)

    if imgui.begin_popup(menu_id) or imgui.begin_popup_context_item():
        roll: Roll = {
            "roll_str": f"{roll_str}{f"+{mod_str}" if mod_str != "0" else ""}",
            "roll_type": roll_type,
            "roll_result": 0
        }
        roll["roll_result"] = calculate_roll(roll["roll_str"], adv_disadv)
        if imgui.menu_item_simple("Add to Roll"):
            static.states["roll_list"].append(roll)
        if imgui.menu_item_simple("Add & Roll"):
            open_popup = True
            static.states["roll_popup_opened"][menu_id] = True
            static.states["roll_list"].append(roll)
        imgui.end_popup()

    if open_popup:
        imgui.open_popup(f"roll_popup_{menu_id}")
        open_popup = False

    draw_roll_popup(menu_id, static)


def draw_roll_popup(menu_id: str, static: MainWindowProtocol) -> None:
    main_size = imgui.get_main_viewport().size
    main_pos = imgui.get_main_viewport().pos
    imgui.set_next_window_pos(ImVec2(main_pos.x + main_size.x - 10, main_pos.y + main_size.y - 10),
                              imgui.Cond_.appearing.value, ImVec2(1, 1))
    
    # TODO: make flashing optional
    fps = imgui.get_io().framerate
    if static.states["roll_color_frames_count"] >= 10*fps or static.states["roll_color_frames_count"] == 0:
        static.states["roll_popup_color"] = random.choices(range(256), k=3)
        static.states["roll_color_frames_count"] = 1
    else:
        static.states["roll_color_frames_count"] += 1

    rgb = static.states["roll_popup_color"]
    imgui.push_style_color(imgui.Col_.border.value, ImColor(rgb[0], rgb[1], rgb[2]).value) # type: ignore
    if imgui.begin_popup(f"roll_popup_{menu_id}"):
        imgui.text("Roll:")
        total = 0
        if imgui.begin_table(f"roll_table_{menu_id}", 3, STRIPED_TABLE_FLAGS):
            for roll in static.states["roll_list"]:
                roll_str, roll_type, roll_result = roll["roll_str"], roll["roll_type"], roll["roll_result"]

                imgui.table_next_row(); imgui.table_next_column()
                imgui.text(roll_str); imgui.table_next_column()

                total += roll_result
                imgui.text(str(roll_result)); imgui.table_next_column()

                imgui.text(roll_type)

            end_table_nested()
        imgui.spacing()

        types = set([roll["roll_type"] for roll in static.states["roll_list"]])
        if len(types) != 1:
            if imgui.begin_table(f"roll_results_table_{menu_id}", 2, STRIPED_TABLE_FLAGS):
                imgui.table_setup_column("Type")
                imgui.table_setup_column("Total")
                imgui.table_headers_row()

                for roll_type, roll_list in itertools.groupby(sorted(static.states["roll_list"],  
                                                                    key=lambda x: x["roll_type"]), 
                                                                    key=lambda x: x["roll_type"]):
                    imgui.table_next_row(); imgui.table_next_column()
                    imgui.text(roll_type); imgui.table_next_column()

                    type_total = sum([roll["roll_result"] for roll in roll_list])
                    imgui.text(str(type_total))

                end_table_nested()

        imgui.spacing()
        imgui.text(f"Total: {total}")

        imgui.end_popup()
    elif static.states["roll_popup_opened"].get(menu_id, False) and static.states["roll_popup_opened"][menu_id]:
        static.states["roll_popup_opened"][menu_id] = False
        static.states["roll_list"] = []
    imgui.pop_style_color()