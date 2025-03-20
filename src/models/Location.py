"""
Модель локации для игры.
Локация содержит ресурсы, которые можно собирать, и соединения с другими локациями.
"""

import random
import time
import json
import copy  # Добавляю импорт модуля copy для глубокого копирования
from typing import Dict, List, Any, Optional

from src.models.interfaces.Require import Require
from src.models.interfaces.Serializable import Serializable

class Location(Require, Serializable):
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
        
        # Связь с регионом
        self.region_id = data.get("region_id", "")
        
        # Координаты внутри региона
        self.region_x = data.get("region_x", 0)
        self.region_y = data.get("region_y", 0)
        
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
        
        # Требования для доступа к локации
        self.requires = data.get("requires", {})
        
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
        Возвращает словарь с данными локации.
        
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
            "region_id": self.region_id,
            "region_x": self.region_x,
            "region_y": self.region_y,
            "resources": self._resources_data,
            "connections": self.connections,
            "characters": self.characters,
            "properties": self.properties,
            "resources_respawn_time": self.resources_respawn_time
        }
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление локации.
        
        Returns:
            str: Строковое представление
        """
        return f"{self.icon} {self.name} [{self.id}]"

    def can_access(self, player, game_system) -> bool:
        """
        Проверяет, может ли игрок получить доступ к этой локации.
        
        Args:
            player: Объект игрока
            game_system: Игровая система
            
        Returns:
            bool: True, если игрок может получить доступ, иначе False
        """
        # Проверяем требования для доступа к локации
        return self.check_requirements(self.requires, player, game_system)
    
    def can_use_connection(self, connection_id: str, player, game_system) -> bool:
        """
        Проверяет, может ли игрок использовать соединение для перехода в другую локацию.
        
        Args:
            connection_id (str): ID соединения
            player: Объект игрока
            game_system: Игровая система
            
        Returns:
            bool: True, если игрок может использовать соединение, иначе False
        """
        # Ищем соединение по ID
        for conn in self.connections:
            # Проверяем, является ли соединение словарем или строкой
            conn_id = ""
            if isinstance(conn, dict):
                conn_id = conn.get("id", "").lower()
                # Проверяем требования для соединения
                requires = conn.get("requires", {})
                if conn_id == connection_id.lower():
                    # Проверяем требования соединения
                    if requires and not self.check_requirements(requires, player, game_system):
                        return False
                    
                    # Проверяем требования целевой локации
                    target_location = game_system.get_location(conn_id)
                    if target_location:
                        return target_location.can_access(player, game_system)
                    return False
            else:
                conn_id = str(conn).lower()
                if conn_id == connection_id.lower():
                    # Проверяем требования целевой локации
                    target_location = game_system.get_location(conn_id)
                    if target_location:
                        return target_location.can_access(player, game_system)
                    return False
                
        return False 