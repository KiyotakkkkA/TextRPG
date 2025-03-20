"""
Модель региона для игры.
Регион объединяет несколько локаций, представляя собой географическую область.
"""

from typing import Dict, List, Any, Optional

class Region:
    """
    Класс, представляющий регион в игровом мире.
    Регион содержит несколько локаций и имеет свои характеристики.
    """
    
    def __init__(self, region_id: str, data: Dict[str, Any]):
        """
        Инициализирует регион.
        
        Args:
            region_id (str): Уникальный идентификатор региона
            data (dict): Данные региона из .desc файла
        """
        self.id = region_id
        self.name = data.get("name", "Неизвестный регион")
        self.description = data.get("description", "Нет описания")
        self.color = data.get("color", "white")
        self.icon = data.get("icon", "🗺️")
        self.location_ids = data.get("locations", [])
        self.difficulty = data.get("difficulty", 1)
        self.climate = data.get("climate", "умеренный")
        self.properties = data.get("properties", {})
        
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
        if location_id not in self.location_ids:
            self.location_ids.append(location_id)
    
    def remove_location(self, location_id: str):
        """
        Удаляет локацию из региона.
        
        Args:
            location_id (str): ID локации
        """
        if location_id in self.location_ids:
            self.location_ids.remove(location_id)
    
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
            "color": self.color,
            "icon": self.icon,
            "locations": self.location_ids.copy(),
            "difficulty": self.difficulty,
            "climate": self.climate,
            "properties": self.properties.copy(),
            "x": self.x,
            "y": self.y,
            "adjacent_regions": self.adjacent_regions.copy()
        }
    
    def __str__(self) -> str:
        """Возвращает строковое представление региона"""
        return f"{self.name} (ID: {self.id}, {len(self.location_ids)} локаций, сложность: {self.difficulty})" 