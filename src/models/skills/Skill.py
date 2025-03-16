class Skill:
    def __init__(self, id, name, description="", max_level=100, base_exp=100, exp_factor=1.5):
        """
        Инициализация навыка
        id - идентификатор навыка
        name - название навыка
        description - описание навыка
        max_level - максимальный уровень навыка
        base_exp - базовый опыт для первого уровня
        exp_factor - множитель опыта для последующих уровней
        """
        self.id = id
        self.name = name
        self.description = description
        self.level = 1
        self.experience = 0
        self.max_level = max_level
        self.base_exp = base_exp
        self.exp_factor = exp_factor
        self.level_thresholds = {}
        self.unlocked_items = []
        self.unlocks_by_level = {}  # Словарь {level: [item_id1, item_id2, ...]}
    
    def calculate_exp_for_level(self, level):
        """Расчет необходимого опыта для достижения указанного уровня"""
        if level <= 1:
            return 0
        
        # Экспоненциальная формула для расчета опыта
        # Можно настроить под нужную кривую роста
        return int(self.base_exp * (self.exp_factor ** (level - 1)))
    
    def add_experience(self, amount):
        """Добавляет опыт к навыку и повышает уровень при необходимости"""
        self.experience += amount
        
        # Проверяем, достаточно ли опыта для следующего уровня
        while self.level < self.max_level:
            exp_needed = self.calculate_exp_for_level(self.level + 1)
            if self.experience >= exp_needed:
                self.level += 1
                # Здесь можно добавить логику для уведомления о повышении уровня
            else:
                break
        
        return self.level
    
    def get_progress_to_next_level(self):
        """Возвращает прогресс к следующему уровню в процентах (0.0 - 1.0)"""
        if self.level >= self.max_level:
            return 1.0
        
        current_level_exp = self.calculate_exp_for_level(self.level)
        next_level_exp = self.calculate_exp_for_level(self.level + 1)
        exp_needed = next_level_exp - current_level_exp
        exp_gained = self.experience - current_level_exp
        
        return min(1.0, max(0.0, exp_gained / exp_needed if exp_needed > 0 else 1.0))
    
    def get_unlocked_items_at_level(self, level):
        """Возвращает предметы, которые разблокируются на указанном уровне"""
        return self.unlocks_by_level.get(level, [])
    
    def get_next_level(self):
        """Возвращает следующий уровень или None, если достигнут максимум"""
        return self.level + 1 if self.level < self.max_level else None
    
    def get_exp_to_next_level(self):
        """Возвращает количество опыта, необходимое для следующего уровня"""
        if self.level >= self.max_level:
            return 0
        
        exp_needed = self.calculate_exp_for_level(self.level + 1)
        return exp_needed - self.experience
    
    def can_collect_item(self, item_id):
        """Проверяет, может ли игрок собирать указанный предмет с текущим уровнем навыка"""
        return item_id in self.unlocked_items
    
    def add_unlocks_by_level(self, level, items):
        """Добавляет разблокируемые предметы для указанного уровня навыка"""
        self.unlocks_by_level[level] = items
        
        # Если текущий уровень >= указанного, добавляем предметы как разблокированные
        if self.level >= level:
            self.unlocked_items.extend(items) 