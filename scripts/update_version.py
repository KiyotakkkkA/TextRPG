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
- python update_version.py --patch --log  # создает запись об обновлении в changelog
- python update_version.py --patch --log --name=UpdateName  # создает запись с названием
"""

import os
import sys
import argparse
import json
import hashlib
import time
from pathlib import Path
import shutil

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

def load_letters():
    """Загружает ASCII-арты для букв из файла."""
    try:
        letters_path = root_dir / "data" / "arts" / "letters.json"
        with open(letters_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}Ошибка при загрузке ASCII-артов букв: {str(e)}{Colors.RESET}")
        return {}

def generate_art(text, letters):
    """Генерирует ASCII-арт из текста."""
    if not text or not letters:
        return ""
    
    # Преобразуем текст в допустимые символы
    text = ''.join([char if char in letters else ' ' for char in text])
    
    # Получаем ASCII-арт для каждого символа
    char_arts = [letters.get(char, letters.get(' ', '')) for char in text]
    
    # Разбиваем арты по строкам
    art_lines = [art.split('\n') for art in char_arts]
    
    # Определяем максимальное количество строк
    max_lines = max([len(lines) for lines in art_lines], default=0)
    
    # Формируем итоговый арт
    result = []
    for i in range(max_lines):
        line = ""
        for char_lines in art_lines:
            if i < len(char_lines):
                line += char_lines[i] + " "
            else:
                # Если у символа меньше строк, добавляем пробелы
                line += " " * (len(char_lines[0]) + 1)
        result.append(line)
    
    return '\n'.join(result)

def create_changelog_entry(update_name=None):
    """
    Создает запись в журнале изменений.
    
    Args:
        update_name (str, optional): Название обновления
    
    Returns:
        str: Хеш обновления
    """
    # Получаем информацию о версии
    version_info = get_full_version_info()
    
    # Формируем строку для хеширования
    version_str = f"{version_info['game']['version']}_{version_info['game']['stage']}_{version_info['game']['build']}"
    
    # Создаем хеш на основе версии
    version_hash = hashlib.md5(version_str.encode()).hexdigest()
    
    # Создаем директорию для обновления
    changelog_dir = root_dir / "changelog" / version_hash
    os.makedirs(changelog_dir, exist_ok=True)
    
    # Создаем файл changes.txt для записи информации об обновлении
    changes_file = changelog_dir / "changes.txt"
    
    # Проверяем, существует ли файл
    if not changes_file.exists():
        with open(changes_file, 'w', encoding='utf-8') as f:
            f.write(f"# Обновление v{version_info['game']['version']} {version_info['game']['stage']}\n")
            f.write(f"Дата: {time.strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"Сборка: {version_info['game']['build']}\n")
            f.write("\n## Изменения\n")
            f.write("- Здесь будет список изменений\n")
            f.write("\n## Исправления\n")
            f.write("- Здесь будет список исправлений\n")
        
        print(f"{Colors.BRIGHT_GREEN}Создан файл с изменениями: {changes_file}{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}Отредактируйте его, чтобы добавить информацию об обновлении.{Colors.RESET}")
    else:
        print(f"{Colors.BRIGHT_YELLOW}Файл с изменениями уже существует: {changes_file}{Colors.RESET}")
    
    # Если указано имя обновления, создаем ASCII-арт
    if update_name:
        # Загружаем буквы
        letters = load_letters()
        
        # Генерируем ASCII-арт
        art = generate_art(update_name, letters)
        
        # Сохраняем арт в файл
        art_file = changelog_dir / "art.json"
        with open(art_file, 'w', encoding='utf-8') as f:
            json.dump({
                "name": update_name,
                "art": art,
                "timestamp": int(time.time())
            }, f, ensure_ascii=False, indent=2)
        
        print(f"{Colors.BRIGHT_GREEN}Создан ASCII-арт для обновления: {art_file}{Colors.RESET}")
    
    # Обновляем head.json
    head_file = root_dir / "changelog" / "head.json"
    
    # Проверяем, существует ли файл head.json и читаем его содержимое
    existing_history = []
    if os.path.exists(head_file):
        try:
            with open(head_file, 'r', encoding='utf-8') as f:
                head_content = json.load(f)
                if "history" in head_content and isinstance(head_content["history"], list):
                    existing_history = head_content["history"]
        except Exception as e:
            print(f"{Colors.BRIGHT_YELLOW}Предупреждение: не удалось прочитать историю обновлений: {str(e)}{Colors.RESET}")
    
    # Создаем новую историю, добавляя текущий хеш в начало
    if version_hash not in existing_history:
        history = [version_hash] + existing_history
    else:
        # Если такой хеш уже есть, удаляем его из старого места и добавляем в начало
        existing_history.remove(version_hash)
        history = [version_hash] + existing_history
    
    # Обновляем данные для head.json
    head_data = {
        "current_hash": version_hash,
        "update_name": update_name,
        "timestamp": int(time.time()),
        "history": history
    }
    
    with open(head_file, 'w', encoding='utf-8') as f:
        json.dump(head_data, f, ensure_ascii=False, indent=2)
    
    print(f"{Colors.BRIGHT_GREEN}Обновлен файл {head_file}{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}История обновлений: {Colors.BRIGHT_YELLOW}{', '.join(history[:3])}{Colors.BRIGHT_BLACK}{'...' if len(history) > 3 else ''}{Colors.RESET}")
    
    return version_hash

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
    
    # Новые параметры для системы changelog
    parser.add_argument('--log', action='store_true', help='Создать запись в журнале изменений')
    parser.add_argument('--name', type=str, help='Название обновления для отображения в главном меню')
    
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
            
            # Если указан флаг --log, создаем запись в журнале изменений
            if args.log:
                print(f"{Colors.BRIGHT_CYAN}Создание записи в журнале изменений...{Colors.RESET}")
                update_hash = create_changelog_entry(args.name)
                print(f"{Colors.BRIGHT_GREEN}Запись создана с хешем: {Colors.BRIGHT_YELLOW}{update_hash}{Colors.RESET}")
    
    # Вывод итоговой информации
    info = get_full_version_info()
    print(f"\n{Colors.BRIGHT_CYAN}Итоговая информация о версии:{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}Игра: {Colors.BRIGHT_YELLOW}{info['game']['full']}{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}Движок: {Colors.BRIGHT_YELLOW}{info['engine']['full']}{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}Pymust: {Colors.BRIGHT_YELLOW}{info['pymust']['full']}{Colors.RESET}")

if __name__ == "__main__":
    main() 