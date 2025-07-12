from imgui_bundle import imgui

from cs_types.core import MainWindowProtocol
from cs_types.stats import RollableStat, StaticStat
from settings import (
    MEDIUM_STRING_INPUT_WIDTH,
    SHORT_STRING_INPUT_WIDTH,
    TWO_DIGIT_BUTTONS_INPUT_WIDTH,
)
from util.calc import calc_static_stat, sum_bonuses
from util.custom_imgui import ColorButton
from util.sheet import draw_add_bonus, draw_bonuses, draw_overrides, draw_roll_menu


def draw_rollable_stat_button(stat_id: str, stat: RollableStat, 
                              bonus_types: list[str],
                              cache_prefix: str,
                              static: MainWindowProtocol) -> None:
    stat["total"], roll = sum_bonuses(stat["bonuses"], static)

    color = ""
    if roll == 1:
        color = "good"
    elif roll == -1:
        color = "bad"
    
    with ColorButton(color):
        if imgui.button(f"{stat["total"]:^+}##{stat_id}"):
            imgui.open_popup(f"{stat_id}_edit_stat")
    
    draw_roll_menu(stat_id, "1d20", str(stat["total"]), "Stat", roll, static)

    if imgui.begin_popup(f"{stat_id}_edit_stat"):
        imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
        _, stat["name"] = imgui.input_text(f"##{stat["id"]}_name", stat["name"], 128)

        imgui.align_text_to_frame_padding();
        imgui.text(f"Manual Bonus"); imgui.same_line()
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        _, stat["bonuses"][0]["value"] = imgui.input_int(f"##{stat_id}_manual_bonus", stat["bonuses"][0]["value"]) # type: ignore

        changed_adv, stat["manual_advantage"] = imgui.checkbox(f"Advantage##{stat_id}", stat["manual_advantage"])
        if changed_adv and stat["manual_advantage"]:
            stat["bonuses"].append({
                "name": "Manual Advantage",
                "value": "advantage",
                "multiplier": 1.0,
                "manual": False
            })
        elif changed_adv and not stat["manual_advantage"]:
            adv_idx = stat["bonuses"].index({
                "name": "Manual Advantage",
                "value": "advantage",
                "multiplier": 1.0,
                "manual": False
            })
            del stat["bonuses"][adv_idx]
        
        changed_dis, stat["manual_disadvantage"] = imgui.checkbox(f"Disadvantage##{stat_id}", stat["manual_disadvantage"])
        if changed_dis and stat["manual_disadvantage"]:
            stat["bonuses"].append({
                "name": "Manual Disadvantage",
                "value": "disadvantage",
                "multiplier": 1.0,
                "manual": False
            })
        elif changed_dis and not stat["manual_disadvantage"]:
            dis_idx = stat["bonuses"].index({
                "name": "Manual Disadvantage",
                "value": "disadvantage",
                "multiplier": 1.0,
                "manual": False
            })
            del stat["bonuses"][dis_idx]

        if stat["bonuses"] != []:
            imgui.separator_text(f"Bonuses")
            draw_bonuses("stat_bonus_list", stat["bonuses"], static)
            
        imgui.separator_text(f"New bonus")
        draw_add_bonus(f"{stat_id}_stat_bonus",
                       f"{cache_prefix}:{stat_id}", 
                       stat["bonuses"], 
                       bonus_types, 
                       static)

        imgui.end_popup()


def draw_static_stat_button(stat_id: str, stat: StaticStat, 
                            bonus_types: list[str],
                            cache_prefix: str,
                            static: MainWindowProtocol,
                            numerical_step: int = 1) -> bool:
    is_override, override_idx = calc_static_stat(stat, static)
    
    if imgui.button(f"{stat["total"]}##{stat_id}"):
        imgui.open_popup(f"{stat_id}_edit_stat")

    name_changed = False
    if imgui.begin_popup(f"{stat_id}_edit_stat"):
        imgui.push_item_width(SHORT_STRING_INPUT_WIDTH)
        name_changed, stat["name"] = imgui.input_text(f"##{stat["id"]}_name", stat["name"], 128)
        
        imgui.align_text_to_frame_padding()
        imgui.text(f"Base Value"); imgui.same_line()
        imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
        _, stat["base"] = imgui.input_int(f"##{stat_id}_base_value", stat["base"], numerical_step) # type: ignore

        if stat["bonuses"] != []:
            imgui.separator_text(f"Bonuses")
            draw_bonuses(f"{stat_id}_stat_bonus_list", stat["bonuses"], static)
        if stat["base_overrides"] != []:
            imgui.separator_text(f"Base overrides")
            draw_overrides(f"{stat_id}_base_overrides_list", stat["base_overrides"], override_idx, is_override, static)

        imgui.separator_text("New Bonus ")
        
        items = ["Value", "Base Override"]
        imgui.push_item_width(MEDIUM_STRING_INPUT_WIDTH)
        _, static.states["static_bonus_type_idx"] = imgui.combo(f"##{stat_id}_select_bonus_type", 
                                                                    static.states["static_bonus_type_idx"], 
                                                                    items, len(items)); imgui.same_line()
        imgui.pop_item_width()
        
        if static.states["static_bonus_type_idx"] == 0:
            draw_add_bonus(f"{stat_id}_stat_bonus", 
                           f"{cache_prefix}:{stat_id}",
                           stat["bonuses"], 
                           bonus_types, 
                           static, 
                           numerical_step)
        elif static.states["static_bonus_type_idx"] == 1:
            draw_add_bonus(f"{stat_id}_base_override",
                           f"{cache_prefix}:{stat_id}",
                           stat["base_overrides"], 
                           bonus_types, 
                           static)
        
        imgui.end_popup()

    return name_changed