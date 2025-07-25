import copy
import itertools
import json
import math
import re
import uuid

from imgui_bundle import ImVec2, icons_fontawesome_6, imgui  # type: ignore

from cs_types.core import MainWindowProtocol
from cs_types.spell import Spell
from settings import (  # type: ignore
    INVISIBLE_TABLE_FLAGS,
    LIST_TYPE_TO_BONUS,
    RE_SPELL_DAMAGE,
    RE_SPELL_SCALING,
    STRIPED_TABLE_FLAGS,
)
from stats import draw_rollable_stat_button
from util.custom_imgui import end_table_nested, help_marker
from util.sheet import draw_roll_menu, draw_search_popup


def process_spell_from_file(static: MainWindowProtocol) -> None:
    with open("assets/spells-phb.json") as spell_file:
        spells = json.load(spell_file)["spell"]
    
    static.loaded_spells = []

    for spell_json in spells:
        spell_py = {}

        spell_py["id"] = str(uuid.uuid4())
        spell_py["name"] = spell_json["name"]
        spell_py["level"] = spell_json["level"]
        spell_py["school"] = spell_json["school"]

        # DESCRIPTION
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

        # CLASS + SUBCLASS
        # TODO: temp
        spell_py["classes"] = []
        spell_py["subclasses"] = []

        # CASTING TIME
        spell_py["casting_time"] = []
        if times := spell_json.get("time"):
            for time in times:
                type = time["unit"]
                types = {
                    "action": "A",
                    "bonus": "BA",
                    "reaction": "R",
                    "round": "r",
                    "minute": "m",
                    "hour": "h",
                    "special": "sp"
                }

                spell_py["casting_time"].append({ # type: ignore
                    "type": types[type],
                    "amount": time["number"]
                })

        # DURATION + CONCENTRATION
        spell_py["concentration"] = False
        spell_py["duration"] = []
        if durations := spell_json.get("duration"):
            for duration in durations:
                duration_type = duration["type"]
                time_type = "no_display"
                time_amount = 0
                if time := duration.get("duration"):
                    types = {
                        "turn": "",
                        "round": "r",
                        "minute": "m",
                        "hour": "h",
                        "day": "d",
                        "week": "w",
                        "month": "mth",
                        "year": "y"
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

        # RANGE
        spell_py["range"] = []
        if spell_range := spell_json.get("range"):
            if spell_range["type"] == "special":
                spell_py["range"].append({ # type: ignore
                        "type": "special",
                        "amount": 0
                })
            else:
                spell_py["range"].append({ # type: ignore
                    "type": spell_range["distance"]["type"],
                    "amount": spell_range["distance"].get("amount", 0)
                })

        # AREA        
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

        # COMPONENTS
        spell_py["components"] = {
            "v": spell_json.get("components", {}).get("v", False),
            "s": spell_json.get("components", {}).get("s", False),
            "m": spell_json.get("components", {}).get("m", False)
        }
        spell_py["components"]["c"] = False
        if isinstance(spell_py["components"]["m"], dict):
            if spell_py["components"]["m"].get("cost", False) or spell_py["components"]["m"].get("consume", False):
                spell_py["components"]["c"] = True
            else:
                spell_py["components"]["c"] = False
            spell_py["components"]["m"] = spell_py["components"]["m"]["text"]

        # RITUAL
        spell_py["ritual"] = spell_json.get("meta", {}).get("ritual", False)

        # TO_HIT
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

        # DAMAGE
        spell_py["damage"] = []
        if damage := spell_json.get("scalingLevelDice"):
            # if the spell has scalingLevelDice key, it is a cantrip, just copy the data
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
                "scaling_level": scaling,
                "scaling_slot": {}
            })
        else:
            scale_damage_match = re.findall(RE_SPELL_SCALING, spell_py["description"])
            damage_match = re.findall(RE_SPELL_DAMAGE, spell_py["description"])
            if scale_damage_match != []:
                # if the spell has {@scaledamage ...}, it has all the info we need:
                #   - initial damage
                #   - damage for each level above the initial level
                for match in scale_damage_match:
                    first_level = int(match[-2].split("-")[0])
                    last_level = int(match[-2].split("-")[1])
                    # for {@scaledamage ...} that have two initial damages: {@scaledamage 4d8;2d8|3-9|1d8}
                    for damage_str in match[0].split(";"):
                        initial_damage = {
                            "dice": int(damage_str.split("d")[1]),
                            "amount": int(damage_str.split("d")[0])
                        }
                        scaling_slot = {
                            str(level): {
                                "dice": initial_damage["dice"], 
                                "amount": initial_damage["amount"] + idx * int(match[-1].split("d")[0])
                                } 
                            for idx, level in enumerate(range(first_level, last_level + 1))
                            }
                        spell_py["damage"].append({ # type: ignore
                            "roll": initial_damage,
                            "scaling_level": {},
                            "scaling_slot": scaling_slot
                        })
            elif damage_match != []:
                # if the spell doesnt have any of the above, the best we can do is find {@damage ...}
                for match in damage_match:
                    damage = {
                        "dice": int(match.split("d")[1]),
                        "amount": int(match.split("d")[0])
                    }
                    spell_py["damage"].append({ # type: ignore
                        "roll": damage,
                        "scaling_level": {},
                        "scaling_slot": {}
                    })

        # DAMAGE TYPE
        spell_py["damage_type"] = spell_json.get("damageInflict", [])
        spell_py["damage_type"] = spell_py["damage_type"] + ["Unknown"] * (len(spell_py["damage"]) - len(spell_py["damage_type"]))

        # CONDITIONS
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
        
        # SAVE
        spell_py["saving_throw"] = []
        if saves := spell_json.get("savingThrow", None):
            for save in saves:
                spell_py["saving_throw"].append(save[:3].upper()) # type: ignore

        # TAGS
        spell_py["tags"] = []

        static.loaded_spells.append(copy.deepcopy(spell_py)) # type: ignore


