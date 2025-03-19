#!/usr/bin/env python3
"""
Скрипт для обновления версии игры и движка.
Используется перед релизом для установки новой версии.

Примеры использования:
- python update_version.py --patch  # увеличивает патч-версию (0.1.0 -> 0.1.1)
- python update_version.py --minor  # увеличивает минорную версию (0.1.0 -> 0.2.0)
- python update_version.py --major  # увеличивает мажорную версию (0.1.0 -> 1.0.0)
- python update_version.py --stage=Beta  # устанавливает стадию разработки
- python update_version.py --engine --patch  # обновляет версию движка
- python update_version.py --pymust --patch  # обновляет версию pymust
"""

import os
import sys
import argparse
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

# Импортируем функции из нашего проекта
from src.utils.scripts.version_utils import (
    update_game_version, 
    update_engine_version,
    update_pymust_version,
    set_game_stage, 
    get_full_version_info
)

# Импортируем цвета из pymustlib, если доступно
try:
    from scripts.pymustlib import Colors
except ImportError:
    # Определение цветов для вывода
    class Colors:
        RESET = '\033[0m'
        BRIGHT_RED = '\033[91m'
        BRIGHT_GREEN = '\033[92m'
        BRIGHT_YELLOW = '\033[93m'
        BRIGHT_BLUE = '\033[94m'
        BRIGHT_MAGENTA = '\033[95m'
        BRIGHT_CYAN = '\033[96m'
        BRIGHT_WHITE = '\033[97m'

def main():
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description='Обновление версии игры TextRPG.')
    
    # Тип инкремента версии
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument('--patch', action='store_true', help='Увеличить патч-версию (0.1.0 -> 0.1.1)')
    version_group.add_argument('--minor', action='store_true', help='Увеличить минорную версию (0.1.0 -> 0.2.0)')
    version_group.add_argument('--major', action='store_true', help='Увеличить мажорную версию (0.1.0 -> 1.0.0)')
    
    # Стадия разработки
    parser.add_argument('--stage', type=str, help='Установить стадию разработки (Alpha, Beta, RC, Release)')
    
    # Выбор компонента для обновления версии
    component_group = parser.add_mutually_exclusive_group()
    component_group.add_argument('--engine', action='store_true', help='Обновлять версию движка вместо игры')
    component_group.add_argument('--pymust', action='store_true', help='Обновлять версию pymust вместо игры')
    
    # Флаг для вывода информации о текущей версии
    parser.add_argument('--info', action='store_true', help='Показать информацию о текущей версии')
    
    args = parser.parse_args()
    
    # Просмотр информации о версии
    if args.info or (not any([args.patch, args.minor, args.major, args.stage])):
        info = get_full_version_info()
        print(f"\n{Colors.BRIGHT_CYAN}Информация о текущей версии:{Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}Игра: {Colors.BRIGHT_YELLOW}{info['game']['full']}{Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}Движок: {Colors.BRIGHT_YELLOW}{info['engine']['full']}{Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}Pymust: {Colors.BRIGHT_YELLOW}{info['pymust']['full']}{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_CYAN}Детали:{Colors.RESET}")
        print(f"  - {Colors.BRIGHT_GREEN}Версия игры: {Colors.BRIGHT_YELLOW}{info['game']['version']}{Colors.RESET}")
        print(f"  - {Colors.BRIGHT_GREEN}Стадия разработки: {Colors.BRIGHT_YELLOW}{info['game']['stage']}{Colors.RESET}")
        print(f"  - {Colors.BRIGHT_GREEN}Номер сборки: {Colors.BRIGHT_YELLOW}{info['game']['build']}{Colors.RESET}")
        print(f"  - {Colors.BRIGHT_GREEN}Название движка: {Colors.BRIGHT_YELLOW}{info['engine']['name']}{Colors.RESET}")
        print(f"  - {Colors.BRIGHT_GREEN}Версия движка: {Colors.BRIGHT_YELLOW}{info['engine']['version']}{Colors.RESET}")
        print(f"  - {Colors.BRIGHT_GREEN}Версия pymust: {Colors.BRIGHT_YELLOW}{info['pymust']['version']}{Colors.RESET}")
        return
    
    # Обновление стадии разработки
    if args.stage:
        print(f"{Colors.BRIGHT_CYAN}Обновление стадии разработки на '{args.stage}'...{Colors.RESET}")
        set_game_stage(args.stage)
        print(f"{Colors.BRIGHT_GREEN}Стадия разработки обновлена!{Colors.RESET}")
    
    # Определяем тип инкремента
    increment_type = 'patch'  # по умолчанию
    if args.minor:
        increment_type = 'minor'
    elif args.major:
        increment_type = 'major'
    
    # Обновление версии
    if args.patch or args.minor or args.major:
        if args.engine:
            print(f"{Colors.BRIGHT_CYAN}Обновление версии движка (тип: {increment_type})...{Colors.RESET}")
            new_version = update_engine_version(increment_type)
            print(f"{Colors.BRIGHT_GREEN}Версия движка обновлена до: {Colors.BRIGHT_YELLOW}{new_version}{Colors.RESET}")
        elif args.pymust:
            print(f"{Colors.BRIGHT_CYAN}Обновление версии pymust (тип: {increment_type})...{Colors.RESET}")
            new_version = update_pymust_version(increment_type)
            print(f"{Colors.BRIGHT_GREEN}Версия pymust обновлена до: {Colors.BRIGHT_YELLOW}{new_version}{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_CYAN}Обновление версии игры (тип: {increment_type})...{Colors.RESET}")
            new_version = update_game_version(increment_type)
            print(f"{Colors.BRIGHT_GREEN}Версия игры обновлена до: {Colors.BRIGHT_YELLOW}{new_version}{Colors.RESET}")
    
    # Вывод итоговой информации
    info = get_full_version_info()
    print(f"\n{Colors.BRIGHT_CYAN}Итоговая информация о версии:{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}Игра: {Colors.BRIGHT_YELLOW}{info['game']['full']}{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}Движок: {Colors.BRIGHT_YELLOW}{info['engine']['full']}{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}Pymust: {Colors.BRIGHT_YELLOW}{info['pymust']['full']}{Colors.RESET}")

if __name__ == "__main__":
    main() 