import json
import os
import shutil

from cs_types import MainWindowProtocol


def save_file(static: MainWindowProtocol) -> None:
    character_file = open(static.file_path[0], "r+")
    character_file.seek(0)
    character_file.truncate(0)
    json.dump(static.data, character_file, indent=4)
    character_file.close()


def open_image(static: MainWindowProtocol) -> None:
    if static.open_image_dialog is not None and static.open_image_dialog.ready():
        file_path = static.open_image_dialog.result()
        if file_path:
            static.data["image_path"] = f"images/{os.path.basename(file_path[0])}"
            try:
                shutil.copy(file_path[0], f"{os.getcwd()}/assets/{static.data["image_path"]}")
            except shutil.SameFileError:
                pass
        
        static.open_image_dialog = None