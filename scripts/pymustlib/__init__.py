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

def print_logo():
    """Выводит логотип Pymust"""
    print(f"{Colors.BRIGHT_GREEN}")
    print("  _____        __  __ _    _  _____ _______")
    print(" |  __ \\      |  \\/  | |  | |/ ____|__   __|")
    print(" | |__) |_   _| \\  / | |  | | (___    | |   ")
    print(" |  ___/| | | | |\\/| | |  | |\\___ \\   | |   ")
    print(" | |    | |_| | |  | | |__| |____) |  | |   ")
    print(" |_|     \\__, |_|  |_|\\____/|_____/   |_|   ")
    print("          __/ |                              ")
    print("         |___/                               ")
    print(f"{Colors.RESET}")

def update_version_command(args: List[str]) -> int:
    """Обновляет версию игры, движка или pymust"""
    print(f"{Colors.BRIGHT_CYAN}Управление версиями...{Colors.RESET}")
    
    # Проверяем наличие параметров --log и --name
    parser = argparse.ArgumentParser(description="Обновление версии")
    parser.add_argument('--log', action='store_true', help='Создать запись в журнале изменений')
    parser.add_argument('--name', type=str, help='Название обновления для отображения в главном меню')
    
    # Парсим только известные аргументы
    parsed_args, remaining_args = parser.parse_known_args(args)
    
    # Импортируем модуль update_version.py
    update_version_module = import_module_from_file(
        str(SCRIPTS_DIR / "update_version.py"), 
        "update_version"
    )
    
    # Просто перенаправляем на основную функцию модуля
    # Передаем аргументы как есть, так как модуль уже использует argparse
    sys.argv = [sys.argv[0]] + args
    update_version_module.main()
    
    # Если создан changelog, выводим дополнительную информацию
    if parsed_args.log:
        print(f"\n{Colors.BRIGHT_CYAN}Журнал изменений создан!{Colors.RESET}")
        if parsed_args.name:
            print(f"{Colors.BRIGHT_GREEN}Название обновления: {Colors.BRIGHT_YELLOW}{parsed_args.name}{Colors.RESET}")
    
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

# Импортируем модуль для установки расширения
try:
    from scripts.install_vscode_extension import install_extension
except ImportError:
    # Определяем заглушку на случай, если модуль не найден
    def install_extension():
        print("Модуль установки расширения VSCode не найден.")
        return False

# Команда для установки расширения VSCode
def install_vscode_extension_command(args: List[str]) -> int:
    """Устанавливает расширение VSCode для подсветки синтаксиса .desc файлов"""
    print(f"{Colors.BRIGHT_CYAN}Установка расширения VSCode для подсветки синтаксиса .desc файлов...{Colors.RESET}")
    
    if "--force" in args:
        print(f"{Colors.YELLOW}Принудительная установка расширения...{Colors.RESET}")
    
    if install_extension():
        print(f"{Colors.BRIGHT_GREEN}Расширение успешно установлено!{Colors.RESET}")
        print(f"\n{Colors.BRIGHT_WHITE}Теперь файлы .desc будут поддерживать подсветку синтаксиса в VSCode и Cursor.{Colors.RESET}")
        return 0
    else:
        print(f"{Colors.BRIGHT_RED}Ошибка при установке расширения.{Colors.RESET}")
        return 1

# Регистрация команд
registry.register("update", "Обновляет версию игры или движка", update_version_command)
registry.register("run", "Запускает игру", run_game_command)
registry.register("version", "Выводит информацию о версии pymust", version_info_command)
registry.register("install-extension", "Устанавливает расширение VSCode для .desc файлов", install_vscode_extension_command)

# Функция для вывода общей справки
def show_help() -> None:
    """Выводит справку по всем командам"""
    version = get_pymust_version()
    print(f"{Colors.YELLOW}Pymust v{version} - менеджер команд{Colors.RESET}")
    print_logo()
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