# pymust - менеджер команд для TextRPG

`pymust` - это инструмент командной строки для TextRPG, который упрощает запуск различных скриптов проекта.
Он работает по аналогии с инструментом `artisan` из фреймворка Laravel, но для Python и проекта TextRPG.

## Установка

Специальной установки не требуется. Скрипт `pymust` нужно запускать из корневой директории проекта:

```bash
python pymust <команда> [аргументы]
```

## Особенности

- **Цветной вывод** - все сообщения выводятся в цвете для лучшей читаемости
- **Семантическое версионирование** - версия pymust управляется через файл `version.properties`
- **Интеграция со скриптами проекта** - единый интерфейс для всех скриптов в проекте

## Доступные команды

### compile - Компиляция .desc файлов в JSON

Компилирует все .desc файлы в JSON формат, необходимый для игры.

Опции:

- `--force` - принудительная компиляция всех файлов, даже если они уже существуют
- `--create-example` - создание примера .desc файла, если нет существующих файлов

```bash
python pymust compile
python pymust compile --force
python pymust compile --create-example
```

### desc2json - Преобразование файла .desc в JSON

Преобразует отдельный файл .desc в JSON формат или целую директорию с файлами.

```bash
python pymust desc2json путь/к/файлу.desc путь/к/выходному/файлу.json
python pymust desc2json --dir путь/к/директории/desc путь/к/директории/json
```

### json2desc - Преобразование JSON файла в формат .desc

Преобразует JSON файл в формат .desc или целую директорию с файлами.

```bash
python pymust json2desc путь/к/файлу.json путь/к/выходному/файлу.desc
python pymust json2desc --dir путь/к/директории/json путь/к/директории/desc
```

### version - Управление версией игры, движка и pymust

Обновляет версию игры, движка или pymust согласно семантическому версионированию.

```bash
# Просмотр информации о текущей версии
python pymust version --info

# Обновление патч-версии игры (0.1.0 -> 0.1.1)
python pymust version --patch

# Обновление минорной версии игры (0.1.0 -> 0.2.0)
python pymust version --minor

# Обновление мажорной версии игры (0.1.0 -> 1.0.0)
python pymust version --major

# Изменение стадии разработки
python pymust version --stage=Beta

# Обновление версии движка
python pymust version --engine --patch

# Обновление версии pymust
python pymust version --pymust --patch
```

### run - Запуск игры

Запускает игру TextRPG.

```bash
python pymust run
```

### info - Информация о версии pymust

Выводит информацию о версии pymust.

```bash
python pymust info
```

## Добавление новых команд

Для добавления новых команд необходимо отредактировать файл `scripts/pymustlib/__init__.py`:

1. Создать функцию-обработчик команды, которая принимает аргументы командной строки и возвращает код возврата:

```python
def my_command(args: List[str]) -> int:
    """Описание моей команды"""
    print(f"{Colors.BRIGHT_CYAN}Выполняю мою команду...{Colors.RESET}")
    # Реализация команды
    print(f"{Colors.BRIGHT_GREEN}Команда успешно выполнена!{Colors.RESET}")
    return 0  # Возвращаем 0 при успешном выполнении
```

2. Зарегистрировать команду в реестре:

```python
registry.register("mycommand", "Описание моей команды", my_command)
```

## Управление версией pymust

Версия pymust хранится в файле `version.properties` в корне проекта и управляется через скрипт `update_version.py`. Для обновления версии pymust используйте:

```bash
python pymust version --pymust --patch  # увеличивает патч-версию
python pymust version --pymust --minor  # увеличивает минорную версию
python pymust version --pymust --major  # увеличивает мажорную версию
```

## Тестирование

Для запуска тестов используйте:

```bash
python -m unittest scripts/pymustlib/tests.py
```
