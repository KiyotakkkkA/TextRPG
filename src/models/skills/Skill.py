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
        self.provides_by_level = {}  # Словарь {level: {bonus_name: value, ...}}
        self.active_bonuses = {}     # Текущие активные бонусы
    
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
        old_level = self.level
        
        # Проверяем, достаточно ли опыта для следующего уровня
        while self.level < self.max_level:
            exp_needed = self.calculate_exp_for_level(self.level + 1)
            if self.experience >= exp_needed:
                self.level += 1
                # Здесь можно добавить логику для уведомления о повышении уровня
            else:
                break
        
        # Если уровень изменился, обновляем разблокированные предметы и бонусы
        if old_level != self.level:
            # Добавляем новые разблокированные предметы
            for level in range(old_level + 1, self.level + 1):
                if level in self.unlocks_by_level:
                    self.unlocked_items.extend(self.unlocks_by_level[level])
            
            # Обновляем активные бонусы
            self._update_active_bonuses()
        
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
            
    def add_provides_by_level(self, level, bonuses):
        """Добавляет бонусы, предоставляемые на указанном уровне навыка"""
        self.provides_by_level[level] = bonuses
        
        # Если текущий уровень >= указанного, применяем бонусы
        if self.level >= level:
            self._update_active_bonuses()
            
    def _update_active_bonuses(self):
        """Обновляет активные бонусы на основе текущего уровня навыка"""
        # Сбрасываем текущие бонусы
        self.active_bonuses = {}
        
        # Применяем бонусы для каждого уровня, до которого дошел игрок
        for level in sorted(self.provides_by_level.keys()):
            if level <= self.level:
                for bonus_name, value in self.provides_by_level[level].items():
                    # Обновляем значение бонуса наивысшим из доступных на текущем уровне
                    if bonus_name not in self.active_bonuses or value > self.active_bonuses[bonus_name]:
                        self.active_bonuses[bonus_name] = value
    
    def get_bonus_value(self, bonus_name):
        """Возвращает значение бонуса для указанного типа"""
        return self.active_bonuses.get(bonus_name, 0)
        
    def get_all_bonuses(self):
        """Возвращает словарь всех активных бонусов"""
        return self.active_bonuses.copy()
        
    def get_detail_info(self):
        """Возвращает подробную информацию о навыке в виде словаря"""
        info = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "max_level": self.max_level,
            "experience": self.experience,
            "experience_to_next": self.get_exp_to_next_level(),
            "progress_percent": int(self.get_progress_to_next_level() * 100),
            "active_bonuses": self.get_all_bonuses(),
            "unlocked_items": self.unlocked_items
        }
        
        # Добавляем информацию о следующем уровне, если он доступен
        if self.level < self.max_level and self.level + 1 in self.provides_by_level:
            info["next_level_bonuses"] = self.provides_by_level[self.level + 1]
        
        if self.level < self.max_level and self.level + 1 in self.unlocks_by_level:
            info["next_level_unlocks"] = self.unlocks_by_level[self.level + 1]
            
        return info
        
    def get_description_text(self):
        """Возвращает отформатированное текстовое описание навыка"""
        # Базовая информация
        desc = [
            f"=== {self.name} (Уровень {self.level}/{self.max_level}) ===",
            f"{self.description}",
            f"Опыт: {self.experience} / {self.calculate_exp_for_level(self.level + 1) if self.level < self.max_level else 'MAX'}"
        ]
        
        # Прогресс до следующего уровня
        if self.level < self.max_level:
            progress_percent = int(self.get_progress_to_next_level() * 100)
            progress_bar = "[" + "=" * (progress_percent // 5) + " " * (20 - progress_percent // 5) + "]"
            desc.append(f"Прогресс: {progress_bar} {progress_percent}%")
        
        # Активные бонусы
        if self.active_bonuses:
            desc.append("\nАктивные бонусы:")
            for bonus, value in self.active_bonuses.items():
                desc.append(f"  • {bonus}: +{value}")
        
        # Разблокированные предметы
        if self.unlocked_items:
            desc.append("\nРазблокированные предметы:")
            for item in self.unlocked_items:
                desc.append(f"  • {item}")
        
        # Информация о следующем уровне
        if self.level < self.max_level:
            desc.append("\nНа следующем уровне:")
            
            # Бонусы следующего уровня
            if self.level + 1 in self.provides_by_level:
                next_bonuses = self.provides_by_level[self.level + 1]
                for bonus, value in next_bonuses.items():
                    current = self.active_bonuses.get(bonus, 0)
                    if current < value:
                        desc.append(f"  • {bonus}: +{current} → +{value}")
                    else:
                        desc.append(f"  • {bonus}: +{value}")
            
            # Предметы, которые будут разблокированы
            if self.level + 1 in self.unlocks_by_level:
                next_unlocks = self.unlocks_by_level[self.level + 1]
                if next_unlocks:
                    desc.append("  • Разблокируются новые предметы:")
                    for item in next_unlocks:
                        desc.append(f"    - {item}")
        
        return "\n".join(desc) 