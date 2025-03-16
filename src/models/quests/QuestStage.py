class QuestStage:
    """Класс для представления отдельной стадии квеста"""
    
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.objectives = []  # Список задач для выполнения
        
    def is_completed(self):
        """Проверяет, все ли задачи стадии выполнены"""
        for objective in self.objectives:
            if not objective.is_completed():
                return False
        return True
        
    def get_progress_text(self, game=None):
        """Возвращает текст прогресса по задачам"""
        result = []
        for objective in self.objectives:
            # Пытаемся вызвать get_progress_text с game
            try:
                # Попробуем вызвать с game
                if hasattr(objective, 'get_progress_text'):
                    text = objective.get_progress_text(game)
                    result.append(text)
                else:
                    # Если метода нет, используем str
                    result.append(str(objective))
            except TypeError:
                # Если метод не принимает game, вызываем без параметра
                try:
                    text = objective.get_progress_text()
                    result.append(text)
                except Exception:
                    # Если все не сработало, просто преобразуем в строку
                    result.append(str(objective))
                
        return "\n".join(result)
        
    def update_progress(self, player, game):
        """Обновляет прогресс всех задач в стадии
        
        Args:
            player: Объект игрока
            game: Объект игры
            
        Returns:
            bool: True, если прогресс хотя бы одной задачи изменился, иначе False
        """
        updated = False
        
        for objective in self.objectives:
            if objective.update_progress(player, game):
                updated = True
                
        return updated 