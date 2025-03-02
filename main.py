import json

from imgui_bundle import hello_imgui, imgui, immapp  # type: ignore
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

import character_sheet_types
import util

# TODO: move to const.py or something
TWO_DIGIT_BUTTONS_INPUT_WIDTH = 75
TWO_DIGIT_INPUT_WIDTH = 25
ADVANTAGE_COLOR = imgui.ImColor.hsv(0.3, 0.6, 0.6).value
ADVANTAGE_HOVER_COLOR = imgui.ImColor.hsv(0.3, 0.7, 0.7).value
ADVANTAGE_ACTIVE_COLOR = imgui.ImColor.hsv(0.3, 0.8, 0.8).value
DISADVANTAGE_COLOR = imgui.ImColor.hsv(0, 0.6, 0.6).value
DISADVANTAGE_HOVER_COLOR = imgui.ImColor.hsv(0, 0.7, 0.7).value
DISADVANTAGE_ACTIVE_COLOR = imgui.ImColor.hsv(0, 0.8, 0.8).value
FORCED_OVERRIDE_COLOR = imgui.ImColor.hsv(0.15, 0.8, 0.8).value


@character_sheet_types.main_window_decorator
def main_window() -> None:
    static = main_window
    draw_file_button(static)

    # Only draw the main interface if the character file is loaded
    if hasattr(static, "character_file"):
        draw_abilities(static)
        draw_misc(static)

        # Clear file and dump current data
        # TODO: move to util.py or something
        static.character_file.seek(0)
        static.character_file.truncate(0)
        json.dump(static.data, static.character_file, indent=4)

    if not hasattr(static, "theme"):
        hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.imgui_colors_dark)
        static.theme = hello_imgui.ImGuiTheme_.imgui_colors_dark.name


def draw_file_button(static: character_sheet_types.MainWindowProtocol) -> None:
    if not hasattr(static, "open_file_dialog"):
        static.open_file_dialog = None
    if imgui.button("Open file"):
        static.open_file_dialog = pfd.open_file("Select file")
    if static.open_file_dialog is not None and static.open_file_dialog.ready():
        result = static.open_file_dialog.result()
        if result:
            if hasattr(static, "character_file"):
                static.character_file.close()

            static.character_file = open(result[0], "r+")
            static.data = json.load(static.character_file)

        static.open_file_dialog = None


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

        if base_score_bonuses:
            imgui.text(f"Base Score bonus ({base_score_bonus} -> {base_score_bonus // 2}):")
            for bonus in base_score_bonuses:
                base_score_bonus_name, base_score_bonus_value = bonus["name"], bonus["value"]
                imgui.text(f"\t{base_score_bonus_name}: {base_score_bonus_value} -> {base_score_bonus_value // 2}")

        if mod_bonuses:
            imgui.text(f"Additional bonus ({mod_bonus}):")
            for bonus in mod_bonuses:
                mod_bonus_name, mod_bonus_value = bonus["name"], bonus["value"]
                imgui.text(f"\t{mod_bonus_name}: {mod_bonus_value}")

        if forced_total_max_idx != -1:
            if is_forced_total:
                imgui.text_colored(FORCED_OVERRIDE_COLOR, f"Forced total ({forced_total_max_value}):")
            else:
                imgui.text_disabled(f"Forced total (Not applied):")

            for idx, total in enumerate(forced_total_base_scores):
                total_name, total_value = total["name"], total["value"]

                if (idx == forced_total_max_idx) and is_forced_total:
                    imgui.text(f"\t{total_name}: {total_value}")
                else:
                    imgui.text_disabled(f"\t{total_name}: {total_value}")

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


