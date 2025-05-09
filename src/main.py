from imgui_bundle import hello_imgui  # type: ignore
from imgui_bundle import imgui_md  # type: ignore
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
from cs_types import MainWindowProtocol
from features import draw_features
from settings import INVISIBLE_TABLE_FLAGS, STRIPED_TABLE_FLAGS  # type: ignore
from util_gui import draw_open_file_button, draw_toolbar
from util_imgui import draw_text_cell, end_table_nested

# TODO[BUG]: do not allow cyclical references for bonuses (e.g. Walking has a Flying bonus, Flying has a Walking Bonus)
# TODO[BUG]: fix hotkeys

# TODO: resistances & effects

# TODO: on process character add all feature bonuses (in case the user added them manually to a JSON file)

# TODO: add `min=` to the text parsing

def post_init(state: MainWindowProtocol) -> None:
    state.states = {
        "hp_dice_idx": 0,
        "ability_bonus_type_idx": 0,
        "static_bonus_type_idx": 0,
        "counter_display_type_idx": 0,
        "hp_add": "",
        "new_item_name": "",
        "new_bonuses": {},
        "new_training": {
            "name": "",
            "type": "",
            "source": "",
            "manual": True
        },
        "target_name": "",
        "target_ref": "",
        "counter_edit": {
            "name": "",
            "parent": "",
            "current": 0,
            "max": 0,
            "display_type": "+- Buttons",
            "bonuses": [],
            "min": 0,
            "manual": True
        },
        "new_window_name": "",
        "feat_name": "",
        "new_tag": ""
    }

    state.is_character_loaded = False

    theme = hello_imgui.ImGuiTweakedTheme()
    theme.theme = hello_imgui.ImGuiTheme_.imgui_colors_dark
    hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.imgui_colors_dark)
    state.theme = hello_imgui.ImGuiTheme_.imgui_colors_dark.name


def draw_name_class_image_hp(static: MainWindowProtocol) -> None:
    if static.is_character_loaded:
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
    else:
        draw_open_file_button(static)


def draw_abilities_saves_misc(static: MainWindowProtocol) -> None:
    if static.is_character_loaded:
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


def draw_speed_sense(static: MainWindowProtocol) -> None:
    if static.is_character_loaded:
        table_id = "speed_proficiencies_skills"
        if imgui.begin_table(table_id, 2, flags=INVISIBLE_TABLE_FLAGS):  # type: ignore
            imgui.table_next_row(); imgui.table_next_column(); imgui.align_text_to_frame_padding()
            imgui.text("Speed"); imgui.same_line()
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_speed"):
                imgui.open_popup("Edit Speed")
            
            imgui.table_next_column(); imgui.align_text_to_frame_padding()
            imgui.text("Senses"); imgui.same_line()
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_senses"):
                imgui.open_popup("Edit Senses")

            imgui.table_next_row()
            imgui.table_next_column()
            draw_speed(static)
            
            imgui.table_next_column()
            draw_senses(static)

            end_table_nested()

def draw_training_window(static: MainWindowProtocol) -> None:
    if static.is_character_loaded:
        imgui.align_text_to_frame_padding()
        imgui.text("Proficiencies & Training"); imgui.same_line()
        if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}"):
            imgui.open_popup("Edit Tool and Language Proficiencies")
        draw_training(static)


def draw_skills_window(static: MainWindowProtocol) -> None:
    if static.is_character_loaded:
        table_id = "skills"
        if imgui.begin_table(table_id, 1, flags=INVISIBLE_TABLE_FLAGS):  # type: ignore
            imgui.align_text_to_frame_padding()
            draw_text_cell("Skills"); imgui.same_line()
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_skills"):
                imgui.open_popup("Edit Skills")
            imgui.table_next_row(); imgui.table_next_column()
            draw_skills(static)

            end_table_nested()

        imgui.spacing()

        imgui.align_text_to_frame_padding()
        imgui.text("Passive Skills"); imgui.same_line()
        if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_passive_skills"):
            imgui.open_popup("Edit Passive Skills")
        draw_passives(static)

def draw_features_window(static: MainWindowProtocol) -> None:
    if static.is_character_loaded:
        draw_features("All Features", static)

def create_default_docking_splits() -> list[hello_imgui.DockingSplit]:
    split_main = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    split_main.initial_dock = "MainDockSpace"
    split_main.new_dock = "LeftSpace"
    split_main.direction = imgui.Dir.left
    split_main.ratio = 0.5

    split_left = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    split_left.initial_dock = "LeftSpace"
    split_left.new_dock = "SkillsSpace"
    split_left.direction = imgui.Dir.right
    split_left.ratio = 0.3

    split_training = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    split_training.initial_dock = "LeftSpace"
    split_training.new_dock = "TrainingSpace"
    split_training.direction = imgui.Dir.down
    split_training.ratio = 0.25

    split_speed_sense = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    split_speed_sense.initial_dock = "LeftSpace"
    split_speed_sense.new_dock = "SpeedSenseSpace"
    split_speed_sense.direction = imgui.Dir.down
    split_speed_sense.ratio = 0.25

    split_abilities_saves_misc = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    split_abilities_saves_misc.initial_dock = "LeftSpace"
    split_abilities_saves_misc.new_dock = "AbilitiesSavesMiscSpace"
    split_abilities_saves_misc.direction = imgui.Dir.down
    split_abilities_saves_misc.ratio = 0.4

    split_name_class_image_hp = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    split_name_class_image_hp.initial_dock = "LeftSpace"
    split_name_class_image_hp.new_dock = "NameClassImageHPSpace"
    split_name_class_image_hp.direction = imgui.Dir.down
    split_name_class_image_hp.ratio = 0.6

    splits = [split_main, 
              split_left, 
              split_training, 
              split_speed_sense, 
              split_abilities_saves_misc, 
              split_name_class_image_hp]
    return splits


