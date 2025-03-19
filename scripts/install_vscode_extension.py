#!/usr/bin/env python3
"""
Скрипт для установки расширения VSCode для подсветки синтаксиса .desc файлов.
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Optional

def get_vscode_extensions_dir() -> Optional[Path]:
    """
    Возвращает путь к директории расширений VSCode.
    
    Returns:
        Optional[Path]: Путь к директории расширений или None, если не найдена
    """
    system = platform.system()
    
    if system == "Windows":
        # %USERPROFILE%\.vscode\extensions
        user_profile = os.environ.get("USERPROFILE")
        if user_profile:
            extensions_dir = Path(user_profile) / ".vscode" / "extensions"
            return extensions_dir
    
    elif system == "Darwin":  # macOS
        # ~/.vscode/extensions
        home = os.environ.get("HOME")
        if home:
            extensions_dir = Path(home) / ".vscode" / "extensions"
            return extensions_dir
    
    elif system == "Linux":
        # ~/.vscode/extensions
        home = os.environ.get("HOME")
        if home:
            extensions_dir = Path(home) / ".vscode" / "extensions"
            return extensions_dir
    
    return None

def is_vscode_installed() -> bool:
    """
    Проверяет, установлен ли VSCode.
    
    Returns:
        bool: True, если VSCode установлен, иначе False
    """
    system = platform.system()
    
    try:
        if system == "Windows":
            # Проверяем, есть ли в PATH команда code
            result = subprocess.run(
                ["where", "code"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        else:  # Linux или macOS
            result = subprocess.run(
                ["which", "code"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
    except Exception:
        return False

def install_extension() -> bool:
    """
    Устанавливает расширение VSCode для подсветки синтаксиса .desc файлов.
    
    Returns:
        bool: True, если установка успешна, иначе False
    """
    # Проверяем, что VSCode установлен
    if not is_vscode_installed():
        print("VSCode не найден. Убедитесь, что VSCode установлен и доступен в PATH.")
        return False
    
    # Получаем директорию расширений VSCode
    extensions_dir = get_vscode_extensions_dir()
    if not extensions_dir:
        print("Не удалось определить директорию расширений VSCode.")
        return False
    
    # Создаем директорию расширений, если её нет
    if not extensions_dir.exists():
        try:
            extensions_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Ошибка при создании директории расширений: {e}")
            return False
    
    # Путь к исходной директории расширения
    current_dir = Path(__file__).parent
    source_dir = current_dir / "pymustlib" / "vscode-desc-extension"
    
    if not source_dir.exists():
        print(f"Директория с расширением не найдена: {source_dir}")
        return False
    
    # Целевая директория для расширения
    target_dir = extensions_dir / "textrpg-team.desc-language"
    
    # Удаляем предыдущую версию расширения, если она существует
    if target_dir.exists():
        try:
            shutil.rmtree(target_dir)
        except Exception as e:
            print(f"Ошибка при удалении предыдущей версии расширения: {e}")
            return False
    
    # Копируем расширение в директорию расширений VSCode
    try:
        shutil.copytree(source_dir, target_dir)
        print(f"Расширение успешно установлено в: {target_dir}")
        
        # Если VSCode запущен, предлагаем перезапустить
        print("Для применения изменений может потребоваться перезапустить VSCode.")
        return True
    except Exception as e:
        print(f"Ошибка при копировании расширения: {e}")
        return False

def main():
    """
    Основная функция скрипта.
    """
    print("Установка расширения VSCode для подсветки синтаксиса .desc файлов...")
    
    if install_extension():
        print("Установка завершена успешно.")
        return 0
    else:
        print("Установка не удалась.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 