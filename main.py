import itertools
import json
from math import trunc

from imgui_bundle import hello_imgui  # type: ignore
from imgui_bundle import ImVec2, icons_fontawesome_6, imgui, immapp  # type: ignore
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

import character_sheet_types
import util

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


@character_sheet_types.main_window_decorator
def main_window(font_holder: character_sheet_types.FontHolder) -> None:
    static = main_window
    static.regular_font = font_holder.regular_font
    static.bold_font = font_holder.bold_font

    # Only draw the main interface if the character file is loaded
    if hasattr(static, "file_paths") and static.file_paths:
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                if imgui.menu_item_simple("Open", "Ctrl+N"):
                    static.open_file_dialog = pfd.open_file("Select file")
                if imgui.menu_item_simple("Save", "Ctrl+S"):
                    save_file(static)
                imgui.end_menu()
            imgui.end_main_menu_bar()

        if imgui.shortcut(imgui.Key.mod_ctrl | imgui.Key.n):  # type: ignore
            static.open_file_dialog = pfd.open_file("Select file")
        # We need to continously try to open a file, otherwise it is called
        # once when the files have not yet been selected
        open_file(static)

        if imgui.shortcut(imgui.Key.mod_ctrl | imgui.Key.s):  # type: ignore
            save_file(static)

        imgui.spacing()

        imgui.text("Abilities: ")
        imgui.same_line()
        draw_abilities(static)
        draw_misc(static)
        imgui.text("Saves: ")
        imgui.same_line()
        draw_saves(static)
        imgui.text("Passives: ")
        imgui.same_line()
        draw_passives(static)
        imgui.text("Skills: ")
        draw_skills(static)
        imgui.text("Tool and Language Proficiencies")
        draw_tool_proficiencies(static)

        # TODO: create a separate button somewhere for creating new stats/skills/etc
        # draw_add_skill_button(static)
    else:
        draw_file_button(static)

    if not hasattr(static, "theme"):
        hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.imgui_colors_dark)
        static.theme = hello_imgui.ImGuiTheme_.imgui_colors_dark.name


def open_file(static: character_sheet_types.MainWindowProtocol) -> None:
    if static.open_file_dialog is not None and static.open_file_dialog.ready():
        static.file_paths = static.open_file_dialog.result()
        if static.file_paths:
            character_file = open(static.file_paths[0], "r+")
            static.data = json.load(character_file)
            character_file.close()

        static.open_file_dialog = None


def draw_file_button(static: character_sheet_types.MainWindowProtocol) -> None:
    if not hasattr(static, "open_file_dialog"):
        static.open_file_dialog = None
    if imgui.button("Open file"):
        static.open_file_dialog = pfd.open_file("Select file")
    open_file(static)


