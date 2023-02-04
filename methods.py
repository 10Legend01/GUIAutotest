import json
import os
import subprocess

import ldtp
import psutil
import pytest
from ldtp.client_exception import LdtpExecutionError


def assert_list_existing(conf, s: str):
    assert s in conf.__dict__ and isinstance(conf.__dict__[s], list)


def assert_existing(conf, s: str, t: type):
    assert s in conf.__dict__ and isinstance(conf.__dict__[s], t)


def existing(conf, s: str, t: type):
    if s in conf.__dict__:
        assert isinstance(conf.__dict__[s], t)
        return True
    return False


def get_window_from_list(windows, needexist=True):
    for window in windows:
        if ldtp.guiexist(window):
            break
    else:
        if needexist:
            assert False, "Didn't find any open window in config: {}".format(windows)
        else:
            return None
    return window


def get_object_from_list(window, objects, needexist=True):
    ldtp.remap(window)
    for obj in objects:
        if ldtp.guiexist(window, obj):
            break
    else:
        if needexist:
            assert False, "Didn't find any objects in config: {}; in window: '{}'".format(objects, window)
        else:
            return None
    return obj


def assert_window_parent(window, parent: str):
    ldtp.remap(window)
    window_new = ldtp.getobjectlist(window)[0]
    assert ldtp.getobjectlist(window_new) == ldtp.getobjectlist(window)
    assert 'parent' in ldtp.getobjectinfo(window_new, window_new)
    print(parent)
    print(ldtp.getobjectproperty(window_new, window_new, 'parent'))
    assert parent == ldtp.getobjectproperty(window_new, window_new, 'parent')
    return window_new


def get_app_windows(name_parent: str):
    app_windows = []
    for window in ldtp.getwindowlist():
        try:
            if name_parent == ldtp.getobjectproperty(window, window, 'parent'):
                app_windows.append(window)
        except LdtpExecutionError:
            pass
    return app_windows


def assert_object(window, obj):
    assert ldtp.guiexist(window)
    assert obj in ldtp.getobjectlist(window)


def click(window, obj):
    assert_object(window, obj)
    assert ldtp.click(window, obj)


def settextvalue(window, obj, txt=''):
    assert_object(window, obj)
    assert ldtp.settextvalue(window, obj, txt)


def kill_process_and_children_if_exist(process: subprocess.Popen = None, pid: int = None):
    if process is None and pid is None or process.poll() is not None:
        return 0
    elif pid is None:
        pid = process.pid

    def _kill_recursive(parent: psutil.Process):
        for child in parent.children():
            _kill_recursive(child)
        try:
            parent.kill()
        except Exception:
            pass

    try:
        parent = psutil.Process(pid)
        _kill_recursive(parent)
    except Exception:
        raise "WARNING: Couldn't kill process: {} PID".format(pid)
    return 1


_json_file = "pids.json"


def save_pid(command: str, pid: int):
    try:
        with open(_json_file) as json_file:
            data = json.load(json_file)
    except:
        data = dict()
    data[command] = pid
    with open(_json_file, 'w') as json_file:
        json.dump(data, json_file)


def kill_by_command(command: str):
    with open(_json_file) as json_file:
        data = json.load(json_file)
    assert data[command]
    kill_process_and_children_if_exist(data[command])
    data.pop(command)
    with open(_json_file, 'w') as json_file:
        json.dump(data, json_file)


def kill_by_name(name):
    os.system("kill -9 $(pgrep {})".format(name))
