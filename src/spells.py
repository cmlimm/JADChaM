import copy
import json

from imgui_bundle import imgui, imgui_md  # type: ignore

from cs_types.core import MainWindowProtocol
from cs_types.spell import Spell
from settings import MARKDOWN_TEXT_TABLE  # type: ignore
from settings import INVISIBLE_TABLE_FLAGS, LIST_TYPE_TO_BONUS  # type: ignore
from stats import draw_rollable_stat_button
from util.custom_imgui import end_table_nested, help_marker


def process_spell_from_file(static: MainWindowProtocol, idx: int) -> None:
    with open("assets/spells-phb.json") as spell_file:
        spells = json.load(spell_file)["spell"]
    
    for spell_json in spells:
        # spell_json = spells[idx]
        spell_py = {}

        spell_py["name"] = spell_json["name"]
        spell_py["level"] = spell_json["level"]
        spell_py["school"] = spell_json["school"]

        spell_py["description"] = ""
        description_lines = []
        entries = spell_json.get("entries", [])
        higher_level = spell_json.get("entriesHigherLevel", [])
        for entry in entries:
            if isinstance(entry, str):
                description_lines.append(entry) # type: ignore
        if higher_level: 
            description_lines.append("\nAt Higher Levels:") # type: ignore
        for entry in higher_level:
            higher_entries = entry.get("entries", [])
            for higher_entry in higher_entries:
                if isinstance(higher_entry, str):
                    description_lines.append(higher_entry) # type: ignore
        spell_py["description"] = "\n".join(description_lines) # type: ignore

        # TODO: temp
        spell_py["classes"] = []
        spell_py["subclasses"] = []

        spell_py["casting_time"] = []
        if times := spell_json.get("casting_time"):
            for time in times:
                spell_py["casting_time"].append({ # type: ignore
                    "type": time["unit"],
                    "amount": time["number"]
                })

        spell_py["concentration"] = False
        spell_py["duration"] = []
        if durations := spell_json.get("duration"):
            for duration in durations:
                duration_type = duration["type"]
                time_type = "no_display"
                time_amount = 0
                if time := duration.get("duration"):
                    time_type = time["type"]
                    time_amount = int(time["amount"])
                spell_py["duration"].append({ # type: ignore
                    "type": duration_type,
                    "time": {
                        "type": time_type,
                        "amount": time_amount
                    }
                })
                if duration.get("concentration", False):
                    spell_py["concentration"] = True

        spell_py["range"] = []
        if range := spell_json.get("range"):
            if range["type"] == "special":
                spell_py["range"].append({ # type: ignore
                        "type": "special",
                        "amount": 0
                })
            else:
                spell_py["range"].append({ # type: ignore
                    "type": range["distance"]["type"],
                    "amount": range["distance"].get("amount", 0)
                })
                        
        area_dict =  {
            "C": "Cube",
            "H": "Hemisphere",
            "L": "Line",
            "MT": "Multiple Targets",
            "N": "Cone",
            "Q": "Square",
            "R": "Circle",
            "ST": "Single Target",
            "S": "Sphere",
            "W": "Wall",
            "Y": "Cylinder",
        }
        spell_py["area"] = []
        if areas := spell_json.get("areaTags"):
            for area in areas:
                spell_py["area"].append(area_dict[area]) # type: ignore

        spell_py["components"] = {
            "v": spell_json.get("components", {}).get("v", False),
            "s": spell_json.get("components", {}).get("s", False),
            "m": spell_json.get("components", {}).get("m", False)
        }
        if isinstance(spell_py["components"]["m"], dict):
            spell_py["components"]["m"] = spell_py["components"]["m"]["text"]

        spell_py["ritual"] = spell_json.get("meta", {}).get("ritual", False)

        spell_py["to_hit"] = {
            "name": spell_py["name"],
            "total": 0,
            "bonuses": [
                {
                    "name": "Manual",
                    "value": 0,
                    "multiplier": 1.0,
                    "manual": False
                },
            ],
            "manual_advantage": False,
            "manual_disadvantage": False,
            "manual": True
        }

        
        spell_py["damage"] = []
        if damage := spell_json.get("scalingLevelDice"):
            roll = {
                "dice": damage["scaling"]["1"].split("d")[1],
                "amount": damage["scaling"]["1"].split("d")[0]
            }
            scaling = {} # type: ignore
            for key, value in damage["scaling"].items():
                scaling[int(key)] = {}
                scaling[int(key)]["dice"] = value.split("d")[1]
                scaling[int(key)]["amount"] = value.split("d")[0]
            spell_py["damage"].append({ # type: ignore
                "roll": roll,
                "scaling": scaling
            })

        spell_py["damage_type"] = spell_json.get("damageInflict", [])

        spell_py["condition_inflicted"] = []
        if conditions := spell_json.get("conditionInflict", None):
            for condition in conditions:
                condition_py = next((item for item in static.data["default_conditions"] if item["name"] == condition.title()), None)
                if condition_py:
                    spell_py["condition_inflicted"].append(condition_py) # type: ignore
                else:
                    spell_py["condition_inflicted"].append({ # type: ignore
                        "name": condition.title(),
                        "description": "",
                        "enabled": False,
                        "custom": True
                    })
        
        spell_py["saving_throw"] = []
        if saves := spell_json.get("savingThrow", None):
            for save in saves:
                spell_py["saving_throw"].append(save[:3].upper()) # type: ignore

        spell_py["tags"] = []

        static.data["spells"].append(copy.deepcopy(spell_py)) # type: ignore
        static.data_refs[f"spell:{spell_py["name"]}:to_hit"] = static.data["spells"][-1]["to_hit"] # type: ignore
        static.bonus_list_refs[f"spell:{spell_py["name"]}:to_hit:bonuses"] = static.data["spells"][-1]["to_hit"]["bonuses"]


def draw_spell(spell: Spell, static: MainWindowProtocol) -> None:
    if imgui.begin_table(f"{spell["name"]}_preview", 14, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
        imgui.table_next_row(); imgui.table_next_column()
        if imgui.button(f"Use##{spell["name"]}_use_button"):
            pass
        
        imgui.table_next_column()
        
        # NAME
        imgui.align_text_to_frame_padding()
        imgui.text(f"{spell["name"]}"); imgui.same_line()
        help_marker(spell["description"])

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
            for damage in spell["damage"]:
                imgui.table_next_row(); imgui.table_next_column()
                imgui.text(f"{damage["roll"]["amount"]}d{damage["roll"]["dice"]}")
            end_table_nested()

        imgui.table_next_column()

        # DAMAGE TYPE
        if imgui.begin_table(f"{spell["name"]}_damage_type", 1, flags=INVISIBLE_TABLE_FLAGS): # type: ignore
            for damage_type in spell["damage_type"]:
                imgui.table_next_row(); imgui.table_next_column()
                imgui.text(f"{damage_type}")
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
            # imgui.open_popup("New Spell")
            imgui.open_popup("New spell name")
        if imgui.begin_popup("New spell name"):
            _, static.states["number"] = imgui.input_int("idx", static.states["number"])
            if static.states["number"] < 0: static.states["number"] = 0
            if imgui.button("Add##new_spell"):
                static.states["number"] += 1
                print(static.states["number"])
                process_spell_from_file(static, static.states["number"])
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
        