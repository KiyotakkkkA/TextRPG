from src.models.SimpleSkill import SimpleSkill
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.Player import Player

class Mining(SimpleSkill):
    def __init__(self):
        super().__init__()
        self.id = "mining"
        self.group_id = "handcrafting"
        self.name = "Горное дело"
        self.description = "Горное дело - навык позволяет добывать минералы и руды более эффективно."
        self.icon = "⛏️"
        self.max_level_experience = 100
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
        Использует навык горного дела для повышения эффективности добычи.
        
        Returns:
            bool: True, если навык успешно применен
        """
        # Проверка возможности использования навыка
        if not self.can_use(player):
            return False
        
        # Логика использования навыка
        # В данном случае просто возвращаем True, так как это пассивный навык
        return True