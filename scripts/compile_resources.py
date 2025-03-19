#!/usr/bin/env python3
"""
Автоматический компилятор ресурсов из .desc в JSON для TextRPG.
Этот скрипт запускается перед запуском игры и конвертирует все .desc файлы в формат JSON.

Использование:
    python compile_resources.py
"""

import os
import sys
import json
import argparse
import time
from typing import List, Dict, Any, Tuple
from pathlib import Path

# Определяем корневой каталог проекта
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
RESOURCES_DIR = DATA_DIR / "resources"
DESC_DIR = ROOT_DIR / "desc"

# Импортируем модуль desc_to_json
sys.path.append(str(ROOT_DIR / "scripts"))
from desc_to_json import DescParser, convert_file


def setup_directories() -> None:
    """
    Настраивает необходимые директории.
    Создает их, если они не существуют.
    """
    directories = [
        DESC_DIR,
        DESC_DIR / "locations",
        DESC_DIR / "items",
        RESOURCES_DIR,
        RESOURCES_DIR / "locations",
        RESOURCES_DIR / "items"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def find_desc_files() -> List[Tuple[Path, Path]]:
    """
    Находит все .desc файлы и определяет для них соответствующие .json файлы.
    
    Returns:
        Список кортежей (путь_к_desc_файлу, путь_к_json_файлу)
    """
    desc_files = []
    
    # Рекурсивно ищем все .desc файлы
    for root, _, files in os.walk(DESC_DIR):
        for file in files:
            if file.endswith('.desc'):
                desc_path = Path(root) / file
                
                # Определяем соответствующий путь к JSON файлу
                rel_path = os.path.relpath(root, DESC_DIR)
                json_dir = RESOURCES_DIR / rel_path
                os.makedirs(json_dir, exist_ok=True)
                
                json_path = json_dir / file.replace('.desc', '.json')
                desc_files.append((desc_path, json_path))
    
    return desc_files


def should_compile(desc_path: Path, json_path: Path) -> bool:
    """
    Определяет, нужно ли компилировать .desc файл.
    Компилируем, если JSON файла нет или .desc файл новее.
    
    Args:
        desc_path: Путь к .desc файлу
        json_path: Путь к JSON файлу
        
    Returns:
        True, если нужно компилировать
    """
    if not json_path.exists():
        return True
    
    desc_time = desc_path.stat().st_mtime
    json_time = json_path.stat().st_mtime
    
    return desc_time > json_time


def compile_resources(force: bool = False) -> Tuple[int, int]:
    """
    Компилирует все .desc файлы в JSON.
    
    Args:
        force: Принудительная компиляция всех файлов, даже если они не изменились
        
    Returns:
        (количество скомпилированных файлов, общее количество файлов)
    """
    desc_files = find_desc_files()
    compiled_count = 0
    
    for desc_path, json_path in desc_files:
        if force or should_compile(desc_path, json_path):
            print(f"Компиляция: {desc_path} -> {json_path}")
            if convert_file(str(desc_path), str(json_path)):
                compiled_count += 1
    
    return compiled_count, len(desc_files)


def create_example_desc() -> None:
    """
    Создает пример .desc файла, если в директории нет .desc файлов.
    """
    if not list(DESC_DIR.glob('**/*.desc')):
        example_path = DESC_DIR / "locations" / "example.desc"
        
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write("""# Пример описания локации в формате .desc

LOCATION forest {
    name: "Лес"
    description: "Густой лес с множеством растений и животных. Здесь можно найти различные лекарственные травы и редкие ингредиенты."
    type: wilderness
    color: green
    
    RESOURCES {
        RESOURCE herb {
            min_amount: 2
            max_amount: 4
            respawn_time: 120
            required_tool: null
        }
        
        RESOURCE mushroom {
            min_amount: 1
            max_amount: 3
            respawn_time: 180
            required_tool: null
        }
    }
    
    CONNECTIONS {
        CONNECTION {
            id: mountains
            name: "Горы"
            condition: null
        }
        
        CONNECTION {
            id: village
            name: "Деревня"
            condition: null
        }
    }
    
    CHARACTERS {
        CHARACTER hermit {
            name: "Отшельник"
            description: "Старый отшельник, живущий в лесу. Знает множество лесных тайн."
        }
    }
    
    PROPERTIES {
        danger_level: 1
        weather: [sunny, rainy, foggy]
    }
}
""")
        
        print(f"Создан пример .desc файла: {example_path}")


def main():
    """
    Основная функция программы.
    """
    parser = argparse.ArgumentParser(description='Компилирует .desc файлы в JSON')
    parser.add_argument('--force', action='store_true', help='Принудительная компиляция всех файлов')
    parser.add_argument('--create-example', action='store_true', help='Создать пример .desc файла')
    
    args = parser.parse_args()
    
    # Настраиваем директории
    setup_directories()
    
    # Создаем пример, если нужно
    if args.create_example:
        create_example_desc()
    
    # Компилируем ресурсы
    start_time = time.time()
    compiled, total = compile_resources(args.force)
    end_time = time.time()
    
    print(f"Компиляция завершена за {end_time - start_time:.2f} секунд.")
    print(f"Скомпилировано {compiled} из {total} файлов.")
    
    # Если нет .desc файлов, предлагаем создать пример
    if total == 0:
        print("Не найдено ни одного .desc файла. Используйте --create-example для создания примера.")


if __name__ == "__main__":
    main() 