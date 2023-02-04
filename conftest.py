from enum import Enum

import test_collector as TestCollector

import pytest
import json5 as json
import sys
import re
import os
from os.path import abspath, exists

os.environ["DISPLAY"] = ":0"

args = sys.argv
print(args)

flag_name = "json"
flag_param = "--{}".format(flag_name)

scenario_key = "scenario"
general_config_key = "general_config"
filename_key = "filename"
config_key = "config"
required_key = "required"
xfail_key = "xfail"


def dollar_handler(self, s: str):
    if re.findall(r"^\$\w+$", s):
        return self.__dict__[s[1:]]

    def _dashrepl(matchobj):
        s = matchobj.group(0)
        if s == "$$":
            return '$'
        else:
            s = s[1:]
            assert s != ""
            assert s in self.__dict__
            assert isinstance(self.__dict__[s], str)
            return self.__dict__[s]

    s = re.sub(r"\$\$|\$\w*", _dashrepl, s)
    return s


def rec_dollar_handler(self, el):
    if isinstance(el, str):
        return dollar_handler(self, el)
    elif isinstance(el, list):
        return list(map(lambda x: rec_dollar_handler(self, x), el))
    elif isinstance(el, dict):
        for k, v in el.items():
            el[k] = rec_dollar_handler(self, v)
    return el


class Variables_block:
    def __repr__(self):
        return str(self)

    def __str__(self):
        s = "{ "
        for var, val in self.__dict__.items():
            s += "{}: {}; ".format(val, val)
        return s + "}"

    def __init__(self, _config, that=None):
        if that is not None:
            self.__dict__ = that.__dict__.copy()
        if isinstance(_config, dict):
            for k, v in _config.items():
                self.__dict__[k] = rec_dollar_handler(self, v)
        elif isinstance(_config, list):
            for i in _config:
                isinstance(i, dict)
                for k, v in i.items():
                    self.__dict__[k] = rec_dollar_handler(self, v)
        else:
            assert False, "Конфиг некоторого блока имеет неправильную структуру."


def get_xfail_bool(_data: dict):
    assert isinstance(_data, dict)
    if xfail_key in _data.keys():
        assert isinstance(_data[xfail_key], bool)
        return _data[xfail_key]
    return None


def get_root_and_data(_path: str, _main_json: str, _args: list):
    def get_json(_path: str, _relative_json: str):
        if _relative_json[-5:] == ".json":
            _relative_json += "5"
        elif _relative_json[-6:] != ".json5":
            _relative_json += ".json5"
        _json = abspath(_relative_json)
        if not exists(_json):
            _json = abspath(_path + '/' + _relative_json)
        assert exists(_json), "File {} doesn't exist".format(_json)
        # Требование, чтобы файл был из той же директории, что указано в пути
        assert _path in _json, "File {} not in directory {}".format(_json, _path)
        return _json

    with open(get_json(_path, _main_json)) as _json_file:
        _data = json.load(_json_file)
        assert {
                   scenario_key,
                   general_config_key,
               } <= set(_data.keys())
    root = Variables_block(_data[general_config_key])
    if required_key in _data.keys():
        assert len(_args) >= len(_data[required_key]), \
            "Недостаточно требуемых json файлов: {} против {}".format(len(_args), len(_data[required_key]))
        for i in range(len(_data[required_key])):
            with open(get_json(_path, _args[i])) as _json_file:
                data = json.load(_json_file)
                for k, v in _data[required_key][i].items():
                    root.__dict__[k] = data[k]

    return root, _data


class Variables:
    def __init__(self, _path: str, _main_json: str, _args: list):

        root, _data = get_root_and_data(_path, _main_json, _args)

        self.id_parents = []
        self.id_leafs = []
        self.id_leafs_set = set()

        self.children = dict()
        self.scenario_filenames = []
        self.list_variables = dict()
        self.success_list = []

        self.is_parallel = set()

        def identify(_data: dict, s):
            if s in _data.keys():
                assert isinstance(_data[s], bool), "Где-то поле '{}' не с типом bool".format(s)
                return _data[s]
            return False

        def identify_parallel(_data: dict):
            return identify(_data, "parallel")

        def identify_success(_data: dict):
            return identify(_data, "success")

        def _rec(id_parent, _data: dict, _root, _xfail):
            that_xfail = get_xfail_bool(_data)
            if that_xfail is not None:
                _xfail = that_xfail

            _id = len(self.id_parents)
            self.id_parents.append(id_parent)

            self.children.setdefault(id_parent, []).append(_id)
            if "scenario" in _data.keys():
                if identify_parallel(_data):
                    self.is_parallel.add(_id)
                self.success_list.append(identify_success(_data))
                _root = Variables_block(_data[general_config_key], _root)
                for val in _data["scenario"]:
                    _rec(_id, val, _root, _xfail)
            elif "json" in _data.keys():
                assert isinstance(_data["json"], list)
                assert len(_data["json"]) >= 1, "Требуется как минимум 1 аргумент"
                _under_json = _data["json"][0]
                _under_args = _data["json"][1:]
                _root, _under_data = get_root_and_data(_path, _under_json, _under_args)
                if identify_parallel(_under_data):
                    self.is_parallel.add(_id)
                self.success_list.append(identify_success(_under_data))
                for val in _under_data["scenario"]:
                    _rec(_id, val, _root, _xfail)
            else:
                self.success_list.append(False)
                name = _data['filename']
                self.scenario_filenames.append(name)
                leaf = Variables_block(_data["config"], _root)
                ma = TestCollector.get_args_value(name, leaf)
                self.list_variables.setdefault(name, []).append(
                    pytest.param(*ma, marks=pytest.mark.xfail if _xfail else ()))
                self.id_leafs.append(_id)

        _rec(-1, _data, root, False)
        self.id_leafs_set = set(self.id_leafs)

    def get_local_classes(self, test_name: str):
        return self.list_variables.setdefault(test_name, [])


