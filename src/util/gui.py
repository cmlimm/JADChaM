
from imgui_bundle import icons_fontawesome_6, imgui
from imgui_bundle import portable_file_dialogs as pfd  # type: ignore

from cs_types import MainWindowProtocol
from util.core import open_image


def draw_open_image_button(static: MainWindowProtocol) -> None:
    if not hasattr(static, "open_image_dialog"):
        static.open_image_dialog = None
    
    if imgui.button(f"{icons_fontawesome_6.ICON_FA_IMAGE}##open_image"):
        static.open_image_dialog = pfd.open_file("Select file", filters=["Image Files", "*.png *.jpg *.jpeg *.bmp"])

    open_image(static)