import os

from imgui_bundle import icons_fontawesome_6, imgui
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

from cs_types import MainWindowProtocol
from util.core import open_file, open_image, save_file


def draw_toolbar(static: MainWindowProtocol) -> None:
    if imgui.begin_menu("File", True):
        if imgui.menu_item_simple("Open", "Ctrl+N"):
            static.open_file_dialog = pfd.open_file("Select file", os.getcwd())
        if imgui.menu_item_simple("Save", "Ctrl+S"):
            save_file(static)
        imgui.end_menu()

    if imgui.shortcut(imgui.Key.mod_ctrl | imgui.Key.n):  # type: ignore
        static.open_file_dialog = pfd.open_file("Select file", os.getcwd())
    # We need to continously try to open a file, otherwise it is called
    # once when the files have not yet been selected
    open_file(static)

    if imgui.shortcut(imgui.Key.mod_ctrl | imgui.Key.s):  # type: ignore
        save_file(static)

def draw_open_image_button(static: MainWindowProtocol) -> None:
    if not hasattr(static, "open_image_dialog"):
        static.open_image_dialog = None
    
    if imgui.button(f"{icons_fontawesome_6.ICON_FA_IMAGE}##open_image"):
        static.open_image_dialog = pfd.open_file("Select file", filters=["Image Files", "*.png *.jpg *.jpeg *.bmp"])

    open_image(static)

def draw_open_file_button(static: MainWindowProtocol) -> None:
    if not hasattr(static, "open_file_dialog"):
        static.open_file_dialog = None

    if imgui.button("Open file"):
        static.open_file_dialog = pfd.open_file("Select file", os.getcwd())
    open_file(static)