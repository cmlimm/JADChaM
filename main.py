import json

from imgui_bundle import hello_imgui, imgui, immapp  # type: ignore
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

import character_sheet_types
import util

TWO_DIGIT_BUTTONS_INPUT_WIDTH = 75
TWO_DIGIT_INPUT_WIDTH = 25


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
            base = ability["base_score"]
            manual_mod = ability["manual_mod"]
            base_score_bonuses = ability["base_score_bonuses"]
            mod_bonuses = ability["mod_bonuses"]

            # Buttons with final abilities' modifiers
            imgui.table_next_column()
            base_score_bonus = sum([bonus["value"] for bonus in base_score_bonuses])
            mod_bonus = sum([bonus["value"] for bonus in mod_bonuses])
            static.data["abilities"][name]["total"] = (base + base_score_bonus - 10) // 2 + manual_mod + mod_bonus
            if imgui.button(f"{name.upper()}: {static.data["abilities"][name]["total"]:+}"):
                imgui.open_popup(f"{name}_popup")

            # Popup windows where you can
            #   - change the basic ability score
            #   - add a manual modifier
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
                    _, static.data["abilities"][name]["base_score"] = imgui.input_int(f"##{name}", base, 1)

                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text("Manual Mod: ")
                    imgui.same_line()
                    imgui.table_next_column()
                    imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                    _, static.data["abilities"][name]["manual_mod"] = imgui.input_int(f"##{name}_manual_mod", manual_mod, 1)
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
        manual_mod, bonuses = static.data["proficiency"]["manual_mod"], static.data["proficiency"]["bonuses"]
        bonus = sum([bonus["value"] for bonus in bonuses])
        static.data["proficiency"]["total"] = manual_mod + bonus

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
                _, static.data["proficiency"]["manual_mod"] = imgui.input_int(f"##prof", manual_mod, 1)
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
        manual_mod, bonuses = static.data["initiative"]["manual_mod"], static.data["initiative"]["bonuses"]

        # TODO: move to a separate function, this will be useful later for skills
        total_bonus = 0
        for init_bonus in bonuses:
            name, value = init_bonus["name"], init_bonus["value"]
            if value == "prof":
                total_bonus += static.data["proficiency"]["total"]
            elif util.isAbilityName(value):
                total_bonus += static.data["abilities"][value]["total"]
            elif util.isRepresentInt(value):
                total_bonus += value

        static.data["initiative"]["total"] = manual_mod + total_bonus

        if imgui.button(f"INIT: {static.data["initiative"]["total"]:+}"):
            imgui.open_popup(f"init_popup")

        # TODO: create a function for these popups
        if imgui.begin_popup(f"init_popup"):
            if imgui.begin_table("init_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.text("Manual Mod: ")
                imgui.same_line()
                imgui.table_next_column()
                imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                _, static.data["initiative"]["manual_mod"] = imgui.input_int(f"##manual_mod", manual_mod, 1)
                imgui.end_table()

            # TODO: move to a separate function
            if bonuses:
                imgui.text(f"Additional bonus ({total_bonus}):")
                for init_bonus in bonuses:
                    name, value = init_bonus["name"], init_bonus["value"]

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
