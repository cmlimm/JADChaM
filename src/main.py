from imgui_bundle import hello_imgui  # type: ignore
from imgui_bundle import icons_fontawesome_6, imgui, immapp  # type: ignore
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

import character_sheet_types
from common_elements import draw_rollable_stat_value
from left_elements import (
    draw_abilities,
    draw_ac_value,
    draw_passives,
    draw_proficiency_value,
    draw_saves,
    draw_senses,
    draw_skills,
    draw_speed,
    draw_tool_proficiencies,
)
from toolbar import draw_file_button
from util import end_table_nested, open_file, save_file

# TODO[bug]: when adding a new tool proficiency, do not enter the name
#      then close the popup and open the popup again
#      a warning about the name is still there -- it should not be


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

        draw_abilities(static)

        if imgui.begin_table("saves_prof_init_ac", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.align_text_to_frame_padding()
            imgui.text("Saving Throws")
            imgui.table_next_column()

            imgui.table_next_row()
            imgui.table_next_column()
            draw_saves(static)

            imgui.table_next_column()
            table_flags = (  # type: ignore
                imgui.TableFlags_.sizing_fixed_fit  # type: ignore
                | imgui.TableFlags_.no_host_extend_x  # type: ignore
                | imgui.TableFlags_.borders.value
                | imgui.TableFlags_.row_bg.value
            )
            if imgui.begin_table("prof_init_ac", 2, flags=table_flags):  # type: ignore
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.align_text_to_frame_padding()
                imgui.text("Proficiency")
                imgui.table_next_column()
                draw_proficiency_value(static)

                imgui.table_next_row()
                imgui.table_next_column()
                imgui.align_text_to_frame_padding()
                imgui.text("Initiative")
                imgui.table_next_column()
                draw_rollable_stat_value("Initiative", static.data["initiative"], "initiative", static)

                imgui.table_next_row()
                imgui.table_next_column()
                imgui.align_text_to_frame_padding()
                imgui.text("Armor Class")
                imgui.table_next_column()
                draw_ac_value(static)

                end_table_nested()
            end_table_nested()

        if imgui.begin_table("speed_passives_skills", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
            imgui.table_next_row()
            imgui.table_next_column()
            if imgui.begin_table("speed_passives_senses", 1, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.align_text_to_frame_padding()
                imgui.text("Speed")
                imgui.same_line()
                if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_speed"):
                    imgui.open_popup("Edit Speed")
                imgui.table_next_row()
                imgui.table_next_column()
                draw_speed(static)

                imgui.table_next_row()
                imgui.table_next_column()
                imgui.align_text_to_frame_padding()
                imgui.text("Passive Skills")
                imgui.same_line()
                if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_passive_skills"):
                    imgui.open_popup("Edit Passive Skills")
                imgui.table_next_row()
                imgui.table_next_column()
                draw_passives(static)

                imgui.table_next_row()
                imgui.table_next_column()
                imgui.align_text_to_frame_padding()
                imgui.text("Senses")
                imgui.same_line()
                if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_senses"):
                    imgui.open_popup("Edit Senses")
                imgui.table_next_row()
                imgui.table_next_column()
                draw_senses(static)

                imgui.table_next_row()
                imgui.table_next_column()
                imgui.align_text_to_frame_padding()
                imgui.text("Proficiencies & Training")
                imgui.same_line()
                if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}"):
                    imgui.open_popup("Edit Tool and Language Proficiencies")
                imgui.table_next_row()
                imgui.table_next_column()
                draw_tool_proficiencies(static)

                end_table_nested()

            imgui.table_next_column()
            if imgui.begin_table("skills_ext", 1, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.align_text_to_frame_padding()
                imgui.text("Skills")
                imgui.same_line()
                if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_skills"):
                    imgui.open_popup("Edit Skills")
                imgui.table_next_row()
                imgui.table_next_column()
                draw_skills(static)

                end_table_nested()

            end_table_nested()
    else:
        draw_file_button(static)

    if not hasattr(static, "theme"):
        hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.imgui_colors_dark)
        static.theme = hello_imgui.ImGuiTheme_.imgui_colors_dark.name


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
    # runner_params.app_window_params.window_geometry.size = (1400, 950)
    runner_params.app_window_params.restore_previous_geometry = True

    # Menu bar
    runner_params.imgui_window_params.show_menu_bar = True
    runner_params.callbacks.show_gui = lambda: main_window(font_holder)
    runner_params.callbacks.load_additional_fonts = lambda: load_fonts(font_holder)

    return runner_params


runner_params = make_params()
immapp.run(runner_params=runner_params)
