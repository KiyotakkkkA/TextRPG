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
    set_game_stage, 
    get_full_version_info
)

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
    
    # Обновление движка
    parser.add_argument('--engine', action='store_true', help='Обновлять версию движка вместо игры')
    
    # Флаг для вывода информации о текущей версии
    parser.add_argument('--info', action='store_true', help='Показать информацию о текущей версии')
    
    args = parser.parse_args()
    
    # Просмотр информации о версии
    if args.info or (not any([args.patch, args.minor, args.major, args.stage])):
        info = get_full_version_info()
        print(f"\nИнформация о текущей версии:")
        print(f"Игра: {info['game']['full']}")
        print(f"Движок: {info['engine']['full']}")
        print(f"\nДетали:")
        print(f"  - Версия игры: {info['game']['version']}")
        print(f"  - Стадия разработки: {info['game']['stage']}")
        print(f"  - Номер сборки: {info['game']['build']}")
        print(f"  - Название движка: {info['engine']['name']}")
        print(f"  - Версия движка: {info['engine']['version']}")
        return
    
    # Обновление стадии разработки
    if args.stage:
        print(f"Обновление стадии разработки на '{args.stage}'...")
        set_game_stage(args.stage)
        print(f"Стадия разработки обновлена!")
    
    # Определяем тип инкремента
    increment_type = 'patch'  # по умолчанию
    if args.minor:
        increment_type = 'minor'
    elif args.major:
        increment_type = 'major'
    
    # Обновление версии
    if args.patch or args.minor or args.major:
        if args.engine:
            print(f"Обновление версии движка (тип: {increment_type})...")
            new_version = update_engine_version(increment_type)
            print(f"Версия движка обновлена до: {new_version}")
        else:
            print(f"Обновление версии игры (тип: {increment_type})...")
            new_version = update_game_version(increment_type)
            print(f"Версия игры обновлена до: {new_version}")
    
    # Вывод итоговой информации
    info = get_full_version_info()
    print(f"\nИтоговая информация о версии:")
    print(f"Игра: {info['game']['full']}")
    print(f"Движок: {info['engine']['full']}")

if __name__ == "__main__":
    main() 