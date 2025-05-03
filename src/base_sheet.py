import itertools

from imgui_bundle import hello_imgui  # type: ignore
from imgui_bundle import imgui_md  # type: ignore
from imgui_bundle import ImVec2, icons_fontawesome_6, imgui, immapp  # type: ignore

from cs_types import Feature, MainWindowProtocol
from features import draw_edit_feature
from settings import MARKDOWN_TEXT_TABLE  # type: ignore
from settings import STRIPED_TABLE_FLAGS  # type: ignore
from settings import (  # type: ignore
    ADVANTAGE_ACTIVE_COLOR,
    ADVANTAGE_COLOR,
    ADVANTAGE_HOVER_COLOR,
    DISADVANTAGE_ACTIVE_COLOR,
    DISADVANTAGE_COLOR,
    DISADVANTAGE_HOVER_COLOR,
    INVISIBLE_TABLE_FLAGS,
    MAGICAL_WORD_WRAP_NUMBER_TABLE,
    MEDIUM_STRING_INPUT_WIDTH,
    SHORT_STRING_INPUT_WIDTH,
    THREE_DIGIT_BUTTONS_INPUT_WIDTH,
    TWO_DIGIT_BUTTONS_INPUT_WIDTH,
    TWO_DIGIT_INPUT_WIDTH,
)
from stats import draw_rollable_stat_button, draw_static_stat_button
from util_cs_types import isRepresentInt
from util_gui import draw_open_image_button, draw_text_cell, end_table_nested
from util_sheet import (
    draw_add_bonus,
    draw_bonuses,
    draw_edit_list_popup,
    draw_overrides,
    find_max_override,
    parse_text,
    sum_bonuses,
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
            if not class_dict["name"].startswith("no_display"):
                draw_text_cell(f"{class_dict["name"]}"); imgui.table_next_column()

                if imgui.button(f"{class_dict["level"]}##class_{class_dict["name"]}"):
                    imgui.open_popup(f"##{class_dict["name"]}_edit_class")

                if imgui.begin_popup(f"##{class_dict["name"]}_edit_class"):
                    if imgui.begin_table("class_settings", 2, flags=imgui.TableFlags_.sizing_fixed_fit):  # type: ignore
                        draw_text_cell("Class"); imgui.table_next_column()
                        imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
                        _, class_dict["name"] = imgui.input_text("##class", class_dict["name"], 128)

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

        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
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
        imgui.pop_style_color(3)
        imgui.same_line()

        imgui.push_item_width(TWO_DIGIT_INPUT_WIDTH)
        _, static.states["hp_add"] = imgui.input_text("##hp_add", static.states["hp_add"], 128)
        imgui.same_line()

        imgui.push_style_color(imgui.Col_.button.value, ADVANTAGE_COLOR)
        imgui.push_style_color(imgui.Col_.button_hovered.value, ADVANTAGE_HOVER_COLOR)
        imgui.push_style_color(imgui.Col_.button_active.value, ADVANTAGE_ACTIVE_COLOR)
        if imgui.button("Heal"):
            if isRepresentInt(static.states["hp_add"]):
                static.data["hp"]["current"] += int(static.states["hp_add"])
                if static.data["hp"]["current"] >= static.data["hp"]["max_total"]:
                    static.data["hp"]["current"] = static.data["hp"]["max_total"]
            static.states["hp_add"] = ""
        imgui.pop_style_color(3)

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

            imgui.separator_text(f"New Max HP bonus:")
            draw_add_bonus("max_hp_bonus", static.data["hp"]["bonuses"], "hp", static)
            
            imgui.end_popup()

        imgui.table_next_column()
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        _, static.data["hp"]["temp"] = imgui.input_int("##hp_temp", static.data["hp"]["temp"])

        end_table_nested()

def draw_abilities(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["abilities"], "ability", "Edit Abilities", static)

    abilities_list_length = len(static.data["abilities"])
    if abilities_list_length != 0 and imgui.begin_table("abilities_table", abilities_list_length, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
        imgui.table_next_row()
        for ability in static.data["abilities"]:
            if not ability["name"].startswith("no_display"):
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
                    imgui.open_popup(f"{ability["name"]}_edit_ability")

                if imgui.begin_popup(f"{ability["name"]}_edit_ability"):
                    imgui.align_text_to_frame_padding()
                    imgui.text(f"Base Score"); imgui.same_line()
                    imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                    _, ability["base_score"] = imgui.input_int("##base_score", ability["base_score"])
                    imgui.pop_item_width()

                    if ability["base_score_bonuses"] != []:
                        imgui.separator_text(f"Base Score bonuses")
                        draw_bonuses(f"{ability["name"]}_base_score_bonus_list", ability["base_score_bonuses"], static)
                    if ability["base_score_overrides"] != []:
                        imgui.separator_text(f"Base Score overrides")
                        draw_overrides(f"{ability["name"]}_base_score_overrides", ability["base_score_overrides"], override_idx, is_override, static)
                    if ability["modifier_bonuses"] != []:
                        imgui.separator_text(f"Modifier bonuses")
                        draw_bonuses(f"{ability["name"]}_modifier_bonus_list", ability["modifier_bonuses"], static)

                    imgui.separator_text("New Bonus ")

                    items = ["Base Score", "Base Score Override", "Modifier"]
                    imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
                    _, static.states["ability_bonus_type_idx"] = imgui.combo(f"##{ability["name"]}_select_bonus_type", 
                                                                             static.states["ability_bonus_type_idx"], 
                                                                             items, len(items)); imgui.same_line()
                    imgui.pop_item_width()
                    
                    if ability["base_score_bonuses"] != []:
                        imgui.separator_text(f"Base Score bonuses")
                        draw_bonuses(f"{ability["name"]}_base_score_bonus_list", ability["base_score_bonuses"], static)
                    if ability["base_score_overrides"] != []:
                        imgui.separator_text(f"Base Score overrides")
                        draw_overrides(f"{ability["name"]}_base_score_overrides", ability["base_score_overrides"], override_idx, is_override, static)
                    if ability["modifier_bonuses"] != []:
                        imgui.separator_text(f"Modifier bonuses")
                        draw_bonuses(f"{ability["name"]}_modifier_bonus_list", ability["modifier_bonuses"], static)

                    if static.states["ability_bonus_type_idx"] == 0:
                        # Base Score bonus
                        draw_add_bonus("base_score_bonus", ability["base_score_bonuses"], "base_score", static)
                    elif static.states["ability_bonus_type_idx"] == 1:
                        # Base Score override
                        draw_add_bonus("base_score_override", ability["base_score_overrides"], "base_score", static)
                    elif static.states["ability_bonus_type_idx"] == 2:
                        # Modifier bonus
                        draw_add_bonus("modifier_bonus", ability["modifier_bonuses"], "base_score", static)

                    imgui.end_popup()
        end_table_nested()
            

def draw_saves(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["saves"], "save", "Edit Saves", static)

    saves_list_length = len(static.data["saves"])
    if saves_list_length != 0 and imgui.begin_table("saves_table", 4, flags=STRIPED_TABLE_FLAGS): # type: ignore
        for save in static.data["saves"]:
            if not save["name"].startswith("no_display"):
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(save["name"]); imgui.table_next_column()
                draw_rollable_stat_button(save["name"], save, "rollable", static)
        
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
    draw_rollable_stat_button("initiative", static.data["initiative"], "rollable", static)


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
        draw_add_bonus(f"ac_bonus", armor_class["bonuses"], "armor_class", static, 1)

        imgui.end_popup()


def draw_speed(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["speed"], "speed", "Edit Speed", static)

    speed_list_length = len(static.data["speed"])
    if speed_list_length != 0 and imgui.begin_table("saves_table", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
        for speed in static.data["speed"]:
            if not speed["name"].startswith("no_display"):
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(speed["name"]); imgui.table_next_column()
                draw_static_stat_button(speed["name"], speed, "speed", static, numerical_step=5)
        
        end_table_nested()

def draw_passives(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["passive_skill"], "passive", "Edit Passive Skills", static)

    passive_list_length = len(static.data["passive_skill"])
    if passive_list_length != 0 and imgui.begin_table("saves_table", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
        for passive in static.data["passive_skill"]:
            if not passive["name"].startswith("no_display"):
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(passive["name"]); imgui.table_next_column()
                draw_static_stat_button(passive["name"], passive, "passive", static)
        
        end_table_nested()

def draw_senses(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["sense"], "sense", "Edit Senses", static)

    sense_list_length = len(static.data["sense"])
    if sense_list_length != 0 and imgui.begin_table("saves_table", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
        for sense in static.data["sense"]:
            if not sense["name"].startswith("no_display"):
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(sense["name"]); imgui.table_next_column()
                draw_static_stat_button(sense["name"], sense, "sense", static)
        
        end_table_nested()

def draw_training(static: MainWindowProtocol) -> None:
    training = static.data["training"]

    if imgui.begin_table("training", 2, flags=STRIPED_TABLE_FLAGS):  # type: ignore
        width = imgui.get_window_width()
        for proficiency_type, proficiencies_list in itertools.groupby(training, key=lambda x: x["type"]):
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text(proficiency_type)
            
            # Sort so that the order of the types is always the same regargdless of the order
            # proficiencies were added
            items = list(proficiencies_list)
            items.sort(key=lambda x: x["name"])
            imgui.table_next_column()
            imgui.push_text_wrap_pos(imgui.get_cursor_pos()[0] + width - MAGICAL_WORD_WRAP_NUMBER_TABLE)
            imgui.text(", ".join([item["name"] for item in items]))
            imgui.pop_text_wrap_pos()
        end_table_nested()
    
    center = imgui.get_main_viewport().get_center()
    imgui.set_next_window_pos(center, imgui.Cond_.appearing.value, ImVec2(0.5, 0.5))

    popup_name = "Edit Tool and Language Proficiencies"
    if imgui.begin_popup_modal(popup_name, None, imgui.WindowFlags_.always_auto_resize.value)[0]:
        imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
        _, static.states["new_training"]["name"] = imgui.input_text_with_hint(
            "##new_training_name", "Name", static.states["new_training"]["name"], 128)
        imgui.same_line()
        
        imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
        _, static.states["new_training"]["type"] = imgui.input_text_with_hint(
            "##new_training_type", "Type", static.states["new_training"]["type"], 128)
        imgui.same_line()
        
        imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
        _, static.states["new_training"]["source"] = imgui.input_text_with_hint(
            "##new_training_source", "Source", static.states["new_training"]["source"], 128)
        imgui.same_line()
        
        if imgui.button("Add##add_new_training") and static.states["new_training"]["name"] != "":
            if static.states["new_training"]["type"] == "":
                static.states["new_training"]["type"] = "Other"

            training.append({
                "name": static.states["new_training"]["name"],
                "type": static.states["new_training"]["type"],
                "source": static.states["new_training"]["source"],
                "manual": True
            })

            static.states["new_training"] = {
                "name": "",
                "type": "",
                "source": "",
                "manual": True
            }

        if imgui.begin_table("training_edit_list", 2, flags=STRIPED_TABLE_FLAGS):  # type: ignore
            for training_type, training_list in itertools.groupby(training, key=lambda x: x["type"]):
                draw_text_cell(training_type); imgui.table_next_column()
                
                # Sort so that the order of the types is always the same regargdless of the order
                # proficiencies were added
                items = list(training_list)
                items.sort(key=lambda x: x["name"])

                if imgui.begin_table("training_of_type", 3, flags=INVISIBLE_TABLE_FLAGS):  # type: ignore
                    for item in items:
                        draw_text_cell(item["name"]); imgui.table_next_column(); imgui.align_text_to_frame_padding()
                        imgui.text(item["source"]); imgui.table_next_column()

                        if item["manual"]:
                            imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                            imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                            imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
                            if imgui.button(f"{icons_fontawesome_6.ICON_FA_XMARK}##{training_type}_{item["name"]}"):
                                delete_idx = training.index(item)
                                del training[delete_idx]
                            imgui.pop_style_color(3)
                    end_table_nested()
            end_table_nested()
        
        imgui.spacing()
        if imgui.button("Close", ImVec2(120, 0)):
            imgui.close_current_popup()
        imgui.end_popup()


def draw_skills(static: MainWindowProtocol) -> None:
    draw_edit_list_popup(static.data["skills"], "skill", "Edit Skills", static)

    skill_list_length = len(static.data["skills"])
    if skill_list_length != 0 and imgui.begin_table("skills_table", 2, flags=STRIPED_TABLE_FLAGS): # type: ignore
        for skill in static.data["skills"]:
            if not skill["name"].startswith("no_display"):
                imgui.table_next_column(); imgui.align_text_to_frame_padding()
                imgui.text(skill["name"]); imgui.table_next_column()
                draw_rollable_stat_button(skill["name"], skill, "rollable", static)
        
        end_table_nested()


def draw_feature(feature: Feature, idx: int, static: MainWindowProtocol) -> None:
    imgui.spacing()
    if imgui.button(f"{feature["name"]}##{idx}"):
        static.states["feat_name"] = feature["name"]
        imgui.open_popup(f"Edit {feature["name"]}##popup")
    draw_edit_feature(feature, static)

    imgui.spacing()
    
    description = parse_text(feature["description"], static)
    split_description = description.split("\n\n")
    for line in split_description:
        imgui_md.render(line)
    
    imgui.spacing()
    imgui.push_id(f"tags_{feature["name"]}_{idx}")
    imgui_md.render(f"**Tags**: {", ".join(feature["tags"])}")
    imgui.pop_id()
    imgui.spacing()

def draw_features(static: MainWindowProtocol) -> None:
    features_list_length = len(static.data["features"])
    if features_list_length != 0 and imgui.begin_table("features_table", 1, flags=MARKDOWN_TEXT_TABLE): # type: ignore
        for idx, feature in enumerate(static.data["features"]):
            if not feature["name"].startswith("no_display"):
                imgui.table_next_row(); imgui.table_next_column()
                draw_feature(feature, idx, static)
        end_table_nested()