def draw_rollable_stat(stat_name: str, dict_key: str, static: character_sheet_types.MainWindowProtocol) -> None:
    custom_mod, bonuses = static.data["skills"][dict_key]["custom_mod"], static.data["skills"][dict_key]["bonuses"]

    total_bonus = 0
    advantage = False
    disadvantage = False
    for bonus in bonuses:
        name, value = bonus["name"], bonus["value"]

        # Advantages (disadvantages) don't stack, so we can just reassing the value
        # instead of calculating a sum or something
        if value == "adv":
            advantage = True
        elif value == "disadv":
            disadvantage = True
        elif value == "prof":
            total_bonus += static.data["proficiency"]["total"]
        elif util.isAbilityName(value):
            total_bonus += static.data["abilities"][value]["total"]
        elif util.isRepresentInt(value):
            total_bonus += value

    custom_proficiency = 0
    if static.data["skills"][dict_key].get("custom_proficiency"):
        custom_proficiency = static.data["proficiency"]["total"]

    static.data["skills"][dict_key]["total"] = custom_mod + custom_proficiency + total_bonus

    advantage = advantage or static.data["skills"][dict_key]["custom_advantage"]
    disadvantage = disadvantage or static.data["skills"][dict_key]["custom_disadvantage"]

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

    if imgui.button(f"{stat_name}: {static.data["skills"][dict_key]["total"]:+}"):
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
            _, static.data["skills"][dict_key]["custom_mod"] = imgui.input_int(
                f"##{dict_key}_custom_mod", static.data["skills"][dict_key]["custom_mod"], 1
            )
            imgui.end_table()

        _, static.data["skills"][dict_key]["custom_advantage"] = imgui.checkbox(
            "Custom Advantage", static.data["skills"][dict_key]["custom_advantage"]
        )
        _, static.data["skills"][dict_key]["custom_disadvantage"] = imgui.checkbox(
            "Custom Disadvantage", static.data["skills"][dict_key]["custom_disadvantage"]
        )
        _, static.data["skills"][dict_key]["custom_proficiency"] = imgui.checkbox(
            "Custom Proficiency", static.data["skills"][dict_key]["custom_proficiency"]
        )

        if bonuses:
            imgui.text(f"Additional bonus ({total_bonus}):")
            for bonus in bonuses:
                name, value = bonus["name"], bonus["value"]

                if value == "adv":
                    imgui.text_colored(ADVANTAGE_ACTIVE_COLOR, f"\t{name}: Advantage")
                elif value == "disadv":
                    imgui.text_colored(DISADVANTAGE_ACTIVE_COLOR, f"\t{name}: Disadvantage")
                if value == "prof":
                    imgui.text(f"\t{name}: {value} ({static.data["proficiency"]["total"]})")
                elif util.isAbilityName(value):
                    imgui.text(f"\t{name}: {value.upper()} ({static.data["abilities"][value]["total"]})")
                elif util.isRepresentInt(value):
                    imgui.text(f"\t{name}: {value}")
        imgui.end_popup()


def draw_proficiency(static: character_sheet_types.MainWindowProtocol) -> None:
    custom_mod, bonuses = static.data["proficiency"]["custom_mod"], static.data["proficiency"]["bonuses"]
    bonus = sum([bonus["value"] for bonus in bonuses])
    static.data["proficiency"]["total"] = custom_mod + bonus

    if imgui.button(f"PROF: {static.data["proficiency"]["total"]:+}"):
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
    dex_bonus = static.data["abilities"]["dex"]["total"]
    for bonus in bonuses:
        name, value = bonus["name"], bonus["value"]

        if value == "prof":
            total_bonus_no_dex += static.data["proficiency"]["total"]
        elif util.isAbilityName(value):
            if value == "dex":
                if armor and armor["max_dex_bonus"]:
                    dex_bonus = min(static.data["abilities"]["dex"]["total"], armor["max_dex_bonus"])
                else:
                    dex_bonus = static.data["abilities"]["dex"]["total"]
            else:
                total_bonus_no_dex += static.data["abilities"][value]["total"]
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

        if bonuses:
            imgui.text(f"Additional bonus ({total_bonus_no_dex + dex_bonus}):")
            for bonus in bonuses:
                name, value = bonus["name"], bonus["value"]

                if value == "prof":
                    imgui.text(f"\t{name}: {value} ({static.data["proficiency"]["total"]})")
                elif util.isAbilityName(value):
                    if value == "dex" and armor and armor["max_dex_bonus"]:
                        imgui.text(f"\tBasic rules: DEX (max {armor["max_dex_bonus"]}) -> {dex_bonus}")
                    else:
                        imgui.text(f"\t{name}: {value.upper()} ({static.data["abilities"][value]["total"]})")
                elif util.isRepresentInt(value):
                    imgui.text(f"\t{name}: {value}")
        imgui.end_popup()


