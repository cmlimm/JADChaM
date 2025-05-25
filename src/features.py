from imgui_bundle import hello_imgui  # type: ignore
from imgui_bundle import ImVec2, icons_fontawesome_6, imgui, imgui_md  # type: ignore

from cs_types import Bonus, BonusTo, Feature, MainWindowProtocol
from settings import MARKDOWN_TEXT_TABLE  # type: ignore
from settings import (  # type: ignore
    DISADVANTAGE_ACTIVE_COLOR,
    DISADVANTAGE_COLOR,
    DISADVANTAGE_HOVER_COLOR,
    INVISIBLE_TABLE_FLAGS,
    LIST_TYPE_TO_BONUS,
    MEDIUM_STRING_INPUT_WIDTH,
    SHORT_STRING_INPUT_WIDTH,
)
from util_imgui import end_table_nested
from util_sheet import STRIPED_TABLE_FLAGS  # type: ignore
from util_sheet import (  # type: ignore
    add_item_to_list,
    delete_feature_bonus,
    delete_item_from_list,
    draw_add_bonus,
    draw_counter,
    draw_edit_counter,
    get_bonus_value,
    parse_text,
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
                if not ability_name.startswith("no_display") and imgui.begin_menu(f"{ability_name}##{menu_id}"):
                    if imgui.menu_item_simple(f"Base Score##{menu_id}"):
                        static.states["target_name"] = f"Ability Base Score, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability_name}:base_score_bonuses"
                    if imgui.menu_item_simple(f"Base Score Override##{menu_id}"):
                        static.states["target_name"] = f"Ability Base Score Override, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability_name}:base_score_overrides"
                    if imgui.menu_item_simple(f"Modifier##{menu_id}"):
                        static.states["target_name"] = f"Ability Modifier, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability_name}:modifier_bonuses"
                    imgui.end_menu()
            imgui.end_menu()
        # Saving Throw
        if imgui.begin_menu(f"Save##{menu_id}"):
            for save in static.data["saves"]:
                save_name = save["name"]
                if not save_name.startswith("no_display") and imgui.menu_item_simple(save_name):
                    static.states["target_name"] = f"Saving Throw, {save_name}"
                    static.states["target_ref"] = f"save:{save_name}:bonuses"
            imgui.end_menu()
        # Skill
        if imgui.begin_menu(f"Skill##{menu_id}"):
            for skill in static.data["skills"]:
                skill_name = skill["name"]
                if not skill_name.startswith("no_display") and imgui.menu_item_simple(skill_name):
                    static.states["target_name"] = f"Skill, {skill_name}"
                    static.states["target_ref"] = f"skill:{skill_name}:bonuses"
            imgui.end_menu()
        # Spell Save
        if imgui.begin_menu(f"Spell Save##{menu_id}"):
            for class_item in static.data["level"]["classes"]:
                class_name = class_item["name"]
                if not class_name.startswith("no_display") and class_item["spell_save_enabled"] and imgui.menu_item_simple(f"{class_name}##{menu_id}"):
                    static.states["target_name"] = f"Spell Save, {class_name}"
                    static.states["target_ref"] = f"spell_save:{class_name}:bonuses"
            imgui.end_menu()
        # Speed
        if imgui.begin_menu(f"Speed##{menu_id}"):
            for speed in static.data["speed"]:
                speed_name = speed["name"]
                if not speed_name.startswith("no_display") and imgui.begin_menu(f"{speed_name}##{menu_id}"):
                    if imgui.menu_item_simple("Bonus"):
                        static.states["target_name"] = f"Speed, {speed_name}"
                        static.states["target_ref"] = f"speed:{speed_name}:bonuses"
                    if imgui.menu_item_simple("Override"):
                        static.states["target_name"] = f"Speed Base Override, {speed_name}"
                        static.states["target_ref"] = f"speed:{speed_name}:base_overrides"
                    imgui.end_menu()
            imgui.end_menu()
        # Passive Skill
        if imgui.begin_menu(f"Passive Skill##{menu_id}"):
            for passive in static.data["passive_skill"]:
                passive_name = passive["name"]
                if not passive_name.startswith("no_display") and imgui.begin_menu(f"{passive_name}##{menu_id}"):
                    if imgui.menu_item_simple("Bonus"):
                        static.states["target_name"] = f"Passive Skill, {passive_name}"
                        static.states["target_ref"] = f"passive:{passive_name}:bonuses"
                    if imgui.menu_item_simple("Override"):
                        static.states["target_name"] = f"Passive Skill Base Override, {passive_name}"
                        static.states["target_ref"] = f"passive:{passive_name}:base_overrides"
                    imgui.end_menu()
            imgui.end_menu()
        # Sense
        if imgui.begin_menu(f"Sense##{menu_id}"):
            for sense in static.data["sense"]:
                sense_name = sense["name"]
                if not sense_name.startswith("no_display") and imgui.begin_menu(f"{sense_name}##{menu_id}"):
                    if imgui.menu_item_simple("Bonus"):
                        static.states["target_name"] = f"Sense, {sense_name}"
                        static.states["target_ref"] = f"sense:{sense_name}:bonuses"
                    if imgui.menu_item_simple("Override"):
                        static.states["target_name"] = f"Sense Base Override, {sense_name}"
                        static.states["target_ref"] = f"sense:{sense_name}:base_overrides"
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
    popup_name = f"Bonus for {feature["name"]}##popup"
    if imgui.begin_popup(popup_name):
        bonus_id = f"{feature["name"]}_bonus"
        if not bonus_id in static.states["new_bonuses"]:
            static.states["new_bonuses"][bonus_id] = {
                "new_bonus_type": "",
                "new_bonus_value": "",
                "new_bonus_mult": 1.0
            }
        new_bonus = static.states["new_bonuses"][bonus_id]

        draw_target_menu(f"{static.states["target_name"] if static.states["target_name"] != "" else "Choose Target"}", 
                         f"{feature["name"]}_target", static)
        
        if static.states["target_ref"] != "":
            draw_add_bonus(bonus_id, static.bonus_list_refs[static.states["target_ref"]],
                           LIST_TYPE_TO_BONUS["all"], static, is_feature_bonus=True)

        imgui.spacing()

        if imgui.button(f"Add##{feature["name"]}_new_bonus_to"):
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

    popup_name = f"Edit {feature["name"]}##popup"
    if imgui.begin_popup_modal(popup_name, None, imgui.WindowFlags_.always_auto_resize.value)[0]:
        # imgui.set_cursor_pos_x(window_size.x/2)
        # imgui.dummy(ImVec2(0, 0))

        imgui.align_text_to_frame_padding()
        imgui.text("Name"); imgui.same_line()
        imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
        _, static.states["feat_name"] = imgui.input_text(f"##{feature["name"]}_feature_name", static.states["feat_name"], 128)
        imgui.pop_item_width(); imgui.same_line()

        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
        if imgui.button("Delete Feature"):
            imgui.close_current_popup()
            if static.states["feat_name"] != "":
                feature["name"] = static.states["feat_name"]
            static.states["feat_name"] = ""
            delete_item_from_list(feature, idx, static.data["features"], "feature", static)
        imgui.pop_style_color(3)

        imgui.text("Description")
        imgui.set_next_window_size_constraints(ImVec2(window_size.x/2, imgui.get_text_line_height() * 5),
                                               ImVec2(window_size.x/2, imgui.get_text_line_height() * 5))
        if imgui.begin_child("description_text"):
            _, feature["description"] = imgui.input_text_multiline(f"##{feature["name"]}_feature_description", 
                                                                feature["description"], 
                                                                ImVec2(-1, imgui.get_text_line_height() * 5), 128)
            imgui.end_child()

        # If we are creating a feature in a specific tab, it should have 
        # the corresponding tag by default
        if not tag in feature["tags"] and tag != "All Features":
            feature["tags"].append(tag)

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

            imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
            imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
            imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{tag}_{idx}"):
                del feature["tags"][idx]
            imgui.pop_style_color(3)
        imgui.dummy(ImVec2(0, 0))

        if imgui.button(f"New Bonus##{feature["name"]}"):
            imgui.open_popup(f"Bonus for {feature["name"]}##popup")
        draw_edit_feature_bonus(feature, static)
        
        imgui.same_line()

        if imgui.button(f"New Counter##{feature["name"]}"):
            imgui.open_popup("Edit Counter##popup")
        draw_edit_counter(feature["counters"], feature["name"], static)

        if imgui.begin_table(f"{feature["name"]}_bonuses_counters_spells_attacks", 4, INVISIBLE_TABLE_FLAGS): # type: ignore
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
                            imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                            imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                            imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                            if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##feature_bonus_{idx}"):
                                delete_feature_bonus(feature, feature_bonus, static)
                            imgui.pop_style_color(3)
                    end_table_nested()

            imgui.table_next_column()
            imgui.separator_text("Counters")
            if feature["counters"] != []:
                if imgui.begin_table("feature_counters", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
                    for idx, feature_counter in enumerate(feature["counters"]):
                        imgui.table_next_row(); imgui.table_next_column()
                        if imgui.button(f"{feature_counter["name"]}##{idx}"):
                            imgui.open_popup(f"Edit Counter##{feature_counter["name"]}_popup")
                        draw_edit_counter(feature["counters"], feature["name"], static, feature_counter)

                        imgui.table_next_column()
                        if feature_counter["manual"]:
                            imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                            imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                            imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                            if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##feature_bonus_{idx}"):
                                del feature["counters"][idx]
                            imgui.pop_style_color(3)
                    end_table_nested()
            end_table_nested()
        imgui.spacing()

        if imgui.button("Close", ImVec2(120, 0)):
            imgui.close_current_popup()
            if static.states["feat_name"] != "":
                feature["name"] = static.states["feat_name"]
            static.states["feat_name"] = ""
        imgui.end_popup()


def draw_feature(feature: Feature, idx: int, tag: str, static: MainWindowProtocol) -> None:
    imgui.spacing()
    draw_edit_feature(feature, idx, tag, static)
    if imgui.button(f"{feature["name"]}##{idx}"):
        static.states["feat_name"] = feature["name"]
        imgui.open_popup(f"Edit {feature["name"]}##popup")

    imgui.spacing()

    description = parse_text(feature["description"], static)
    split_description = description.split("\n\n")
    for line in split_description:
        imgui_md.render(line)

    imgui.spacing()

    for counter in feature["counters"]:
        draw_counter(counter, static); imgui.same_line()

    imgui.spacing()

    imgui.push_id(f"tags_{feature["name"]}_{idx}")
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
            if imgui.button(f"Delete {window_name} tab"):
                idx = static.data["feature_windows"].index(window_name)
                del static.data["feature_windows"][idx]
                hello_imgui.remove_dockable_window(window_name)
        imgui.end_popup()
    # TODO: research if you can add a callback to the built-in close window button

    features_list_length = len(static.data["features"])
    if features_list_length != 0 and imgui.begin_table("features_table", 1, flags=MARKDOWN_TEXT_TABLE): # type: ignore
        for idx, feature in enumerate(static.data["features"]):
            if not feature["name"].startswith("no_display") and (window_name in feature["tags"] or window_name == "All Features"):
                imgui.table_next_row(); imgui.table_next_column()
                draw_feature(feature, idx, window_name, static)
        end_table_nested()