def create_dockable_windows(static: MainWindowProtocol) -> list[hello_imgui.DockableWindow]:
    name_class_image_hp_window = hello_imgui.DockableWindow()
    name_class_image_hp_window.label = "Name Class Image HP"
    name_class_image_hp_window.dock_space_name = "NameClassImageHPSpace"
    name_class_image_hp_window.gui_function = lambda: draw_name_class_image_hp(static)

    abilities_saves_misc_window = hello_imgui.DockableWindow()
    abilities_saves_misc_window.label = "Abilities Saves Misc"
    abilities_saves_misc_window.dock_space_name = "AbilitiesSavesMiscSpace"
    abilities_saves_misc_window.gui_function = lambda: draw_abilities_saves_misc(static)

    speed_sense_window = hello_imgui.DockableWindow()
    speed_sense_window.label = "Speed Sense"
    speed_sense_window.dock_space_name = "SpeedSenseSpace"
    speed_sense_window.gui_function = lambda: draw_speed_sense(static)

    training_window = hello_imgui.DockableWindow()
    training_window.label = "Training"
    training_window.dock_space_name = "TrainingSpace"
    training_window.gui_function = lambda: draw_training_window(static)

    skills_window = hello_imgui.DockableWindow()
    skills_window.label = "Skills"
    skills_window.dock_space_name = "SkillsSpace"
    skills_window.gui_function = lambda: draw_skills_window(static)

    right_window = hello_imgui.DockableWindow()
    right_window.label = "All Features"
    right_window.dock_space_name = "MainDockSpace"
    right_window.gui_function = lambda: draw_features_window(static)

    dockable_windows = [
        name_class_image_hp_window,
        abilities_saves_misc_window,
        speed_sense_window,
        training_window,
        skills_window,
        right_window
    ]
    return dockable_windows


def create_default_layout(static: MainWindowProtocol) -> hello_imgui.DockingParams:
    docking_params = hello_imgui.DockingParams()
    docking_params.main_dock_space_node_flags = imgui.DockNodeFlags_.auto_hide_tab_bar # type: ignore
    docking_params.docking_splits = create_default_docking_splits()
    docking_params.dockable_windows = create_dockable_windows(static)
    return docking_params


def load_fonts(static: MainWindowProtocol) -> None:
    hello_imgui.get_runner_params().callbacks.default_icon_font = hello_imgui.DefaultIconFont.font_awesome6
    hello_imgui.imgui_default_settings.load_default_font_with_font_awesome_icons()

    font_loading_params_bold_icons = hello_imgui.FontLoadingParams()
    font_loading_params_bold_icons.use_full_glyph_range = True
    font_loading_params_bold_icons.merge_font_awesome = True
    static.bold_font = hello_imgui.load_font("/ft-bold.otf", 14, font_loading_params_bold_icons)

    font_loading_params_regular_icons = hello_imgui.FontLoadingParams()
    font_loading_params_regular_icons.use_full_glyph_range = True
    font_loading_params_regular_icons.merge_font_awesome = True
    static.regular_font = hello_imgui.load_font("/fa-regular.otf", 14, font_loading_params_regular_icons)


def make_params() -> tuple[hello_imgui.RunnerParams, immapp.AddOnsParams]:
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Just Another D&D Character Manager"
    # runner_params.app_window_params.window_geometry.size = (1400, 950)
    runner_params.app_window_params.restore_previous_geometry = True

    main_window_state = MainWindowProtocol()

    runner_params.imgui_window_params.show_menu_bar = True
    runner_params.callbacks.show_app_menu_items = lambda: draw_toolbar(main_window_state)

    runner_params.callbacks.load_additional_fonts = lambda: load_fonts(main_window_state)
    runner_params.callbacks.post_init = lambda: post_init(main_window_state)

    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )
    runner_params.imgui_window_params.enable_viewports = True
    runner_params.docking_params = create_default_layout(main_window_state)

    addons = immapp.AddOnsParams()
    addons.with_markdown = True
    font_options = imgui_md.MarkdownFontOptions()
    font_options.regular_size = 15
    markdown_options = imgui_md.MarkdownOptions()
    markdown_options.font_options = font_options
    addons.with_markdown_options = markdown_options

    return (runner_params, addons)


runner_params, addons = make_params()
immapp.run(runner_params=runner_params, add_ons_params=addons)
