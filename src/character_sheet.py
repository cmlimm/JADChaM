from imgui_bundle import icons_fontawesome_6, imgui

from base_sheet import (
    draw_abilities,
    draw_armor_class_button,
    draw_class,
    draw_conditions,
    draw_damage_effects,
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
from cs_types.core import MainWindowProtocol
from features import draw_features
from settings import INVISIBLE_TABLE_FLAGS, STRIPED_TABLE_FLAGS  # type: ignore
from spells import draw_spells
from util.custom_imgui import draw_text_cell, end_table_nested
from util.sheet import draw_exhaustion_penalty


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

        imgui.spacing()

        table_id = "damage_effects_conditions"
        if imgui.begin_table(table_id, 2, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
            imgui.table_next_row(); imgui.table_next_column()
            imgui.align_text_to_frame_padding()
            imgui.text("Damage Effects"); imgui.same_line()
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_damage_effects"):
                imgui.open_popup("Edit Damage Effects")
            draw_damage_effects(static)

            imgui.table_next_column()

            imgui.align_text_to_frame_padding()
            imgui.text("Conditions"); imgui.same_line()
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_conditions"):
                imgui.open_popup("Edit Conditions")
            draw_conditions(static)
            end_table_nested()


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
            draw_exhaustion_penalty("rollable", static)
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
            draw_exhaustion_penalty("static", static)

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


def draw_skills_window(static: MainWindowProtocol) -> None:
    if static.is_character_loaded:
        table_id = "skills"
        if imgui.begin_table(table_id, 1, flags=INVISIBLE_TABLE_FLAGS):  # type: ignore
            imgui.align_text_to_frame_padding()
            draw_text_cell("Skills"); imgui.same_line()
            if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_skills"):
                imgui.open_popup("Edit Skills")
            draw_exhaustion_penalty("rollable", static)
            imgui.table_next_row(); imgui.table_next_column()
            draw_skills(static)

            end_table_nested()

        imgui.spacing()

        imgui.align_text_to_frame_padding()
        imgui.text("Passive Skills"); imgui.same_line()
        draw_exhaustion_penalty("rollable", static); imgui.same_line()
        if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}##edit_passive_skills"):
            imgui.open_popup("Edit Passive Skills")
        draw_passives(static)


def draw_features_window(static: MainWindowProtocol) -> None:
    if static.is_character_loaded:
        draw_features("All Features", static)


def draw_spells_window(static: MainWindowProtocol) -> None:
    if static.is_character_loaded:
        draw_spells(static)


def draw_training_window(static: MainWindowProtocol) -> None:
    if static.is_character_loaded:
        imgui.align_text_to_frame_padding()
        imgui.text("Proficiencies & Training"); imgui.same_line()
        if imgui.button(f"{icons_fontawesome_6.ICON_FA_PENCIL}"):
            imgui.open_popup("Edit Proficiencies & Training")
        draw_training(static)