from imgui_bundle import ImVec2, icons_fontawesome_6, imgui

from cs_types import Bonus, BonusTo, Feature, MainWindowProtocol
from settings import (
    DISADVANTAGE_ACTIVE_COLOR,
    DISADVANTAGE_COLOR,
    DISADVANTAGE_HOVER_COLOR,
    MEDIUM_STRING_INPUT_WIDTH,
    SHORT_STRING_INPUT_WIDTH,
)
from util_gui import end_table_nested
from util_sheet import STRIPED_TABLE_FLAGS, draw_add_bonus  # type: ignore


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
                    if imgui.menu_item_simple(f"Modifier##{menu_id}"):
                        static.states["target_name"] = f"Ability Modifier, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability_name}:modifier_bonuses"
                    if imgui.menu_item_simple(f"Base Score##{menu_id}"):
                        static.states["target_name"] = f"Ability Base Score, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability_name}:base_score_bonuses"
                    if imgui.menu_item_simple(f"Base Score Override##{menu_id}"):
                        static.states["target_name"] = f"Ability Base Score Override, {ability_name}"
                        static.states["target_ref"] = f"ability:{ability_name}:base_score_overrides"
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
                           "all", static, is_feature_bonus=True)

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


def draw_edit_feature(feature: Feature, static: MainWindowProtocol) -> None:
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
        imgui.pop_item_width()

        imgui.text("Description")
        imgui.set_next_window_size_constraints(ImVec2(window_size.x/2, imgui.get_text_line_height() * 5),
                                               ImVec2(window_size.x/2, imgui.get_text_line_height() * 5))
        if imgui.begin_child("description_text"):
            _, feature["description"] = imgui.input_text_multiline(f"##{feature["name"]}_feature_description", 
                                                                feature["description"], 
                                                                ImVec2(-1, imgui.get_text_line_height() * 5), 128)
            imgui.end_child()

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

        if imgui.button(f"New Bonus##{feature["name"]}"):
            imgui.open_popup(f"Bonus for {feature["name"]}##popup")
        draw_edit_feature_bonus(feature, static)

        if feature["bonuses"] != []:
            imgui.separator_text("Bonuses")
            if imgui.begin_table("feature_bonuses", 3, flags=STRIPED_TABLE_FLAGS): # type: ignore
                for idx, feature_bonus in enumerate(feature["bonuses"]):
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
                            delete_target = static.bonus_list_refs[feature_bonus["target"]]
                            delete_idx = delete_target.index(feature_bonus["bonus"])
                            del delete_target[delete_idx]

                            del feature["bonuses"][idx]
                        imgui.pop_style_color(3)
                end_table_nested()

        imgui.spacing()

        if imgui.button("Close", ImVec2(120, 0)):
            imgui.close_current_popup()
            if static.states["feat_name"] != "":
                feature["name"] = static.states["feat_name"]
            static.states["feat_name"] = ""
        imgui.end_popup()