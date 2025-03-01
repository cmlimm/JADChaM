import json

from imgui_bundle import hello_imgui, imgui, immapp  # type: ignore
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

import character_sheet_types
import util

TWO_DIGIT_BUTTONS_INPUT_WIDTH = 75
TWO_DIGIT_INPUT_WIDTH = 25
ADVANTAGE_COLOR = imgui.ImColor.hsv(0.3, 0.6, 0.6).value
ADVANTAGE_HOVER_COLOR = imgui.ImColor.hsv(0.3, 0.7, 0.7).value
ADVANTAGE_ACTIVE_COLOR = imgui.ImColor.hsv(0.3, 0.8, 0.8).value
DISADVANTAGE_COLOR = imgui.ImColor.hsv(0, 0.6, 0.6).value
DISADVANTAGE_HOVER_COLOR = imgui.ImColor.hsv(0, 0.7, 0.7).value
DISADVANTAGE_ACTIVE_COLOR = imgui.ImColor.hsv(0, 0.8, 0.8).value


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


def draw_abilities(static: character_sheet_types.MainWindowProtocol) -> None:
    if imgui.begin_table("abilities_table", 10, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
        imgui.table_next_row()
        for name, ability in static.data["abilities"].items():
            base_score = ability["base_score"]
            custom_mod = ability["custom_mod"]
            base_score_bonuses = ability["base_score_bonuses"]
            mod_bonuses = ability["mod_bonuses"]

            # Buttons with final abilities' modifiers
            imgui.table_next_column()
            base_score_bonus = sum([bonus["value"] for bonus in base_score_bonuses])
            mod_bonus = sum([bonus["value"] for bonus in mod_bonuses])
            static.data["abilities"][name]["total"] = (base_score + base_score_bonus - 10) // 2 + custom_mod + mod_bonus
            if imgui.button(f"{name.upper()}: {static.data["abilities"][name]["total"]:+}"):
                imgui.open_popup(f"{name}_popup")

            # Popup windows where you can
            #   - change the basic ability score
            #   - add a custom modifier
            #   - see what gives you additional bonuses

            # TODO: create a function for these popups
            if imgui.begin_popup(f"{name}_popup"):
                if imgui.begin_table("abilities_base_and_mod_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text("Base Score: ")
                    imgui.same_line()
                    imgui.table_next_column()
                    imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                    _, static.data["abilities"][name]["base_score"] = imgui.input_int(
                        f"##{name}", static.data["abilities"][name]["base_score"], 1
                    )

                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text("Custom Mod: ")
                    imgui.same_line()
                    imgui.table_next_column()
                    imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                    _, static.data["abilities"][name]["custom_mod"] = imgui.input_int(
                        f"##{name}_custom_mod", static.data["abilities"][name]["custom_mod"], 1
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

                imgui.end_popup()
        imgui.end_table()


# Proficiency, initiative, walking speed, armor class
def draw_misc(static: character_sheet_types.MainWindowProtocol) -> None:
    if imgui.begin_table("misc_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
        imgui.table_next_row()

        # Proficiency
        imgui.table_next_column()
        custom_mod, bonuses = static.data["proficiency"]["custom_mod"], static.data["proficiency"]["bonuses"]
        bonus = sum([bonus["value"] for bonus in bonuses])
        static.data["proficiency"]["total"] = custom_mod + bonus

        if imgui.button(f"PROF: {static.data["proficiency"]["total"]:+}"):
            imgui.open_popup(f"prof_popup")

        # TODO: create a function for these popups
        if imgui.begin_popup(f"prof_popup"):
            if imgui.begin_table("prof_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.text("Base: ")
                imgui.same_line()
                imgui.table_next_column()
                imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                _, static.data["proficiency"]["custom_mod"] = imgui.input_int(
                    f"##prof", static.data["proficiency"]["custom_mod"], 1
                )
                imgui.end_table()

            # TODO: move to a separate function
            if bonuses:
                imgui.text(f"Additional bonus ({bonus}):")
                for item in bonuses:
                    name, value = item.values()
                    imgui.text(f"\t{name}: {value}")
            imgui.end_popup()

        # Initiative
        imgui.table_next_column()
        custom_mod, bonuses = static.data["initiative"]["custom_mod"], static.data["initiative"]["bonuses"]

        # TODO: move to a separate function, this will be useful later for skills
        total_bonus = 0
        advantage = False
        disadvantage = False
        for init_bonus in bonuses:
            name, value = init_bonus["name"], init_bonus["value"]

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

        static.data["initiative"]["total"] = custom_mod + total_bonus

        advantage = advantage or static.data["initiative"]["custom_advantage"]
        disadvantage = disadvantage or static.data["initiative"]["custom_disadvantage"]

        init_button_color_applied = False
        if not (advantage and disadvantage):
            if advantage:
                imgui.push_style_color(imgui.Col_.button.value, ADVANTAGE_COLOR)
                imgui.push_style_color(imgui.Col_.button_hovered.value, ADVANTAGE_HOVER_COLOR)
                imgui.push_style_color(imgui.Col_.button_active.value, ADVANTAGE_ACTIVE_COLOR)
            elif disadvantage:
                imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
            init_button_color_applied = True

        if imgui.button(f"INIT: {static.data["initiative"]["total"]:+}"):
            imgui.open_popup(f"init_popup")
        if init_button_color_applied:
            imgui.pop_style_color(3)

        # TODO: create a function for these popups
        if imgui.begin_popup(f"init_popup"):
            if imgui.begin_table("init_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.text("Custom Mod: ")
                imgui.same_line()
                imgui.table_next_column()
                imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                _, static.data["initiative"]["custom_mod"] = imgui.input_int(
                    f"##custom_mod", static.data["initiative"]["custom_mod"], 1
                )
                imgui.end_table()

            _, static.data["initiative"]["custom_advantage"] = imgui.checkbox(
                "Custom Advantage", static.data["initiative"]["custom_advantage"]
            )
            _, static.data["initiative"]["custom_disadvantage"] = imgui.checkbox(
                "Custom Disadvantage", static.data["initiative"]["custom_disadvantage"]
            )

            # TODO: move to a separate function
            if bonuses:
                imgui.text(f"Additional bonus ({total_bonus}):")
                for init_bonus in bonuses:
                    name, value = init_bonus["name"], init_bonus["value"]

                    if value == "adv":
                        imgui.text_colored(ADVANTAGE_ACTIVE_COLOR, f"\t{name}: Advantage")
                    elif value == "disadv":
                        imgui.text_colored(DISADVANTAGE_ACTIVE_COLOR, f"\t{name}: Disadvantage")
                    if value == "prof":
                        imgui.text(f"\t{name}: {value} ({static.data["proficiency"]["total"]})")
                    elif util.isAbilityName(value):
                        imgui.text(f"\t{name}: {value} ({static.data["abilities"][value]["total"]})")
                    elif util.isRepresentInt(value):
                        imgui.text(f"\t{name}: {value}")
            imgui.end_popup()
        imgui.end_table()


immapp.run(
    gui_function=main_window,
    window_title="Just Another D&D Character Manager",
    window_restore_previous_geometry=True,
)
