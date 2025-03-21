"""
Класс для группировки навыков по категориям.
"""

from typing import Dict, Any, List
from src.models.interfaces import Serializable

class SkillGroup(Serializable):
    """
    Класс для группировки навыков по логическим категориям.
    Используется для организации отображения навыков в интерфейсе.
    
    Атрибуты:
        id (str): Уникальный идентификатор группы.
        name (str): Название группы.
        description (str): Описание группы.
        icon (str): Иконка группы (эмодзи или символ).
        skills_ids (List[str]): Список идентификаторов навыков в группе.
        order (int): Порядок отображения группы (чем меньше, тем выше).
    """
    
    def __init__(self):
        """
        Инициализирует группу навыков с базовыми атрибутами.
        """
        self.id = "base_group"
        self.name = "Базовая группа"
        self.description = "Базовая группа навыков."
        self.icon = "📋"
        self.skills_ids = []
        self.order = 99  # По умолчанию в конце списка
        self.group_id = "base_group"
    
    def add_skill(self, skill_id: str):
        """
        Добавляет навык в группу.
        
        Args:
            skill_id (str): Идентификатор навыка.
        """
        if skill_id not in self.skills_ids:
            self.skills_ids.append(skill_id)
    
    def remove_skill(self, skill_id: str):
        """
        Удаляет навык из группы.
        
        Args:
            skill_id (str): Идентификатор навыка.
        """
        if skill_id in self.skills_ids:
            self.skills_ids.remove(skill_id)
    
    def has_skill(self, skill_id: str) -> bool:
        """
        Проверяет, содержит ли группа указанный навык.
        
        Args:
            skill_id (str): Идентификатор навыка.
            
        Returns:
            bool: True, если навык в группе, иначе False.
        """
        return skill_id in self.skills_ids
    
    def get_skills_ids(self) -> List[str]:
        """
        Возвращает список идентификаторов навыков в группе.
        
        Returns:
            List[str]: Список идентификаторов навыков.
        """
        return self.skills_ids
    
    def get_group_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о группе в формате словаря.
        
        Returns:
            Dict[str, Any]: Информация о группе.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "skills_count": len(self.skills_ids),
            "order": self.order
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Сериализует группу навыков в словарь для сохранения.
        
        Returns:
            Dict[str, Any]: Сериализованная группа.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "skills_ids": self.skills_ids,
            "order": self.order
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillGroup':
        """
        Создает группу навыков из словаря (десериализация).
        
        Args:
            data (Dict[str, Any]): Словарь с данными группы.
            
        Returns:
            SkillGroup: Созданная группа.
        """
        group = cls()
        group.id = data.get("id", "base_group")
        group.name = data.get("name", "Базовая группа")
        group.description = data.get("description", "Базовая группа навыков.")
        group.icon = data.get("icon", "📋")
        group.skills_ids = data.get("skills_ids", [])
        group.order = data.get("order", 99)
        return group 