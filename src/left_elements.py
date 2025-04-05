import itertools
from math import trunc

from imgui_bundle import ImVec2, icons_fontawesome_6, imgui

import character_sheet_types
import type_checking_guards
from common_elements import (
    DISADVANTAGE_ACTIVE_COLOR,
    DISADVANTAGE_COLOR,
    DISADVANTAGE_HOVER_COLOR,
    FORCED_OVERRIDE_COLOR,
    MIDDLE_STRING_INPUT_WIDTH,
    SHORT_STRING_INPUT_WIDTH,
    TWO_DIGIT_BUTTONS_INPUT_WIDTH,
    draw_add_bonus,
    draw_edit_list_popup,
    draw_rollable_stat_value,
    draw_static_stat,
)
from util import end_table_nested


def calculate_level(static: character_sheet_types.MainWindowProtocol) -> None:
    total = sum([item["level"] for item in static.data["level"]["classes"]])
    static.data["level"]["total"] = total


def draw_level_class(static: character_sheet_types.MainWindowProtocol) -> None:
    table_flags = (  # type: ignore
        imgui.TableFlags_.sizing_fixed_fit  # type: ignore
        | imgui.TableFlags_.no_host_extend_x  # type: ignore
        | imgui.TableFlags_.borders.value
        | imgui.TableFlags_.row_bg.value
    )
    calculate_level(static)
    imgui.text(f"Level {static.data["level"]["total"]}, Classes")
    imgui.same_line()
    if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_classes"):
        imgui.open_popup("Edit Classes")

    if imgui.begin_table("classes", 2, flags=table_flags):
        for class_dict in static.data["level"]["classes"]:
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text(f"{class_dict["name"]}")

            imgui.table_next_column()
            if imgui.button(f"{class_dict["level"]}"):
                imgui.open_popup(f"##{class_dict["name"]}_edit_class")

            if imgui.begin_popup(f"##{class_dict["name"]}_edit_class"):
                if imgui.begin_table("class_settings", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text("Class")
                    imgui.table_next_column()
                    imgui.push_item_width(MIDDLE_STRING_INPUT_WIDTH)
                    _, class_dict["name"] = imgui.input_text("##class", class_dict["name"], 128)

                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text("Level")
                    imgui.table_next_column()
                    imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                    _, class_dict["level"] = imgui.input_int("##level", class_dict["level"])

                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text(f"HP dice type ({class_dict["level"]}d{class_dict["dice"]})")
                    imgui.table_next_column()
                    dice_types = [4, 6, 8, 10, 12, 20]
                    if not hasattr(static, "class_dice_type_idx"):
                        static.class_dice_type_idx = 0
                    imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                    _, static.class_dice_type_idx = imgui.combo(
                        f"##dice_combo", dice_types.index(class_dict["dice"]), [str(item) for item in dice_types], len(dice_types)
                    )
                    class_dict["dice"] = dice_types[static.class_dice_type_idx]

                    end_table_nested()
                imgui.end_popup()
        end_table_nested()

    draw_edit_list_popup(static.data["level"]["classes"], "Edit Classes", static)


def draw_name_level_class(static: character_sheet_types.MainWindowProtocol) -> None:
    if imgui.begin_table("name_level_class", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
        imgui.table_next_row()
        imgui.table_next_column()
        imgui.push_item_width(MIDDLE_STRING_INPUT_WIDTH)
        _, static.data["name"] = imgui.input_text("##name", static.data["name"], 128)
        imgui.same_line()

        imgui.table_next_column()
        imgui.text("HP placeholder")

        imgui.table_next_row()
        imgui.table_next_column()
        draw_level_class(static)

        end_table_nested()


def draw_add_skill_button(static: character_sheet_types.MainWindowProtocol) -> None:
    center = imgui.get_main_viewport().get_center()
    imgui.set_next_window_pos(center, imgui.Cond_.appearing.value, ImVec2(0.5, 0.5))

    if imgui.begin_popup_modal("Add new skill", None, imgui.WindowFlags_.always_auto_resize.value)[0]:
        abilities = ["STR", "DEX", "CON", "WIS", "INT", "CHA"]

        if not hasattr(static, "skill_name"):
            static.skill_name = ""

        if not hasattr(static, "skill_ability"):
            static.skill_ability = 0

        _, static.skill_name = imgui.input_text("Name", static.skill_name, 128)
        _, static.skill_ability = imgui.combo("Ability", static.skill_ability, abilities, len(abilities))

        if imgui.button("Cancel", ImVec2(120, 0)):
            imgui.close_current_popup()
        imgui.set_item_default_focus()
        imgui.same_line()
        if imgui.button("Add", ImVec2(120, 0)):
            imgui.close_current_popup()

            static.data["skills"].append(
                {
                    "name": static.skill_name,
                    "total": 0,
                    "custom_mod": 0,
                    "bonuses": [
                        {"name": "Basic Rules", "value": abilities[static.skill_ability].lower(), "multiplier": 1, "manual": True}
                    ],
                    "custom_advantage": False,
                    "custom_disadvantage": False,
                    "custom_proficiency": False,
                    "manual": True,
                }
            )

            static.skill_name = ""
            static.skill_ability = 0
        imgui.end_popup()


def draw_ability_button(
    ability_name: str, dict_key: character_sheet_types.AbilityNameType, static: character_sheet_types.MainWindowProtocol
) -> None:
    forced_total_base_scores = static.data["abilities"][dict_key]["forced_total_base_scores"]
    base_score = static.data["abilities"][dict_key]["base_score"]
    custom_mod = static.data["abilities"][dict_key]["custom_mod"]
    base_score_bonuses = static.data["abilities"][dict_key]["base_score_bonuses"]
    mod_bonuses = static.data["abilities"][dict_key]["mod_bonuses"]

    base_score_bonus = sum([bonus["value"] for bonus in base_score_bonuses])
    base_score_total = base_score + base_score_bonus

    # Override the ability score (for example, with Headband of Intellect)
    forced_total_max_idx = -1
    forced_total_max_value = 0
    is_forced_total = False
    if forced_total_base_scores:
        forced_total_max = max([total for total in forced_total_base_scores], key=lambda x: x["value"])
        forced_total_max_idx = forced_total_base_scores.index(forced_total_max)
        forced_total_max_value = forced_total_max["value"]

        if base_score_total < forced_total_max_value:
            base_score_total = forced_total_max_value
            is_forced_total = True

    mod_bonus = sum([bonus["value"] for bonus in mod_bonuses])
    static.data["abilities"][dict_key]["total"] = (base_score_total - 10) // 2 + custom_mod + mod_bonus

    # Button with final ability modifier
    if imgui.button(f"{ability_name.upper()}[{base_score_total}]\n{static.data["abilities"][dict_key]["total"]:^+}"):
        imgui.open_popup(f"{dict_key}_popup")

    # Popup window where you can
    #   - change the basic ability score
    #   - add a custom modifier
    #   - see what gives you additional bonuses
    if imgui.begin_popup(f"{dict_key}_popup"):
        if imgui.begin_table("abilities_base_and_mod_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Base Score: ")
            imgui.same_line()
            imgui.table_next_column()
            imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
            _, static.data["abilities"][dict_key]["base_score"] = imgui.input_int(
                f"##{dict_key}", static.data["abilities"][dict_key]["base_score"], 1
            )

            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Custom Mod: ")
            imgui.same_line()
            imgui.table_next_column()
            imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
            _, static.data["abilities"][dict_key]["custom_mod"] = imgui.input_int(
                f"##{dict_key}_custom_mod", static.data["abilities"][dict_key]["custom_mod"], 1
            )
            end_table_nested()

        imgui.text("Add new base score bonus:")
        bonus_types = ["Numerical"]
        draw_add_bonus(
            f"{dict_key}_base_score_bonus", static.data["abilities"][dict_key]["base_score_bonuses"], bonus_types, 1, static
        )

        if base_score_bonuses:
            # TODO: extract the table + delete bonus boilerplate to some kind of wrapper
            imgui.text(f"Base Score bonus ({base_score_bonus} -> {base_score_bonus // 2}):")
            table_flags = (  # type: ignore
                imgui.TableFlags_.sizing_fixed_fit  # type: ignore
                | imgui.TableFlags_.no_host_extend_x  # type: ignore
                | imgui.TableFlags_.row_bg.value
            )
            if imgui.begin_table("base_score_bonuses", 2, flags=table_flags):  # type: ignore
                for idx, bonus in enumerate(base_score_bonuses):
                    imgui.table_next_row()
                    base_score_bonus_name, base_score_bonus_value, base_score_bonus_manual = (
                        bonus["name"],
                        bonus["value"],
                        bonus["manual"],
                    )

                    imgui.table_next_column()
                    imgui.text(f"\t{base_score_bonus_name}: {base_score_bonus_value} -> {base_score_bonus_value // 2}")

                    imgui.table_next_column()
                    if base_score_bonus_manual:
                        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                        if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                            del static.data["abilities"][dict_key]["base_score_bonuses"][idx]
                        imgui.pop_style_color(3)
                end_table_nested()

        imgui.text("Add new bonus:")
        bonus_types = ["Numerical"]
        draw_add_bonus(f"{dict_key}_bonus", static.data["abilities"][dict_key]["mod_bonuses"], bonus_types, 1, static)

        if mod_bonuses:
            imgui.text(f"Additional bonus ({mod_bonus}):")
            table_flags = (  # type: ignore
                imgui.TableFlags_.sizing_fixed_fit  # type: ignore
                | imgui.TableFlags_.no_host_extend_x  # type: ignore
                | imgui.TableFlags_.row_bg.value
            )
            if imgui.begin_table("mod_bonuses", 2, flags=table_flags):  # type: ignore
                for idx, bonus in enumerate(mod_bonuses):
                    imgui.table_next_row()
                    mod_bonus_name, mod_bonus_value, mod_bonus_manual = bonus["name"], bonus["value"], bonus["manual"]
                    imgui.table_next_column()
                    imgui.text(f"\t{mod_bonus_name}: {mod_bonus_value}")

                    imgui.table_next_column()
                    if mod_bonus_manual:
                        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                        if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                            del static.data["abilities"][dict_key]["mod_bonuses"][idx]
                        imgui.pop_style_color(3)
                end_table_nested()

        imgui.text("Add new base override:")
        bonus_types = ["Numerical"]
        draw_add_bonus(
            f"{dict_key}_base_override", static.data["abilities"][dict_key]["forced_total_base_scores"], bonus_types, 1, static
        )

        if forced_total_max_idx != -1:
            if is_forced_total:
                imgui.text_colored(FORCED_OVERRIDE_COLOR, f"Forced total ({forced_total_max_value}):")
            else:
                imgui.text_disabled(f"Forced total (Not applied):")

            table_flags = (  # type: ignore
                imgui.TableFlags_.sizing_fixed_fit  # type: ignore
                | imgui.TableFlags_.no_host_extend_x  # type: ignore
                | imgui.TableFlags_.row_bg.value
            )
            if imgui.begin_table("additional_bonuses", 2, flags=table_flags):  # type: ignore
                for idx, total in enumerate(forced_total_base_scores):
                    imgui.table_next_row()
                    total_name, total_value, total_manual = total["name"], total["value"], total["manual"]

                    imgui.table_next_column()
                    if (idx == forced_total_max_idx) and is_forced_total:
                        imgui.text(f"\t{total_name}: {total_value}")
                    else:
                        imgui.text_disabled(f"\t{total_name}: {total_value}")

                    imgui.table_next_column()
                    if total_manual:
                        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                        if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                            del static.data["abilities"][dict_key]["forced_total_base_scores"][idx]
                        imgui.pop_style_color(3)
                end_table_nested()
        imgui.end_popup()


def draw_abilities(static: character_sheet_types.MainWindowProtocol) -> None:
    if imgui.begin_table("abilities_table", 6, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
        imgui.table_next_row()

        imgui.table_next_column()
        draw_ability_button("STR", "str", static)

        imgui.table_next_column()
        draw_ability_button("DEX", "dex", static)

        imgui.table_next_column()
        draw_ability_button("CON", "con", static)

        imgui.table_next_column()
        draw_ability_button("WIS", "wis", static)

        imgui.table_next_column()
        draw_ability_button("INT", "int", static)

        imgui.table_next_column()
        draw_ability_button("CHA", "cha", static)

        end_table_nested()


def draw_saves(static: character_sheet_types.MainWindowProtocol):
    table_flags = (  # type: ignore
        imgui.TableFlags_.sizing_fixed_fit  # type: ignore
        | imgui.TableFlags_.no_host_extend_x  # type: ignore
        | imgui.TableFlags_.borders.value  # type: ignore
        | imgui.TableFlags_.no_borders_in_body.value
    )
    if imgui.begin_table("saves_table", 4, flags=table_flags):  # type: ignore
        for save_pair in [["str", "dex"], ["con", "wis"], ["int", "cha"]]:
            imgui.table_next_row()
            for save_name in save_pair:
                imgui.table_next_column()
                imgui.align_text_to_frame_padding()
                imgui.text(f"{save_name.upper()}")
                imgui.table_next_column()
                if type_checking_guards.isAbilityName(save_name):
                    draw_rollable_stat_value(save_name, static.data["saves"][save_name], save_name, static)

        end_table_nested()


def draw_proficiency_value(static: character_sheet_types.MainWindowProtocol) -> None:
    custom_mod, bonuses = static.data["proficiency"]["custom_mod"], static.data["proficiency"]["bonuses"]
    bonus = sum([bonus["value"] for bonus in bonuses])
    static.data["proficiency"]["total"] = custom_mod + bonus

    if imgui.button(f"{static.data["proficiency"]["total"]:+}"):
        imgui.open_popup(f"prof_popup")

    if imgui.begin_popup(f"prof_popup"):
        if imgui.begin_table("prof_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Base: ")
            imgui.same_line()
            imgui.table_next_column()
            imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
            _, static.data["proficiency"]["custom_mod"] = imgui.input_int(f"##prof", static.data["proficiency"]["custom_mod"], 1)
            end_table_nested()

        if bonuses:
            imgui.text(f"Additional bonus ({bonus}):")
            for item in bonuses:
                name, value = item.values()
                imgui.text(f"\t{name}: {value}")
        imgui.end_popup()


def draw_ac_value(static: character_sheet_types.MainWindowProtocol) -> None:
    base, armor, custom_mod, bonuses = (
        static.data["ac"]["base"],
        static.data["ac"]["armor"],
        static.data["ac"]["custom_mod"],
        static.data["ac"]["bonuses"],
    )

    if armor:
        base = armor["value"]

    total_bonus_no_dex = 0
    dex_bonus = 0
    for bonus in bonuses:
        name, value, mult = bonus["name"], bonus["value"], bonus["multiplier"]

        if value == "prof":
            total_bonus_no_dex += trunc(static.data["proficiency"]["total"] * mult)
        elif type_checking_guards.isAbilityName(value):
            if value == "dex":
                if armor and armor["max_dex_bonus"]:
                    dex_bonus = min(trunc(static.data["abilities"]["dex"]["total"] * mult), armor["max_dex_bonus"])
                else:
                    dex_bonus = trunc(static.data["abilities"]["dex"]["total"] * mult)
            else:
                total_bonus_no_dex += trunc(static.data["abilities"][value]["total"] * mult)
        elif type_checking_guards.isRepresentInt(value):
            total_bonus_no_dex += value

    static.data["ac"]["total"] = base + total_bonus_no_dex + dex_bonus + custom_mod

    if imgui.button(f"{static.data["ac"]["total"]}"):
        imgui.open_popup(f"ac_popup")

    if imgui.begin_popup(f"ac_popup"):
        if imgui.begin_table(f"ac_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Custom Mod: ")
            imgui.same_line()
            imgui.table_next_column()
            imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
            _, static.data["ac"]["custom_mod"] = imgui.input_int(f"##ac_custom_mod", static.data["ac"]["custom_mod"], 1)
            end_table_nested()

        if armor:
            imgui.text(f"Armor:")
            if armor["max_dex_bonus"]:
                imgui.text(
                    f"\t{armor["name"]}: {armor["value"]} + DEX (max {armor["max_dex_bonus"]}) = {armor["value"] + dex_bonus}"
                )
            else:
                imgui.text(f"\t{armor["name"]}: {armor["value"]} + DEX ({dex_bonus})")

        imgui.text("Add new bonus:")
        bonus_types = ["Numerical", "Ability", "Proficiency"]
        draw_add_bonus("ac_bonus", static.data["ac"]["bonuses"], bonus_types, 1, static)

        if bonuses:
            imgui.text(f"Bonuses ({total_bonus_no_dex + dex_bonus}):")
            table_flags = (  # type: ignore
                imgui.TableFlags_.sizing_fixed_fit  # type: ignore
                | imgui.TableFlags_.no_host_extend_x  # type: ignore
                | imgui.TableFlags_.row_bg.value
            )
            if imgui.begin_table("additional_bonuses", 2, flags=table_flags):  # type: ignore
                for idx, bonus in enumerate(bonuses):
                    imgui.table_next_row()
                    name, value, mult, manual = bonus["name"], bonus["value"], bonus["multiplier"], bonus["manual"]
                    mult_str = str(trunc(mult) if mult != 0.5 else 0.5)

                    imgui.table_next_column()
                    if value == "prof":
                        imgui.text(
                            f"\t{name}: Proficiency ({static.data["proficiency"]["total"]}{" x" + mult_str if mult_str != "1" else ""})"
                        )
                    elif type_checking_guards.isAbilityName(value):
                        if value == "dex" and armor and armor["max_dex_bonus"]:
                            imgui.text(
                                f"\tBasic rules: DEX ({static.data["abilities"]["dex"]["total"]}{" x" + mult_str if mult_str != "1" else ""}) (max {armor["max_dex_bonus"]})"
                            )
                        else:
                            imgui.text(
                                f"\t{name}: {value.upper()} ({static.data["abilities"][value]["total"]}{" x" + mult_str if mult_str != "1" else ""})"
                            )
                    elif type_checking_guards.isRepresentInt(value):
                        imgui.text(f"\t{name}: {value}")

                    imgui.table_next_column()
                    if manual:
                        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                        if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                            del static.data["ac"]["bonuses"][idx]
                        imgui.pop_style_color(3)

                end_table_nested()
        imgui.end_popup()


def draw_speed(static: character_sheet_types.MainWindowProtocol) -> None:
    table_flags = (  # type: ignore
        imgui.TableFlags_.sizing_fixed_fit  # type: ignore
        | imgui.TableFlags_.no_host_extend_x  # type: ignore
        | imgui.TableFlags_.borders.value
        | imgui.TableFlags_.row_bg.value
    )
    if imgui.begin_table("speed_table", 2, flags=table_flags):  # type: ignore
        for speed in static.data["speed"]:
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.align_text_to_frame_padding()
            imgui.text(f"{speed["name"].title()}")
            imgui.table_next_column()
            draw_static_stat(
                speed["name"], speed, speed["name"], 5, ["Numerical", "Speed"], ["Numerical", "Ability", "Speed"], static
            )

        end_table_nested()

    draw_edit_list_popup(static.data["speed"], "Edit Speed", static)


def draw_senses(static: character_sheet_types.MainWindowProtocol) -> None:
    table_flags = (  # type: ignore
        imgui.TableFlags_.sizing_fixed_fit  # type: ignore
        | imgui.TableFlags_.no_host_extend_x  # type: ignore
        | imgui.TableFlags_.borders.value
        | imgui.TableFlags_.row_bg.value
    )
    if imgui.begin_table("senses_table", 2, flags=table_flags):  # type: ignore
        for sense in static.data["senses"]:
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.align_text_to_frame_padding()
            imgui.text(f"{sense["name"].title()}")
            imgui.table_next_column()
            draw_static_stat(
                sense["name"], sense, sense["name"], 5, ["Numerical", "Sense"], ["Numerical", "Ability", "Sense"], static
            )

        end_table_nested()

    draw_edit_list_popup(static.data["senses"], "Edit Senses", static)


def draw_passives(static: character_sheet_types.MainWindowProtocol):
    table_flags = (  # type: ignore
        imgui.TableFlags_.sizing_fixed_fit  # type: ignore
        | imgui.TableFlags_.no_host_extend_x  # type: ignore
        | imgui.TableFlags_.borders.value
        | imgui.TableFlags_.row_bg.value
    )
    if imgui.begin_table("passives_table", 2, flags=table_flags):  # type: ignore
        for passive in static.data["passives"]:
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.align_text_to_frame_padding()
            imgui.text(f"{passive["name"].title()}")
            imgui.table_next_column()
            draw_static_stat(
                passive["name"],
                passive,
                passive["name"],
                1,
                ["Numerical", "Ability", "Proficiency"],
                ["Numerical", "Ability", "Proficiency"],
                static,
            )
        end_table_nested()

    draw_edit_list_popup(static.data["passives"], "Edit Passive Skills", static)


def draw_skills(static: character_sheet_types.MainWindowProtocol) -> None:
    table_flags = (  # type: ignore
        imgui.TableFlags_.sizing_fixed_fit  # type: ignore
        | imgui.TableFlags_.no_host_extend_x  # type: ignore
        | imgui.TableFlags_.borders.value
        | imgui.TableFlags_.row_bg.value
    )
    if imgui.begin_table("skills", 2, flags=table_flags):  # type: ignore
        for skill in static.data["skills"]:
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.align_text_to_frame_padding()
            imgui.text(skill["name"].title())

            imgui.table_next_column()
            draw_rollable_stat_value(skill["name"].title(), skill, skill["name"], static)
        end_table_nested()

    draw_edit_list_popup(static.data["skills"], "Edit Skills", static)


def draw_tool_proficiencies(static: character_sheet_types.MainWindowProtocol) -> None:
    proficiencies = static.data["tool_proficiencies"]["proficiencies"]
    # Sort so that the order of the types is always the same regargdless of the order
    # proficiencies were added
    proficiencies.sort(key=lambda x: x["type"])

    table_flags = (  # type: ignore
        imgui.TableFlags_.sizing_fixed_fit  # type: ignore
        | imgui.TableFlags_.no_host_extend_x  # type: ignore
        | imgui.TableFlags_.borders.value
        | imgui.TableFlags_.row_bg.value
    )
    if imgui.begin_table("tool_proficiencies", 2, flags=table_flags):  # type: ignore
        for proficiency_type, proficiencies_list in itertools.groupby(proficiencies, key=lambda x: x["type"]):
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text(proficiency_type)
            items = list(proficiencies_list)
            # Sort so that the order of the types is always the same regargdless of the order
            # proficiencies were added
            items.sort(key=lambda x: x["name"])
            imgui.table_next_column()
            imgui.text("\n".join([item["name"] for item in items]))

        end_table_nested()

    center = imgui.get_main_viewport().get_center()
    imgui.set_next_window_pos(center, imgui.Cond_.appearing.value, ImVec2(0.5, 0.5))

    if imgui.begin_popup_modal("Edit Tool and Language Proficiencies", None, imgui.WindowFlags_.always_auto_resize.value)[0]:
        if imgui.begin_table("add_tool_proficiencies", 4, flags=table_flags):  # type: ignore
            imgui.table_setup_column("Name")
            imgui.table_setup_column("Type")
            imgui.table_setup_column("Source")
            imgui.table_setup_column("##add")
            imgui.table_headers_row()

            imgui.table_next_row()

            imgui.table_next_column()

            imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
            if not hasattr(static, "tool_proficiency_name_missing"):
                static.tool_proficiency_name_missing = False
            if not hasattr(static, "tool_proficiency_name"):
                static.tool_proficiency_name = ""
            _, static.tool_proficiency_name = imgui.input_text("##tool_proficiency_name", static.tool_proficiency_name, 128)

            if static.tool_proficiency_name_missing:
                imgui.push_style_color(imgui.Col_.text.value, DISADVANTAGE_ACTIVE_COLOR)
                imgui.text("Enter the name")
                imgui.pop_style_color()

            imgui.table_next_column()
            if not hasattr(static, "tool_proficiency_type"):
                static.tool_proficiency_type = ""
            imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
            _, static.tool_proficiency_type = imgui.input_text_with_hint(
                "##tool_proficiency_type", "Other", static.tool_proficiency_type, 128
            )

            imgui.table_next_column()
            if not hasattr(static, "tool_proficiency_source"):
                static.tool_proficiency_source = ""
            imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
            _, static.tool_proficiency_source = imgui.input_text_with_hint(
                "##tool_proficiency_source", "optional", static.tool_proficiency_source, 128
            )

            imgui.table_next_column()
            if imgui.button("Add##proficiency"):
                if static.tool_proficiency_name == "":
                    static.tool_proficiency_name_missing = True
                else:
                    proficiencies.append(
                        {
                            "name": static.tool_proficiency_name,
                            "source": static.tool_proficiency_source,
                            "type": static.tool_proficiency_type if not (static.tool_proficiency_type == "") else "Other",
                            "manual": True,
                        }
                    )
                    static.tool_proficiency_name = ""
                    static.tool_proficiency_type = ""
                    static.tool_proficiency_source = ""
                    static.tool_proficiency_name_missing = False
            end_table_nested()

        imgui.spacing()

        if imgui.begin_table("edit_tool_proficiencies", 4, flags=table_flags | imgui.TableFlags_.sortable):  # type: ignore
            imgui.table_setup_column("Name")
            imgui.table_setup_column("Type")
            imgui.table_setup_column("Source")
            imgui.table_setup_column("##delete")
            imgui.table_headers_row()

            # We need to copy the original list because otherwise sorting in the edit mode
            # would affect how proficiencies are displayed in the character sheet
            proficiencies_for_table = proficiencies.copy()

            # We need to sort data in the copied list every frame because otherwise
            # it will always be displayed in the order it is stored in the original list
            sort_by = static.data["tool_proficiencies"]["sorting_in_edit_mode"]["sort_by"]
            sort_descending = static.data["tool_proficiencies"]["sorting_in_edit_mode"]["sort_descending"]
            proficiencies_for_table.sort(key=lambda x: x[sort_by], reverse=sort_descending)  # type: ignore

            for idx, prof in enumerate(proficiencies_for_table):
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.text(prof["name"])
                imgui.table_next_column()
                imgui.text(prof["type"])
                imgui.table_next_column()
                imgui.text(prof["source"])
                imgui.table_next_column()

                if prof["manual"]:
                    imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                    imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                    imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                    if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                        delete_idx = next(
                            (
                                index
                                for (index, item) in enumerate(proficiencies)
                                if (
                                    item["name"] == prof["name"]
                                    and item["type"] == prof["type"]
                                    and item["source"] == prof["source"]
                                    and item["manual"] == True
                                )
                            )
                        )
                        del proficiencies[delete_idx]
                    imgui.pop_style_color(3)

            if sort_specs := imgui.table_get_sort_specs():
                sort_specs_list = ("name", "type", "source", "manual")
                sort_by_idx = sort_specs.specs.column_index
                sort_by = sort_specs_list[sort_by_idx]
                # Save the sorting settings so the user would not need to re-sort the list
                # every time they open the edit mode
                static.data["tool_proficiencies"]["sorting_in_edit_mode"]["sort_by"] = sort_by

                sort_direction = sort_specs.specs.sort_direction
                sort_descending = False
                if sort_direction == imgui.SortDirection.descending:
                    sort_descending = True
                static.data["tool_proficiencies"]["sorting_in_edit_mode"]["sort_descending"] = sort_descending

                proficiencies_for_table.sort(key=lambda x: x[sort_by], reverse=sort_descending)  # type: ignore
                sort_specs.specs_dirty = False

            end_table_nested()

        imgui.spacing()

        if imgui.button("Close", ImVec2(120, 0)):
            imgui.close_current_popup()
        imgui.end_popup()
