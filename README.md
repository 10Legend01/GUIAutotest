Первая пробная версия автоматизации GUI тестов.

### Пример запуска:
``python3 ./launch_pytest.py /home/user/GUIAutotest/jsons/ launch_main.json5 logins/Operator.json5 passwords/_.json5``

### Требования:
- Версия python >= 3.5.3
- ldtp: https://github.com/10Legend01/ldtp3
- Библиотеки (устанавливать через `pip install`)
- - `pytest`
- - `psutil`
- - `regex`
- - `json5`

[Ссылка на документацию](doc/simple_doc.md)

Пример json5 файлов можно найти в папке [jsons](jsons) 

