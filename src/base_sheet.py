from imgui_bundle import hello_imgui  # type: ignore
from imgui_bundle import ImVec2, icons_fontawesome_6, imgui, immapp  # type: ignore

from cs_types.core import MainWindowProtocol
from cs_types.guards import isRepresentInt
from settings import (  # type: ignore
    DAMAGE_EFFECTS_DEFAULT,
    DAMAGE_TYPES,
    INVISIBLE_TABLE_FLAGS,
    LARGE_STRING_INPUT_WIDTH,
    LIST_TYPE_TO_BONUS,
    MEDIUM_STRING_INPUT_WIDTH,
    PROFICIENCIES_DEFAULT,
    PROFICIENCIES_TYPES,
    SHORT_STRING_INPUT_WIDTH,
    STRIPED_TABLE_FLAGS,
    THREE_DIGIT_BUTTONS_INPUT_WIDTH,
    TWO_DIGIT_BUTTONS_INPUT_WIDTH,
    TWO_DIGIT_INPUT_WIDTH,
)
from stats import draw_rollable_stat_button, draw_static_stat_button
from util.calc import calc_static_stat, find_max_override, sum_bonuses
from util.custom_imgui import ColorButton, draw_text_cell, end_table_nested, help_marker
from util.sheet import (
    draw_add_bonus,
    draw_bonuses,
    draw_edit_list_popup,
    draw_open_image_button,
    draw_overrides,
    draw_roll_menu,
    draw_roll_popup,
    draw_text_table,
)


def draw_name(static: MainWindowProtocol) -> None:
    imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
    _, static.data["name"] = imgui.input_text("##name", static.data["name"], 128)


def draw_image(static: MainWindowProtocol) -> None:
    if static.data["image_path"] == "":
        draw_open_image_button(static)    
    else:
        hello_imgui.image_from_asset(static.data["image_path"], immapp.em_to_vec2(0.0, 10.0))

        if imgui.button("Remove Image"):
            static.data["image_path"] = ""


