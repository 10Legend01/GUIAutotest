from ..methods import *


def test_activatewindow(windows):
    window = get_window_from_list(windows)

    assert ldtp.activatewindow(window)
