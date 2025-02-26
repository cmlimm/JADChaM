from imgui_bundle import imgui, immapp, hello_imgui

TWO_DIGIT_BUTTONS_INPUT_WIDTH = 75
TWO_DIGIT_INPUT_WIDTH = 25

def draw_abilities(static):

    # TEMP: until save on every change is implemented
    if not hasattr(static, 'abilities'):
        
        abilities = {
            "str": {"base_score": 10, "manual_mod": 0, "base_score_bonuses": [{"name": "something 1", "value": 4}], "mod_bonuses": [{"name": "something 2", "value": 3}, {"name": "something 2", "value": 3}]},
            "dex": {"base_score": 10, "manual_mod": 0, "base_score_bonuses": [], "mod_bonuses": []},
            "con": {"base_score": 10, "manual_mod": 0, "base_score_bonuses": [], "mod_bonuses": [{"name": "something 3", "value": 2}]},
            "wis": {"base_score": 10, "manual_mod": 0, "base_score_bonuses": [], "mod_bonuses": []},
            "int": {"base_score": 10, "manual_mod": 0, "base_score_bonuses": [], "mod_bonuses": []},
            "cha": {"base_score": 10, "manual_mod": 0, "base_score_bonuses": [{"name": "something 4", "value": 1}, {"name": "something 4", "value": 1}], "mod_bonuses": []}
        }
        static.abilities = abilities

    if imgui.begin_table("abilities_table", 10, flags=imgui.TableFlags_.sizing_fixed_fit):
        imgui.table_next_row()
        for name, data in static.abilities.items():
            base, manual_mod, base_score_bonuses, mod_bonuses = data.values()

            # Buttons with final abilities' modifiers
            imgui.table_next_column()
            base_score_bonus = sum([bonus['value'] for bonus in base_score_bonuses])
            mod_bonus = sum([bonus['value'] for bonus in mod_bonuses])
            total_mod = (base + base_score_bonus - 10) // 2 + manual_mod + mod_bonus
            if imgui.button(f"{name.upper()}: {total_mod:+}"):
                imgui.open_popup(f"{name}_popup")

            # Popup windows where you can change the basic ability score and add a manual modifier
            if imgui.begin_popup(f"{name}_popup"):
                if imgui.begin_table("abilities_base_and_mod_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):
                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text("Base Score: "); imgui.same_line()
                    imgui.table_next_column()
                    imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                    changed, static.abilities[name]["base_score"] = imgui.input_int(f"##{name}", base, 1)

                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text("Manual Mod: "); imgui.same_line()
                    imgui.table_next_column()
                    imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                    changed, static.abilities[name]["manual_mod"] = imgui.input_int(f"##{name}_manual_mod", manual_mod, 1)
                    imgui.end_table()

                    if base_score_bonuses:
                        imgui.text(f"Base Score bonus ({base_score_bonus}):")
                        for item in base_score_bonuses:
                            name, value = item.values()
                            imgui.text(f"\t{name}: {value}")

                    if mod_bonuses:
                        imgui.text(f"Additional bonus ({mod_bonus}):")
                        for item in mod_bonuses:
                            name, value = item.values()
                            imgui.text(f"\t{name}: {value}")

                    imgui.end_popup()
        imgui.end_table()

# Proficiency, initiative, walking speed, armor class
def draw_misc(static):
    pass

def main_window():
    static = main_window
    draw_abilities(static)

def gui():
    main_window()
    
    if not theme_applied:
        hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.imgui_colors_dark)

theme_applied = False
immapp.run(
    gui_function=gui,
    window_title="Just Another D&D Character Manager",
    window_restore_previous_geometry=True
)