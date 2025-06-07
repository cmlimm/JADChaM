from imgui_bundle import imgui, imgui_md  # type: ignore

from cs_types.core import MainWindowProtocol
from cs_types.spell import Spell
from settings import MARKDOWN_TEXT_TABLE  # type: ignore
from settings import INVISIBLE_TABLE_FLAGS, LIST_TYPE_TO_BONUS  # type: ignore
from stats import draw_rollable_stat_button
from util.custom_imgui import end_table_nested, help_marker


def draw_spell(spell: Spell, static: MainWindowProtocol) -> None:
    if imgui.begin_table(f"{spell["name"]}_preview", 13, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
        imgui.table_next_row(); imgui.table_next_column()
        if imgui.button(f"Use##{spell["name"]}_use_button"):
            pass
        
        imgui.table_next_column()
        
        # NAME
        imgui.align_text_to_frame_padding()
        imgui.text(f"{spell["name"]}"); imgui.same_line()

        imgui.table_next_column()

        # CASTING TIME
        if imgui.begin_table(f"{spell["name"]}_casting_times", 1, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
            for casting_time in spell["casting_time"]:
                imgui.table_next_row(); imgui.table_next_column()
                type = casting_time["type"]
                if type in ["hour", "minute", "round"]:
                    amount = casting_time["amount"]
                    if amount > 1:
                        type += "s"
                    imgui.text(f"{amount} {type}" if amount != 0 else type)
                else:
                    imgui.text(type)
            end_table_nested()
        
        imgui.table_next_column()

        # DURATION
        if imgui.begin_table(f"{spell["name"]}_durations", 1, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
            for duration in spell["duration"]:
                imgui.table_next_row(); imgui.table_next_column()
                duration_type = duration["type"]
                if duration_type == "timed":
                    time = duration["time"]
                    time_type = time["type"]
                    if time_type in ["hour", "minute", "round"]:
                        amount = time["amount"]
                        if amount > 1:
                            time_type += "s"
                        imgui.text(f"{amount} {time_type}" if amount != 0 else time_type)
                    else:
                        imgui.text(time_type)
                else:
                    imgui.text(duration_type)
            end_table_nested()

        imgui.table_next_column()

        # RANGE
        if imgui.begin_table(f"{spell["name"]}_ranges", 1, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
            for spell_range in spell["range"]:
                imgui.table_next_row(); imgui.table_next_column()
                type = spell_range["type"]
                amount = spell_range["amount"]
                imgui.text(f"{amount} {type}" if amount != 0 else type)
            end_table_nested()

        imgui.table_next_column()

        # AREA OF EFFECT
        if imgui.begin_table(f"{spell["name"]}_areas", 1, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
            for area in spell["area"]:
                imgui.table_next_row(); imgui.table_next_column()
                imgui.text(f"{area}")
            end_table_nested()

        imgui.table_next_column()

        # TO HIT
        if spell.get("to_hit", None):
            draw_rollable_stat_button(f"{spell["name"]}_to_hit", 
                                    spell["to_hit"],
                                    LIST_TYPE_TO_BONUS["rollable"],
                                    f"spell:{spell["name"]}:to_hit",
                                    static)

        imgui.table_next_column()

        # DAMAGE
        if imgui.begin_table(f"{spell["name"]}_damage", 1, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
            for damage in spell["damage_inflicted"]:
                imgui.table_next_row(); imgui.table_next_column()
                imgui.text(f"{damage["roll"]["amount"]}d{damage["roll"]["dice"]} {damage["type"]}")
            end_table_nested()

        imgui.table_next_column()

        # CONDITION
        if imgui.begin_table(f"{spell["name"]}_condition", 1, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
            for condition in spell["condition_inflicted"]:
                imgui.table_next_row(); imgui.table_next_column()
                imgui.text(f"{condition["name"]}")
                imgui.same_line()
                help_marker(condition["description"])
            end_table_nested()

        imgui.table_next_column()
        
        # SAVES
        if imgui.begin_table(f"{spell["name"]}_saves", 1, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
            for save in spell["saving_throw"]:
                imgui.table_next_row(); imgui.table_next_column()
                imgui.text(f"{save}")
            end_table_nested()

        imgui.table_next_column()

        # CONCENTRATION
        if spell["concentration"]:
            imgui.align_text_to_frame_padding()
            imgui.text("C")

        imgui.table_next_column()

        # RITUAL
        if spell["ritual"]:
            imgui.align_text_to_frame_padding()
            imgui.text("R")

        imgui.table_next_column()

        # COMPONENTS
        components: list[str] = []
        material_desc = ""
        if spell["components"]["v"]:
            components += ["V"]
        if spell["components"]["s"]:
            components += ["S"]
        if spell["components"]["m"]:
            components += ["M"]
            material_desc = spell["components"]["m"] # type: ignore
        components_string = ", ".join(components)
        imgui.align_text_to_frame_padding()
        imgui.text(components_string)
        if material_desc != "":
            imgui.same_line()
            help_marker(material_desc) # type: ignore

        end_table_nested()
    
    imgui.push_id(f"tags_{spell["name"]}")
    imgui_md.render(f"**Tags**: {", ".join(spell["tags"])}")
    imgui.pop_id()

    
def draw_spells(static: MainWindowProtocol) -> None:
    if imgui.button("Spells"):
        imgui.open_popup("Modify Spells")

    if imgui.begin_popup("Modify Spells"):
        if imgui.button("New Spell"):
            imgui.open_popup("New Spell")
        if imgui.begin_popup("New spell name"):
            imgui.text("Placeholder")
            imgui.end_popup()

        if imgui.button("Edit Spell Slots"):
            imgui.open_popup("Edit Spell Slots")
        if imgui.begin_popup("Edit Spell Slots"):
            imgui.text("Placeholder")
            imgui.end_popup()
        
        imgui.end_popup()

    spells_list_len = len(static.data["spells"])
    if spells_list_len != 0 and imgui.begin_table("spells_table", 1, flags=MARKDOWN_TEXT_TABLE): # type: ignore
        for _, spell in enumerate(static.data["spells"]):
            if spell["name"] != "no_display":
                imgui.table_next_row(); imgui.table_next_column()
                draw_spell(spell, static)
        end_table_nested()
        