class Status(Enum):
    NONE = 0
    SUCCESS = 1
    FAILED = 2
    SKIP = 3


def pytest_configure(config):
    assert flag_name in config.option.__dict__, "Не найден флаг {}".format(flag_param)
    flag_args = config.option.__dict__[flag_name].split()
    assert len(
        flag_args) >= 2, "Требуется набор при запуске: {} [путь до директории с json-ами] [относительный путь до json]".format(flag_param)
    path_jsons_dir = flag_args[0]
    main_json = flag_args[1]
    print("json: {}".format(path_jsons_dir + '/' + main_json))
    global variables, list_status
    variables = Variables(path_jsons_dir, main_json, flag_args[2:])
    list_status = [Status.NONE for _ in range(len(variables.id_parents) + len(variables.id_leafs))]


def pytest_addoption(parser, pluginmanager):
    parser.addoption(flag_param)


def _get_test_configs(test_name: str):
    ma = variables.get_local_classes(test_name)
    return ma


def pytest_generate_tests(metafunc):
    name = metafunc.definition.fspath.purebasename
    ma = _get_test_configs(name)
    if ma:
        metafunc.parametrize(TestCollector.get_args_list(name), ma)


def pytest_make_parametrize_id(config, val):
    if isinstance(val, list):
        while isinstance(val, list) and 0 < len(val):
            val = val[0]
    return repr(val)


def pytest_collection_modifyitems(session, config, items):
    new_items = []

    for test_name in variables.scenario_filenames:
        for item in items:
            if item.fspath.purebasename == test_name:
                new_items.append(item)
                items.remove(item)
                break

    items[:] = new_items

    assert len(items) == len(variables.id_leafs)


def push_status(_id: int, new_status: Status):
    if _id == -1:
        return
    curr_status = list_status[_id]
    parent = variables.id_parents[_id]
    if new_status == Status.SUCCESS:  # Пропихиваем SUCCESS родителям
        list_status[_id] = new_status
        if curr_status == Status.NONE:
            push_status(parent, Status.SUCCESS)
        return
    elif curr_status == Status.NONE and new_status == Status.SKIP:  # Пропихиваем SKIP потомкам
        list_status[_id] = new_status
        for child in variables.children.setdefault(_id, []):
            push_status(child, Status.SKIP)
        return
    elif curr_status in {Status.SUCCESS, Status.FAILED} and new_status == Status.SKIP:  # Ничего не меняем
        return

    if _id in variables.id_leafs_set:  # Leaf
        if curr_status == Status.SKIP and new_status == Status.FAILED:
            pass
        elif curr_status == Status.SUCCESS and new_status == Status.FAILED:
            list_status[_id] = new_status
            push_status(parent, Status.FAILED)
        else:
            raise
    else:
        if curr_status == Status.SUCCESS and new_status == Status.FAILED:
            list_status[_id] = new_status
            if not variables.success_list[_id]:
                push_status(parent, Status.FAILED)
            if _id not in variables.is_parallel:
                for child in variables.children[_id]:
                    push_status(child, Status.SKIP)
        else:
            raise


curr_id = -1
curr_setup = 0


def pytest_runtest_makereport(item, call):
    if call.excinfo is not None:
        global curr_id
        push_status(curr_id, Status.FAILED)


def pytest_runtest_setup(item):
    global curr_id, curr_setup
    curr_id = variables.id_leafs[curr_setup]
    curr_setup += 1
    if list_status[curr_id] == Status.SKIP:
        pytest.skip()
    else:
        assert list_status[curr_id] == Status.NONE
        push_status(curr_id, Status.SUCCESS)
