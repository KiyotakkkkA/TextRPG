from src.models.SimpleSkill import SimpleSkill
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.Player import Player

class Herbalism(SimpleSkill):
    def __init__(self):
        super().__init__()
        self.id = "herbalism"
        self.group_id = "handcrafting"
        self.name = "Травничество"
        self.description = "Травничество - навык позволяет собирать лекарственные травы и готовить из них полезные зелья."
        self.icon = "🌿"
        self.max_level_experience = 100
        self.max_level = 100
        self.unlocked_at_level = 1  # Доступен со 1 уровня игрока
        
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
        Использует навык травничества для сбора трав или приготовления зелий.
        
        Args:
            location (str, optional): ID локации для сбора трав
            recipe (str, optional): ID рецепта для приготовления зелья
            
        Returns:
            bool: True, если навык успешно применен
        """
        # Проверка возможности использования навыка
        if not self.can_use(player):
            return False
            
        # Получаем параметры
        location_id = kwargs.get('location')
        recipe_id = kwargs.get('recipe')
        
        # Если указана локация, собираем травы
        if location_id:
            # Здесь была бы логика сбора трав в указанной локации
            # Сейчас просто возвращаем True как заглушку
            return True
            
        # Если указан рецепт, готовим зелье
        if recipe_id:
            # Здесь была бы логика приготовления зелья по указанному рецепту
            # Сейчас просто возвращаем True как заглушку
            return True
            
        return False