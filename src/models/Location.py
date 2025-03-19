"""
Модель локации для игры.
Локация содержит ресурсы, которые можно собирать, и соединения с другими локациями.
"""

import random
import time
import json
import copy  # Добавляю импорт модуля copy для глубокого копирования
from typing import Dict, List, Any, Optional

class Location:
    """
    Класс, представляющий локацию в игровом мире.
    Локация содержит ресурсы, которые можно собирать, и соединения с другими локациями.
    """
    
    def __init__(self, location_id: str, data: Dict[str, Any]):
        """
        Инициализирует локацию.
        
        Args:
            location_id (str): Уникальный идентификатор локации
            data (dict): Данные локации из JSON
        """
        self.id = location_id
        self.name = data.get("name", "Неизвестная локация")
        self.description = data.get("description", "Нет описания")
        self.type = data.get("type", "generic")
        self.icon = data.get("icon", "🌍")
        self.color = data.get("color", "white")
        
        # Ресурсы, доступные на локации
        self.available_resources = {}
        self._resources_data = data.get("resources", {})
        self._spawn_resources()
        
        # Соединения с другими локациями
        self.connections = data.get("connections", [])
        
        # Персонажи на локации
        self.characters = data.get("characters", [])
        
        # Дополнительные свойства локации
        self.properties = data.get("properties", {})
        
        # Время последнего обновления ресурсов
        self.last_resources_update = 0
        self.resources_respawn_time = data.get("resources_respawn_time", 600)  # в секундах
    
    def _spawn_resources(self):
        """
        Спавнит ресурсы на локации в случайном количестве согласно настройкам.
        """
        # Создаем новый пустой словарь для ресурсов
        self.available_resources = {}
        
        # Создаем глубокие копии данных о ресурсах для каждой локации
        # Это предотвратит проблему с удалением ресурсов со всех локаций при сборе на одной локации
        for resource_id, resource_data in self._resources_data.items():
            # Создаем глубокую копию данных о ресурсе
            resource_copy = copy.deepcopy(resource_data)
            min_amount = resource_copy.get("min_amount", 0)
            max_amount = resource_copy.get("max_amount", 0)
            
            # Если max_amount == 0, то ресурс не спавнится
            if max_amount > 0:
                # Выбираем случайное количество ресурса между min и max
                amount = random.randint(min_amount, max_amount)
                if amount > 0:
                    self.available_resources[resource_id] = amount
    
    def respawn_resources(self, current_time: float) -> bool:
        """
        Проверяет, нужно ли обновить ресурсы на локации.
        
        Args:
            current_time (float): Текущее время
            
        Returns:
            bool: True, если ресурсы были обновлены
        """
        # Если прошло достаточно времени с момента последнего обновления
        if current_time - self.last_resources_update >= self.resources_respawn_time:
            self._spawn_resources()
            self.last_resources_update = current_time
            return True
        return False
    
    def collect_resource(self, resource_id: str, amount: int = 1) -> int:
        """
        Собирает ресурс с локации.
        
        Args:
            resource_id (str): ID ресурса
            amount (int): Количество для сбора
            
        Returns:
            int: Фактическое количество собранного ресурса
        """
        if resource_id not in self.available_resources:
            return 0
        
        available = self.available_resources[resource_id]
        
        # Определяем, сколько можно собрать
        to_collect = min(available, amount)
        
        # Уменьшаем доступное количество
        self.available_resources[resource_id] -= to_collect
        
        # Оставляем ресурс в списке даже если его количество равно 0
        # Это позволяет отображать его в интерфейсе и проверять время респауна
        # Ресурс с количеством 0 все равно не может быть собран (проверка выше)
        # Удалять ресурс будем только при инициализации новых ресурсов методом _spawn_resources
        
        return to_collect
    
    def get_resource_data(self, resource_id: str) -> Dict[str, Any]:
        """
        Возвращает данные ресурса.
        
        Args:
            resource_id (str): ID ресурса
            
        Returns:
            dict: Данные ресурса
        """
        return self._resources_data.get(resource_id, {})
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует локацию в словарь для сериализации.
        
        Returns:
            dict: Словарь с данными локации
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "icon": self.icon,
            "color": self.color,
            "available_resources": self.available_resources,
            "connections": self.connections,
            "characters": self.characters,
            "properties": self.properties,
            "last_resources_update": self.last_resources_update
        }
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление локации.
        
        Returns:
            str: Строковое представление
        """
        return f"{self.icon} {self.name} [{self.id}]" 