class QuestObjective:
    """Базовый класс для представления цели квеста"""
    
    TYPE_COLLECT = "collect"
    TYPE_TALK = "talk"
    TYPE_GOTO = "goto"
    TYPE_KILL = "kill"
    
    def __init__(self, type, description):
        self.type = type
        self.description = description
        self.completed = False
    
    def update_progress(self, player, game):
        """Обновляет прогресс цели на основе текущего состояния игры"""
        # Переопределяется в подклассах
        return False
    
    def is_completed(self):
        """Возвращает статус выполнения цели"""
        return self.completed
    
    def get_progress_text(self):
        """Возвращает текст с описанием прогресса цели"""
        status = "✅" if self.completed else "❌"
        return f"{status} {self.description}" 