"""
Утилиты для управления версиями игры.
Позволяют обновлять версии игры и движка в файле свойств.
"""
import os
import re
from pathlib import Path
from src.utils.PropertiesLoader import get_version_properties

def get_version_components(version_str):
    """
    Разбивает строку версии на компоненты.
    
    Args:
        version_str (str): Строка версии в формате "x.y.z"
        
    Returns:
        tuple: (major, minor, patch) - компоненты версии в виде целых чисел
    """
    if not version_str:
        return (0, 0, 0)
    
    components = re.findall(r'\d+', version_str)
    major = int(components[0]) if len(components) > 0 else 0
    minor = int(components[1]) if len(components) > 1 else 0
    patch = int(components[2]) if len(components) > 2 else 0
    
    return (major, minor, patch)

def increment_version(version_str, increment_type='patch'):
    """
    Увеличивает версию согласно семантическому версионированию.
    
    Args:
        version_str (str): Текущая версия в формате "x.y.z"
        increment_type (str): Тип инкремента ('major', 'minor', 'patch')
        
    Returns:
        str: Новая версия в формате "x.y.z"
    """
    major, minor, patch = get_version_components(version_str)
    
    if increment_type == 'major':
        return f"{major + 1}.0.0"
    elif increment_type == 'minor':
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"

def update_game_version(increment_type='patch'):
    """
    Обновляет версию игры в файле свойств.
    
    Args:
        increment_type (str): Тип инкремента ('major', 'minor', 'patch')
        
    Returns:
        str: Новая версия игры
    """
    props = get_version_properties()
    current_version = props.get('game.version', '0.1.0')
    new_version = increment_version(current_version, increment_type)
    
    # Обновляем версию в свойствах
    props.set('game.version', new_version)
    
    # Обновляем дату сборки (опционально)
    from datetime import datetime
    build_date = datetime.now().strftime('%Y%m%d')
    props.set('game.build', build_date)
    
    # Сохраняем изменения
    props.save()
    
    return new_version

def update_engine_version(increment_type='patch'):
    """
    Обновляет версию движка в файле свойств.
    
    Args:
        increment_type (str): Тип инкремента ('major', 'minor', 'patch')
        
    Returns:
        str: Новая версия движка
    """
    props = get_version_properties()
    current_version = props.get('engine.version', '1.0.0')
    new_version = increment_version(current_version, increment_type)
    
    # Обновляем версию в свойствах
    props.set('engine.version', new_version)
    
    # Сохраняем изменения
    props.save()
    
    return new_version

def update_pymust_version(increment_type='patch'):
    """
    Обновляет версию pymust в файле свойств.
    
    Args:
        increment_type (str): Тип инкремента ('major', 'minor', 'patch')
        
    Returns:
        str: Новая версия pymust
    """
    props = get_version_properties()
    current_version = props.get('pymust.version', '0.1.0')
    new_version = increment_version(current_version, increment_type)
    
    # Обновляем версию в свойствах
    props.set('pymust.version', new_version)
    
    # Сохраняем изменения
    props.save()
    
    return new_version

def set_game_stage(stage):
    """
    Устанавливает стадию разработки игры.
    
    Args:
        stage (str): Стадия разработки (например, "Alpha", "Beta", "Release")
        
    Returns:
        str: Новая стадия
    """
    props = get_version_properties()
    props.set('game.stage', stage)
    props.save()
    return stage

def get_full_version_info():
    """
    Возвращает полную информацию о версии в удобном формате.
    
    Returns:
        dict: Словарь с информацией о версии
    """
    props = get_version_properties()
    game_version = props.get('game.version', '0.1.0')
    game_stage = props.get('game.stage', 'Alpha')
    engine_version = props.get('engine.version', '1.0.0')
    engine_name = props.get('engine.name', 'TextRPG Engine')
    build = props.get('game.build', 'unknown')
    pymust_version = props.get('pymust.version', '0.1.0')
    
    return {
        'game': {
            'version': game_version,
            'stage': game_stage,
            'build': build,
            'full': f"v{game_version} {game_stage} (build {build})"
        },
        'engine': {
            'version': engine_version,
            'name': engine_name,
            'full': f"{engine_name} v{engine_version}"
        },
        'pymust': {
            'version': pymust_version,
            'full': f"pymust v{pymust_version}"
        }
    }

# Пример использования
if __name__ == "__main__":
    info = get_full_version_info()
    print(f"Версия игры: {info['game']['full']}")
    print(f"Версия движка: {info['engine']['full']}")
    print(f"Версия pymust: {info['pymust']['full']}") 