def draw_class(static: MainWindowProtocol) -> None:
    static.data["level"]["total"] = sum([item["level"] for item in static.data["level"]["classes"]])
    
    # Draw title
    imgui.text(f"Level {static.data["level"]["total"]}")
    imgui.same_line()
    if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_classes"):
        imgui.open_popup("Edit Classes")
    draw_edit_list_popup(static.data["level"]["classes"], "level", "Edit Classes", static)

    if imgui.begin_table("classes", 2, flags=STRIPED_TABLE_FLAGS):  # type: ignore
        for class_dict in static.data["level"]["classes"]:
            class_dict["total"] = class_dict["level"]
            if class_dict["name"] != "no_display":
                draw_text_cell(f"{class_dict["name"]}"); imgui.table_next_column()

                # Recalculate spell save even if the button is not visible
                if class_dict["spell_save_enabled"]:
                    calc_static_stat(class_dict["spell_save"], static)

                if imgui.button(f"{class_dict["level"]}##class_{class_dict["name"]}"):
                    imgui.open_popup(f"##{class_dict["id"]}_edit_class")

                if imgui.begin_popup(f"##{class_dict["id"]}_edit_class"):
                    if imgui.begin_table("class_settings", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
                        draw_text_cell("Class"); imgui.table_next_column()
                        imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
                        _, class_dict["name"] = imgui.input_text(f"##{class_dict["id"]}_name", class_dict["name"], 128)

                        draw_text_cell("Subclass"); imgui.table_next_column()
                        imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
                        _, class_dict["subclass"] = imgui.input_text("##subclass", class_dict["subclass"], 128)

                        draw_text_cell("Level"); imgui.table_next_column()
                        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                        _, class_dict["level"] = imgui.input_int("##level", class_dict["level"])

                        draw_text_cell(f"HP dice"); imgui.table_next_column()
                        dice_types = ["4", "6", "8", "10", "12", "20"]
                        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                        _, static.states["hp_dice_idx"] = imgui.combo(
                            f"##dice",
                            dice_types.index(str(class_dict["dice"])),
                            dice_types,
                            len(dice_types))
                        class_dict["dice"] = int(dice_types[static.states["hp_dice_idx"]])

                        draw_text_cell(f"Has Spellcasting"); imgui.table_next_column()
                        changed, class_dict["spell_save_enabled"] = imgui.checkbox(f"##{class_dict["id"]}_spell_save_enabled", 
                                                                             class_dict["spell_save_enabled"])
                        if changed and class_dict["spell_save_enabled"]:
                            static.data_refs[f"spell_save:{class_dict["id"]}"] = class_dict["spell_save"]
                            static.bonus_list_refs[f"spell_save:{class_dict["id"]}:bonuses"] = class_dict["spell_save"]["bonuses"]
                        if changed and not class_dict["spell_save_enabled"]:
                            del static.data_refs[f"spell_save:{class_dict["id"]}"]
                            del static.bonus_list_refs[f"spell_save:{class_dict["id"]}:bonuses"]

                        if class_dict["spell_save_enabled"]:
                            draw_text_cell(f"Spell Save"); imgui.table_next_column()
                            draw_static_stat_button(f"{class_dict["id"]}_spell_save", 
                                                    class_dict["spell_save"],
                                                    LIST_TYPE_TO_BONUS["all_no_advantage"],
                                                    "spell_save",
                                                    static)
                        end_table_nested()

                    if class_dict["spell_save_enabled"]:
                        imgui.separator_text("Spell Slots per Class Level")
                        
                        imgui.align_text_to_frame_padding()
                        imgui.text("When Multiclassing, use this ratio of this class spell slots"); imgui.same_line()

                        imgui.push_item_width(TWO_DIGIT_INPUT_WIDTH)
                        _, class_dict["multiclass_ratio"] = imgui.input_float(f"##use_multiclass_spell_slots_{class_dict["id"]}", 
                                                                              class_dict["multiclass_ratio"], format="%.1f")
                        
                        imgui.align_text_to_frame_padding()
                        imgui.text("Special name for Spell Slots"); imgui.same_line()

                        imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
                        _, class_dict["separate_slots_name"] = imgui.input_text_with_hint(f"##special_slots_name_{class_dict["id"]}",
                                                                                          "Like 'Pact'", class_dict["separate_slots_name"], 128)

                        imgui.align_text_to_frame_padding()
                        imgui.text("Max Spell Slot"); imgui.same_line()
                        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                        changed, max_spell_slot = imgui.input_int(f"##max_spell_slot_{class_dict["id"]}", len(class_dict["spell_slots"][0]))
                        if max_spell_slot < 0: max_spell_slot = 0
                        
                        if changed and max_spell_slot > len(class_dict["spell_slots"][0]):
                            for level in class_dict["spell_slots"]:
                                level.append(0)
                        if changed and max_spell_slot < len(class_dict["spell_slots"][0]):
                            for level in class_dict["spell_slots"]:
                                level.pop()
                        
                        if imgui.begin_table(f"spell_slots_{class_dict["id"]}", max_spell_slot + 1, STRIPED_TABLE_FLAGS):
                            imgui.table_setup_column("")
                            for spell_level in range(1, max_spell_slot + 1):
                                imgui.table_setup_column(f"{spell_level}")
                            imgui.table_headers_row()

                            for class_level in range(1, 21):
                                imgui.table_next_row()
                                imgui.table_next_column()
                                imgui.align_text_to_frame_padding()
                                imgui.text(f"{class_level}")

                                for spell_level in range(1, max_spell_slot + 1):
                                    imgui.table_next_column()
                                    imgui.push_item_width(TWO_DIGIT_INPUT_WIDTH)
                                    _, class_dict["spell_slots"][class_level - 1][spell_level - 1] = imgui.input_int(f"##spell_slots_{class_level}_{spell_level}_{class_dict["id"]}",
                                                                                                                     class_dict["spell_slots"][class_level - 1][spell_level - 1], 0)
                                    
                            end_table_nested()

                    imgui.end_popup()
        end_table_nested()


def draw_hp(static: MainWindowProtocol) -> None:
    if imgui.begin_table("hp_table", 3, flags=STRIPED_TABLE_FLAGS):  # type: ignore
        imgui.table_setup_column("Hit Points")
        imgui.table_setup_column("Current / Max")
        imgui.table_setup_column("Temp")
        imgui.table_headers_row()

        imgui.table_next_row()
        imgui.table_next_column()

        with ColorButton("bad"):
            if imgui.button("Damage"):
                if isRepresentInt(static.states["hp_add"]):
                    int_hp_add = int(static.states["hp_add"])
                    if static.data["hp"]["temp"] != 0:
                        if int_hp_add <= static.data["hp"]["temp"]:
                            static.data["hp"]["temp"] -= int_hp_add
                            int_hp_add = 0
                        else:
                            int_hp_add -= static.data["hp"]["temp"]
                            static.data["hp"]["temp"] = 0
                    static.data["hp"]["current"] -= int_hp_add
                    if static.data["hp"]["current"] < 0:
                        static.data["hp"]["current"] = 0
                static.states["hp_add"] = ""
        imgui.same_line()

        imgui.push_item_width(TWO_DIGIT_INPUT_WIDTH)
        _, static.states["hp_add"] = imgui.input_text("##hp_add", static.states["hp_add"], 128)
        imgui.same_line()

        with ColorButton("good"):
            if imgui.button("Heal"):
                if isRepresentInt(static.states["hp_add"]):
                    static.data["hp"]["current"] += int(static.states["hp_add"])
                    if static.data["hp"]["current"] >= static.data["hp"]["max_total"]:
                        static.data["hp"]["current"] = static.data["hp"]["max_total"]
                static.states["hp_add"] = ""

        imgui.table_next_column()
        total_bonus, _ = sum_bonuses(static.data["hp"]["bonuses"], static)
        static.data["hp"]["max_total"] = static.data["hp"]["max_base"] + total_bonus

        imgui.align_text_to_frame_padding()
        imgui.text(f"{static.data["hp"]["current"]} / {static.data["hp"]["max_total"]}")
        imgui.same_line()
        if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}"):
            imgui.open_popup("edit_max_hp")

        if imgui.begin_popup("edit_max_hp"):
            imgui.align_text_to_frame_padding();
            imgui.text(f"Max HP"); imgui.same_line()
            imgui.push_item_width(THREE_DIGIT_BUTTONS_INPUT_WIDTH)
            _, static.data["hp"]["max_base"] = imgui.input_int("##max_hp", static.data["hp"]["max_base"])
            
            if static.data["hp"]["bonuses"] != []:
                imgui.separator_text(f"Max HP bonuses")
                draw_bonuses("hp_bonus_list", static.data["hp"]["bonuses"], static)

            imgui.separator_text(f"New Max HP bonus")
            draw_add_bonus("max_hp_bonus", 
                           "hp", 
                           static.data["hp"]["bonuses"], 
                           LIST_TYPE_TO_BONUS["all_no_advantage"], 
                           static)
            
            imgui.end_popup()

        imgui.table_next_column()
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        _, static.data["hp"]["temp"] = imgui.input_int("##hp_temp", static.data["hp"]["temp"])

        end_table_nested()


