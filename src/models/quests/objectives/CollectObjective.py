from src.models.quests.QuestObjective import QuestObjective

class CollectObjective(QuestObjective):
    """Цель квеста: собрать определенное количество предметов"""
    
    def __init__(self, item_id, required_count, description=None):
        super().__init__(QuestObjective.TYPE_COLLECT, description or f"Собрать {required_count} {item_id}")
        self.item_id = item_id
        self.required_count = required_count
        self.current_count = 0
    
    def update_progress(self, player, game):
        """Обновляет прогресс сбора предметов"""
        if self.completed:
            return False
        
        # Получаем текущее количество предметов у игрока
        item_count = player.inventory.count_item(self.item_id)
        
        # Логирование для отладки
        if game.logger:
            game.logger.debug(f"Проверка предмета для квеста: {self.item_id} - текущее количество: {item_count}, требуется: {self.required_count}")
        
        # Если количество изменилось, обновляем прогресс
        if item_count != self.current_count:
            self.current_count = item_count
            
            # Если собрано достаточно предметов, отмечаем цель как выполненную
            if self.current_count >= self.required_count:
                self.completed = True
                if game.logger:
                    game.logger.info(f"Задача сбора выполнена: {self.item_id} ({self.current_count}/{self.required_count})")
            else:
                if game.logger:
                    game.logger.info(f"Прогресс задачи сбора: {self.item_id} ({self.current_count}/{self.required_count})")
            
            return True
            
        return False
    
    def get_progress_text(self):
        """Возвращает текст с описанием прогресса сбора предметов"""
        status = "✅" if self.completed else "❌"
        
        # Используем более короткую запись и ориентируемся на описание
        # В GameMenu.py будет добавлен цвет
        progress = f"{self.current_count}/{self.required_count}"
        
        # Если есть готовое описание, используем его
        if self.description:
            return f"{status} {self.description}: {progress}"
        else:
            # Иначе формируем стандартное описание
            return f"{status} Собрать {self.item_id}: {progress}" 