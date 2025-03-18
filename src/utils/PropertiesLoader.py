"""
Модуль для загрузки и чтения файлов свойств (.properties).
"""

import os
from typing import Dict, Any, Optional

class PropertiesLoader:
    """
    Класс для загрузки и чтения файлов свойств (.properties).
    Поддерживает комментарии (начинающиеся с # или !) и свойства в формате ключ=значение.
    """
    
    def __init__(self, file_path: str):
        """
        Инициализирует загрузчик свойств с указанным путем к файлу.
        
        :param file_path: Путь к файлу свойств.
        """
        self.file_path = file_path
        self.properties = {}
        self.load()
    
    def load(self) -> Dict[str, str]:
        """
        Загружает свойства из файла.
        
        :return: Словарь свойств.
        """
        try:
            if not os.path.exists(self.file_path):
                # Файл не существует, возвращаем пустой словарь
                return {}
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith('#') or line.startswith('!'):
                        continue
                    
                    # Разбиваем строку на ключ и значение
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        self.properties[key] = value
            
            return self.properties
        except Exception as e:
            print(f"Ошибка при загрузке свойств из {self.file_path}: {str(e)}")
            return {}
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Получает значение свойства по ключу.
        
        :param key: Ключ свойства.
        :param default: Значение по умолчанию, если свойство не найдено.
        :return: Значение свойства или значение по умолчанию.
        """
        return self.properties.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        Получает целочисленное значение свойства по ключу.
        
        :param key: Ключ свойства.
        :param default: Значение по умолчанию, если свойство не найдено или не может быть преобразовано в int.
        :return: Целочисленное значение свойства или значение по умолчанию.
        """
        try:
            return int(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        Получает значение свойства в виде числа с плавающей точкой по ключу.
        
        :param key: Ключ свойства.
        :param default: Значение по умолчанию, если свойство не найдено или не может быть преобразовано в float.
        :return: Значение свойства в виде числа с плавающей точкой или значение по умолчанию.
        """
        try:
            return float(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Получает булево значение свойства по ключу.
        Строки 'true', 'yes', '1', 'on' (без учета регистра) считаются True,
        все остальные - False.
        
        :param key: Ключ свойства.
        :param default: Значение по умолчанию, если свойство не найдено.
        :return: Булево значение свойства или значение по умолчанию.
        """
        value = self.get(key)
        if value is None:
            return default
        
        return value.lower() in ('true', 'yes', '1', 'on')
    
    def get_all(self) -> Dict[str, str]:
        """
        Получает все свойства.
        
        :return: Словарь всех свойств.
        """
        return self.properties
    
    def get_with_prefix(self, prefix: str) -> Dict[str, str]:
        """
        Получает все свойства, ключи которых начинаются с указанного префикса.
        
        :param prefix: Префикс ключей.
        :return: Словарь свойств с указанным префиксом.
        """
        return {k: v for k, v in self.properties.items() if k.startswith(prefix)}
    
    def set(self, key: str, value: Any) -> None:
        """
        Устанавливает значение свойства.
        
        :param key: Ключ свойства.
        :param value: Значение свойства.
        """
        self.properties[key] = str(value)
    
    def save(self) -> bool:
        """
        Сохраняет свойства в файл.
        
        :return: True, если сохранение прошло успешно, иначе False.
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                for key, value in self.properties.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Ошибка при сохранении свойств в {self.file_path}: {str(e)}")
            return False

# Функция для получения глобального загрузчика свойств версии
_version_loader = None

def get_version_properties():
    """
    Получает глобальный загрузчик свойств версии.
    
    :return: Экземпляр PropertiesLoader для файла версии.
    """
    global _version_loader
    if _version_loader is None:
        # Определяем путь к файлу свойств в корне проекта
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '../..'))
        properties_path = os.path.join(project_root, 'version.properties')
        _version_loader = PropertiesLoader(properties_path)
    
    return _version_loader