def save_file(static: character_sheet_types.MainWindowProtocol) -> None:
    character_file = open(static.file_paths[0], "r+")
    character_file.seek(0)
    character_file.truncate(0)
    json.dump(static.data, character_file, indent=4)
    character_file.close()


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
    if imgui.button(f"{ability_name.upper()}: {static.data["abilities"][dict_key]["total"]:+}"):
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
            imgui.end_table()

        imgui.text("Add new base score bonus:")
        bonus_types = ["Numerical"]
        draw_add_bonus(
            f"{dict_key}_base_score_bonus", static.data["abilities"][dict_key]["base_score_bonuses"], bonus_types, static
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
                imgui.end_table()

        imgui.text("Add new bonus:")
        bonus_types = ["Numerical"]
        draw_add_bonus(f"{dict_key}_bonus", static.data["abilities"][dict_key]["mod_bonuses"], bonus_types, static)

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
                imgui.end_table()

        imgui.text("Add new base override:")
        bonus_types = ["Numerical"]
        draw_add_bonus(
            f"{dict_key}_base_override", static.data["abilities"][dict_key]["forced_total_base_scores"], bonus_types, static
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
                imgui.end_table()
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

        imgui.end_table()


def draw_saves(static: character_sheet_types.MainWindowProtocol):
    if imgui.begin_table("abilities_table", 6, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
        imgui.table_next_row()

        imgui.table_next_column()
        draw_rollable_stat("STR", static.data["saves"]["str"], "str", static)

        imgui.table_next_column()
        draw_rollable_stat("DEX", static.data["saves"]["dex"], "dex", static)

        imgui.table_next_column()
        draw_rollable_stat("CON", static.data["saves"]["con"], "con", static)

        imgui.table_next_column()
        draw_rollable_stat("WIS", static.data["saves"]["wis"], "wis", static)

        imgui.table_next_column()
        draw_rollable_stat("INT", static.data["saves"]["int"], "int", static)

        imgui.table_next_column()
        draw_rollable_stat("CHA", static.data["saves"]["cha"], "cha", static)

        imgui.end_table()


def clean_up_new_bonuses(ids: list[str], static: character_sheet_types.MainWindowProtocol):
    pass


def draw_add_bonus(
    id: str,
    bonus_list: list[character_sheet_types.IntOrStrBonusType] | list[character_sheet_types.IntBonusType],
    bonus_types: list[str],
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
    new_bonus_value: int | str = 0
    new_bonus_multiplier = 1.0
    multipliers = ["Single", "Half", "Double"]

    # NUMERICAL BONUS
    if bonus_types[static.new_bonuses[id]["current_new_bonus_type_idx"]] == "Numerical":
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        _, static.new_bonuses[id]["new_bonus_numerical"] = imgui.input_int(
            f"##new_bonus_numerical_{id}", static.new_bonuses[id]["new_bonus_numerical"], 1
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
        if util.isAbilityName(abilities[static.new_bonuses[id]["current_new_bonus_ability_idx"]]):
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
        speed_types = ["walking", "climbing", "swimming", "flying"]
        imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
        _, static.new_bonuses[id]["current_new_bonus_speed_idx"] = imgui.combo(
            f"##current_new_bonus_speed_{id}",
            static.new_bonuses[id]["current_new_bonus_speed_idx"],
            speed_types,
            len(speed_types),
        )
        if util.isSpeedName(speed_types[static.new_bonuses[id]["current_new_bonus_speed_idx"]]):
            new_bonus_value = speed_types[static.new_bonuses[id]["current_new_bonus_speed_idx"]]

        imgui.same_line()
        imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
        _, static.new_bonuses[id]["current_new_bonus_mult_idx"] = imgui.combo(
            f"##current_new_bonus_mult_{id}", static.new_bonuses[id]["current_new_bonus_mult_idx"], multipliers, len(multipliers)
        )
    imgui.same_line()

    # ADD BONUS
    if imgui.button(f"{icons_fontawesome_6.ICON_FA_CHECK}##{id}"):
        if util.isListIntOrStrBonusType(bonus_list):
            if multipliers[static.new_bonuses[id]["current_new_bonus_mult_idx"]] == "Single":
                new_bonus_multiplier = 1.0
            elif multipliers[static.new_bonuses[id]["current_new_bonus_mult_idx"]] == "Double":
                new_bonus_multiplier = 2.0
            else:
                new_bonus_multiplier = 0.5
            bonus_list.append(
                {"name": new_bonus_name, "value": new_bonus_value, "multiplier": new_bonus_multiplier, "manual": True}
            )
        elif util.isListIntBonusType(bonus_list) and isinstance(new_bonus_value, int):
            bonus_list.append({"name": new_bonus_name, "value": new_bonus_value, "manual": True})
        static.new_bonuses[id]["new_bonus_name"] = ""
        static.new_bonuses[id]["current_new_bonus_type_idx"] = 0
        static.new_bonuses[id]["current_new_bonus_ability_idx"] = 0
        static.new_bonuses[id]["new_bonus_numerical"] = 0
        static.new_bonuses[id]["current_new_bonus_mult_idx"] = 0


def draw_rollable_stat(
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
        elif util.isAbilityName(value):
            total_bonus += trunc(static.data["abilities"][value]["total"] * mult)
        elif util.isRepresentInt(value):
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
    if imgui.button(f"{stat_name}: {stat_dict["total"]:+}"):
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
            imgui.end_table()

        _, stat_dict["custom_advantage"] = imgui.checkbox("Custom Advantage", stat_dict["custom_advantage"])
        _, stat_dict["custom_disadvantage"] = imgui.checkbox("Custom Disadvantage", stat_dict["custom_disadvantage"])

        imgui.text("Add new bonus:")
        bonus_types = ["Numerical", "Ability", "Proficiency"]
        draw_add_bonus(f"{dict_key}_rollable_bonus", stat_dict["bonuses"], bonus_types, static)

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
                    elif util.isAbilityName(value):
                        imgui.text(
                            f"\t{name}: {value.upper()} ({static.data["abilities"][value]["total"]}{" x" + mult_str if mult_str != "1" else ""})"
                        )
                    elif util.isRepresentInt(value):
                        imgui.text(f"\t{name}: {value}")

                    imgui.table_next_column()
                    if manual:
                        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                        if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                            del stat_dict["bonuses"][idx]
                        imgui.pop_style_color(3)
                imgui.end_table()

        imgui.end_popup()


def draw_proficiency(static: character_sheet_types.MainWindowProtocol) -> None:
    custom_mod, bonuses = static.data["proficiency"]["custom_mod"], static.data["proficiency"]["bonuses"]
    bonus = sum([bonus["value"] for bonus in bonuses])
    static.data["proficiency"]["total"] = custom_mod + bonus

    if imgui.button(f"Proficiency: {static.data["proficiency"]["total"]:+}"):
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
            imgui.end_table()

        if bonuses:
            imgui.text(f"Additional bonus ({bonus}):")
            for item in bonuses:
                name, value = item.values()
                imgui.text(f"\t{name}: {value}")
        imgui.end_popup()


def draw_ac(static: character_sheet_types.MainWindowProtocol) -> None:
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
        elif util.isAbilityName(value):
            if value == "dex":
                if armor and armor["max_dex_bonus"]:
                    dex_bonus = min(trunc(static.data["abilities"]["dex"]["total"] * mult), armor["max_dex_bonus"])
                else:
                    dex_bonus = trunc(static.data["abilities"]["dex"]["total"] * mult)
            else:
                total_bonus_no_dex += trunc(static.data["abilities"][value]["total"] * mult)
        elif util.isRepresentInt(value):
            total_bonus_no_dex += value

    static.data["ac"]["total"] = base + total_bonus_no_dex + dex_bonus + custom_mod

    if imgui.button(f"AC: {static.data["ac"]["total"]}"):
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
            imgui.end_table()

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
        draw_add_bonus("ac_bonus", static.data["ac"]["bonuses"], bonus_types, static)

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
                    elif util.isAbilityName(value):
                        if value == "dex" and armor and armor["max_dex_bonus"]:
                            imgui.text(
                                f"\tBasic rules: DEX ({static.data["abilities"]["dex"]["total"]}{" x" + mult_str if mult_str != "1" else ""}) (max {armor["max_dex_bonus"]})"
                            )
                        else:
                            imgui.text(
                                f"\t{name}: {value.upper()} ({static.data["abilities"][value]["total"]}{" x" + mult_str if mult_str != "1" else ""})"
                            )
                    elif util.isRepresentInt(value):
                        imgui.text(f"\t{name}: {value}")

                    imgui.table_next_column()
                    if manual:
                        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                        if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                            del static.data["ac"]["bonuses"][idx]
                        imgui.pop_style_color(3)

                imgui.end_table()
        imgui.end_popup()


def draw_speed(static: character_sheet_types.MainWindowProtocol) -> None:
    if imgui.begin_table("speed_table", 5, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
        imgui.table_next_row()
        imgui.table_next_column()
        imgui.text("Speed: ")

        imgui.table_next_column()
        draw_static_stat("Walking", static.data["speed"]["walking"], "walking", static)
        imgui.table_next_column()
        draw_static_stat("Climbing", static.data["speed"]["climbing"], "climbing", static)
        imgui.table_next_column()
        draw_static_stat("Swimming", static.data["speed"]["swimming"], "swimming", static)
        imgui.table_next_column()
        draw_static_stat("Flying", static.data["speed"]["flying"], "flying", static)

        imgui.end_table()


def draw_passives(static: character_sheet_types.MainWindowProtocol):
    if imgui.begin_table("passives_table", 6, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
        imgui.table_next_row()

        imgui.table_next_column()
        draw_static_stat("Perception", static.data["passives"]["perception"], "perception", static)

        imgui.table_next_column()
        draw_static_stat("Investigation", static.data["passives"]["investigation"], "investigation", static)

        imgui.table_next_column()
        draw_static_stat("Insight", static.data["passives"]["insight"], "insight", static)

        imgui.end_table()


def draw_static_stat(
    stat_name: str,
    stat_dict: character_sheet_types.StaticStatType,
    dict_key: str,
    static: character_sheet_types.MainWindowProtocol,
) -> None:

    is_speed = util.isSpeedName(dict_key)

    base = stat_dict["base"]

    # Override the stat base
    forced_base_max_idx = -1
    is_forced_base = False
    if stat_dict["forced_bases"]:
        for idx, forced_base in enumerate(stat_dict["forced_bases"]):
            value = 0
            if is_speed and util.isSpeedName(forced_base["value"]):
                value = trunc(static.data["speed"][forced_base["value"]]["total"] * forced_base["multiplier"])
            elif util.isRepresentInt(forced_base["value"]):
                value = forced_base["value"]

            if base < value:
                base = value
                forced_base_max_idx = idx
                is_forced_base = True

    total_bonus = 0
    for bonus in stat_dict["bonuses"]:
        if is_speed and util.isSpeedName(bonus["value"]):
            total_bonus += trunc(static.data["speed"][bonus["value"]]["total"] * bonus["multiplier"])
        elif bonus["value"] == "prof":
            total_bonus += trunc(static.data["proficiency"]["total"] * bonus["multiplier"])
        elif util.isAbilityName(bonus["value"]):
            total_bonus += trunc(static.data["abilities"][bonus["value"]]["total"] * bonus["multiplier"])
        elif util.isRepresentInt(bonus["value"]):
            total_bonus += bonus["value"]

    stat_dict["total"] = base + total_bonus + stat_dict["custom_mod"]

    if imgui.button(f"{stat_name}: {stat_dict["total"]}"):
        imgui.open_popup(f"{dict_key}_popup")

    if imgui.begin_popup(f"{dict_key}_popup"):
        button_step = 1
        if is_speed:
            button_step = 5

        if imgui.begin_table(f"{dict_key}_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Base: ")
            imgui.same_line()
            imgui.table_next_column()
            imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
            _, stat_dict["base"] = imgui.input_int(f"##{dict_key}", stat_dict["base"], button_step)

            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Custom Mod: ")
            imgui.same_line()
            imgui.table_next_column()
            imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
            _, stat_dict["custom_mod"] = imgui.input_int(f"##{dict_key}_custom_mod", stat_dict["custom_mod"], button_step)
            imgui.end_table()

        if is_speed:
            # TODO: if there is an ability bonus to the speed, floor to the closest 5
            # TODO: arbitrarty multipliers?
            # TODO: make numerical modifier for a speed bonus have a step of 5
            bonus_types = ["Numerical", "Speed"]
        else:
            bonus_types = ["Numerical", "Ability", "Proficiency"]
        imgui.text("Add new base override:")
        # TODO: rename the stat_dict["forced_bases"] to stat_dict["base_overrides"]
        draw_add_bonus(f"{dict_key}_base_override", stat_dict["forced_bases"], bonus_types, static)

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
                    if is_speed and util.isSpeedName(forced_base["value"]):
                        speed_value = static.data["speed"][forced_base["value"]]["total"]
                        mult_str = str(trunc(forced_base["multiplier"]) if forced_base["multiplier"] != 0.5 else 0.5)
                        display_value = (
                            f"{forced_base["value"].capitalize()} ({speed_value}{" x" + mult_str if mult_str != "1" else ""})"
                        )
                    elif util.isRepresentInt(forced_base["value"]):
                        display_value = str(forced_base["value"])

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
                imgui.end_table()

        if is_speed:
            # TODO: if there is an ability bonus to the speed, floor to the closest 5
            # TODO: arbitrarty multipliers?
            # TODO: make numerical modifier for a speed bonus have a step of 5
            bonus_types = ["Numerical", "Ability", "Speed"]
        else:
            bonus_types = ["Numerical", "Ability", "Proficiency"]
        imgui.text("Add new bonus:")
        draw_add_bonus(f"{dict_key}_static_bonus", stat_dict["bonuses"], bonus_types, static)

        if stat_dict["bonuses"]:
            table_flags = (  # type: ignore
                imgui.TableFlags_.sizing_fixed_fit  # type: ignore
                | imgui.TableFlags_.no_host_extend_x  # type: ignore
                | imgui.TableFlags_.row_bg.value
            )
            if imgui.begin_table("additional_bonuses", 2, flags=table_flags):  # type: ignore
                imgui.text(f"Additional bonus ({total_bonus}):")
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

                    if is_speed and util.isSpeedName(bonus_value):
                        imgui.text(
                            f"\t{bonus_name}: {bonus_value.capitalize()} ({static.data["speed"][bonus_value]["total"]}{" x" + bonus_mult_str if bonus_mult_str != "1" else ""})"
                        )
                    elif util.isAbilityName(bonus_value):
                        imgui.text(
                            f"\t{bonus_name}: {bonus_value.upper()} ({static.data["abilities"][bonus_value]["total"]}{" x" + bonus_mult_str if bonus_mult_str != "1" else ""})"
                        )
                    elif util.isRepresentInt(bonus_value):
                        imgui.text(f"\t{bonus_name}: {bonus_value}")

                    imgui.table_next_column()
                    if manual:
                        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                        if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{idx}"):
                            del stat_dict["bonuses"][idx]
                        imgui.pop_style_color(3)
                imgui.end_table()
        imgui.end_popup()


def draw_skills(static: character_sheet_types.MainWindowProtocol) -> None:
    for skill in static.data["skills"]:
        draw_rollable_stat(skill["name"].title(), skill, skill["name"], static)


# TODO: create a separate button somewhere for creating new stats/skills/etc
def draw_add_skill_button(static: character_sheet_types.MainWindowProtocol) -> None:
    if imgui.button("Add new skill.."):
        imgui.open_popup("Add new skill")

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
                }
            )

            static.skill_name = ""
            static.skill_ability = 0
        imgui.end_popup()


def draw_tool_proficiencies(static: character_sheet_types.MainWindowProtocol) -> None:
    proficiencies = static.data["tool_proficiencies"]["proficiencies"]
    # Sort so that the order of the types is always the same regargdless of the order
    # proficiencies were added
    proficiencies.sort(key=lambda x: x["type"])

    imgui.same_line()
    if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}"):
        imgui.open_popup("Edit Tool and Language Proficiencies")

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

        imgui.end_table()

    center = imgui.get_main_viewport().get_center()
    imgui.set_next_window_pos(center, imgui.Cond_.appearing.value, ImVec2(0.5, 0.5))

    if imgui.begin_popup_modal("Edit Tool and Language Proficiencies", None, imgui.WindowFlags_.always_auto_resize.value)[0]:
        if imgui.begin_table("add_tool_proficiencies", 4, flags=table_flags):  # type: ignore
            imgui.table_setup_column("Name")
            imgui.table_setup_column("Type")
            imgui.table_setup_column("Source")
            imgui.table_setup_column("Add")
            imgui.table_headers_row()

            imgui.table_next_row()

            imgui.table_next_column()

            imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
            if not hasattr(static, "tool_proficiency_name_missing"):
                static.tool_proficiency_name_missing = False
            if not hasattr(static, "tool_proficiency_name"):
                static.tool_proficiency_name = ""
            _, static.tool_proficiency_name = imgui.input_text("##tool_proficiency_name", static.tool_proficiency_name, 128)
            if static.tool_proficiency_name != "":
                static.tool_proficiency_name_missing = False
            if static.tool_proficiency_name_missing:
                imgui.push_style_color(imgui.Col_.text.value, DISADVANTAGE_ACTIVE_COLOR)
                imgui.text("Enter the name")
                imgui.pop_style_color()

            imgui.table_next_column()
            if not hasattr(static, "tool_proficiency_type"):
                static.tool_proficiency_type = ""
            imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
            _, static.tool_proficiency_type = imgui.input_text_with_hint(
                "##tool_proficiency_type", "Other", static.tool_proficiency_type, 128
            )

            imgui.table_next_column()
            if not hasattr(static, "tool_proficiency_source"):
                static.tool_proficiency_source = ""
            imgui.push_item_width(SHORT_STRING_INPUT_WINDTH)
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
            imgui.end_table()

        if imgui.begin_table("edit_tool_proficiencies", 4, flags=table_flags | imgui.TableFlags_.sortable):  # type: ignore
            imgui.table_setup_column("Name")
            imgui.table_setup_column("Type")
            imgui.table_setup_column("Source")
            imgui.table_setup_column("Delete")
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

            imgui.end_table()

        if imgui.button("Close", ImVec2(120, 0)):
            imgui.close_current_popup()
        imgui.end_popup()


# Proficiency, initiative, walking speed, armor class
def draw_misc(static: character_sheet_types.MainWindowProtocol) -> None:
    if imgui.begin_table("misc_table", 3, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
        imgui.table_next_row()

        # Proficiency
        imgui.table_next_column()
        draw_proficiency(static)

        # Initiative
        imgui.table_next_column()
        draw_rollable_stat("Initiative", static.data["initiative"], "initiative", static)

        # AC
        imgui.table_next_column()
        draw_ac(static)

        imgui.end_table()

    draw_speed(static)


# immapp.run(
#     gui_function=main_window,
#     window_title="Just Another D&D Character Manager",
#     window_restore_previous_geometry=True,
# )


def load_fonts(font_holder: character_sheet_types.FontHolder) -> None:
    hello_imgui.get_runner_params().callbacks.default_icon_font = hello_imgui.DefaultIconFont.font_awesome6
    hello_imgui.imgui_default_settings.load_default_font_with_font_awesome_icons()

    font_loading_params_bold_icons = hello_imgui.FontLoadingParams()
    font_loading_params_bold_icons.use_full_glyph_range = True
    font_loading_params_bold_icons.merge_font_awesome = True
    font_holder.bold_font = hello_imgui.load_font("/ft-bold.otf", 14, font_loading_params_bold_icons)

    font_loading_params_regular_icons = hello_imgui.FontLoadingParams()
    font_loading_params_regular_icons.use_full_glyph_range = True
    font_loading_params_regular_icons.merge_font_awesome = True
    font_holder.regular_font = hello_imgui.load_font("/fa-regular.otf", 14, font_loading_params_regular_icons)


def make_params() -> hello_imgui.RunnerParams:
    font_holder = character_sheet_types.FontHolder()

    # Hello ImGui params (they hold the settings as well as the Gui callbacks)
    runner_params = hello_imgui.RunnerParams()
    # Window size and title
    runner_params.app_window_params.window_title = "Just Another D&D Character Manager"
    runner_params.app_window_params.window_geometry.size = (1400, 950)

    # Menu bar
    runner_params.imgui_window_params.show_menu_bar = True
    runner_params.callbacks.show_gui = lambda: main_window(font_holder)
    runner_params.callbacks.load_additional_fonts = lambda: load_fonts(font_holder)

    return runner_params


runner_params = make_params()
immapp.run(runner_params=runner_params)
