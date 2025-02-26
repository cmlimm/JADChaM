from imgui_bundle import imgui, immapp, hello_imgui

TWO_DIGIT_BUTTONS_INPUT_WIDTH = 75
TWO_DIGIT_INPUT_WIDTH = 25
ABILITY_BUTTON_WIDTH = 70

def draw_abilities(static):

    # TEMP: until save on every change is implemented
    if not hasattr(static, 'abilities'): 
        abilities = {
            "str": {"base": 10, "manual_mod": 0},
            "dex": {"base": 10, "manual_mod": 0},
            "con": {"base": 10, "manual_mod": 0},
            "wis": {"base": 10, "manual_mod": 0},
            "int": {"base": 10, "manual_mod": 0},
            "cha": {"base": 10, "manual_mod": 0}
        }
        static.abilities = abilities

    if imgui.begin_table("abilities_table", 10, flags=imgui.TableFlags_.sizing_fixed_fit):
        imgui.table_next_row()
        for name, data in static.abilities.items():
            base, manual_mod = data.values()

            # Buttons with final abilities' modifiers
            imgui.table_next_column()
            if imgui.button(f"{name.upper()}: {(base - 10) // 2 + manual_mod:+}"):
                imgui.open_popup(f"{name}_popup")

            # Popup windows where you can change basic ability score and add a manual modifier
            if imgui.begin_popup(f"{name}_popup"):
                if imgui.begin_table("abilities_base_and_mod_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):
                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text("Base Score: "); imgui.same_line()
                    imgui.table_next_column()
                    imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                    changed, static.abilities[name]["base"] = imgui.input_int(f"##{name}", base, 1)

                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text("Manual Mod: "); imgui.same_line()
                    imgui.table_next_column()
                    imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                    changed, static.abilities[name]["manual_mod"] = imgui.input_int(f"##{name}_manual_mod", manual_mod, 1)
                    
                    imgui.end_table()
                    imgui.end_popup()
        imgui.end_table()

def main_window():
    static = main_window
    draw_abilities(static)

def gui():
    main_window()
    
    theme_applied = False
    if not theme_applied:
        hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.imgui_colors_dark)

immapp.run(
    gui_function=gui,
    window_title="Just Another D&D Character Manager",
    window_restore_previous_geometry=True
)