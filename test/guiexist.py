from ..methods import *


def test_guiexist(windows, objects):
    window = get_window_from_list(windows)
    if isinstance(objects, list):
        get_object_from_list(window, objects)
