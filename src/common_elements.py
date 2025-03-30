from math import trunc

from imgui_bundle import ImVec2, icons_fontawesome_6, imgui

import character_sheet_types
import type_checking_guards
from util import end_table_nested

# TODO: move to const.py or something
TWO_DIGIT_BUTTONS_INPUT_WIDTH = 75
TWO_DIGIT_INPUT_WIDTH = 25
SHORT_STRING_INPUT_WINDTH = 110
ADVANTAGE_COLOR = imgui.ImColor.hsv(0.3, 0.6, 0.6).value
ADVANTAGE_HOVER_COLOR = imgui.ImColor.hsv(0.3, 0.7, 0.7).value
ADVANTAGE_ACTIVE_COLOR = imgui.ImColor.hsv(0.3, 0.8, 0.8).value
DISADVANTAGE_COLOR = imgui.ImColor.hsv(0, 0.6, 0.6).value
DISADVANTAGE_HOVER_COLOR = imgui.ImColor.hsv(0, 0.7, 0.7).value
DISADVANTAGE_ACTIVE_COLOR = imgui.ImColor.hsv(0, 0.8, 0.8).value
FORCED_OVERRIDE_COLOR = imgui.ImColor.hsv(0.15, 0.8, 0.8).value


def draw_add_bonus(
    id: str,
    bonus_list: list[character_sheet_types.IntOrStrBonusType] | list[character_sheet_types.IntBonusType],
    bonus_types: list[str],
    numerical_bonus_step: int,
    static: character_sheet_types.MainWindowProtocol,
) -> None:
    if not hasattr(static, "new_bonuses"):
        static.new_bonuses = {}

    if not (id in static.new_bonuses.keys()):
        static.new_bonuses[id] = {
            "new_bonus_name": "",
            "current_new_bonus_type_idx": 0,
            "current_new_bonus_ability_idx": 0,
            "new_bonus_numerical": 0,
            "current_new_bonus_speed_idx": 0,
            "current_new_bonus_sense_idx": 0,
            "current_new_bonus_mult_idx": 0,
        }

    # NEW BONUS NAME
    imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
    _, static.new_bonuses[id]["new_bonus_name"] = imgui.input_text_with_hint(
        f"##new_bonus_name_{id}", "Name", static.new_bonuses[id]["new_bonus_name"], 128
    )
    imgui.same_line()

    # NEW BONUS TYPE
    imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
    _, static.new_bonuses[id]["current_new_bonus_type_idx"] = imgui.combo(
        f"##current_new_bonus_type_{id}", static.new_bonuses[id]["current_new_bonus_type_idx"], bonus_types, len(bonus_types)
    )
    imgui.same_line()

    new_bonus_name = static.new_bonuses[id]["new_bonus_name"]
    new_bonus_value: int | str | character_sheet_types.StaticStatType = 0
    new_bonus_multiplier = 1.0
    multipliers = ["Single", "Half", "Double"]

    # NUMERICAL BONUS
    if bonus_types[static.new_bonuses[id]["current_new_bonus_type_idx"]] == "Numerical":
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        _, static.new_bonuses[id]["new_bonus_numerical"] = imgui.input_int(
            f"##new_bonus_numerical_{id}", static.new_bonuses[id]["new_bonus_numerical"], numerical_bonus_step
        )
        new_bonus_value = static.new_bonuses[id]["new_bonus_numerical"]

    # ABILITY BONUS
    if bonus_types[static.new_bonuses[id]["current_new_bonus_type_idx"]] == "Ability":
        # TODO: extract to a constant or something, same with speed
        abilities = ["str", "dex", "con", "wis", "int", "cha"]
        imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
        _, static.new_bonuses[id]["current_new_bonus_ability_idx"] = imgui.combo(
            f"##current_new_bonus_ability_{id}",
            static.new_bonuses[id]["current_new_bonus_ability_idx"],
            abilities,
            len(abilities),
        )
        if type_checking_guards.isAbilityName(abilities[static.new_bonuses[id]["current_new_bonus_ability_idx"]]):
            new_bonus_value = abilities[static.new_bonuses[id]["current_new_bonus_ability_idx"]]

        imgui.same_line()
        imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
        _, static.new_bonuses[id]["current_new_bonus_mult_idx"] = imgui.combo(
            f"##current_new_bonus_mult_{id}", static.new_bonuses[id]["current_new_bonus_mult_idx"], multipliers, len(multipliers)
        )

    # PROFICICENCY BONUS
    if bonus_types[static.new_bonuses[id]["current_new_bonus_type_idx"]] == "Proficiency":
        imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
        _, static.new_bonuses[id]["current_new_bonus_mult_idx"] = imgui.combo(
            f"##current_new_bonus_mult_{id}", static.new_bonuses[id]["current_new_bonus_mult_idx"], multipliers, len(multipliers)
        )
        new_bonus_value = "prof"

    # SPEED BONUS
    if bonus_types[static.new_bonuses[id]["current_new_bonus_type_idx"]] == "Speed":
        # TODO: make a guard so that the user could not create cyclical speed references
        speed_types = [speed["name"] for speed in static.data["speed"]]
        imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
        _, static.new_bonuses[id]["current_new_bonus_speed_idx"] = imgui.combo(
            f"##current_new_bonus_speed_{id}",
            static.new_bonuses[id]["current_new_bonus_speed_idx"],
            speed_types,
            len(speed_types),
        )
        new_bonus_value = static.data["speed"][static.new_bonuses[id]["current_new_bonus_speed_idx"]]

        imgui.same_line()
        imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
        _, static.new_bonuses[id]["current_new_bonus_mult_idx"] = imgui.combo(
            f"##current_new_bonus_mult_{id}", static.new_bonuses[id]["current_new_bonus_mult_idx"], multipliers, len(multipliers)
        )
    imgui.same_line()

    # SENSE BONUS
    if bonus_types[static.new_bonuses[id]["current_new_bonus_type_idx"]] == "Sense":
        # TODO: make a guard so that the user could not create cyclical sense references
        sense_types = [sense["name"] for sense in static.data["senses"]]
        imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
        _, static.new_bonuses[id]["current_new_bonus_sense_idx"] = imgui.combo(
            f"##current_new_bonus_sense_{id}",
            static.new_bonuses[id]["current_new_bonus_sense_idx"],
            sense_types,
            len(sense_types),
        )
        new_bonus_value = static.data["senses"][static.new_bonuses[id]["current_new_bonus_sense_idx"]]

        imgui.same_line()
        imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
        _, static.new_bonuses[id]["current_new_bonus_mult_idx"] = imgui.combo(
            f"##current_new_bonus_mult_{id}", static.new_bonuses[id]["current_new_bonus_mult_idx"], multipliers, len(multipliers)
        )
    imgui.same_line()

    # TODO: advantage/disadvantage bonus

    # ADD BONUS
    if imgui.button(f"{icons_fontawesome_6.ICON_FA_CHECK}##{id}"):
        if type_checking_guards.isListIntOrStrBonusType(bonus_list):
            if multipliers[static.new_bonuses[id]["current_new_bonus_mult_idx"]] == "Single":
                new_bonus_multiplier = 1.0
            elif multipliers[static.new_bonuses[id]["current_new_bonus_mult_idx"]] == "Double":
                new_bonus_multiplier = 2.0
            else:
                new_bonus_multiplier = 0.5
            bonus_list.append(
                {"name": new_bonus_name, "value": new_bonus_value, "multiplier": new_bonus_multiplier, "manual": True}
            )
        elif type_checking_guards.isListIntBonusType(bonus_list) and isinstance(new_bonus_value, int):
            bonus_list.append({"name": new_bonus_name, "value": new_bonus_value, "manual": True})
        static.new_bonuses[id]["new_bonus_name"] = ""
        static.new_bonuses[id]["current_new_bonus_type_idx"] = 0
        static.new_bonuses[id]["current_new_bonus_ability_idx"] = 0
        static.new_bonuses[id]["new_bonus_numerical"] = 0
        static.new_bonuses[id]["current_new_bonus_mult_idx"] = 0


