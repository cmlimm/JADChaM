# Local solution for squashed nested fixed fit table
# See https://github.com/ocornut/imgui/issues/6586#issuecomment-1631455446
import json

from imgui_bundle import imgui

import character_sheet_types


def end_table_nested() -> None:
    table_width = imgui.get_current_context().current_table.columns_auto_fit_width
    imgui.push_style_var(imgui.StyleVar_.item_spacing, imgui.ImVec2(0, 0))  # type: ignore
    imgui.end_table()
    imgui.dummy(imgui.ImVec2(table_width, 0))
    imgui.pop_style_var()


def open_file(static: character_sheet_types.MainWindowProtocol) -> None:
    if static.open_file_dialog is not None and static.open_file_dialog.ready():
        static.file_paths = static.open_file_dialog.result()
        if static.file_paths:
            character_file = open(static.file_paths[0], "r+")
            static.data = json.load(character_file)
            character_file.close()

        static.open_file_dialog = None


def save_file(static: character_sheet_types.MainWindowProtocol) -> None:
    character_file = open(static.file_paths[0], "r+")
    character_file.seek(0)
    character_file.truncate(0)
    json.dump(static.data, character_file, indent=4)
    character_file.close()
