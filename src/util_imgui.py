from imgui_bundle import imgui


# Local solution for squashed nested fixed fit table
# See https://github.com/ocornut/imgui/issues/6586#issuecomment-1631455446
def end_table_nested() -> None:
    table_width = imgui.get_current_context().current_table.columns_auto_fit_width
    imgui.push_style_var(imgui.StyleVar_.item_spacing, imgui.ImVec2(0, 0))  # type: ignore
    imgui.end_table()
    imgui.dummy(imgui.ImVec2(table_width, 0))
    imgui.pop_style_var()


def draw_text_cell(name: str) -> None:
    imgui.table_next_row(); imgui.table_next_column(); imgui.align_text_to_frame_padding()
    imgui.text(name)