def draw_spell(spell: Spell, static: MainWindowProtocol) -> None:
    if imgui.button(f"Use##{spell["id"]}_use_button"):
        pass
    
    imgui.table_next_column()

    # CONCENTRATION + RITUAL
    cr_str = []
    if spell["concentration"]:
        cr_str.append("C")
    if spell["ritual"]:
        cr_str.append("R")
    imgui.text("/".join(cr_str))

    imgui.table_next_column()

    # NAME
    imgui.align_text_to_frame_padding()
    imgui.text(f"{spell["name"]}"); imgui.same_line()
    help_marker(spell["description"])

    imgui.table_next_column()

    # CASTING TIME
    casting_times: list[str] = []
    for casting_time in spell["casting_time"]:
        type = casting_time["type"]
        if type in ["h", "m", "r"]:
            amount = casting_time["amount"]
            casting_times.append(f"{amount}{type}" if amount != 0 else type)
        else:
            casting_times.append(type)
    imgui.text(", ".join(casting_times))
    
    imgui.table_next_column()

    # DURATION
    durations: list[str] = []
    for duration in spell["duration"]:
        duration_type = duration["type"]
        if duration_type == "timed":
            time = duration["time"]
            time_type: str = time["type"]
            if time_type in ["h", "m", "r", "d", "w", "mth", "y"]:
                amount = time["amount"]
                durations.append(f"{amount}{time_type}" if amount != 0 else time_type)
            else:
                durations.append(time_type)
        else:
            duration_dict = {
                "instant": "inst",
                "permanent": "perm",
                "special": "S"
            }
            durations.append(duration_dict[duration_type])
    imgui.text(", ".join(durations))

    imgui.table_next_column()

    # RANGE
    ranges = [f"{spell_range["amount"]} {spell_range["type"]}" if spell_range["amount"] != 0 else spell_range["type"] for spell_range in spell["range"]]
    imgui.text(", ".join(ranges))

    imgui.table_next_column()

    # AREA OF EFFECT
    area_dict =  {
        "Cube": icons_fontawesome_6.ICON_FA_CUBE,
        "Hemisphere": icons_fontawesome_6.ICON_FA_CIRCLE_HALF_STROKE,
        "Line": icons_fontawesome_6.ICON_FA_MINUS,
        "Multiple Targets": icons_fontawesome_6.ICON_FA_PEOPLE_GROUP,
        "Cone": icons_fontawesome_6.ICON_FA_CIRCLE_NODES,
        "Square": icons_fontawesome_6.ICON_FA_EXPAND,
        "Circle": icons_fontawesome_6.ICON_FA_BULLSEYE,
        "Single Target": icons_fontawesome_6.ICON_FA_PERSON,
        "Sphere": icons_fontawesome_6.ICON_FA_GLOBE,
        "Wall": icons_fontawesome_6.ICON_FA_ALIGN_JUSTIFY,
        "Cylinder": icons_fontawesome_6.ICON_FA_DATABASE,
    }
    imgui.text(" ".join([f"{area_dict[area]}" for area in spell["area"]]))
    
    imgui.table_next_column()

    # TO HIT
    if spell.get("to_hit", None):
        draw_rollable_stat_button(f"{spell["id"]}_to_hit", 
                                spell["to_hit"],
                                LIST_TYPE_TO_BONUS["rollable"],
                                f"spell:{spell["id"]}:to_hit",
                                static)

    imgui.table_next_column()

    # DAMAGE + DAMAGE TYPE + CONDITIONS
    for idx, damage in enumerate(spell["damage"]):
        damage_roll_str = f"{damage["roll"]["amount"]}d{damage["roll"]["dice"]}"
        button_result = imgui.button(f"{damage_roll_str}##{spell["id"]}_{idx}")
        draw_roll_menu(f"damage_roll_{spell["id"]}_{idx}", damage_roll_str, "0", spell["damage_type"][idx], 0, static, button_result)
        imgui.same_line()

    damage_types_dict = {
        "acid": "acid",
        "bludgeoning": "bldg",
        "cold": "cold",
        "fire": "fire",
        "force": "frce",
        "lightning": "lght",
        "necrotic": "necr",
        "piercing": "prcng",
        "poison": "poisn",
        "psychic": "psy",
        "radiant": "rad",
        "slashing": "slsh",
        "thunder": "tndr"
    }
    damage_types = [f"{damage_types_dict[damage_type]}" for damage_type in spell["damage_type"] if damage_type != "Unknown"]
    conditions = [condition["name"] for condition in spell["condition_inflicted"]]
    conditions_descs = [f"{condition["name"]}\n\n{condition["description"]}" for condition in spell["condition_inflicted"]]
    
    damage_types_str = ", ".join(damage_types)
    conditions_str = ", ".join(conditions)
    conditions_descs_str = "\n\n\n".join(conditions_descs)
    total_str = ""
    if damage_types_str != "":
        if total_str != "": total_str += " | " 
        total_str += damage_types_str
    if conditions_str != "":
        if total_str != "": total_str += " | "
        total_str += conditions_str
    imgui.text(total_str)
    if conditions_str != "":
        imgui.same_line()
        help_marker(conditions_descs_str)

    imgui.table_next_column()
    
    # SAVES
    imgui.text(", ".join([save for save in spell["saving_throw"]]))

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
    if spell["components"]["c"]:
        components_string += " (C)"

    imgui.align_text_to_frame_padding()
    imgui.text(components_string)
    if material_desc != "":
        imgui.same_line()
        help_marker(material_desc) # type: ignore
    
    # imgui.push_id(f"tags_{spell["name"]}")
    # imgui_md.render(f"**Tags**: {", ".join(spell["tags"])}")
    # imgui.pop_id()


