from imgui_bundle import hello_imgui  # type: ignore
from imgui_bundle import icons_fontawesome_6, imgui, immapp  # type: ignore

from base_sheet import (
    draw_abilities,
    draw_armor_class_button,
    draw_class,
    draw_hp,
    draw_image,
    draw_initiative_button,
    draw_name,
    draw_passives,
    draw_proficiency_button,
    draw_saves,
    draw_senses,
    draw_skills,
    draw_speed,
    draw_training,
)
from cs_types import FontHolder, MainWindowProtocol, main_window_decorator
from settings import INVISIBLE_TABLE_FLAGS, STRIPED_TABLE_FLAGS
from util_gui import (
    draw_open_file_button,
    draw_text_cell,
    draw_toolbar,
    end_table_nested,
)

# TODO[BUG]: do not allow cyclical references for bonuses (e.g. Walking has a Flying bonus, Flying has a Walking Bonus) 

@main_window_decorator
def main_window(font_holder: FontHolder) -> None:
    static = main_window
    static.regular_font = font_holder.regular_font
    static.bold_font = font_holder.bold_font
    
    if not hasattr(static, "states"):
        static.states = {
            "hp_dice_idx": 0,
            "new_item_name": "",
            "hp_add": "",
            "new_bonuses": {},
            "new_training": {
                "name": "",
                "type": "",
                "source": "",
                "manual": True
            }
        }

    if not hasattr(static, "is_character_loaded"):
        static.is_character_loaded = False

    if not static.is_character_loaded:
        draw_main_menu(static)
    else:
        draw_character_sheet(static)

    if not hasattr(static, "theme"):
        hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.imgui_colors_dark)
        static.theme = hello_imgui.ImGuiTheme_.imgui_colors_dark.name


def draw_main_menu(static: MainWindowProtocol) -> None:
    draw_open_file_button(static)


def draw_character_sheet(static: MainWindowProtocol) -> None:
    draw_toolbar(static)

    table_id = "name_image_class"
    if imgui.begin_table(table_id, 2, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
        imgui.table_next_row(); imgui.table_next_column()
        draw_name(static)

        imgui.table_next_row(); imgui.table_next_column()
        draw_image(static)

        imgui.table_next_column()
        draw_class(static)

        end_table_nested()

    imgui.spacing()
    draw_hp(static)

    imgui.spacing()

    imgui.align_text_to_frame_padding()
    imgui.text("Abilities"); imgui.same_line()
    if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_abilities"):
        imgui.open_popup("Edit Abilities")
    draw_abilities(static)

    table_id = "saves_prof_init_ac"
    if imgui.begin_table(table_id, 2, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
        draw_text_cell("Saving Throws"); imgui.same_line()
        if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_saves"):
            imgui.open_popup("Edit Saves") 
        imgui.table_next_column()

        imgui.table_next_row(); imgui.table_next_column()
        draw_saves(static); imgui.table_next_column()
        
        table_id = "prof_init_ac"
        if imgui.begin_table("prof_init_ac", 2, flags=STRIPED_TABLE_FLAGS):  # type: ignore
            draw_text_cell("Proficiency"); imgui.table_next_column()
            draw_proficiency_button(static)
            
            draw_text_cell("Initiative"); imgui.table_next_column()
            draw_initiative_button(static)

            draw_text_cell("Armor Class"); imgui.table_next_column()
            draw_armor_class_button(static)

            end_table_nested()
        end_table_nested()

    table_id = "speed_passives_proficiencies_skills"
    if imgui.begin_table(table_id, 2, flags=INVISIBLE_TABLE_FLAGS):  # type: ignore
        imgui.table_next_row()
        imgui.table_next_column()
        table_id = "speed_passives_senses"
        if imgui.begin_table(table_id, 1, flags=INVISIBLE_TABLE_FLAGS):  # type: ignore
            imgui.align_text_to_frame_padding()
            draw_text_cell("Speed"); imgui.same_line()
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_speed"):
                imgui.open_popup("Edit Speed")
            imgui.table_next_row(); imgui.table_next_column()
            draw_speed(static)

            imgui.align_text_to_frame_padding()
            draw_text_cell("Passive Skills"); imgui.same_line()
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_passive_skills"):
                imgui.open_popup("Edit Passive Skills")
            imgui.table_next_row(); imgui.table_next_column()
            draw_passives(static)

            imgui.align_text_to_frame_padding()
            draw_text_cell("Senses"); imgui.same_line()
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_senses"):
                imgui.open_popup("Edit Senses")
            imgui.table_next_row(); imgui.table_next_column()
            draw_senses(static)

            imgui.align_text_to_frame_padding()
            draw_text_cell("Proficiencies & Training"); imgui.same_line()
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}"):
                imgui.open_popup("Edit Tool and Language Proficiencies")
            imgui.table_next_row(); imgui.table_next_column()
            draw_training(static)

            end_table_nested()

        imgui.table_next_column()
        table_id = "skills"
        if imgui.begin_table(table_id, 1, flags=INVISIBLE_TABLE_FLAGS):  # type: ignore
            imgui.align_text_to_frame_padding()
            draw_text_cell("Skills"); imgui.same_line()
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_skills"):
                imgui.open_popup("Edit Skills")
            imgui.table_next_row(); imgui.table_next_column()
            draw_skills(static)

            end_table_nested()

        end_table_nested()

def load_fonts(font_holder: FontHolder) -> None:
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
    font_holder = FontHolder()

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
