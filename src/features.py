import functools
from uuid import uuid4

from imgui_bundle import hello_imgui  # type: ignore
from imgui_bundle import ImVec2, icons_fontawesome_6, imgui, imgui_md  # type: ignore

import settings
from cs_types.components import Bonus, BonusTo
from cs_types.core import Feature, MainWindowProtocol
from settings import (  # type: ignore
    DAMAGE_EFFECTS_DEFAULT,
    DAMAGE_TYPES,
    INVISIBLE_TABLE_FLAGS,
    LIST_TYPE_TO_BONUS,
    MARKDOWN_TEXT_TABLE,
    MEDIUM_STRING_INPUT_WIDTH,
    PROFICIENCIES_DEFAULT,
    PROFICIENCIES_TYPES,
    SHORT_STRING_INPUT_WIDTH,
)
from stats import draw_static_stat_button
from util.calc import get_bonus_value, parse_description
from util.custom_imgui import ColorButton, end_table_nested
from util.sheet import (  # type: ignore
    STRIPED_TABLE_FLAGS,
    add_item_to_list,
    delete_feature_bonus,
    delete_item_from_list,
    draw_add_bonus,
    draw_counter,
    draw_edit_counter,
    draw_entities_menu,
    draw_new_text_item_popup,
)


def draw_target_menu(menu_name: str, menu_id: str, static: MainWindowProtocol):
    imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
    imgui.push_item_flag(imgui.ItemFlags_.auto_close_popups, False) # type: ignore
    
    if menu_name == "":
        menu_name = "Choose Target"

    if imgui.begin_menu(f"{menu_name}##{menu_id}"):
        # Ability
        if imgui.begin_menu(f"Ability##{menu_id}"):
            for ability in static.data["abilities"]:
                ability_name = ability["name"]
                if ability_name != "no_display" and imgui.begin_menu(f"{ability_name}##{menu_id}"):
                    if imgui.menu_item_simple(f"Base Score##{menu_id}"):
                        static.states["target_name"] = f"Ability Base Score, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability["id"]}:base_score_bonuses"
                    if imgui.menu_item_simple(f"Base Score Override##{menu_id}"):
                        static.states["target_name"] = f"Ability Base Score Override, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability["id"]}:base_score_overrides"
                    if imgui.menu_item_simple(f"Modifier##{menu_id}"):
                        static.states["target_name"] = f"Ability Modifier, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability["id"]}:modifier_bonuses"
                    imgui.end_menu()
            imgui.end_menu()
        # Saving Throw
        if imgui.begin_menu(f"Save##{menu_id}"):
            for save in static.data["saves"]:
                save_name = save["name"]
                if save_name != "no_display" and imgui.menu_item_simple(save_name):
                    static.states["target_name"] = f"Saving Throw, {save_name}"
                    static.states["target_ref"] = f"save:{save["id"]}:bonuses"
            imgui.end_menu()
        # Skill
        if imgui.begin_menu(f"Skill##{menu_id}"):
            for skill in static.data["skills"]:
                skill_name = skill["name"]
                if skill_name != "no_display" and imgui.menu_item_simple(skill_name):
                    static.states["target_name"] = f"Skill, {skill_name}"
                    static.states["target_ref"] = f"skill:{skill["id"]}:bonuses"
            imgui.end_menu()
        # Spell Save
        if imgui.begin_menu(f"Spell Save##{menu_id}"):
            for class_item in static.data["level"]["classes"]:
                class_name = class_item["name"]
                if class_name != "no_display" and class_item["spell_save_enabled"] and imgui.menu_item_simple(f"{class_name}##{menu_id}"):
                    static.states["target_name"] = f"Spell Save, {class_name}"
                    static.states["target_ref"] = f"spell_save:{class_item["id"]}:bonuses"
            imgui.end_menu()
        # Speed
        if imgui.begin_menu(f"Speed##{menu_id}"):
            for speed in static.data["speed"]:
                speed_name = speed["name"]
                if speed_name != "no_display" and imgui.begin_menu(f"{speed_name}##{menu_id}"):
                    if imgui.menu_item_simple("Bonus"):
                        static.states["target_name"] = f"Speed, {speed_name}"
                        static.states["target_ref"] = f"speed:{speed["id"]}:bonuses"
                    if imgui.menu_item_simple("Override"):
                        static.states["target_name"] = f"Speed Base Override, {speed_name}"
                        static.states["target_ref"] = f"speed:{speed["id"]}:base_overrides"
                    imgui.end_menu()
            imgui.end_menu()
        # Passive Skill
        if imgui.begin_menu(f"Passive Skill##{menu_id}"):
            for passive in static.data["passive_skill"]:
                passive_name = passive["name"]
                if passive_name != "no_display" and imgui.begin_menu(f"{passive_name}##{menu_id}"):
                    if imgui.menu_item_simple("Bonus"):
                        static.states["target_name"] = f"Passive Skill, {passive_name}"
                        static.states["target_ref"] = f"passive:{passive["id"]}:bonuses"
                    if imgui.menu_item_simple("Override"):
                        static.states["target_name"] = f"Passive Skill Base Override, {passive_name}"
                        static.states["target_ref"] = f"passive:{passive["id"]}:base_overrides"
                    imgui.end_menu()
            imgui.end_menu()
        # Sense
        if imgui.begin_menu(f"Sense##{menu_id}"):
            for sense in static.data["sense"]:
                sense_name = sense["name"]
                if sense_name != "no_display" and imgui.begin_menu(f"{sense_name}##{menu_id}"):
                    if imgui.menu_item_simple("Bonus"):
                        static.states["target_name"] = f"Sense, {sense_name}"
                        static.states["target_ref"] = f"sense:{sense["id"]}:bonuses"
                    if imgui.menu_item_simple("Override"):
                        static.states["target_name"] = f"Sense Base Override, {sense_name}"
                        static.states["target_ref"] = f"sense:{sense["id"]}:base_overrides"
                    imgui.end_menu()
            imgui.end_menu()
        # Initiative
        if imgui.menu_item_simple(f"Initiative##{menu_id}"):
            static.states["target_name"] = f"Initiative"
            static.states["target_ref"] = f"initiative:bonuses"
        # Armor Class
        if imgui.menu_item_simple(f"Armor Class##{menu_id}"):
            static.states["target_name"] = f"Armor Class"
            static.states["target_ref"] = f"armor_class:bonuses"
        # HP
        if imgui.menu_item_simple(f"HP##{menu_id}"):
            static.states["target_name"] = f"HP Max"
            static.states["target_ref"] = f"hp:bonuses"

        imgui.end_menu()
    imgui.pop_item_flag()