def on_add_spell(static: MainWindowProtocol) -> None:
    id = static.data["spells"][-1]["id"]
    static.data_refs[f"spell:{id}:to_hit"] = static.data["spells"][-1]["to_hit"]
    static.bonus_list_refs[f"spell:{id}:to_hit:bonuses"] = static.data["spells"][-1]["to_hit"]["bonuses"]

    static.data["spells"].sort(key=lambda x: x["level"])


def calculate_spell_slots(static: MainWindowProtocol) -> None:
    tables_multiclass = [(class_dict["spell_slots"][class_dict["level"] - 1], class_dict["level"], class_dict["multiclass_ratio"]) \
                         for class_dict in static.data["level"]["classes"] \
                         if class_dict["separate_slots_name"] == "" and class_dict["spell_save_enabled"]]
    tables_separate = {
        class_dict["separate_slots_name"]: {
                "spell_slots_max": class_dict["spell_slots"][class_dict["level"] - 1],
                "spell_slots_current": static.data["special_slots"].get(class_dict["separate_slots_name"], {}).get("spell_slots_current", class_dict["spell_slots"][class_dict["level"] - 1])
            } for class_dict in static.data["level"]["classes"] if class_dict["separate_slots_name"] != "" and class_dict["spell_save_enabled"]
        }

    multiclass_spell_slots = [0]
    if len(tables_multiclass) > 1:
        total_levels = sum([math.ceil(table[1]*table[2]) for table in tables_multiclass])
        if total_levels > 20: total_levels = 20

        multiclass_spell_slots = [
            [2,0,0,0,0,0,0,0,0],
            [3,0,0,0,0,0,0,0,0],
            [4,2,0,0,0,0,0,0,0],
            [4,3,0,0,0,0,0,0,0],
            [4,3,2,0,0,0,0,0,0],
            [4,3,3,0,0,0,0,0,0],
            [4,3,3,1,0,0,0,0,0],
            [4,3,3,2,0,0,0,0,0],
            [4,3,3,3,1,0,0,0,0],
            [4,3,3,3,2,0,0,0,0],
            [4,3,3,3,2,1,0,0,0],
            [4,3,3,3,2,1,0,0,0],
            [4,3,3,3,2,1,1,0,0],
            [4,3,3,3,2,1,1,0,0],
            [4,3,3,3,2,1,1,1,0],
            [4,3,3,3,2,1,1,1,0],
            [4,3,3,3,2,1,1,1,1],
            [4,3,3,3,3,1,1,1,1],
            [4,3,3,3,3,2,1,1,1],
            [4,3,3,3,3,2,2,1,1]
        ][total_levels - 1]
    if len(tables_multiclass) == 1:
        multiclass_spell_slots = tables_multiclass[0][0]

    static.data["spell_slots"]["spell_slots_max"] = multiclass_spell_slots
    static.data["special_slots"] = tables_separate # type: ignore


