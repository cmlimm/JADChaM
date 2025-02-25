from imgui_bundle import imgui, immapp, hello_imgui

def draw_abilities(static):

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

    ABILITY_WIDGET_WIDTH = 25

    # TODO:
    #   - horizonal layout
    #   - hide base + manual modifier under expand
    if imgui.begin_table("abilities_tables", 4, flags=imgui.TableFlags_.sizing_fixed_fit):
        for name, data in static.abilities.items():
            imgui.table_next_row()

            base, manual_mod = data.values() 

            imgui.table_next_column()
            imgui.text(f"BASE:"); imgui.same_line()
            imgui.push_item_width(75)
            changed, static.abilities[name]["base"] = imgui.input_int(f"##{name}", base, 1); imgui.same_line()
            imgui.text("// 2")

            imgui.table_next_column()
            imgui.text(f"+"); imgui.same_line()
            imgui.push_item_width(ABILITY_WIDGET_WIDTH)
            changed, static.abilities[name]["manual_mod"] = imgui.input_int(f"##{name}_manual_mod", manual_mod, 0)
            
            imgui.table_next_column()
            imgui.text(f"{name.upper()}:")
            imgui.table_next_column()
            imgui.text(f"{(base - 10) // 2 + manual_mod:+}")
        
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