def draw_rollable_stat_value(
    stat_name: str,
    stat_dict: character_sheet_types.RollableStatType,
    dict_key: str,
    static: character_sheet_types.MainWindowProtocol,
) -> None:
    total_bonus = 0
    advantage = False
    disadvantage = False
    for bonus in stat_dict["bonuses"]:
        name, value, mult = bonus["name"], bonus["value"], bonus["multiplier"]

        # Advantages (disadvantages) don't stack, so we can just reassing the value
        # instead of calculating a sum or something
        if value == "adv":
            advantage = True
        elif value == "disadv":
            disadvantage = True
        elif value == "prof":
            total_bonus += trunc(static.data["proficiency"]["total"] * mult)
        elif type_checking_guards.isAbilityName(value):
            total_bonus += trunc(static.data["abilities"][value]["total"] * mult)
        elif type_checking_guards.isRepresentInt(value):
            total_bonus += value

    stat_dict["total"] = stat_dict["custom_mod"] + total_bonus

    advantage = advantage or stat_dict["custom_advantage"]
    disadvantage = disadvantage or stat_dict["custom_disadvantage"]

    # Color the skill button depending on having a (dis)advantage
    # Advantage and Disadvantage override each other, so we use XOR instead of OR
    button_color_applied = False
    if advantage ^ disadvantage:
        if advantage:
            imgui.push_style_color(imgui.Col_.button.value, ADVANTAGE_COLOR)
            imgui.push_style_color(imgui.Col_.button_hovered.value, ADVANTAGE_HOVER_COLOR)
            imgui.push_style_color(imgui.Col_.button_active.value, ADVANTAGE_ACTIVE_COLOR)
        elif disadvantage:
            imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
            imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
            imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
        button_color_applied = True

    # imgui.push_font(static.regular_font)
    # imgui.text(f"{icons_fontawesome_6.ICON_FA_CIRCLE}")
    # imgui.pop_font()
    # imgui.same_line()
    # imgui.push_font(static.bold_font)
    # imgui.text(f"{icons_fontawesome_6.ICON_FA_CIRCLE}")
    # imgui.pop_font()
    # imgui.same_line()
    # imgui.push_font(static.bold_font)
    # imgui.text(f"{icons_fontawesome_6.ICON_FA_CIRCLE_HALF_STROKE}")
    # imgui.pop_font()
    # imgui.same_line()
    if imgui.button(f"{stat_dict["total"]:+}##{stat_name}"):
        imgui.open_popup(f"{dict_key}_popup")
    if button_color_applied:
        imgui.pop_style_color(3)

    if imgui.begin_popup(f"{dict_key}_popup"):
        if imgui.begin_table(f"{dict_key}_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Custom Mod: ")
            imgui.same_line()
            imgui.table_next_column()
            imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
            _, stat_dict["custom_mod"] = imgui.input_int(f"##{dict_key}_custom_mod", stat_dict["custom_mod"], 1)
            end_table_nested()

        _, stat_dict["custom_advantage"] = imgui.checkbox("Custom Advantage", stat_dict["custom_advantage"])
        _, stat_dict["custom_disadvantage"] = imgui.checkbox("Custom Disadvantage", stat_dict["custom_disadvantage"])

        imgui.text("Add new bonus:")
        bonus_types = ["Numerical", "Ability", "Proficiency"]
        draw_add_bonus(f"{dict_key}_rollable_bonus", stat_dict["bonuses"], bonus_types, 1, static)

        if stat_dict["bonuses"]:
            imgui.text(f"Bonuses ({total_bonus}):")
            table_flags = (  # type: ignore
                imgui.TableFlags_.sizing_fixed_fit  # type: ignore
                | imgui.TableFlags_.no_host_extend_x  # type: ignore
                | imgui.TableFlags_.row_bg.value
            )
            if imgui.begin_table("additional_bonuses", 2, flags=table_flags):  # type: ignore
                for idx, bonus in enumerate(stat_dict["bonuses"]):
                    imgui.table_next_row()
                    name, value, mult, manual = bonus["name"], bonus["value"], bonus["multiplier"], bonus["manual"]
                    mult_str = str(trunc(mult) if mult != 0.5 else 0.5)

                    imgui.table_next_column()
                    if value == "adv":
                        imgui.text_colored(ADVANTAGE_ACTIVE_COLOR, f"\t{name}: Advantage")
                    elif value == "disadv":
                        imgui.text_colored(DISADVANTAGE_ACTIVE_COLOR, f"\t{name}: Disadvantage")
                    if value == "prof":
                        imgui.text(
                            f"\t{name}: Proficicency ({static.data["proficiency"]["total"]}{" x" + mult_str if mult_str != "1" else ""})"
                        )
                    elif type_checking_guards.isAbilityName(value):
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
                            del stat_dict["bonuses"][idx]
                        imgui.pop_style_color(3)
                end_table_nested()

        imgui.end_popup()


