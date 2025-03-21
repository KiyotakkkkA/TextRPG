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
            vscode_extensions_dir = Path(user_profile) / ".vscode" / "extensions"
            cursor_extensions_dir = Path(user_profile) / ".cursor" / "extensions"
            return vscode_extensions_dir, cursor_extensions_dir
    
    elif system == "Darwin":  # macOS
        # ~/.vscode/extensions
        home = os.environ.get("HOME")
        if home:
            vscode_extensions_dir = Path(home) / ".vscode" / "extensions"
            cursor_extensions_dir = Path(home) / ".cursor" / "extensions"
            return vscode_extensions_dir, cursor_extensions_dir
    
    elif system == "Linux":
        # ~/.vscode/extensions
        home = os.environ.get("HOME")
        if home:
            vscode_extensions_dir = Path(home) / ".vscode" / "extensions"
            cursor_extensions_dir = Path(home) / ".cursor" / "extensions"
            return vscode_extensions_dir, cursor_extensions_dir
    
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
    vscode_extensions_dir, cursor_extensions_dir = get_vscode_extensions_dir()
    if not vscode_extensions_dir:
        print("Не удалось определить директорию расширений VSCode.")
        return False
    if not cursor_extensions_dir:
        print("Не удалось определить директорию расширений Cursor.")
        return False
    
    # Путь к исходной директории расширения
    current_dir = Path(__file__).parent
    source_dir = current_dir / "pymustlib" / "vscode-desc-extension"
    
    if not source_dir.exists():
        print(f"Директория с расширением не найдена: {source_dir}")
        return False
    
    # Целевая директория для расширения
    vscode_target_dir = vscode_extensions_dir / "textrpg-team.desc-language"
    cursor_target_dir = cursor_extensions_dir / "textrpg-team.desc-language"
    
    # Удаляем предыдущую версию расширения, если она существует
    if vscode_target_dir.exists():
        try:
            shutil.rmtree(vscode_target_dir)
        except Exception as e:
            print(f"Ошибка при удалении предыдущей версии расширения: {e}")
            return False
    if cursor_target_dir.exists():
        try:
            shutil.rmtree(cursor_target_dir)
        except Exception as e:
            print(f"Ошибка при удалении предыдущей версии расширения: {e}")
            return False
    
    # Копируем расширение в директорию расширений VSCode
    try:
        shutil.copytree(source_dir, vscode_target_dir)
        shutil.copytree(source_dir, cursor_target_dir)
        print(f"Расширение успешно установлено в: {vscode_target_dir}")
        print(f"Расширение успешно установлено в: {cursor_target_dir}")
        
        # Если VSCode запущен, предлагаем перезапустить
        print("Для применения изменений может потребоваться перезапустить VSCode и Cursor")
        return True
    except Exception as e:
        print(f"Ошибка при копировании расширения: {e}")
        return False

def main():
    """
    Основная функция скрипта.
    """
    print("Установка расширения VSCode и Cursor для подсветки синтаксиса .desc файлов...")
    
    if install_extension():
        print("Установка завершена успешно.")
        return 0
    else:
        print("Установка не удалась.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 