def draw_damage_effects(static: MainWindowProtocol) -> None:
    draw_text_table("Damage Effects", static.data["damage_effects"], DAMAGE_TYPES, DAMAGE_EFFECTS_DEFAULT, static)


def draw_conditions(static: MainWindowProtocol) -> None:
    all_conditions = static.data["default_conditions"] + static.data["custom_conditions"]

    if imgui.begin_table("conditions_table", 1, STRIPED_TABLE_FLAGS): # type: ignore
        if static.data["exhaustion"]["total"] > 0 and static.data["exhaustion"]["total"] < 6:
            draw_text_cell(f"Exhaustion ({static.data["exhaustion"]["total"]})"); imgui.same_line()
            help_marker(static.data["exhaustion"]["description"])
        elif static.data["exhaustion"]["total"] == 6:
            draw_text_cell("Exhaustion (Dead)"); imgui.same_line()
            help_marker(static.data["exhaustion"]["description"])

        for condition in all_conditions:
            if condition["enabled"]:
                draw_text_cell(condition["name"]); imgui.same_line()
                help_marker(condition["description"])
        end_table_nested()

    popup_name = f"Edit Conditions"
    if imgui.begin_popup_modal(popup_name, None, imgui.WindowFlags_.always_auto_resize.value)[0]:
        imgui.align_text_to_frame_padding()
        imgui.text("Exhaustion"); imgui.same_line()
        help_marker(static.data["exhaustion"]["description"]); imgui.same_line()
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        changed, static.data["exhaustion"]["total"] = imgui.input_int("##exhaustion",
                                                                      static.data["exhaustion"]["total"])
        imgui.pop_item_width()
        
        if changed and static.data["exhaustion"]["total"] > 6:
            static.data["exhaustion"]["total"] = 6
        elif changed and static.data["exhaustion"]["total"] < 0:
            static.data["exhaustion"]["total"] = 0

        if imgui.begin_table("edit_conditions_table", 3, STRIPED_TABLE_FLAGS): # type: ignore
            all_conditions = static.data["default_conditions"] + static.data["custom_conditions"]

            for idx, condition in enumerate(all_conditions):
                draw_text_cell(condition["name"]); imgui.same_line()
                help_marker(condition["description"])

                imgui.table_next_column()
                _, condition["enabled"] = imgui.checkbox(f"##{condition["name"]}_{idx}", condition["enabled"])

                if condition["custom"]:
                    imgui.table_next_column()

                    with ColorButton("bad"):
                        if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{condition["name"]}_{idx}"):
                            idx_delete = static.data["custom_conditions"].index(condition)
                            del static.data["custom_conditions"][idx_delete]
            end_table_nested()

        imgui.spacing()
        imgui.separator_text("New Condition")
        
        imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
        _, static.states["new_condition_name"] = imgui.input_text_with_hint("##new_condition_name", "Name", static.states["new_condition_name"], 128)
        imgui.pop_item_width()
        imgui.push_item_width(LARGE_STRING_INPUT_WIDTH)
        _, static.states["new_condition_description"] = imgui.input_text_multiline("##new_condition_description", 
                                                                                   static.states["new_condition_description"], 
                                                                                   ImVec2(LARGE_STRING_INPUT_WIDTH, imgui.get_text_line_height() * 5), 
                                                                                   128)
        imgui.pop_item_width()
        
        if imgui.button("Add##new_item") and static.states["new_condition_name"] != "":
            static.data["custom_conditions"].append(
                {
                    "name": static.states["new_condition_name"],
                    "description": static.states["new_condition_description"],
                    "enabled": False,
                    "custom": True
                }
            )
            static.states["new_condition_name"] = ""
            static.states["new_condition_description"] = ""

        imgui.spacing()
        if imgui.button("Close", ImVec2(120, 0)):
            static.states["new_condition_name"] = ""
            static.states["new_condition_description"] = ""
            imgui.close_current_popup()
        imgui.end_popup()
    


