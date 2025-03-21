from src.models.SimpleSkill import SimpleSkill
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.Player import Player

class OneHanded(SimpleSkill):
    def __init__(self):
        super().__init__()
        self.id = "one_handed"
        self.group_id = "combat"
        self.name = "Одноручное оружие"
        self.description = "Одноручное оружие - навык позволяет использовать одноручное оружие более эффективно."
        self.icon = "🗡️"
        self.level = 1
        self.current_experience = 0
        self.max_level_experience = 100
        self.max_level = 100
        self.unlocked_at_level = 1  # Доступен с 1 уровня игрока
        
        # Пассивные бонусы на разных уровнях навыка
        self.passive_bonuses = {
        }
        
        # Способности, которые разблокируются на разных уровнях
        self.unlocked_abilities = {
        }
