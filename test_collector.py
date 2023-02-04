_test_names_to_args = {
    "activatewindow": [
        "windows",
    ],
    "click": [
        "windows",
        "objects",
    ],
    "force_kill": [
        "command",  # необязательно
        "name",  # необязательно
        "names",  # необязательно
    ],
    "generatekeyevent": [
        "text",
    ],
    "guiexist": [
        "windows",
        "objects",  # необязательно
    ],
    "guinotexist": [
        "windows",
        "objects",  # необязательно
    ],
    "settextvalue": [
        "windows",
        "objects",
        "text",
    ],
    "start_subprocess": [
        "command",
    ],
    "waittillguiexist": [
        "windows",
        "objects",  # необязательно
    ],
    "waittillguinotexist": [
        "windows",
        "objects",  # необязательно
    ],
}

_test_names_skips = {
    "activatewindow": {
    },
    "click": {
    },
    "force_kill": {
        "command",  # необязательно
        "name",  # необязательно
        "names",  # необязательно
    },
    "generatekeyevent": {
    },
    "guiexist": {
        "objects",  # необязательно
    },
    "guinotexist": {
        "objects",  # необязательно
    },
    "settextvalue": {
    },
    "start_subprocess": {
    },
    "waittillguiexist": {
        "objects",  # необязательно
    },
    "waittillguinotexist": {
        "objects",  # необязательно
    },
}


def get_args_list(name: str):
    return _test_names_to_args[name]


def get_args_value(name: str, leaf):
    assert name in _test_names_to_args
    assert name in _test_names_skips

    ma = []
    for arg in _test_names_to_args[name]:
        if arg not in leaf.__dict__:
            if arg in _test_names_skips[name]:
                val = None
            else:
                assert False, "Не объявлена обязательная переменная {}".format(arg)
        else:
            val = leaf.__dict__[arg]
        ma += [val]
    return ma
