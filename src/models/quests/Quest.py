class Quest:
    """Класс для представления квеста в игре"""
    
    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    
    def __init__(self, id, name, description, giver_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.giver_id = giver_id  # ID NPC, который дает квест
        self.taker_id = None      # ID NPC, которому сдается квест (может совпадать с giver_id)
        self.status = self.STATUS_NOT_STARTED
        self.stages = []          # Стадии квеста
        self.current_stage_index = 0
        self.tracked = False      # Флаг, указывающий, отслеживается ли квест
        self.rewards = {
            "experience": 0,      # Опыт персонажа
            "money": 0,           # Деньги
            "items": {},          # Предметы: {item_id: count}
            "skills": {}          # Опыт навыков: {skill_id: amount}
        }
        self.requirements = {     # Требования для начала квеста
            "level": 1,           # Минимальный уровень персонажа
            "skills": {},         # Требуемые навыки: {skill_id: level}
            "items": {},          # Требуемые предметы: {item_id: count}
            "quests": []          # ID квестов, которые должны быть выполнены
        }
        self.is_completed = False
    
    def start(self):
        """Начинает квест"""
        if self.status == self.STATUS_NOT_STARTED:
            self.status = self.STATUS_IN_PROGRESS
            return True
        return False
    
    def complete(self):
        """Завершает квест"""
        if self.status == self.STATUS_IN_PROGRESS and self.is_ready_to_complete():
            self.status = self.STATUS_COMPLETED
            return True
        return False
    
    def fail(self):
        """Проваливает квест"""
        if self.status == self.STATUS_IN_PROGRESS:
            self.status = self.STATUS_FAILED
            return True
        return False
    
    def add_stage(self, stage):
        """Добавляет стадию к квесту"""
        self.stages.append(stage)
    
    def advance_stage(self):
        """Переходит к следующей стадии квеста"""
        if self.current_stage_index < len(self.stages) - 1:
            self.current_stage_index += 1
            return True
        else:
            self.is_completed = True
            return False
    
    def get_current_stage(self):
        """Возвращает текущую стадию квеста"""
        if 0 <= self.current_stage_index < len(self.stages):
            return self.stages[self.current_stage_index]
        return None
    
    def is_ready_to_complete(self):
        """Проверяет, выполнены ли все условия для завершения квеста"""
        if self.status != self.STATUS_IN_PROGRESS:
            return False
        
        # Если есть стадии, последняя должна быть выполнена
        if self.stages and self.current_stage_index < len(self.stages) - 1:
            return False
        
        # Если последняя стадия не выполнена
        if self.stages and not self.stages[self.current_stage_index].is_completed():
            return False
        
        return True
    
    def update_progress(self, player, game):
        """Обновляет прогресс квеста на основе текущего состояния игры"""
        if self.status != self.STATUS_IN_PROGRESS:
            return False
        
        current_stage = self.get_current_stage()
        if not current_stage:
            return False
        
        # Обновляем прогресс текущей стадии
        updated = current_stage.update_progress(player, game)
        
        # Если стадия выполнена и это не последняя стадия, переходим к следующей
        if current_stage.is_completed() and self.current_stage_index < len(self.stages) - 1:
            self.advance_stage()
            updated = True
        
        return updated
    
    def set_tracked(self, tracked=True):
        """Устанавливает, отслеживается ли квест"""
        self.tracked = tracked
        return self.tracked
    
    def get_status_text(self):
        """Возвращает текстовое описание статуса квеста"""
        if self.status == self.STATUS_NOT_STARTED:
            return "Не начат"
        elif self.status == self.STATUS_IN_PROGRESS:
            return "В процессе"
        elif self.status == self.STATUS_COMPLETED:
            return "Выполнен"
        elif self.status == self.STATUS_FAILED:
            return "Провален"
        return "Неизвестный статус"
    
    def get_progress_text(self, game=None):
        """Возвращает текст с описанием прогресса квеста"""
        if not self.stages:
            return ""
        
        current_stage = self.get_current_stage()
        if not current_stage:
            return ""
        
        return current_stage.get_progress_text(game)
    
    def can_be_started(self, player):
        """Проверяет, может ли игрок начать квест"""
        # Проверка уровня
        if player.level < self.requirements["level"]:
            return False
        
        # Проверка навыков
        for skill_id, required_level in self.requirements["skills"].items():
            skill = player.skill_system.get_skill(skill_id)
            if not skill or skill.level < required_level:
                return False
        
        # Проверка предметов
        for item_id, required_count in self.requirements["items"].items():
            if not player.inventory.has_item(item_id, required_count):
                return False
        
        return True 