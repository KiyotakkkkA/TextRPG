"""
Базовый класс для всех навыков в игре.
"""

from typing import Dict, Any, List, Optional, Callable, TYPE_CHECKING
from src.utils.Logger import Logger
from src.EventSystem import get_event_system
from src.models.interfaces.Serializable import Serializable

if TYPE_CHECKING:
    from src.models.Player import Player

class SimpleSkill(Serializable):
    """
    Базовый класс для всех навыков в игре.
    
    Навык представляет собой способность персонажа, которая может быть улучшена
    с помощью получения опыта. Навыки могут быть пассивными (дающими постоянные бонусы)
    или активными (которые игрок может использовать).
    
    Атрибуты:
        id (str): Уникальный идентификатор навыка.
        name (str): Название навыка.
        description (str): Описание навыка.
        icon (str): Иконка навыка (эмодзи или символ).
        group_id (str): Идентификатор группы, к которой принадлежит навык.
        level (int): Текущий уровень навыка.
        current_experience (int): Текущий опыт навыка.
        max_level_experience (int): Опыт, необходимый для достижения максимального уровня.
        max_level (int): Максимальный уровень навыка.
        passive_bonuses (Dict[int, Dict[str, Any]]): Пассивные бонусы на каждом уровне.
        unlocked_abilities (Dict[int, List[str]]): Способности, разблокированные на каждом уровне.
    """
    
    def __init__(self):
        """
        Инициализирует навык с базовыми значениями.
        Переопределяется в дочерних классах.
        """
        self.id = "base_skill"
        self.group_id = "misc"
        self.name = "Базовый навык"
        self.description = "Базовый навык без особых свойств."
        self.icon = "🔄"
        self.level = 1
        self.current_experience = 0
        self.max_level_experience = 100  # Базовое количество опыта для первого уровня
        self.max_level = 100
        self.unlocked_at_level = 1  # Уровень игрока, при котором навык разблокируется
        
        # Пассивные бонусы на разных уровнях навыка
        self.passive_bonuses = {}
        
        # Способности, которые разблокируются на разных уровнях
        self.unlocked_abilities = {}
        
        # Логгер для отладки
        self.logger = Logger()
    
    def set_level(self, level: int) -> None:
        """
        Устанавливает уровень навыка и соответствующее требование опыта.
        
        Args:
            level (int): Новый уровень навыка.
        """
        if level < 1:
            level = 1
        if level > self.max_level:
            level = self.max_level
        
        # Устанавливаем уровень
        old_level = self.level
        self.level = level
        
        # Устанавливаем базовый опыт для первого уровня
        base_exp = 100
        
        # Устанавливаем требуемый опыт для текущего уровня
        # Формула: базовый_опыт * (1.5 ^ (уровень - 1))
        self.max_level_experience = int(base_exp * (1.5 ** (level - 1)))
        
        # Обнуляем текущий опыт
        self.current_experience = 0
    
    def add_experience(self, amount: int) -> bool:
        """
        Добавляет опыт к навыку и повышает уровень, если достигнут необходимый опыт.
        При повышении уровня текущий опыт обнуляется, а требуемый опыт увеличивается.
        
        Args:
            amount (int): Количество опыта для добавления.
            
        Returns:
            bool: True, если уровень был повышен, иначе False.
        """
        if self.level >= self.max_level:
            return False
            
        self.current_experience += amount
        
        # Сохраняем старый уровень для события
        old_level = self.level
        levelups = 0
        
        # Проверяем, достаточно ли опыта для повышения уровня
        while self.current_experience >= self.max_level_experience:
            # Повышаем уровень
            
            levelups += 1
            # Обнуляем текущий опыт
            self.current_experience -= self.max_level_experience
            
            # Увеличиваем требуемый опыт для следующего уровня
            # Формула: базовый_опыт * (1.5 ^ (уровень - 1))
            base_exp = 100
            self.max_level_experience = int(base_exp * (1.5 ** (old_level + levelups - 1)))
        
        if levelups > 0:
            self.level += levelups
            
            event_system = get_event_system()
            event_system.emit("skill_level_up", {
                "skill_id": self.id,
                "skill_name": self.name,
                "old_level": old_level,
                "new_level": self.level
            })
            return True
        
        return False
    
    def get_level(self) -> int:
        """
        Возвращает текущий уровень навыка.
        
        Returns:
            int: Текущий уровень навыка.
        """
        return self.level
    
    def get_experience_percent(self) -> float:
        """
        Возвращает процент прогресса к следующему уровню.
        
        Returns:
            float: Процент прогресса (0.0 - 1.0).
        """
        if self.level >= self.max_level:
            return 1.0
            
        # Просто делим текущий опыт на требуемый для этого уровня
        progress = self.current_experience / self.max_level_experience
        return max(0.0, min(1.0, progress))
    
    def get_passive_bonuses(self) -> Dict[str, Any]:
        """
        Возвращает все активные пассивные бонусы на текущем уровне.
        
        Returns:
            Dict[str, Any]: Словарь активных бонусов (имя_бонуса: значение).
        """
        bonuses = {}
        
        # Добавляем бонусы со всех уровней до текущего
        for level in range(1, self.level + 1):
            if level in self.passive_bonuses:
                for bonus_name, bonus_value in self.passive_bonuses[level].items():
                    bonuses[bonus_name] = bonus_value
                    
        return bonuses
    
    def get_unlocked_abilities(self) -> List[str]:
        """
        Возвращает все разблокированные способности на текущем уровне.
        
        Returns:
            List[str]: Список идентификаторов разблокированных способностей.
        """
        abilities = []
        
        # Добавляем способности со всех уровней до текущего
        for level in range(1, self.level + 1):
            if level in self.unlocked_abilities:
                abilities.extend(self.unlocked_abilities[level])
                
        return abilities
    
    def is_unlocked(self, player_level: int) -> bool:
        """
        Проверяет, разблокирован ли навык на основе уровня игрока.
        Использует атрибут unlocked_at_level для определения минимального уровня.
        
        Args:
            player_level (int): Уровень игрока.
            
        Returns:
            bool: True, если навык разблокирован, иначе False.
        """
        # Проверяем, существует ли атрибут unlocked_at_level
        if hasattr(self, 'unlocked_at_level'):
            return player_level >= self.unlocked_at_level
        # По умолчанию, если атрибут не определен, доступно с 1 уровня
        return player_level >= 1
    
    def can_use(self, player: 'Player') -> bool:
        """
        Проверяет, может ли игрок использовать навык.
        По умолчанию все навыки доступны для использования.
        
        Args:
            player: Игрок, который пытается использовать навык.
            
        Returns:
            bool: True, если навык можно использовать, иначе False.
        """
        return True
    
    def use(self, player: 'Player', *args, **kwargs) -> bool:
        """
        Использует навык с указанными параметрами.
        Должен быть переопределен в подклассах для активных навыков.
        
        Args:
            player: Игрок, использующий навык.
            *args, **kwargs: Дополнительные аргументы, специфичные для навыка.
            
        Returns:
            bool: True, если навык был успешно использован, иначе False.
        """
        self.logger.info(f"Использован навык {self.name} (уровень {self.level})")
        return True
    
    def get_skill_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о навыке в формате словаря.
        
        Returns:
            Dict[str, Any]: Информация о навыке.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "group_id": self.group_id,
            "level": self.level,
            "current_experience": self.current_experience,
            "max_level_experience": self.max_level_experience,
            "max_level": self.max_level,
            "progress_percent": self.get_experience_percent(),
            "passive_bonuses": self.get_passive_bonuses(),
            "unlocked_abilities": self.get_unlocked_abilities()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Сериализует навык в словарь для сохранения.
        
        Returns:
            Dict[str, Any]: Сериализованный навык.
        """
        return {
            "id": self.id,
            "level": self.level,
            "current_experience": self.current_experience,
            "max_level": self.max_level,
            "max_level_experience": self.max_level_experience
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimpleSkill':
        """
        Создает навык из словаря (десериализация).
        
        Args:
            data (Dict[str, Any]): Словарь с данными навыка.
            
        Returns:
            SimpleSkill: Созданный навык.
        """
        skill = cls()
        
        # Устанавливаем уровень - это автоматически установит правильный max_level_experience
        level = data.get("level", 1)
        skill.set_level(level)
        
        # Устанавливаем текущий опыт
        skill.current_experience = data.get("current_experience", 0)
        
        # Если в данных есть max_level_experience, используем его (для обратной совместимости)
        if "max_level_experience" in data:
            skill.max_level_experience = data["max_level_experience"]
            
        # Устанавливаем максимальный уровень, если он задан
        if "max_level" in data:
            skill.max_level = data["max_level"]
        
        return skill 