def draw_abilities(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["abilities"], "ability", "Edit Abilities", static)

    abilities_list_length = len(static.data["abilities"])
    if abilities_list_length != 0 and imgui.begin_table("abilities_table", abilities_list_length, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
        imgui.table_next_row()
        for ability in static.data["abilities"]:
            if ability["name"] != "no_display":
                base_score_bonus_total, _ = sum_bonuses(ability["base_score_bonuses"], static)
                no_override_base_score_total = ability["base_score"] + base_score_bonus_total
                override_idx, override_value = find_max_override(ability["base_score_overrides"], static)

                is_override = False
                if override_value > no_override_base_score_total:
                    ability["total_base_score"] = override_value
                    is_override = True
                else:
                    ability["total_base_score"] = no_override_base_score_total
                
                modifier_bonus_total, _ = sum_bonuses(ability["modifier_bonuses"], static)
                ability["total"] = (ability["total_base_score"] - 10) // 2 + modifier_bonus_total

                imgui.table_next_column()
                if imgui.button(f"{ability["name"]}[{ability["total_base_score"]}]\n{ability["total"]:^+}"):
                    imgui.open_popup(f"{ability["id"]}_edit_ability")

                draw_roll_menu(f"{ability["id"]}_ability", "1d20", str(ability["total"]), "Stat", 0, static)

                if imgui.begin_popup(f"{ability["id"]}_edit_ability"):
                    imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
                    _, ability["name"] = imgui.input_text(f"##{ability["id"]}_name", ability["name"], 128)

                    imgui.align_text_to_frame_padding()
                    imgui.text(f"Base Score"); imgui.same_line()
                    imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                    _, ability["base_score"] = imgui.input_int("##base_score", ability["base_score"])
                    imgui.pop_item_width()

                    if ability["base_score_bonuses"] != []:
                        imgui.separator_text(f"Base Score bonuses")
                        draw_bonuses(f"{ability["id"]}_base_score_bonus_list", ability["base_score_bonuses"], static)
                    if ability["base_score_overrides"] != []:
                        imgui.separator_text(f"Base Score overrides")
                        draw_overrides(f"{ability["id"]}_base_score_overrides", ability["base_score_overrides"], override_idx, is_override, static)
                    if ability["modifier_bonuses"] != []:
                        imgui.separator_text(f"Modifier bonuses")
                        draw_bonuses(f"{ability["id"]}_modifier_bonus_list", ability["modifier_bonuses"], static)

                    imgui.separator_text("New Bonus ")

                    items = ["Base Score", "Base Score Override", "Modifier"]
                    imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
                    _, static.states["ability_bonus_type_idx"] = imgui.combo(f"##{ability["id"]}_select_bonus_type", 
                                                                             static.states["ability_bonus_type_idx"], 
                                                                             items, len(items)); imgui.same_line()
                    imgui.pop_item_width()
                
                    if static.states["ability_bonus_type_idx"] == 0:
                        # Base Score bonus
                        draw_add_bonus("base_score_bonus", 
                                       f"ability:{ability["id"]}",
                                       ability["base_score_bonuses"], 
                                       LIST_TYPE_TO_BONUS["base_score"], 
                                       static)
                    elif static.states["ability_bonus_type_idx"] == 1:
                        # Base Score override
                        draw_add_bonus("base_score_override", 
                                       f"ability:{ability["id"]}",
                                       ability["base_score_overrides"], 
                                       LIST_TYPE_TO_BONUS["base_score"], 
                                       static)
                    elif static.states["ability_bonus_type_idx"] == 2:
                        # Modifier bonus
                        draw_add_bonus("modifier_bonus", 
                                       f"ability:{ability["id"]}",
                                       ability["modifier_bonuses"], 
                                       LIST_TYPE_TO_BONUS["base_score"], 
                                       static)

                    imgui.end_popup()
        end_table_nested()
            

def draw_saves(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["saves"], "save", "Edit Saves", static)

    saves_list_length = len(static.data["saves"])
    if saves_list_length != 0 and imgui.begin_table("saves_table", 4, flags=STRIPED_TABLE_FLAGS): # type: ignore
        for save in static.data["saves"]:
            if save["name"] != "no_display":
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(save["name"]); imgui.table_next_column()
                draw_rollable_stat_button(save["id"], 
                                          save, 
                                          LIST_TYPE_TO_BONUS["rollable"],
                                          "save", 
                                          static)
        
        end_table_nested()


def draw_proficiency_button(static: MainWindowProtocol) -> None:
    proficiency = static.data["proficiency"]

    if imgui.button(f"{proficiency["total"]:^+}"):
        imgui.open_popup(f"edit_proficiency")

    if imgui.begin_popup(f"edit_proficiency"):
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        _, proficiency["total"] = imgui.input_int("##proficiency_total", proficiency["total"])

        imgui.end_popup()


def draw_initiative_button(static: MainWindowProtocol) -> None:
    draw_rollable_stat_button("initiative", 
                              static.data["initiative"], 
                              LIST_TYPE_TO_BONUS["rollable"], 
                              "initiative",
                              static)


def draw_armor_class_button(static: MainWindowProtocol) -> None:
    armor_class = static.data["armor_class"]
    
    base = armor_class["base"]
    max_dex_bonus = 100
    if armor_class["armor"]:
        base = armor_class["armor"]["armor_class"]
        max_dex_bonus = armor_class["armor"]["max_dex_bonus"]

    total_bonus, _ = sum_bonuses(armor_class["bonuses"], static, max_dex_bonus)
    armor_class["total"] = base + total_bonus

    if imgui.button(f"{armor_class["total"]}"):
        imgui.open_popup(f"edit_armor_class")

    if imgui.begin_popup(f"edit_armor_class"):
        imgui.align_text_to_frame_padding()
        imgui.text(f"Base Value"); imgui.same_line()
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        _, armor_class["base"] = imgui.input_int(f"##ac_base_value", armor_class["base"])

        if armor_class["armor"]:
            armor = armor_class["armor"]
            imgui.separator_text("Armor")
            imgui.text(f"    {armor["name"]} " + \
                       f"(AC {armor["armor_class"]}" + \
                       f"{", Max DEX " + str(armor["max_dex_bonus"]) if armor["max_dex_bonus"] != 100 else ""})")
            imgui.spacing()

        if armor_class["bonuses"] != []:
            imgui.separator_text(f"Bonuses")
            draw_bonuses("ac_bonus_list", armor_class["bonuses"], static)

        imgui.separator_text(f"New bonus")
        draw_add_bonus(f"ac_bonus", 
                       "armor_class", 
                       armor_class["bonuses"], 
                       LIST_TYPE_TO_BONUS["armor_class"], 
                       static, 
                       1)

        imgui.end_popup()


def draw_speed(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["speed"], "speed", "Edit Speed", static)

    speed_list_length = len(static.data["speed"])
    if speed_list_length != 0 and imgui.begin_table("saves_table", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
        for speed in static.data["speed"]:
            if speed["name"] != "no_display":
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(speed["name"]); imgui.table_next_column()
                draw_static_stat_button(speed["id"], 
                                        speed, 
                                        LIST_TYPE_TO_BONUS["speed"], 
                                        "speed",
                                        static, 
                                        numerical_step=5)
        
        end_table_nested()


def draw_passives(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["passive_skill"], "passive", "Edit Passive Skills", static)

    passive_list_length = len(static.data["passive_skill"])
    if passive_list_length != 0 and imgui.begin_table("saves_table", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
        for passive in static.data["passive_skill"]:
            if passive["name"] != "no_display":
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(passive["name"]); imgui.table_next_column()
                draw_static_stat_button(passive["id"], 
                                        passive, 
                                        LIST_TYPE_TO_BONUS["passive"],
                                        "passive",
                                        static)
        
        end_table_nested()


def draw_senses(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["sense"], "sense", "Edit Senses", static)

    sense_list_length = len(static.data["sense"])
    if sense_list_length != 0 and imgui.begin_table("saves_table", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
        for sense in static.data["sense"]:
            if sense["name"] != "no_display":
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(sense["name"]); imgui.table_next_column()
                draw_static_stat_button(sense["id"], 
                                        sense, 
                                        LIST_TYPE_TO_BONUS["sense"], 
                                        "sense",
                                        static)
        
        end_table_nested()


def draw_training(static: MainWindowProtocol) -> None:
    draw_text_table("Proficiencies & Training", static.data["training"], PROFICIENCIES_TYPES, PROFICIENCIES_DEFAULT, static)


def draw_skills(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["skills"], "skill", "Edit Skills", static)

    skill_list_length = len(static.data["skills"])
    if skill_list_length != 0 and imgui.begin_table("skills_table", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
        for skill in static.data["skills"]:
            if skill["name"] != "no_display":
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(skill["name"]); imgui.table_next_column()
                draw_rollable_stat_button(skill["id"], 
                                          skill, 
                                          LIST_TYPE_TO_BONUS["rollable"], 
                                          "skill",
                                          static)
        
        end_table_nested()


def draw_status(static: MainWindowProtocol) -> None:
    if static.states["roll_list"] != []:
        imgui.align_text_to_frame_padding()
        imgui.text("Current Roll:"); imgui.same_line()

        imgui.align_text_to_frame_padding()
        imgui.text(", ".join([roll["roll_str"] for roll in static.states["roll_list"]]))
        
        imgui.same_line()
        
        if imgui.button("Roll"):
            static.states["roll_popup_opened"]["status_roll"] = True
            imgui.open_popup(f"roll_popup_status_roll")

        draw_roll_popup("status_roll", static)