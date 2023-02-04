from ..methods import *
import time


def test_waittillguiexist(windows, objects):
    timer = 10
    score = 2

    assert (windows, list)
    start_time = time.time()
    while timer > 0 or score > 0:
        timer -= time.time() - start_time
        start_time = time.time()
        if score > 0:
            score -= 1
        window = get_window_from_list(windows, False)
        if window is None:
            continue
        if isinstance(objects, list):
            obj = get_object_from_list(window, objects)
            if obj is not None:
                return
        else:
            return

    assert False, "Wasn't found no one of windows: {}".format(windows) \
                  + "; objects: {}".format(objects) if isinstance(objects, list) else ""
