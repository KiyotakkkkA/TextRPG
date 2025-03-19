"""
Библиотека pymustlib для TextRPG.
Предоставляет удобный интерфейс для запуска и управления скриптами игры.
"""

import os
import sys
import importlib.util
import argparse
from pathlib import Path
from typing import Dict, List, Callable, Any, Optional, Tuple

# Получаем корневой каталог проекта
ROOT_DIR = Path(__file__).parent.parent.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"

# Класс для цветного вывода
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

class Command:
    """Базовый класс для команд pymust"""
    
    def __init__(self, name: str, description: str, callback: Callable):
        self.name = name
        self.description = description
        self.callback = callback
        
    def execute(self, args: List[str]) -> int:
        """Выполняет команду с переданными аргументами"""
        return self.callback(args)
    
    def get_help(self) -> str:
        """Возвращает справку по команде"""
        return self.description

class CommandRegistry:
    """Реестр команд pymust"""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        
    def register(self, name: str, description: str, callback: Callable) -> None:
        """Регистрирует новую команду"""
        command = Command(name, description, callback)
        self.commands[name] = command
        
    def get_command(self, name: str) -> Optional[Command]:
        """Возвращает команду по имени"""
        return self.commands.get(name)
    
    def list_commands(self) -> List[Tuple[str, str]]:
        """Возвращает список всех команд с их описаниями"""
        return [(name, cmd.description) for name, cmd in self.commands.items()]

# Глобальный реестр команд
registry = CommandRegistry()

