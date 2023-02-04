from ..methods import *


def test_settextvalue(windows, objects, text):
    assert isinstance(text, str)

    window = get_window_from_list(windows)
    obj = get_object_from_list(window, objects)

    assert ldtp.settextvalue(window, obj, text)
