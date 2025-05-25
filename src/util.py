import json
import os
import shutil

from imgui_bundle import hello_imgui  # type: ignore

from cs_types import MainWindowProtocol
from features import draw_features


def open_file(static: MainWindowProtocol) -> None:
    if static.open_file_dialog is not None and static.open_file_dialog.ready():
        static.file_path = static.open_file_dialog.result()
        if static.file_path:
            character_file = open(static.file_path[0], "r+")

            static.data = json.load(character_file)
            process_character(static)
            static.is_character_loaded = True
    
            character_file.close()

        static.open_file_dialog = None


def save_file(static: MainWindowProtocol) -> None:
    character_file = open(static.file_path[0], "r+")
    character_file.seek(0)
    character_file.truncate(0)
    json.dump(static.data, character_file, indent=4)
    character_file.close()


def open_image(static: MainWindowProtocol) -> None:
    if static.open_image_dialog is not None and static.open_image_dialog.ready():
        file_path = static.open_image_dialog.result()
        if file_path:
            static.data["image_path"] = f"images/{os.path.basename(file_path[0])}"
            try:
                shutil.copy(file_path[0], f"{os.getcwd()}/assets/{static.data["image_path"]}")
            except shutil.SameFileError:
                pass
        
        static.open_image_dialog = None


# Create a dict that stores references to complex objects, i. e:
# "abilities:animal_handling": reference to static.data["abilities"]["animal_handling"]
#
# This allows us to quickly access an object without searching through a dict.
def process_character(static: MainWindowProtocol) -> None:
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
