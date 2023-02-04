from ..methods import *


def test_start_subprocess(command):
    assert isinstance(command, str)
    command_split = command.split()
    assert len(command_split) > 0
    if len(command_split) == 1:
        pid = ldtp.launchapp(command_split[0])
    else:
        pid = ldtp.launchapp(command_split[0], command_split[1:], lang="")
    save_pid(command, pid)
