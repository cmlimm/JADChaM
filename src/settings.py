from imgui_bundle import imgui

INVISIBLE_TABLE_FLAGS = imgui.TableFlags_.sizing_fixed_fit
STRIPED_TABLE_FLAGS = ( # type: ignore
    imgui.TableFlags_.sizing_fixed_fit
    | imgui.TableFlags_.no_host_extend_x  # type: ignore
    | imgui.TableFlags_.borders.value
    | imgui.TableFlags_.row_bg.value
)
STRIPED_NO_BORDERS_TABLE_FLAGS = ( # type: ignore
    imgui.TableFlags_.sizing_fixed_fit
    | imgui.TableFlags_.no_host_extend_x  # type: ignore
    | imgui.TableFlags_.row_bg.value
)
MARKDOWN_TEXT_TABLE = ( # type: ignore
    imgui.TableFlags_.no_host_extend_x  # type: ignore
    | imgui.TableFlags_.borders.value
    | imgui.TableFlags_.row_bg.value
)

SHORT_STRING_INPUT_WIDTH = 110
MEDIUM_STRING_INPUT_WIDTH = 150
MAGICAL_WORD_WRAP_NUMBER_TABLE = 90
MAGICAL_WORD_WRAP_NUMBER = 20

THREE_DIGIT_BUTTONS_INPUT_WIDTH = 100
TWO_DIGIT_BUTTONS_INPUT_WIDTH = 75
TWO_DIGIT_INPUT_WIDTH = 25

ADVANTAGE_COLOR = imgui.ImColor.hsv(0.3, 0.6, 0.6).value
ADVANTAGE_HOVER_COLOR = imgui.ImColor.hsv(0.3, 0.7, 0.7).value
ADVANTAGE_ACTIVE_COLOR = imgui.ImColor.hsv(0.3, 0.8, 0.8).value
DISADVANTAGE_COLOR = imgui.ImColor.hsv(0, 0.6, 0.6).value
DISADVANTAGE_HOVER_COLOR = imgui.ImColor.hsv(0, 0.7, 0.7).value
DISADVANTAGE_ACTIVE_COLOR = imgui.ImColor.hsv(0, 0.8, 0.8).value
OVERRIDE_COLOR = imgui.ImColor.hsv(0.15, 0.8, 0.8).value

RE_VALUE = "{\w+?.+?}" # type: ignore
RE_NEW_LINE = "\\n"