# Функция для импорта модуля из файла
def import_module_from_file(file_path: str, module_name: str) -> Any:
    """Импортирует модуль из файла"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Функция для получения версии pymust из version.properties
def get_pymust_version() -> str:
    """Возвращает текущую версию pymust"""
    try:
        # Импортируем модуль для работы с version.properties
        sys.path.append(str(ROOT_DIR))
        from src.utils.PropertiesLoader import get_version_properties
        
        version_props = get_version_properties()
        return version_props.get("pymust.version", "0.1.0")
    except Exception as e:
        return "0.1.0"  # Версия по умолчанию

# Команды для работы с ресурсами
def compile_resources_command(args: List[str]) -> int:
    """Компилирует все .desc файлы в JSON"""
    print(f"{Colors.BRIGHT_CYAN}Компиляция ресурсов...{Colors.RESET}")
    
    parser = argparse.ArgumentParser(description="Компилирует файлы .desc в JSON")
    parser.add_argument("--force", action="store_true", help="Принудительная компиляция всех файлов")
    parser.add_argument("--create-example", action="store_true", help="Создать пример .desc файла")
    
    # Парсим только известные аргументы
    parsed_args, _ = parser.parse_known_args(args)
    
    # Импортируем модуль compile_resources.py
    compile_resources_module = import_module_from_file(
        str(SCRIPTS_DIR / "compile_resources.py"), 
        "compile_resources"
    )
    
    # Вызываем функцию компиляции
    start_time = compile_resources_module.time.time()
    compiled, total = compile_resources_module.compile_resources(parsed_args.force)
    end_time = compile_resources_module.time.time()
    
    print(f"{Colors.BRIGHT_GREEN}Компиляция завершена за {Colors.BRIGHT_YELLOW}{end_time - start_time:.2f}{Colors.BRIGHT_GREEN} секунд.{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}Скомпилировано {Colors.BRIGHT_YELLOW}{compiled}{Colors.BRIGHT_GREEN} из {Colors.BRIGHT_YELLOW}{total}{Colors.BRIGHT_GREEN} файлов.{Colors.RESET}")
    
    # Если нет .desc файлов и указан флаг create-example, создаем пример
    if total == 0 and parsed_args.create_example:
        compile_resources_module.create_example_desc()
        print(f"{Colors.BRIGHT_GREEN}Создан пример .desc файла{Colors.RESET}")
    
    return 0

def desc_to_json_command(args: List[str]) -> int:
    """Преобразует файл .desc в JSON"""
    print(f"{Colors.BRIGHT_CYAN}Преобразование .desc в JSON...{Colors.RESET}")
    
    parser = argparse.ArgumentParser(description="Преобразует файл .desc в JSON")
    parser.add_argument("input", help="Путь к входному файлу .desc")
    parser.add_argument("output", help="Путь к выходному файлу JSON")
    parser.add_argument("--dir", action="store_true", help="Обработать целую директорию")
    
    # Парсим только известные аргументы
    parsed_args, _ = parser.parse_known_args(args)
    
    # Импортируем модуль desc_to_json.py
    desc_to_json_module = import_module_from_file(
        str(SCRIPTS_DIR / "desc_to_json.py"), 
        "desc_to_json"
    )
    
    # Вызываем соответствующую функцию
    if parsed_args.dir:
        converted, total = desc_to_json_module.convert_directory(parsed_args.input, parsed_args.output)
        print(f"{Colors.BRIGHT_GREEN}Преобразовано {Colors.BRIGHT_YELLOW}{converted}{Colors.BRIGHT_GREEN} из {Colors.BRIGHT_YELLOW}{total}{Colors.BRIGHT_GREEN} файлов из директории {Colors.BRIGHT_YELLOW}{parsed_args.input}{Colors.RESET}")
    else:
        if desc_to_json_module.convert_file(parsed_args.input, parsed_args.output):
            print(f"{Colors.BRIGHT_GREEN}Файл {Colors.BRIGHT_YELLOW}{parsed_args.input}{Colors.BRIGHT_GREEN} успешно преобразован в {Colors.BRIGHT_YELLOW}{parsed_args.output}{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_RED}Ошибка при преобразовании файла {parsed_args.input}{Colors.RESET}")
            return 1
    
    return 0

def json_to_desc_command(args: List[str]) -> int:
    """Преобразует JSON файл в формат .desc"""
    print(f"{Colors.BRIGHT_CYAN}Преобразование JSON в .desc...{Colors.RESET}")
    
    parser = argparse.ArgumentParser(description="Преобразует JSON файл в формат .desc")
    parser.add_argument("input", help="Путь к входному файлу JSON")
    parser.add_argument("output", help="Путь к выходному файлу .desc")
    parser.add_argument("--dir", action="store_true", help="Обработать целую директорию")
    
    # Парсим только известные аргументы
    parsed_args, _ = parser.parse_known_args(args)
    
    # Импортируем модуль json_to_desc.py
    json_to_desc_module = import_module_from_file(
        str(SCRIPTS_DIR / "json_to_desc.py"), 
        "json_to_desc"
    )
    
    # Вызываем соответствующую функцию
    if parsed_args.dir:
        # Предполагаем, что в модуле есть функция convert_directory
        converted, total = json_to_desc_module.convert_directory(parsed_args.input, parsed_args.output)
        print(f"{Colors.BRIGHT_GREEN}Преобразовано {Colors.BRIGHT_YELLOW}{converted}{Colors.BRIGHT_GREEN} из {Colors.BRIGHT_YELLOW}{total}{Colors.BRIGHT_GREEN} файлов из директории {Colors.BRIGHT_YELLOW}{parsed_args.input}{Colors.RESET}")
    else:
        # Создаем конвертер и вызываем его
        converter = json_to_desc_module.JsonToDescConverter()
        if converter.convert_file(parsed_args.input, parsed_args.output):
            print(f"{Colors.BRIGHT_GREEN}Файл {Colors.BRIGHT_YELLOW}{parsed_args.input}{Colors.BRIGHT_GREEN} успешно преобразован в {Colors.BRIGHT_YELLOW}{parsed_args.output}{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_RED}Ошибка при преобразовании файла {parsed_args.input}{Colors.RESET}")
            return 1
    
    return 0

def update_version_command(args: List[str]) -> int:
    """Обновляет версию игры, движка или pymust"""
    print(f"{Colors.BRIGHT_CYAN}Управление версиями...{Colors.RESET}")
    
    # Импортируем модуль update_version.py
    update_version_module = import_module_from_file(
        str(SCRIPTS_DIR / "update_version.py"), 
        "update_version"
    )
    
    # Просто перенаправляем на основную функцию модуля
    # Передаем аргументы как есть, так как модуль уже использует argparse
    sys.argv = [sys.argv[0]] + args
    update_version_module.main()
    
    return 0

# Команда для запуска игры
def run_game_command(args: List[str]) -> int:
    """Запускает игру"""
    print(f"{Colors.BRIGHT_CYAN}Запуск игры...{Colors.RESET}")
    
    # Импортируем и запускаем main.py
    main_module = import_module_from_file(
        str(ROOT_DIR / "main.py"), 
        "main"
    )
    
    try:
        main_module.main()
        return 0
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}Ошибка при запуске игры: {str(e)}{Colors.RESET}")
        return 1

# Команда для вывода информации о версии pymust
def version_info_command(args: List[str]) -> int:
    """Выводит информацию о версии pymust"""
    version = get_pymust_version()
    print(f"{Colors.YELLOW}Pymust v{version}{Colors.RESET}")
    return 0

# Регистрация команд
registry.register("compile", "Компилирует файлы .desc в JSON", compile_resources_command)
registry.register("desc2json", "Преобразует файл .desc в JSON", desc_to_json_command)
registry.register("json2desc", "Преобразует JSON файл в формат .desc", json_to_desc_command)
registry.register("update", "Обновляет версию игры или движка", update_version_command)
registry.register("run", "Запускает игру", run_game_command)
registry.register("version", "Выводит информацию о версии pymust", version_info_command)

# Функция для вывода общей справки
def show_help() -> None:
    """Выводит справку по всем командам"""
    version = get_pymust_version()
    print(f"{Colors.YELLOW}Pymust v{version} - менеджер команд{Colors.RESET}")
    print(f"\n{Colors.BRIGHT_WHITE}Доступные команды:{Colors.RESET}")
    
    for name, description in registry.list_commands():
        print(f"  {Colors.BRIGHT_CYAN}{name:12}{Colors.RESET} - {description}")
    
    print(f"\n{Colors.BRIGHT_WHITE}Использование:{Colors.RESET} python pymust <команда> [аргументы]")
    print(f"{Colors.BRIGHT_WHITE}Для получения справки:{Colors.RESET} python pymust <команда> --help")

# Функция для запуска команды
def run_command(command_name: str, args: List[str]) -> int:
    """Запускает команду с указанным именем"""
    command = registry.get_command(command_name)
    if command:
        return command.execute(args)
    else:
        print(f"{Colors.BRIGHT_RED}Ошибка: команда '{command_name}' не найдена{Colors.RESET}")
        show_help()
        return 1 