def draw_spells(static: MainWindowProtocol) -> None:
    if imgui.button("Spells"):
        imgui.open_popup("Modify Spells")

    imgui.same_line()

    if imgui.button("Add Spell"):
        process_spell_from_file(static)
        imgui.open_popup("search_spells")
        if not static.states["search_data"].get("spells", False):
            static.states["search_data"]["spells"] = {
                "search_text": "",
                "search_results": []
            }

    imgui.same_line()

    # DEBUG
    if imgui.button("Add All Spells"):
        process_spell_from_file(static)
        for spell in static.loaded_spells:
            static.data["spells"].append(spell)
            on_add_spell(static)

    if imgui.begin_popup("Modify Spells"):
        imgui.text("Placeholder")
        imgui.end_popup()

    if not hasattr(static, "loaded_spells"):
        static.loaded_spells = []

    draw_search_popup("spells", static.loaded_spells, "name", "description", static.data["spells"], static,
                      callback_on_add=lambda x=static: on_add_spell(x)) # type: ignore

    calculate_spell_slots(static)

    grouped_spells = itertools.groupby(static.data["spells"], key=lambda x: x["level"])
    for level, spell_list in grouped_spells:
        imgui.align_text_to_frame_padding()
        if level != 0:
            imgui.text(f"Level {level}")
        else:
            imgui.text("Cantrips")
        
        # TODO: reverse current spell slots maybe
        #       fix special spell slots
        # DRAW SPELL SLOTS
        if level != 0 and len(static.data["spell_slots"]["spell_slots_max"]) >= level and \
           static.data["spell_slots"]["spell_slots_max"][level - 1] != 0:
            
            imgui.same_line()
            spell_slots = static.data["spell_slots"]["spell_slots_max"][level - 1]
            current_spell_slots = static.data["spell_slots"]["spell_slots_current"][level - 1]

            spell_slots_states: list[bool] = []
            for _ in range(spell_slots):
                if current_spell_slots != 0:
                    spell_slots_states.append(True)
                    current_spell_slots -= 1
                else:
                    spell_slots_states.append(False)
            for idx, _ in enumerate(spell_slots_states):
                _, spell_slots_states[idx] = imgui.checkbox(f"##spell_slots_{level}_{idx}", spell_slots_states[idx])
                if idx != len(spell_slots_states) - 1: imgui.same_line()
            static.data["spell_slots"]["spell_slots_current"][level - 1] = sum([int(state) for state in spell_slots_states])
        
        for name, spell_slots_data in static.data["special_slots"].items():
            if level != 0 and  len(spell_slots_data["spell_slots_max"]) >= level and \
               spell_slots_data["spell_slots_max"][level - 1] != 0:
                
                imgui.same_line()
                imgui.align_text_to_frame_padding()
                imgui.text(name); imgui.same_line()

                spell_slots = spell_slots_data["spell_slots_max"][level - 1]
                current_spell_slots = spell_slots_data["spell_slots_current"][level - 1]

                spell_slots_states: list[bool] = []
                for _ in range(spell_slots):
                    if current_spell_slots != 0:
                        spell_slots_states.append(True)
                        current_spell_slots -= 1
                    else:
                        spell_slots_states.append(False)
                for idx, _ in enumerate(spell_slots_states):
                    _, spell_slots_states[idx] = imgui.checkbox(f"##spell_slots_{name}_{level}_{idx}", spell_slots_states[idx])
                    if idx != len(spell_slots_states) - 1: imgui.same_line()
                spell_slots_data["spell_slots_current"][level - 1] = sum([int(state) for state in spell_slots_states])
        
        if imgui.begin_table(f"spells_table_{level}", 11, flags=STRIPED_TABLE_FLAGS): # type: ignore
            imgui.table_setup_column("Use")
            imgui.table_setup_column("C/R")
            imgui.table_setup_column("Name")
            imgui.table_setup_column("CT")
            imgui.table_setup_column("Dur")
            imgui.table_setup_column("Range")
            imgui.table_setup_column("Area")
            imgui.table_setup_column("To Hit")
            imgui.table_setup_column("Effect")
            imgui.table_setup_column("Saves")
            imgui.table_setup_column("Comp.")
            imgui.table_headers_row()

            for spell in spell_list:
                if spell["name"] != "no_display":
                    imgui.table_next_row(); imgui.table_next_column()
                    draw_spell(spell, static)
            imgui.end_table()