def draw_edit_feature_bonus(feature: Feature, static: MainWindowProtocol) -> None:
    popup_name = f"Bonus for {feature["id"]}##popup"
    if imgui.begin_popup(popup_name):
        bonus_id = f"{feature["id"]}_bonus"
        if not bonus_id in static.states["new_bonuses"]:
            static.states["new_bonuses"][bonus_id] = {
                "new_bonus_type": "",
                "new_bonus_value": "",
                "new_bonus_mult": 1.0
            }
        new_bonus = static.states["new_bonuses"][bonus_id]

        draw_target_menu(f"{static.states["target_name"] if static.states["target_name"] != "" else "Choose Target"}", 
                         f"{feature["id"]}_target", static)
        
        if static.states["target_ref"] != "":
            draw_add_bonus(bonus_id,
                           static.states["target_ref"], 
                           static.bonus_list_refs[static.states["target_ref"]],
                           LIST_TYPE_TO_BONUS["all"],
                           static, is_feature_bonus=True)

        imgui.spacing()

        if imgui.button(f"Add##{feature["id"]}_new_bonus_to"):
            imgui.close_current_popup()
            
            if static.states["target_ref"] != "" and new_bonus["new_bonus_value"] != "":
                bonus_mult = new_bonus["new_bonus_mult"]
                bonus_name = f"{new_bonus["new_bonus_type"]}{" x" + str(bonus_mult) if bonus_mult != 1.0 else ""} ({feature["name"]})"

                target_bonus: Bonus = {
                    "name": bonus_name,
                    "value": new_bonus["new_bonus_value"],
                    "multiplier": new_bonus["new_bonus_mult"],
                    "manual": False
                }

                feature_bonus: BonusTo = {
                    "name": static.states["target_name"],
                    "target": static.states["target_ref"],
                    "bonus": target_bonus,
                    "manual": True
                }

                static.bonus_list_refs[static.states["target_ref"]].append(target_bonus)
                feature["bonuses"].append(feature_bonus)
            
            static.states["target_name"] = ""
            static.states["target_ref"] = ""

            del static.states["new_bonuses"][bonus_id] # type: ignore
        imgui.end_popup()


