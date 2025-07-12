import os

from imgui_bundle import hello_imgui, imgui, imgui_md, immapp  # type: ignore
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

from base_sheet import draw_status
from cs_types.core import MainWindowProtocol
from util.character_loading import draw_load_character_button, load_character
from util.core import save_file

# TODO[BUG]: deleted skill is not deleted from the feature bonuses
# TODO[BUG]: widgets in feature windows (i.e. Warlock or Paladin) duplicate when loading a new character sheet

# TODO: on process character add all feature bonuses (in case the user added them manually to a JSON file)
# TODO: hide long feature descriptions?
# TODO: find a way to create a tab with dockable windows for managing more than one character

def post_init(state: MainWindowProtocol) -> None:
    state.states = {
        "hp_dice_idx": 0,
        "ability_bonus_type_idx": 0,
        "static_bonus_type_idx": 0,
        "counter_display_type_idx": 0,
        "hp_add": "",
        "new_item_name": "",
        "new_bonuses": {},
        "new_training": {},
        "target_name": "",
        "target_ref": "",
        "counter_edit": {
            "id": "",
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
        "new_tag": "",
        "new_desc_ref": "",
        "new_condition_name": "",
        "new_condition_description": "",
        "cyclic_bonus": False,
        "cyclic_bonus_path": [],
        "search_data": {},
        "roll_list": [],
        "roll_popup_opened": {},
        "roll_color_frames_count": 0,
        "roll_popup_color": [0, 0, 0]
    }

    state.are_windows_loaded = False
    state.is_character_loaded = False

    theme = hello_imgui.ImGuiTweakedTheme()
    theme.theme = hello_imgui.ImGuiTheme_.imgui_colors_dark
    hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.imgui_colors_dark)
    state.theme = hello_imgui.ImGuiTheme_.imgui_colors_dark.name


def draw_home_window(static: MainWindowProtocol) -> None:
    if not static.is_character_loaded:
        draw_load_character_button(static)


def draw_toolbar(static: MainWindowProtocol) -> None:
    if imgui.begin_menu("File", True):
        if imgui.menu_item_simple("Open", "Ctrl+N"):
            static.open_file_dialog = pfd.open_file("Select file", os.getcwd())
        if static.is_character_loaded and imgui.menu_item_simple("Save", "Ctrl+S"):
            save_file(static)
        imgui.end_menu()


def register_callbacks(static: MainWindowProtocol) -> None:
    if imgui.is_key_chord_pressed(imgui.Key.mod_ctrl | imgui.Key.n):  # type: ignore
        static.open_file_dialog = pfd.open_file("Select file", os.getcwd())
    # We need to continously try to open a file, otherwise it is called
    # once when the files have not yet been selected
    load_character(static)

    if imgui.is_key_chord_pressed(imgui.Key.mod_ctrl | imgui.Key.s):  # type: ignore
        save_file(static)


def each_frame(static: MainWindowProtocol) -> None:
    register_callbacks(static)


def create_default_docking_splits() -> list[hello_imgui.DockingSplit]:
    left = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    left.initial_dock = "MainDockSpace"
    left.new_dock = "Left"
    left.direction = imgui.Dir.left
    left.ratio = 0.6

    middle = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    middle.initial_dock = "Left"
    middle.new_dock = "Skills"
    middle.direction = imgui.Dir.right
    middle.ratio = 0.33

    # Name Class Image HP
    ncip = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    ncip.initial_dock = "Left"
    ncip.new_dock = "Name Class Image HP"
    ncip.direction = imgui.Dir.up
    ncip.ratio = 0.25

    # Abilities Saves Misc
    asm = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    asm.initial_dock = "Left"
    asm.new_dock = "Abilities Saves Misc"
    asm.direction = imgui.Dir.up
    asm.ratio = 0.25

    # Speed Sense
    ss = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    ss.initial_dock = "Left"
    ss.new_dock = "Speed Sense"
    ss.direction = imgui.Dir.up
    ss.ratio = 0.25

    # Proficiencies & Training
    pt = hello_imgui.DockingSplit(node_flags_=imgui.DockNodeFlags_.auto_hide_tab_bar) # type: ignore
    pt.initial_dock = "Left"
    pt.new_dock = "Proficiencies & Training"
    pt.direction = imgui.Dir.up
    pt.ratio = 0.25

    return [left, middle, ncip, asm, ss, pt]


def create_dockable_windows(static: MainWindowProtocol) -> list[hello_imgui.DockableWindow]:
    home_window = hello_imgui.DockableWindow()
    home_window.label = "Home"
    home_window.dock_space_name = "MainDockSpace"
    home_window.gui_function = lambda: draw_home_window(static)
    
    return [home_window]


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
    runner_params.callbacks.show_app_menu_items = lambda main_window_state=main_window_state: draw_toolbar(main_window_state)

    runner_params.callbacks.load_additional_fonts = lambda main_window_state=main_window_state: load_fonts(main_window_state)
    runner_params.callbacks.post_init = lambda main_window_state=main_window_state: post_init(main_window_state)
    runner_params.callbacks.before_imgui_render = lambda main_window_state=main_window_state: each_frame(main_window_state)

    runner_params.imgui_window_params.show_status_bar = True
    runner_params.callbacks.show_status = lambda main_window_state=main_window_state: draw_status(main_window_state)
    runner_params.imgui_window_params.show_status_fps = False

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
