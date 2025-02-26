from imgui_bundle import imgui, immapp, hello_imgui

TWO_DIGIT_BUTTONS_INPUT_WIDTH = 75
TWO_DIGIT_INPUT_WIDTH = 25

# TODO: move to util.py or something
def check_int(s):
    if isinstance(s, int):
        return True
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def draw_abilities(static):

    # TEMP: until save on every change is implemented
    if not hasattr(static, "abilities"):
        # "total" is used for adding a modifier to other modifiers/score (e.g. Skills, Initiative, AC, etc.)
        # "total" is recalculated on every frame
        abilities = {
            "str": {"total": 0, "base_score": 10, "manual_mod": 0, "base_score_bonuses": [{"name": "something 1", "value": 4}], "mod_bonuses": [{"name": "something 2", "value": 3}, {"name": "something 2", "value": 3}]},
            "dex": {"total": 0, "base_score": 10, "manual_mod": 0, "base_score_bonuses": [], "mod_bonuses": []},
            "con": {"total": 0, "base_score": 10, "manual_mod": 0, "base_score_bonuses": [], "mod_bonuses": [{"name": "something 3", "value": 2}]},
            "wis": {"total": 0, "base_score": 10, "manual_mod": 0, "base_score_bonuses": [], "mod_bonuses": []},
            "int": {"total": 0, "base_score": 10, "manual_mod": 0, "base_score_bonuses": [], "mod_bonuses": []},
            "cha": {"total": 0, "base_score": 10, "manual_mod": 0, "base_score_bonuses": [{"name": "something 4", "value": 1}, {"name": "something 4", "value": 1}], "mod_bonuses": []}
        }
        static.abilities = abilities

    if imgui.begin_table("abilities_table", 10, flags=imgui.TableFlags_.sizing_fixed_fit):
        imgui.table_next_row()
        for name, data in static.abilities.items():
            _, base, manual_mod, base_score_bonuses, mod_bonuses = data.values()

            # Buttons with final abilities' modifiers
            imgui.table_next_column()
            base_score_bonus = sum([bonus["value"] for bonus in base_score_bonuses])
            mod_bonus = sum([bonus["value"] for bonus in mod_bonuses])
            static.abilities[name]["total"] = (base + base_score_bonus - 10) // 2 + manual_mod + mod_bonus
            if imgui.button(f"{name.upper()}: {static.abilities[name]["total"]:+}"):
                imgui.open_popup(f"{name}_popup")

            # Popup windows where you can 
            #   - change the basic ability score
            #   - add a manual modifier
            #   - see what gives you additional bonuses

            # TODO: create a function for these popups
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
                    imgui.text(f"Base Score bonus ({base_score_bonus} -> {base_score_bonus // 2}):")
                    for item in base_score_bonuses:
                        name, value = item.values()
                        imgui.text(f"\t{name}: {value} -> {value // 2}")

                if mod_bonuses:
                    imgui.text(f"Additional bonus ({mod_bonus}):")
                    for item in mod_bonuses:
                        name, value = item.values()
                        imgui.text(f"\t{name}: {value}")

                imgui.end_popup()
        imgui.end_table()

# Proficiency, initiative, walking speed, armor class
def draw_misc(static):
    # TEMP: until save on every change is implemented
    if not hasattr(static, "misc"):
        # "total" is used for adding a modifier to other modifiers/score (e.g. Skills)
        # "total" is recalculated on every frame
        misc = {
            "proficiency": {"total": 0, "base_mod": 3, "bonuses": [{"name": "something", "value": 1}]},
            "initiative": {"manual_mod": 0, "bonuses": [{"name": "basic rule", "value": "dex"}, {"name": "Feat 'add prof to init'", "value": "prof"}, {"name": "something", "value": 1}]},
            "ac": {"base": 10, "bonuses": [{"name": "something", "value": 1}]},
            "speed": {"base": 30, "bonuses": [{"name": "something", "value": 5}]}
        }
        static.misc = misc

    if imgui.begin_table("misc_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):
        imgui.table_next_row()

        # Proficiency
        imgui.table_next_column()
        base_mod, bonuses = static.misc["proficiency"]["base_mod"], static.misc["proficiency"]["bonuses"]
        bonus = sum([bonus["value"] for bonus in bonuses])
        static.misc["proficiency"]["total"] = base_mod + bonus

        if imgui.button(f"PROF: {static.misc["proficiency"]["total"]:+}"):
            imgui.open_popup(f"prof_popup")

        # TODO: create a function for these popups
        if imgui.begin_popup(f"prof_popup"):
            if imgui.begin_table("prof_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.text("Base: "); imgui.same_line()
                imgui.table_next_column()
                imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                changed, static.misc["proficiency"]["base_mod"] = imgui.input_int(f"##prof", base_mod, 1)
                imgui.end_table()

            # TODO: move to a separate function
            if bonuses:
                imgui.text(f"Additional bonus ({bonus}):")
                for item in bonuses:
                    name, value = item.values()
                    imgui.text(f"\t{name}: {value}")
            imgui.end_popup()
        
        # Initiative
        imgui.table_next_column()
        manual_mod, bonuses = static.misc["initiative"]["manual_mod"], static.misc["initiative"]["bonuses"]

        # TODO: move to a separate function, this will be useful later for skills
        total_bonus = 0 
        for bonus in bonuses:
            name, value = bonus["name"], bonus["value"]
            if value == "prof":
                total_bonus += static.misc["proficiency"]["total"]  
            elif value in static.abilities.keys():
                total_bonus += static.abilities[value]["total"]
            elif check_int(value):
                total_bonus += value

        total = manual_mod + total_bonus
        
        if imgui.button(f"INIT: {total:+}"):
            imgui.open_popup(f"init_popup")

        # TODO: create a function for these popups
        if imgui.begin_popup(f"init_popup"):
            if imgui.begin_table("init_table", 2, flags=imgui.TableFlags_.sizing_fixed_fit):
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.text("Manual Mod: "); imgui.same_line()
                imgui.table_next_column()
                imgui.push_item_width(TWO_DIGIT_BUTTONS_INPUT_WIDTH)
                changed, static.misc["initiative"]["manual_mod"] = imgui.input_int(f"##init_manual_mod", manual_mod, 1)
                imgui.end_table()

            # TODO: move to a separate function
            if bonuses:
                imgui.text(f"Additional bonus ({total_bonus}):")
                for item in bonuses:
                    name, value = item.values()

                    if value == "prof":
                        imgui.text(f"\t{name}: {value} ({static.misc["proficiency"]["total"]})") 
                    elif value in static.abilities.keys():
                        imgui.text(f"\t{name}: {value} ({static.abilities[value]["total"]})") 
                    elif check_int(value):
                        imgui.text(f"\t{name}: {value}")
            imgui.end_popup()
        imgui.end_table()

def main_window():
    static = main_window
    draw_abilities(static)
    draw_misc(static)

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