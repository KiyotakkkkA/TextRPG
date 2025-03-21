from src.models.SimpleSkill import SimpleSkill
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.Player import Player

class Fishing(SimpleSkill):
    def __init__(self):
        super().__init__()
        self.id = "fishing"
        self.group_id = "handcrafting"
        self.name = "Рыболовство"
        self.description = "Рыболовство - навык позволяет ловить рыбу в водоемах для получения пищи и ценных ресурсов."
        self.icon = "🎣"
        self.max_level_experience = 10000
        self.max_level = 100
        self.unlocked_at_level = 1  # Доступен с 1 уровня игрока
        
        # Пассивные бонусы на разных уровнях навыка
        self.passive_bonuses = {
            # Будут добавлены позже
        }
        
        # Способности, которые разблокируются на разных уровнях
        self.unlocked_abilities = {
            # Будут добавлены позже
        }
        
        # Устанавливаем начальный уровень
        self.set_level(1)
    
    def use(self, player: 'Player', *args, **kwargs) -> bool:
        """
        Использует навык рыболовства для ловли рыбы.
        
        Args:
            location (str, optional): ID локации для рыбалки
            tool (str, optional): ID используемой снасти
            
        Returns:
            bool: True, если навык успешно применен
        """
        # Проверка возможности использования навыка
        if not self.can_use(player):
            return False
            
        # Получаем параметры
        location_id = kwargs.get('location')
        tool_id = kwargs.get('tool')
        
        # Простая проверка наличия водоема в локации
        # В реальной реализации здесь была бы более сложная логика
        if location_id and "river" in location_id or "lake" in location_id:
            # Здесь была бы логика рыбалки в указанной локации
            # Сейчас просто возвращаем True как заглушку
            return True
            
        return False 