def draw_edit_list_popup(
    display_list: list[character_sheet_types.RollableStatType] | list[character_sheet_types.StaticStatType],
    window_name: str,
    static: character_sheet_types.MainWindowProtocol,
):
    center = imgui.get_main_viewport().get_center()
    imgui.set_next_window_pos(center, imgui.Cond_.appearing.value, ImVec2(0.5, 0.5))

    table_flags = (  # type: ignore
        imgui.TableFlags_.sizing_fixed_fit  # type: ignore
        | imgui.TableFlags_.no_host_extend_x  # type: ignore
        | imgui.TableFlags_.borders.value
        | imgui.TableFlags_.row_bg.value
        | imgui.TableFlags_.no_borders_in_body.value
    )

    if imgui.begin_popup_modal(window_name, None, imgui.WindowFlags_.always_auto_resize.value)[0]:
        if imgui.begin_table(f"{window_name}_new_item_table", 2, flags=table_flags):  # type: ignore
            imgui.table_setup_column("Name")
            imgui.table_setup_column("##add")
            imgui.table_headers_row()

            imgui.table_next_row()
            imgui.table_next_column()
            imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)

            if not hasattr(static, "new_list_item_name"):
                static.new_list_item_name = ""
            if not hasattr(static, "new_list_item_name_missing"):
                static.new_list_item_name_missing = False

            _, static.new_list_item_name = imgui.input_text("##new_list_item_name", static.new_list_item_name, 128)

            if static.new_list_item_name_missing:
                imgui.push_style_color(imgui.Col_.text.value, DISADVANTAGE_ACTIVE_COLOR)
                imgui.text("Enter the name")
                imgui.pop_style_color()

            imgui.table_next_column()
            if imgui.button("Add##new_list_item"):
                if static.new_list_item_name == "":
                    static.new_list_item_name_missing = True
                else:
                    if type_checking_guards.isListStaticStatType(display_list):
                        display_list.append(
                            {
                                "name": static.new_list_item_name,
                                "total": 10,
                                "base": 0,
                                "forced_bases": [],
                                "custom_mod": 0,
                                "bonuses": [],
                                "manual": True,
                            }
                        )
                    elif type_checking_guards.isListRollableStatType(display_list):
                        display_list.append(
                            {
                                "name": static.new_list_item_name,
                                "total": 0,
                                "custom_mod": 0,
                                "bonuses": [],
                                "custom_advantage": False,
                                "custom_disadvantage": False,
                                "custom_proficiency": False,
                                "manual": True,
                            }
                        )
                    static.new_list_item_name = ""
                    static.new_list_item_name_missing = False
            end_table_nested()

        imgui.spacing()

        if imgui.begin_table("display_list", 2, flags=table_flags):  # type: ignore
            imgui.table_setup_column("Name")
            imgui.table_setup_column("##delete")
            imgui.table_headers_row()

            for idx, list_item in enumerate(display_list):
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.text(list_item["name"].title())

                imgui.table_next_column()
                if list_item["manual"]:
                    imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                    imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                    imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                    if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                        del display_list[idx]
                    imgui.pop_style_color(3)

            end_table_nested()

        imgui.spacing()

        if imgui.button("Close", ImVec2(120, 0)):
            imgui.close_current_popup()
        imgui.end_popup()