# [TODO][MAYBE?] DISPLAY SPELLS IN A TREE
# spells_list_len = len(static.data["spells"])
# # min_height = imgui.get_frame_height() * 1.5 * (spells_list_len + 2)
# # max_height = imgui.get_window_size().y - imgui.get_text_line_height_with_spacing()*4
# # outer_size = ImVec2(0.0, min(min_height, max_height))
# if spells_list_len != 0 and imgui.begin_table("spells_table", 11, flags=STRIPED_TABLE_FLAGS): # type: ignore
#     # imgui.table_setup_scroll_freeze(0, 1)
#     imgui.table_setup_column("Use")
#     imgui.table_setup_column("C/R")
#     imgui.table_setup_column("Name")
#     imgui.table_setup_column("CT")
#     imgui.table_setup_column("Dur")
#     imgui.table_setup_column("Range")
#     imgui.table_setup_column("Area")
#     imgui.table_setup_column("To Hit")
#     imgui.table_setup_column("Effect")
#     imgui.table_setup_column("Saves")
#     imgui.table_setup_column("Comp.")
#     imgui.table_headers_row()

#     grouped_spells = itertools.groupby(static.data["spells"], key=lambda x: x["level"])
#     for level, spell_list in grouped_spells:
#         imgui.table_next_row(); imgui.table_next_column()
#         open = False
#         if level != 0:
#             open = imgui.tree_node_ex(f"Level {level}", imgui.TreeNodeFlags_.span_all_columns | imgui.TreeNodeFlags_.label_span_all_columns) # type: ignore
#             # imgui.text(f"Level {level}")
#         else:
#             open = imgui.tree_node_ex(f"Cantrips", imgui.TreeNodeFlags_.span_all_columns | imgui.TreeNodeFlags_.label_span_all_columns) # type: ignore
#             # imgui.text("Cantrips")
        
#         if open:
#             for spell in spell_list:
#                 if spell["name"] != "no_display":
#                     imgui.table_next_row(); imgui.table_next_column()
#                     imgui.tree_node_ex(f"##{spell["id"]}", imgui.TreeNodeFlags_.span_all_columns | imgui.TreeNodeFlags_.leaf | imgui.TreeNodeFlags_.no_tree_push_on_open | imgui.TreeNodeFlags_.frame_padding) # type: ignore
#                     imgui.same_line()
#                     draw_spell(spell, static)
#             imgui.tree_pop()
#     imgui.end_table()