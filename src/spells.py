import copy
import json

from imgui_bundle import ImVec2, imgui  # type: ignore

from cs_types.core import MainWindowProtocol
from cs_types.spell import Spell
from settings import STRIPED_TABLE_FLAGS  # type: ignore
from settings import INVISIBLE_TABLE_FLAGS, LIST_TYPE_TO_BONUS  # type: ignore
from stats import draw_rollable_stat_button
from util.custom_imgui import end_table_nested, help_marker
from util.sheet import draw_search_popup


def process_spell_from_file(static: MainWindowProtocol) -> None:
    with open("assets/spells-phb.json") as spell_file:
        spells = json.load(spell_file)["spell"]
    
    static.loaded_spells = []

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
        if times := spell_json.get("time"):
            for time in times:
                type = time["unit"]
                types = {
                    "minute": "m",
                    "minutes": "m",
                    "hour": "h",
                    "hours": "h",
                    "round": "r",
                    "action": "A",
                    "bonus": "BA",
                    "reaction": "R"
                }

                spell_py["casting_time"].append({ # type: ignore
                    "type": types[type],
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
                    types = {
                        "minute": "m",
                        "minutes": "m",
                        "hour": "h",
                        "hours": "h",
                        "day": "d",
                        "year": "y",
                        "round": "r",
                        "action": "A",
                        "bonus": "BA",
                        "reaction": "R",
                    }
                    time_type = types[time["type"]]
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

        static.loaded_spells.append(copy.deepcopy(spell_py)) # type: ignore


def draw_spell(spell: Spell, static: MainWindowProtocol) -> None:
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
            if type in ["h", "m", "r"]:
                amount = casting_time["amount"]
                imgui.text(f"{amount}{type}" if amount != 0 else type)
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
                if time_type in ["h", "m", "r"]:
                    amount = time["amount"]
                    imgui.text(f"{amount}{time_type}" if amount != 0 else time_type)
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
    
    # imgui.push_id(f"tags_{spell["name"]}")
    # imgui_md.render(f"**Tags**: {", ".join(spell["tags"])}")
    # imgui.pop_id()


def on_add_spell(static: MainWindowProtocol) -> None:
    name = static.data["spells"][-1]["name"]
    static.data_refs[f"spell:{name}:to_hit"] = static.data["spells"][-1]["to_hit"]
    static.bonus_list_refs[f"spell:{name}:to_hit:bonuses"] = static.data["spells"][-1]["to_hit"]["bonuses"]


def draw_spells(static: MainWindowProtocol) -> None:
    if imgui.button("Spells"):
        imgui.open_popup("Modify Spells")

    imgui.same_line()

    if imgui.button("Add Spell"):
        process_spell_from_file(static)
        imgui.open_popup("search_spells")
        if not static.states["search_data"].get("spells", False):
            static.states["search_data"]["spells"] = {
                "search_window_opened": True,
                "search_text": "",
                "search_results": []
            }

    if imgui.begin_popup("Modify Spells"):
        imgui.text("Placeholder")
        imgui.end_popup()

    if not hasattr(static, "loaded_spells"):
        static.loaded_spells = []

    draw_search_popup("spells", static.loaded_spells, "name", "description", static.data["spells"], static,
                      callback_on_add=lambda x=static: on_add_spell(x)) # type: ignore

    # TODO: maybe use Clipper to clip the table, but in that case all rows must be the same height
    spells_list_len = len(static.data["spells"])
    min_height = imgui.get_frame_height() * 1.5 * (spells_list_len + 2)
    max_height = imgui.get_window_size().y - imgui.get_text_line_height_with_spacing()*4
    outer_size = ImVec2(0.0, min(min_height, max_height))
    if spells_list_len != 0 and imgui.begin_table("spells_table", 14, flags=STRIPED_TABLE_FLAGS | imgui.TableFlags_.scroll_y, outer_size=outer_size): # type: ignore
        imgui.table_setup_scroll_freeze(0, 1)
        imgui.table_setup_column("Use")
        imgui.table_setup_column("Name")
        imgui.table_setup_column("Casting Time")
        imgui.table_setup_column("Duration")
        imgui.table_setup_column("Range")
        imgui.table_setup_column("Area")
        imgui.table_setup_column("To Hit")
        imgui.table_setup_column("Damage")
        imgui.table_setup_column("Damage Type")
        imgui.table_setup_column("Conditions")
        imgui.table_setup_column("Saves")
        imgui.table_setup_column("Conc.")
        imgui.table_setup_column("Ritual")
        imgui.table_setup_column("Components")
        imgui.table_headers_row()

        for _, spell in enumerate(static.data["spells"]):
            if spell["name"] != "no_display":
                imgui.table_next_row(); imgui.table_next_column()
                draw_spell(spell, static)
        imgui.end_table()