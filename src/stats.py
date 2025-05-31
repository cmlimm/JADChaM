from imgui_bundle import imgui

from cs_types import MainWindowProtocol, RollableStat, StaticStat
from settings import (
    ADVANTAGE_ACTIVE_COLOR,
    ADVANTAGE_COLOR,
    ADVANTAGE_HOVER_COLOR,
    DISADVANTAGE_ACTIVE_COLOR,
    DISADVANTAGE_COLOR,
    DISADVANTAGE_HOVER_COLOR,
    MEDIUM_STRING_INPUT_WIDTH,
    TWO_DIGIT_BUTTONS_INPUT_WIDTH,
)
from util.calc import find_max_override, sum_bonuses
from util.sheet import draw_add_bonus, draw_bonuses, draw_overrides


def draw_rollable_stat_button(stat_id: str, stat: RollableStat, 
                              bonus_types: list[str],
                              static: MainWindowProtocol) -> None:
    stat["total"], roll = sum_bonuses(stat["bonuses"], static)

    if roll == 1:
        imgui.push_style_color(imgui.Col_.button.value, ADVANTAGE_COLOR)
        imgui.push_style_color(imgui.Col_.button_hovered.value, ADVANTAGE_HOVER_COLOR)
        imgui.push_style_color(imgui.Col_.button_active.value, ADVANTAGE_ACTIVE_COLOR)
    elif roll == -1:
        imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
        imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
        imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
    
    if imgui.button(f"{stat["total"]:^+}##{stat_id}"):
        imgui.open_popup(f"{stat["name"]}_edit_stat")
    if roll == 1 or roll == -1:
        imgui.pop_style_color(3)

    if imgui.begin_popup(f"{stat["name"]}_edit_stat"):
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
        draw_add_bonus(f"{stat_id}_stat_bonus", stat["bonuses"], bonus_types, static)

        imgui.end_popup()


def draw_static_stat_button(stat_id: str, stat: StaticStat, 
                            bonus_types: list[str],
                            static: MainWindowProtocol,
                            numerical_step: int = 1) -> None:
    override_idx, override_value = find_max_override(stat["base_overrides"], static)
    bonus_total, _ = sum_bonuses(stat["bonuses"], static)

    is_override = False
    if override_value > stat["base"]:
        stat["total"] = override_value + bonus_total
        is_override = True
    else:
        stat["total"] = stat["base"] + bonus_total
    
    if imgui.button(f"{stat["total"]}##{stat_id}"):
        imgui.open_popup(f"{stat["name"]}_edit_stat")

    if imgui.begin_popup(f"{stat["name"]}_edit_stat"):
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
        _, static.states["static_bonus_type_idx"] = imgui.combo(f"##{stat["name"]}_select_bonus_type", 
                                                                    static.states["static_bonus_type_idx"], 
                                                                    items, len(items)); imgui.same_line()
        imgui.pop_item_width()
        
        if static.states["static_bonus_type_idx"] == 0:
            draw_add_bonus(f"{stat_id}_stat_bonus", stat["bonuses"], bonus_types, static, numerical_step)
        elif static.states["static_bonus_type_idx"] == 1:
            draw_add_bonus(f"{stat_id}_base_override", stat["base_overrides"], bonus_types, static)
        
        imgui.end_popup()