def draw_static_stat(
    stat_name: str,
    stat_dict: character_sheet_types.StaticStatType,
    dict_key: str,
    numerical_bonus_step: int,
    base_override_bonus_types: list[str],
    bonus_types: list[str],
    static: character_sheet_types.MainWindowProtocol,
) -> None:

    base = stat_dict["base"]

    # Override the stat base
    forced_base_max_idx = -1
    is_forced_base = False
    if stat_dict["forced_bases"]:
        for idx, forced_base in enumerate(stat_dict["forced_bases"]):
            value = 0
            if type_checking_guards.isStaticStatType(forced_base["value"]):
                value = trunc(forced_base["value"]["total"] * forced_base["multiplier"])
            elif type_checking_guards.isRepresentInt(forced_base["value"]):
                value = trunc(forced_base["value"] * forced_base["multiplier"])

            if base < value:
                base = value
                forced_base_max_idx = idx
                is_forced_base = True

    total_bonus = 0
    for bonus in stat_dict["bonuses"]:
        if bonus["value"] == "prof":
            total_bonus += trunc(static.data["proficiency"]["total"] * bonus["multiplier"])
        if type_checking_guards.isStaticStatType(bonus["value"]):
            total_bonus += trunc(bonus["value"]["total"] * bonus["multiplier"])
        elif type_checking_guards.isAbilityName(bonus["value"]):
            total_bonus += trunc(static.data["abilities"][bonus["value"]]["total"] * bonus["multiplier"])
        elif type_checking_guards.isRepresentInt(bonus["value"]):
            total_bonus += trunc(bonus["value"] * bonus["multiplier"])

    stat_dict["total"] = base + total_bonus + stat_dict["custom_mod"]

    if imgui.button(f"{stat_dict["total"]}##{stat_name}"):
        imgui.open_popup(f"{dict_key}_popup")

    if imgui.begin_popup(f"{dict_key}_popup"):
        if imgui.begin_table(f"{dict_key}_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Base: ")
            imgui.same_line()
            imgui.table_next_column()
            imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
            _, stat_dict["base"] = imgui.input_int(f"##{dict_key}", stat_dict["base"], numerical_bonus_step)

            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Custom Mod: ")
            imgui.same_line()
            imgui.table_next_column()
            imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
            _, stat_dict["custom_mod"] = imgui.input_int(
                f"##{dict_key}_custom_mod", stat_dict["custom_mod"], numerical_bonus_step
            )
            end_table_nested()

        # TODO: if there is an ability bonus to the speed, floor to the closest 5
        # TODO: arbitrarty multipliers?
        imgui.text("Add new base override:")
        # TODO: rename the stat_dict["forced_bases"] to stat_dict["base_overrides"]
        draw_add_bonus(
            f"{dict_key}_base_override", stat_dict["forced_bases"], base_override_bonus_types, numerical_bonus_step, static
        )

        if stat_dict["forced_bases"]:
            if is_forced_base:
                imgui.text_colored(FORCED_OVERRIDE_COLOR, f"Base override ({base}):")
            else:
                imgui.text_disabled(f"Base override total (Not applied):")

            table_flags = (  # type: ignore
                imgui.TableFlags_.sizing_fixed_fit  # type: ignore
                | imgui.TableFlags_.no_host_extend_x  # type: ignore
                | imgui.TableFlags_.row_bg.value
            )
            if imgui.begin_table("base_overrides", 2, flags=table_flags):  # type: ignore
                for idx, forced_base in enumerate(stat_dict["forced_bases"]):
                    imgui.table_next_row()
                    imgui.table_next_column()
                    display_value = ""
                    mult_str = str(trunc(forced_base["multiplier"]) if forced_base["multiplier"] != 0.5 else 0.5)
                    forced_base_value: int = 0

                    if type_checking_guards.isStaticStatType(forced_base["value"]):
                        forced_base_value = forced_base["value"]["total"]
                    elif type_checking_guards.isRepresentInt(forced_base["value"]):
                        forced_base_value = forced_base["value"]

                    display_value = f"{forced_base_value}{" x" + mult_str if mult_str != "1" else ""}"

                    if (idx == forced_base_max_idx) and is_forced_base:
                        imgui.text(f"\t{forced_base["name"]}: {display_value}")
                    else:
                        imgui.text_disabled(f"\t{forced_base["name"]}: {display_value}")

                    imgui.table_next_column()
                    # TODO: move to a separate function `draw_delete_bonus`
                    if forced_base["manual"]:
                        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                        if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                            del stat_dict["forced_bases"][idx]
                        imgui.pop_style_color(3)
                end_table_nested()

        # TODO: if there is an ability bonus to the speed, floor to the closest 5
        # TODO: arbitrarty multipliers?
        imgui.text("Add new bonus:")
        draw_add_bonus(f"{dict_key}_static_bonus", stat_dict["bonuses"], bonus_types, numerical_bonus_step, static)

        if stat_dict["bonuses"]:
            imgui.text(f"Additional bonus ({total_bonus}):")
            table_flags = (  # type: ignore
                imgui.TableFlags_.sizing_fixed_fit  # type: ignore
                | imgui.TableFlags_.no_host_extend_x  # type: ignore
                | imgui.TableFlags_.row_bg.value
            )
            if imgui.begin_table("additional_bonuses", 2, flags=table_flags):  # type: ignore
                for idx, bonus in enumerate(stat_dict["bonuses"]):
                    imgui.table_next_row()
                    imgui.table_next_column()
                    bonus_name, bonus_value, bonus_mult, manual = (
                        bonus["name"],
                        bonus["value"],
                        bonus["multiplier"],
                        bonus["manual"],
                    )
                    bonus_mult_str = str(trunc(bonus_mult) if bonus_mult != 0.5 else 0.5)

                    if type_checking_guards.isStaticStatType(bonus_value):
                        imgui.text(
                            f"\t{bonus_name}: {bonus_value["total"]}{" x" + bonus_mult_str if bonus_mult_str != "1" else ""}"
                        )
                    elif type_checking_guards.isAbilityName(bonus_value):
                        imgui.text(
                            f"\t{bonus_name}: {bonus_value.upper()} ({static.data["abilities"][bonus_value]["total"]}{" x" + bonus_mult_str if bonus_mult_str != "1" else ""})"
                        )
                    elif type_checking_guards.isRepresentInt(bonus_value):
                        imgui.text(f"\t{bonus_name}: {bonus_value}{" x" + bonus_mult_str if bonus_mult_str != "1" else ""}")

                    imgui.table_next_column()
                    if manual:
                        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                        if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                            del stat_dict["bonuses"][idx]
                        imgui.pop_style_color(3)
                end_table_nested()
        imgui.end_popup()
