import os

from imgui_bundle import imgui
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

import character_sheet_types
from util import open_file


def draw_file_button(static: character_sheet_types.MainWindowProtocol) -> None:
    if not hasattr(static, "open_file_dialog"):
        static.open_file_dialog = None
    if imgui.button("Open file"):
        static.open_file_dialog = pfd.open_file("Select file", os.getcwd())
    open_file(static)
