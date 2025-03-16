from src.models.quests.QuestObjective import QuestObjective

class GotoObjective(QuestObjective):
    """Цель квеста: посетить определенную локацию"""
    
    def __init__(self, location_id, description=None):
        super().__init__(QuestObjective.TYPE_GOTO, description or f"Посетить локацию {location_id}")
        self.location_id = location_id
        self.visited = False
    
    def update_progress(self, player, game):
        """Обновляет прогресс посещения локации"""
        if self.completed:
            return False
        
        # Проверяем, находится ли игрок в нужной локации
        if player.current_location and player.current_location.id == self.location_id:
            if not self.visited:
                self.visited = True
                self.completed = True
                return True
                
        return False
    
    def get_progress_text(self):
        """Возвращает текст с описанием прогресса посещения локации"""
        # Пытаемся получить название локации для более понятного отображения
        location = None  # В реальном коде здесь будет доступ к game.get_location(self.location_id)
        location_name = location.name if location else self.location_id
        
        status = "✅" if self.completed else "❌"
        return f"{status} Посетить {location_name}" 