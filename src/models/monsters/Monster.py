import random
from src.utils.Logger import Logger

class Monster:
    """Базовый класс для всех монстров в игре"""
    
    def __init__(self, id, name, description="", level=1, health=10, damage=2):
        self.id = id
        self.name = name
        self.description = description
        self.level = level
        self.max_health = health
        self.health = health
        self.damage = damage
        self.logger = Logger()
        
        # Дополнительные боевые характеристики
        self.dodge_chance = 5  # Шанс уклонения (в процентах)
        self.crit_chance = 5   # Шанс критического удара (в процентах)
        self.crit_damage = 1.5 # Множитель критического урона (х1.5)
    
    def get_id(self):
        """Возвращает идентификатор монстра"""
        return self.id
    
    def get_name(self):
        """Возвращает имя монстра"""
        return self.name
    
    def get_description(self):
        """Возвращает описание монстра"""
        return self.description
    
    def get_level(self):
        """Возвращает уровень монстра"""
        return self.level
    
    def get_health(self):
        """Возвращает текущее здоровье монстра"""
        return self.health
    
    def is_alive(self):
        """Проверяет, жив ли монстр"""
        return self.health > 0
    
    def take_damage(self, damage):
        """Монстр получает урон
        
        Args:
            damage: Количество урона
            
        Returns:
            bool: True, если монстр умер после получения урона
            bool: Было ли уклонение
        """
        # Проверяем шанс уклонения
        is_dodged = random.randint(1, 100) <= self.dodge_chance
        
        if is_dodged:
            self.logger.debug(f"Монстр {self.name} уклонился от атаки")
            return False, True
            
        self.health = max(0, self.health - damage)
        self.logger.debug(f"Монстр {self.name} получил {damage} урона, осталось {self.health} HP")
        return not self.is_alive(), False
    
    def attack(self, target):
        """Монстр атакует цель
        
        Args:
            target: Цель атаки (обычно игрок)
            
        Returns:
            int: Количество нанесенного урона
            bool: Критический удар или нет
            bool: Было ли уклонение
        """
        # Проверяем, уклонилась ли цель
        dodge_chance = 0  # Базовый шанс уклонения
        if hasattr(target, 'dodge_chance'):
            dodge_chance = target.dodge_chance + target.equipment_bonuses.get("dodge", 0)
            
        is_dodged = random.randint(1, 100) <= dodge_chance
        
        if is_dodged:
            self.logger.debug(f"Игрок {target.name} уклонился от атаки монстра {self.name}")
            return 0, False, True
        
        # Расчет урона с учетом крита
        damage, is_critical = self.calculate_damage()
        
        # Наносим урон цели
        died, _ = target.take_damage(damage)
        
        if is_critical:
            self.logger.debug(f"Монстр {self.name} нанес КРИТИЧЕСКИЙ удар {target.name} на {damage} урона")
        else:
            self.logger.debug(f"Монстр {self.name} атаковал {target.name} на {damage} урона")
            
        return damage, is_critical, False
    
    def calculate_damage(self):
        """Рассчитывает урон атаки монстра
        
        Returns:
            int: Количество нанесенного урона
            bool: Критический удар или нет
        """
        # Проверяем, будет ли критический удар
        is_critical = random.randint(1, 100) <= self.crit_chance
        
        # Базовый урон
        base_damage = self.damage
        
        # Если критический удар, увеличиваем урон
        if is_critical:
            base_damage = base_damage * self.crit_damage
        
        # Базовая формула: базовый урон +/- 20%
        variation = random.uniform(0.8, 1.2)
        return max(1, int(base_damage * variation)), is_critical
    
    def heal(self, amount):
        """Восстанавливает здоровье монстра
        
        Args:
            amount: Количество восстанавливаемого здоровья
        """
        self.health = min(self.max_health, self.health + amount)
        self.logger.debug(f"Монстр {self.name} восстановил {amount} HP, теперь {self.health} HP") 