def draw_edit_feature(feature: Feature, idx: int, tag: str, static: MainWindowProtocol) -> None:
    center = imgui.get_main_viewport().get_center()
    imgui.set_next_window_pos(center, imgui.Cond_.appearing.value, ImVec2(0.5, 0.5))
    window_size = imgui.get_main_viewport().size

    popup_name = f"Edit Feature##popup_{feature["id"]}"
    if imgui.begin_popup_modal(popup_name, None, imgui.WindowFlags_.always_auto_resize.value)[0]:
        # imgui.set_cursor_pos_x(window_size.x/2)
        # imgui.dummy(ImVec2(0, 0))

        imgui.align_text_to_frame_padding()
        imgui.text("Name"); imgui.same_line()
        imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
        _, feature["name"] = imgui.input_text(f"##{feature["id"]}_feature_name", feature["name"], 128)
        imgui.pop_item_width(); imgui.same_line()

        with ColorButton("bad"):
            if imgui.button("Delete Feature"):
                imgui.close_current_popup()
                delete_item_from_list(feature, idx, static.data["features"], "feature", static)

        imgui.text("Description")
        imgui.set_next_window_size_constraints(ImVec2(window_size.x/2, imgui.get_text_line_height() * 5),
                                               ImVec2(window_size.x/2, imgui.get_text_line_height() * 5))
        if imgui.begin_child("description_text"):
            _, feature["description"]["text"] = imgui.input_text_multiline(f"##{feature["id"]}_feature_description", 
                                                                           feature["description"]["text"],
                                                                           ImVec2(-1, imgui.get_text_line_height() * 5))
            imgui.end_child()

        imgui.text("Description references")
        
        imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
        _, static.states["new_desc_ref"] = imgui.input_text_with_hint("##new_desc_ref", "Reference", static.states["new_desc_ref"], 128)
        imgui.pop_item_width(); imgui.same_line()
        if imgui.button(f"Add##new_desc_ref"):
            feature["description"]["references"][f"{static.states["new_desc_ref"]}"]= {
                "id": str(uuid4()),
                "name": static.states["new_desc_ref"],
                "total": 0,
                "base": 0,
                "base_overrides": [],
                "bonuses": [],
                "manual": True
            }
            static.states["new_desc_ref"] = ""

        if feature["description"]["references"] != {}:
            imgui.same_line()

        changed_names = {}
        for idx, (name, reference) in enumerate(feature["description"]["references"].items()):
            imgui.align_text_to_frame_padding()
            imgui.text(name); imgui.same_line()
            name_changed = draw_static_stat_button(f"desc_ref_{idx}_feature_{feature["id"]}", 
                                                   reference, 
                                                   LIST_TYPE_TO_BONUS["all"],
                                                   f"{feature["id"]}_{idx}",
                                                   static); imgui.same_line()
            
            if name_changed:
                changed_names[name] = reference["name"]

            with ColorButton("bad"):
                if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##desc_ref_{idx}"):
                    del feature["description"]["references"][name]
        for old_name, new_name in changed_names.items():
            feature["description"]["references"][new_name] = feature["description"]["references"].pop(old_name)

        # If we are creating a feature in a specific tab, it should have 
        # the corresponding tag by default
        if not tag in feature["tags"] and tag != "All Features":
            feature["tags"].append(tag)

        imgui.text("Tags")

        imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
        _, static.states["new_tag"] = imgui.input_text_with_hint("##new_tag", "Tag", static.states["new_tag"], 128)
        imgui.pop_item_width(); imgui.same_line()
        if imgui.button(f"Add##add_tag"):
            feature["tags"].append(static.states["new_tag"])
            static.states["new_tag"] = ""
        imgui.same_line()

        for idx, tag in enumerate(feature["tags"]):
            imgui.same_line(); imgui.align_text_to_frame_padding()
            imgui.text(f"{tag}"); imgui.same_line()

            with ColorButton("bad"):
                if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{tag}_{idx}"):
                    del feature["tags"][idx]
        imgui.dummy(ImVec2(0, 0))

        if imgui.button(f"New Bonus##{feature["id"]}"):
            imgui.open_popup(f"Bonus for {feature["id"]}##popup")
        draw_edit_feature_bonus(feature, static)
        
        imgui.same_line()

        if imgui.button(f"New Counter##{feature["id"]}"):
            imgui.open_popup("Edit Counter##popup")
        draw_edit_counter(feature["counters"], feature["id"], static)

        imgui.same_line()

        if imgui.button(f"New Damage Effect##{feature["id"]}"):
            imgui.open_popup(f"New Text Table Item Popup##{feature["id"]}_damage_effects")

        draw_new_text_item_popup(f"{feature["id"]}_damage_effects", DAMAGE_TYPES, DAMAGE_EFFECTS_DEFAULT, 
                                 [static.data["damage_effects"], feature["damage_effects"]], static, 
                                 feature["name"], False)

        imgui.same_line()

        if imgui.button(f"New Proficiency##{feature["id"]}"):
            imgui.open_popup(f"New Text Table Item Popup##{feature["id"]}_proficiency")
            
        draw_new_text_item_popup(f"{feature["id"]}_proficiency", PROFICIENCIES_TYPES, PROFICIENCIES_DEFAULT, 
                                 [static.data["training"], feature["proficiencies"]], static, 
                                 feature["name"], False)

        if imgui.begin_table(f"{feature["id"]}_bonuses_counters_spells_attacks", 4, INVISIBLE_TABLE_FLAGS): # type: ignore
            imgui.table_next_row(); imgui.table_next_column()
            imgui.separator_text("Bonuses")
            if feature["bonuses"] != []:
                if imgui.begin_table("feature_bonuses", 3, flags=STRIPED_TABLE_FLAGS): # type: ignore
                    for idx, feature_bonus in enumerate(feature["bonuses"]):
                        if get_bonus_value(feature_bonus["bonus"]["value"], static) == "delete":
                            del feature["bonuses"][idx]

                        imgui.table_next_row(); imgui.table_next_column(); imgui.align_text_to_frame_padding()
                        imgui.text(feature_bonus["name"])

                        imgui.table_next_column()
                        imgui.text(f"{feature_bonus["bonus"]["name"].replace(f" ({feature["name"]})", "")}")

                        imgui.table_next_column()
                        if feature_bonus["manual"]:
                            with ColorButton("bad"):
                                if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##feature_bonus_{idx}"):
                                    delete_feature_bonus(feature, feature_bonus, static)
                    end_table_nested()

            imgui.table_next_column()
            imgui.separator_text("Counters")
            if feature["counters"] != []:
                if imgui.begin_table("feature_counters", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
                    for idx, feature_counter in enumerate(feature["counters"]):
                        imgui.table_next_row(); imgui.table_next_column()
                        if imgui.button(f"{feature_counter["name"]}##{idx}"):
                            imgui.open_popup(f"Edit Counter##{feature_counter["id"]}_popup")
                        draw_edit_counter(feature["counters"], feature["id"], static, feature_counter)

                        imgui.table_next_column()
                        if feature_counter["manual"]:
                            with ColorButton("bad"):
                                if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##feature_counter_{idx}"):
                                    del feature["counters"][idx]
                    end_table_nested()

            imgui.table_next_column()
            imgui.separator_text("Damage Effects")
            if feature["damage_effects"] != []:
                if imgui.begin_table("feature_damage_effects", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
                    for idx, feature_damage_effect in enumerate(feature["damage_effects"]):
                        imgui.table_next_row(); imgui.table_next_column()
                        imgui.align_text_to_frame_padding()
                        imgui.text(f"{feature_damage_effect["name"]} ({feature_damage_effect["type"]})")

                        imgui.table_next_column()
                        with ColorButton("bad"):
                            if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##feature_damage_effect_{idx}"):
                                del feature["damage_effects"][idx]
                                idx_delete = static.data["damage_effects"].index(feature_damage_effect)
                                del static.data["damage_effects"][idx_delete]
                    end_table_nested()

            imgui.table_next_column()
            imgui.separator_text("Proficiencies")
            if feature["proficiencies"] != []:
                if imgui.begin_table("feature_proficiencies", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
                    for idx, feature_proficiency in enumerate(feature["proficiencies"]):
                        imgui.table_next_row(); imgui.table_next_column()
                        imgui.align_text_to_frame_padding()
                        imgui.text(f"{feature_proficiency["name"]} ({feature_proficiency["type"]})")

                        imgui.table_next_column()
                        with ColorButton("bad"):
                            if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##feature_proficiency_{idx}"):
                                del feature["proficiencies"][idx]
                                idx_delete = static.data["training"].index(feature_proficiency)
                                del static.data["training"][idx_delete]
                    end_table_nested()
            end_table_nested()

        imgui.spacing()

        if imgui.button("Close", ImVec2(120, 0)):
            imgui.close_current_popup()
        imgui.end_popup()


def draw_feature(feature: Feature, idx: int, tag: str, static: MainWindowProtocol) -> None:
    imgui.spacing()
    draw_edit_feature(feature, idx, tag, static)
    if imgui.button(f"{feature["name"]}##{idx}"):
        imgui.open_popup(f"Edit Feature##popup_{feature["id"]}")

    imgui.spacing()

    description = parse_description(feature["description"], static)
    split_description = description.split("\n\n")
    for line in split_description:
        imgui_md.render(line)

    imgui.spacing()

    for counter in feature["counters"]:
        draw_counter(counter, static); imgui.same_line()

    imgui.spacing()

    imgui.push_id(f"tags_{feature["id"]}_{idx}")
    imgui_md.render(f"**Tags**: {", ".join(feature["tags"])}")
    imgui.pop_id()
    imgui.spacing()


def add_feature_window(window_name: str, static: MainWindowProtocol) -> None:
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


def draw_features(window_name: str, static: MainWindowProtocol) -> None:
    imgui.align_text_to_frame_padding()
    if imgui.button(f"{window_name}"):
        imgui.open_popup("Modify Tabs")
    if imgui.is_item_hovered():
        imgui.set_mouse_cursor(imgui.MouseCursor_.hand) # type: ignore
    if imgui.begin_popup("Modify Tabs"):
        if imgui.button(f"New Tab"):
            imgui.open_popup("New tab name")
        if imgui.begin_popup("New tab name"):
            imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
            _, static.states["new_window_name"] = imgui.input_text_with_hint("##new_window_name", "Name", static.states["new_window_name"], 128)
            imgui.pop_item_width()
            if imgui.button("Add##new_tab") and static.states["new_window_name"] != "":
                add_feature_window(static.states["new_window_name"], static)
                static.data["feature_windows"].append(static.states["new_window_name"])
                static.states["new_window_name"] = ""
            imgui.end_popup()

        if imgui.button(f"New Feature"):
            imgui.open_popup("New feature name")
        if imgui.begin_popup("New feature name"):
            imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
            _, static.states["new_item_name"] = imgui.input_text_with_hint(
                "##new_item", 
                "Name", 
                static.states["new_item_name"],
                128); imgui.same_line()
            imgui.pop_item_width()
            if imgui.button("Add##new_list_item"):
                add_item_to_list(static.states["new_item_name"], static.data["features"], "feature", static, tag=window_name)
                static.states["new_item_name"] = ""
            imgui.end_popup()

        if window_name != "All Features":
            with ColorButton("bad"):
                if imgui.button(f"Delete {window_name} tab"):
                    idx = static.data["feature_windows"].index(window_name)
                    del static.data["feature_windows"][idx]
                    hello_imgui.remove_dockable_window(window_name)
        imgui.end_popup()

    features_list_length = len(static.data["features"])
    if features_list_length != 0 and imgui.begin_table(f"{window_name}_features_table", 1, flags=MARKDOWN_TEXT_TABLE): # type: ignore
        for idx, feature in enumerate(static.data["features"]):
            if feature["name"] != "no_display" and (window_name in feature["tags"] or window_name == "All Features"):
                imgui.table_next_row(); imgui.table_next_column()
                draw_feature(feature, idx, window_name, static)
        end_table_nested()