import json
import os
from typing import Callable

from imgui_bundle import hello_imgui  # type: ignore
from imgui_bundle import imgui
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

from character_sheet import (
    draw_abilities_saves_misc,
    draw_features_window,
    draw_name_class_image_hp,
    draw_skills_window,
    draw_speed_sense,
    draw_training_window,
)
from cs_types import MainWindowProtocol
from features import draw_features


def open_character_window(static: MainWindowProtocol) -> None:
    # Open windows for character data
    windows: list[dict[str, str | Callable[[MainWindowProtocol], None]]] = [
        {"name": "Skills", "function": draw_skills_window},
        {"name": "Name Class Image HP", "function": draw_name_class_image_hp},
        {"name": "Abilities Saves Misc", "function": draw_abilities_saves_misc},
        {"name": "Speed Sense", "function": draw_speed_sense},
        {"name": "Proficiencies & Training", "function": draw_training_window},
        {"name": "Features", "function": draw_features_window},
    ]

    for window in windows:
        additional_window = hello_imgui.DockableWindow()
        additional_window.label = window["name"] # type: ignore
        additional_window.include_in_view_menu = True
        additional_window.remember_is_visible = True

        if window["name"] == "Features":
            additional_window.dock_space_name = "MainDockSpace"
        else:
            additional_window.dock_space_name = window["name"] # type: ignore
        # https://stackoverflow.com/questions/11723217/python-lambda-doesnt-remember-argument-in-for-loop
        additional_window.gui_function = lambda func=window["function"]: func(static) # type: ignore
        hello_imgui.add_dockable_window(
            additional_window,
            force_dockspace=False
        )


def process_character(static: MainWindowProtocol) -> None:
    """"
    Create a dict that stores references to complex objects, i. e:
    "abilities:animal_handling": reference to static.data["abilities"]["animal_handling"]
    
    This allows us to quickly access an object without searching through a dict.
    """
    static.data_refs = {}
    static.bonus_list_refs = {}

    static.data_refs["armor_class"] = static.data["armor_class"]
    static.bonus_list_refs["armor_class:bonuses"] = static.data["armor_class"]["bonuses"]

    static.data_refs["initiative"] = static.data["initiative"]
    static.bonus_list_refs["initiative:bonuses"] = static.data["initiative"]["bonuses"]

    static.data_refs["hp"] = static.data["hp"]
    static.bonus_list_refs["hp:bonuses"] = static.data["hp"]["bonuses"]

    static.data_refs["proficiency"] = static.data["proficiency"]

    # Classes
    for class_dict in static.data["level"]["classes"]:
        static.data_refs[f"level:{class_dict["name"]}"] = class_dict
        if class_dict["spell_save_enabled"]:
            static.data_refs[f"spell_save:{class_dict["name"]}"] = class_dict["spell_save"]
            static.bonus_list_refs[f"spell_save:{class_dict["name"]}:bonuses"] = class_dict["spell_save"]["bonuses"]

    # Abilities
    for ability in static.data["abilities"]:
        static.data_refs[f"ability:{ability["name"]}"] = ability

        static.bonus_list_refs[f"ability:{ability["name"]}:base_score_bonuses"] = ability["base_score_bonuses"]
        static.bonus_list_refs[f"ability:{ability["name"]}:base_score_overrides"] = ability["base_score_overrides"]
        static.bonus_list_refs[f"ability:{ability["name"]}:modifier_bonuses"] = ability["modifier_bonuses"]

    # Saves
    for save in static.data["saves"]:
        static.data_refs[f"save:{save["name"]}"] = save
        static.bonus_list_refs[f"save:{save["name"]}:bonuses"] = save["bonuses"]

    # Skills
    for skill in static.data["skills"]:
        static.data_refs[f"skill:{skill["name"]}"] = skill
        static.bonus_list_refs[f"skill:{skill["name"]}:bonuses"] = skill["bonuses"]

    # Speed
    for speed in static.data["speed"]:
        static.data_refs[f"speed:{speed["name"]}"] = speed
        static.bonus_list_refs[f"speed:{speed["name"]}:base_overrides"] = speed["base_overrides"]
        static.bonus_list_refs[f"speed:{speed["name"]}:bonuses"] = speed["bonuses"]

    # Passives
    for passive in static.data["passive_skill"]:
        static.data_refs[f"passive:{passive["name"]}"] = passive
        static.bonus_list_refs[f"passive:{passive["name"]}:base_overrides"] = passive["base_overrides"]
        static.bonus_list_refs[f"passive:{passive["name"]}:bonuses"] = passive["bonuses"]

    # Senses
    for sense in static.data["sense"]:
        static.data_refs[f"sense:{sense["name"]}"] = sense
        static.bonus_list_refs[f"sense:{sense["name"]}:base_overrides"] = sense["base_overrides"]
        static.bonus_list_refs[f"sense:{sense["name"]}:bonuses"] = sense["bonuses"]

    # Features
    for feature in static.data["features"]:
        static.data_refs[f"feature:{feature["name"]}"] = feature
        for counter in feature["counters"]:
            static.data_refs[f"counter:{feature["name"]}:{counter["name"]}"] = counter

    # Open windows for feature tags
    for window_name in static.data["feature_windows"]:
        additional_window = hello_imgui.DockableWindow()
        additional_window.label = window_name
        additional_window.include_in_view_menu = True
        additional_window.remember_is_visible = True
        additional_window.dock_space_name = "MainDockSpace"
        # https://stackoverflow.com/questions/11723217/python-lambda-doesnt-remember-argument-in-for-loop
        additional_window.gui_function = lambda window_name=window_name: draw_features(window_name, static) # type: ignore
        hello_imgui.add_dockable_window(
            additional_window,
            force_dockspace=False
        )


def load_character(static: MainWindowProtocol) -> None:
    if static.open_file_dialog is not None and static.open_file_dialog.ready():
        static.file_path = static.open_file_dialog.result()
        if static.file_path:
            character_file = open(static.file_path[0], "r+")

            static.data = json.load(character_file)
            open_character_window(static)
            hello_imgui.remove_dockable_window("Home")
            process_character(static)
            static.is_character_loaded = True

            character_file.close()

        static.open_file_dialog = None


def draw_load_character_button(static: MainWindowProtocol) -> None:
    if not hasattr(static, "open_file_dialog"):
        static.open_file_dialog = None

    if imgui.button("Open file"):
        static.open_file_dialog = pfd.open_file("Select file", os.getcwd())
    load_character(static)