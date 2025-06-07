from imgui_bundle import imgui

from settings import (  # type: ignore
    ADVANTAGE_ACTIVE_COLOR,
    ADVANTAGE_COLOR,
    ADVANTAGE_HOVER_COLOR,
    DISADVANTAGE_ACTIVE_COLOR,
    DISADVANTAGE_COLOR,
    DISADVANTAGE_HOVER_COLOR,
)


def end_table_nested() -> None:
    """
    Local solution for squashed nested fixed fit table
    See https://github.com/ocornut/imgui/issues/6586#issuecomment-1631455446
    """

    table_width = imgui.get_current_context().current_table.columns_auto_fit_width
    imgui.push_style_var(imgui.StyleVar_.item_spacing, imgui.ImVec2(0, 0))  # type: ignore
    imgui.end_table()
    imgui.dummy(imgui.ImVec2(table_width, 0))
    imgui.pop_style_var()


def draw_text_cell(name: str) -> None:
    imgui.table_next_row(); imgui.table_next_column(); imgui.align_text_to_frame_padding()
    imgui.text(name)

def help_marker(desc: str) -> None:
    imgui.text_disabled("(?)")
    if imgui.begin_item_tooltip():
        imgui.push_text_wrap_pos(imgui.get_font_size() * 35.0)
        imgui.text_unformatted(desc)
        imgui.pop_text_wrap_pos()
        imgui.end_tooltip()


class ColorButton():
    def __init__(self, color: str) -> None:
        self.color = color

    def __enter__(self) -> None:
        if self.color == "bad" or self.color == "good":
            if self.color == "bad":
                imgui.push_style_color(imgui.Col_.button.value, DISADVANTAGE_COLOR)
                imgui.push_style_color(imgui.Col_.button_hovered.value, DISADVANTAGE_HOVER_COLOR)
                imgui.push_style_color(imgui.Col_.button_active.value, DISADVANTAGE_ACTIVE_COLOR)
            elif self.color == "good":
                imgui.push_style_color(imgui.Col_.button.value, ADVANTAGE_COLOR)
                imgui.push_style_color(imgui.Col_.button_hovered.value, ADVANTAGE_HOVER_COLOR)
                imgui.push_style_color(imgui.Col_.button_active.value, ADVANTAGE_ACTIVE_COLOR)

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None: # type: ignore
        if self.color == "bad" or self.color == "good":
            imgui.pop_style_color(3)
        