def draw_speed_button(speed_name: str, dict_key: str, static: character_sheet_types.MainWindowProtocol) -> None:
    base = static.data["speed"][dict_key]["base"]
    forced_bases = static.data["speed"][dict_key]["forced_bases"]
    custom_mod = static.data["speed"][dict_key]["custom_mod"]
    bonuses = static.data["speed"][dict_key]["bonuses"]

    # Override the speed base
    forced_base_max_idx = -1
    is_forced_base = False
    if forced_bases:
        for idx, forced_base in enumerate(forced_bases):
            value = 0
            if util.isSpeedName(forced_base["value"]):
                value = static.data["speed"][forced_base["value"]]["total"]
            elif util.isRepresentInt(forced_base["value"]):
                value = forced_base["value"]

            if base < value:
                base = value
                forced_base_max_idx = idx
                is_forced_base = True

    total_bonus = 0
    for bonus in bonuses:
        if util.isSpeedName(bonus["value"]):
            total_bonus += static.data["speed"][bonus["value"]]["total"]
        elif util.isRepresentInt(bonus["value"]):
            total_bonus += bonus["value"]

    static.data["speed"][dict_key]["total"] = base + total_bonus + custom_mod

    if imgui.button(f"{speed_name}: {static.data["speed"][dict_key]["total"]}"):
        imgui.open_popup(f"{dict_key}_popup")

    if imgui.begin_popup(f"{dict_key}_popup"):
        if imgui.begin_table(f"{dict_key}_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Base: ")
            imgui.same_line()
            imgui.table_next_column()
            imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
            _, static.data["speed"][dict_key]["base"] = imgui.input_int(
                f"##{dict_key}", static.data["speed"][dict_key]["base"], 1
            )

            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Custom Mod: ")
            imgui.same_line()
            imgui.table_next_column()
            imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
            _, static.data["speed"][dict_key]["custom_mod"] = imgui.input_int(
                f"##{dict_key}_custom_mod", static.data["speed"][dict_key]["custom_mod"], 1
            )
            imgui.end_table()

        if forced_bases:
            if is_forced_base:
                imgui.text_colored(FORCED_OVERRIDE_COLOR, f"Forced base ({base}):")
            else:
                imgui.text_disabled(f"Forced total (Not applied):")

            for idx, forced_base in enumerate(static.data["speed"][dict_key]["forced_bases"]):
                display_value = ""
                if util.isSpeedName(forced_base["value"]):
                    speed_value = static.data["speed"][forced_base["value"]]["total"]
                    display_value = f"{dict_key} ({speed_value})"
                elif util.isRepresentInt(forced_base["value"]):
                    display_value = str(forced_base["value"])

                if (idx == forced_base_max_idx) and is_forced_base:
                    imgui.text(f"\t{forced_base["name"]}: {display_value}")
                else:
                    imgui.text_disabled(f"\t{forced_base["name"]}: {display_value}")

        if bonuses:
            imgui.text(f"Additional bonus ({total_bonus}):")
            for bonus in bonuses:
                if util.isSpeedName(bonus["value"]):
                    imgui.text(f"\t{bonus["name"]}: {bonus["value"].capitalize()} ({static.data["speed"][dict_key]["total"]})")
                elif util.isRepresentInt(bonus["value"]):
                    imgui.text(f"\t{bonus["name"]}: {bonus["value"]}")

        imgui.end_popup()


def draw_speed(static: character_sheet_types.MainWindowProtocol) -> None:
    if imgui.begin_table("speed_table", 5, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
        imgui.table_next_row()
        imgui.table_next_column()
        imgui.text("Speed: ")

        imgui.table_next_column()
        draw_speed_button("Walking", "walking", static)
        imgui.table_next_column()
        draw_speed_button("Climbing", "climbing", static)
        imgui.table_next_column()
        draw_speed_button("Swimming", "swimming", static)
        imgui.table_next_column()
        draw_speed_button("Flying", "flying", static)

        imgui.end_table()


# Proficiency, initiative, walking speed, armor class
def draw_misc(static: character_sheet_types.MainWindowProtocol) -> None:
    if imgui.begin_table("misc_table", 3, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
        imgui.table_next_row()

        # Proficiency
        imgui.table_next_column()
        draw_proficiency(static)

        # Initiative
        imgui.table_next_column()
        draw_rollable_stat("INIT", "initiative", static)

        # AC
        imgui.table_next_column()
        draw_ac(static)

        imgui.end_table()

    draw_speed(static)


immapp.run(
    gui_function=main_window,
    window_title="Just Another D&D Character Manager",
    window_restore_previous_geometry=True,
)
