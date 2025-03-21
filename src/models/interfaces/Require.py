"""
Интерфейс Require для определения условий и ограничений в игре.
Этот интерфейс предоставляет набор методов для проверки различных условий,
которые могут быть наложены на квесты, локации, предметы и другие игровые объекты.
"""

from abc import ABC
from typing import Dict, List, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.GameSystem import GameSystem
    from src.models.Player import Player

class Require(ABC):
    """
    Абстрактный класс для реализации условий и проверок в игре.
    Любая сущность, которая хочет использовать систему условий, должна наследоваться от этого класса.
    """
    
    def check_requirements(self, requirements: Dict[str, Any], player: 'Player', game_system: 'GameSystem') -> bool:
        """
        Проверяет соответствие игрока всем указанным требованиям.
        
        Args:
            requirements (Dict[str, Any]): Словарь с требованиями
            player (Player): Объект игрока
            game_system (GameSystem): Игровая система
            
        Returns:
            bool: True, если игрок соответствует всем требованиям, иначе False
        """
        if not requirements:
            return True
            
        # Проходимся по всем требованиям
        for req_type, req_data in requirements.items():
            # Вызываем соответствующий метод проверки в зависимости от типа требования
            method_name = f"check_{req_type}"
            if hasattr(self, method_name):
                check_method = getattr(self, method_name)
                if not check_method(req_data, player, game_system):
                    return False
            else:
                # Если метод проверки не найден, считаем требование не выполненным
                return False
                
        return True
    
    def check_player_has_items(self, req_data: Dict[str, int], player: 'Player', game_system: 'GameSystem') -> bool:
        """
        Проверяет наличие у игрока указанных предметов в требуемом количестве.
        
        Args:
            req_data (Dict[str, int]): Словарь с ID предметов и их количеством
            player (Player): Объект игрока
            game_system (GameSystem): Игровая система
            
        Returns:
            bool: True, если у игрока есть все требуемые предметы, иначе False
        """
        for item_id, count in req_data.items():
            if player.inventory.get_item_count_by_id(item_id) < count:
                return False
        return True
    
    def check_player_has_gold(self, amount: int, player: 'Player', game_system: 'GameSystem') -> bool:
        """
        Проверяет наличие у игрока указанной суммы золота.
        
        Args:
            amount (int): Требуемое количество золота
            player (Player): Объект игрока
            game_system (GameSystem): Игровая система
            
        Returns:
            bool: True, если у игрока достаточно золота, иначе False
        """
        # Предполагаем, что золото - это особый предмет с ID "gold"
        return player.gold >= amount
    
    def check_player_has_level(self, level: int, player: 'Player', game_system: 'GameSystem') -> bool:
        """
        Проверяет, что уровень игрока не ниже требуемого.
        
        Args:
            level (int): Требуемый уровень
            player (Player): Объект игрока
            game_system (GameSystem): Игровая система
            
        Returns:
            bool: True, если у игрока достаточный уровень, иначе False
        """
        # Предполагаем, что у игрока есть атрибут level
        return player.level >= level
    
    def check_player_has_quest_stage(self, req_data: Dict[str, str], player: 'Player', game_system: 'GameSystem') -> bool:
        """
        Проверяет, что игрок находится на указанной стадии квеста.
        
        Args:
            req_data (Dict[str, str]): Словарь с ID квеста и ID стадии
            player (Player): Объект игрока
            game_system (GameSystem): Игровая система
            
        Returns:
            bool: True, если игрок находится на указанной стадии квеста, иначе False
        """
        # Механика квестов пока не реализована
        pass
    
    def check_player_has_completed_quest(self, quest_id: str, player: 'Player', game_system: 'GameSystem') -> bool:
        """
        Проверяет, что игрок выполнил указанный квест.
        
        Args:
            quest_id (str): ID квеста
            player (Player): Объект игрока
            game_system (GameSystem): Игровая система
            
        Returns:
            bool: True, если игрок выполнил квест, иначе False
        """
        # Механика квестов пока не реализована
        pass
    
    def check_player_has_failed_quest(self, quest_id: str, player: 'Player', game_system: 'GameSystem') -> bool:
        """
        Проверяет, что игрок провалил указанный квест.
        
        Args:
            quest_id (str): ID квеста
            player (Player): Объект игрока
            game_system (GameSystem): Игровая система
            
        Returns:
            bool: True, если игрок провалил квест, иначе False
        """
        # Механика квестов пока не реализована
        pass
    
    def check_player_has_skill_level(self, req_data: Dict[str, int], player: 'Player', game_system: 'GameSystem') -> bool:
        """
        Проверяет, что у игрока есть указанный навык с требуемым уровнем.
        
        Args:
            req_data (Dict[str, int]): Словарь с ID навыка и требуемым уровнем
            player (Player): Объект игрока
            game_system (GameSystem): Игровая система
            
        Returns:
            bool: True, если у игрока есть навык с требуемым уровнем, иначе False
        """
        # Проверяем наличие навыка у игрока
        for skill_id, required_level in req_data.items():
            # Получаем навык игрока
            skill = player.get_skill(skill_id)
            
            # Если навыка нет или его уровень меньше требуемого
            if skill is None or skill.level < required_level:
                return False
                
        return True 