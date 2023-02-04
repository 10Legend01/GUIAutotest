from ..methods import *
import time


def test_waittillguinotexist(windows, objects):
    window = None
    obj = None
    timer = 10
    score = 2

    assert (windows, list)
    while timer > 0 or score > 0:
        start_time = time.time()
        window = get_window_from_list(windows, False)
        if window is None:
            return
        if isinstance(objects, list):
            not_one = True
            for obj in objects:
                if not ldtp.waittillguinotexist(window, obj, 0):
                    not_one = True
            if not_one:
                return
        if score > 0:
            score -= 1
        timer -= time.time() - start_time

    assert False, "Was found window: '{}'".format(window) + "; object: '{}'".format(obj) if isinstance(objects, list) else ""
