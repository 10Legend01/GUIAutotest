from ..methods import *


def test_guinotexist(windows, objects):
    window = get_window_from_list(windows, False)
    if window is None:
        return
    if isinstance(objects, list):
        obj = get_object_from_list(window, objects, False)
        if obj is None:
            return
        assert False, "Object: '{}' in window: '{}' exist.".format(obj, window)
    assert False, "Window: '{}' exist.".format(window)
