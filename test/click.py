from ..methods import *


def test_click(windows, objects):
    window = get_window_from_list(windows)
    obj = get_object_from_list(window, objects)

    assert ldtp.click(window, obj)
