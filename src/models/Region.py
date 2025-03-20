"""
Модель региона для игры.
Регион объединяет несколько локаций, представляя собой географическую область.
"""

from typing import Dict, List, Any, Optional
import random
from src.models.interfaces import Require, Serializable

class Region(Require, Serializable):
    """
    Класс, представляющий регион в игре.
    Регион содержит несколько локаций и имеет свои характеристики.
    """
    
    def __init__(self, data):
        """
        Инициализирует регион на основе данных.
        
        Args:
            data (dict): Данные региона.
        """
        self.id = data.get("id", "")
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.locations = data.get("locations", [])
        self.starting_location = data.get("starting_location", "")
        self.connections = data.get("connections", [])
        self.climate = data.get("climate", "умеренный")
        self.difficulty = data.get("difficulty", "нормальный")
        self.requires = data.get("requires", {})
        self.icon = data.get("icon", "🌍")
        
        # Координаты региона на глобальной карте
        self.x = data.get("x", 0)
        self.y = data.get("y", 0)
        
        # Соседние регионы
        self.adjacent_regions = data.get("adjacent_regions", [])
    
    def add_location(self, location_id: str):
        """
        Добавляет локацию в регион.
        
        Args:
            location_id (str): ID локации
        """
        if location_id not in self.locations:
            self.locations.append(location_id)
    
    def remove_location(self, location_id: str):
        """
        Удаляет локацию из региона.
        
        Args:
            location_id (str): ID локации
        """
        if location_id in self.locations:
            self.locations.remove(location_id)
    
    def is_adjacent_to(self, region_id: str) -> bool:
        """
        Проверяет, соседствует ли данный регион с указанным.
        
        Args:
            region_id (str): ID региона для проверки
            
        Returns:
            bool: True, если регионы соседствуют
        """
        return region_id in self.adjacent_regions
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Возвращает словарь с данными региона.
        
        Returns:
            dict: Словарь с данными региона
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "locations": self.locations.copy(),
            "starting_location": self.starting_location,
            "connections": self.connections.copy(),
            "climate": self.climate,
            "difficulty": self.difficulty,
            "requires": self.requires.copy(),
            "icon": self.icon,
            "x": self.x,
            "y": self.y,
            "adjacent_regions": self.adjacent_regions.copy()
        }
    
    def __str__(self) -> str:
        """Возвращает строковое представление региона"""
        return f"{self.name} (ID: {self.id}, {len(self.locations)} локаций, сложность: {self.difficulty})"
    
    def can_access(self, player, game_system):
        """
        Проверяет, может ли игрок получить доступ к региону.
        
        Args:
            player: Объект игрока
            game_system: Объект игровой системы
            
        Returns:
            bool: True, если игрок может получить доступ к региону
        """
        return self.check_requirements(self.requires, player, game_system) 