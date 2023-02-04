from ..methods import *


def test_force_kill(command, name, names):
    if isinstance(command, str):
        kill_by_command(command)
    elif isinstance(name, str):
        kill_by_name(name)
    elif isinstance(names, list):
        for name in names:
            kill_by_name(name)
