import random
from src.utils.Logger import Logger

class Location:
    def __init__(self, id, name, description=""):
        self.id = id
        self.name = name
        self.description = description
        self.connected_locations = []  # ID локаций, доступных из текущей
        self.available_resources = {}  # Словарь {resource_id: {count: X, respawn_time: Y}}
        self.resources = {}  # Текущее состояние ресурсов {resource_id: count}
        self.logger = Logger()
    
    def add_connection(self, location_id):
        """Добавляет связь с другой локацией"""
        if location_id not in self.connected_locations:
            self.connected_locations.append(location_id)
            self.logger.debug("Добавлена связь локации {} с {}", self.id, location_id)
    
    def add_resource(self, resource_id, max_count, respawn_time):
        """Добавляет ресурс в локацию"""
        self.available_resources[resource_id] = {
            "max_count": max_count,
            "respawn_time": respawn_time,
        }
        # Инициализируем случайным количеством ресурсов от 1 до max_count
        self.resources[resource_id] = random.randint(1, max_count)
        self.logger.debug("Добавлен ресурс {} в локацию {} ({})", 
                         resource_id, self.id, self.resources[resource_id])
    
    def collect_resource(self, resource_id, count=1):
        """Собирает ресурс из локации, возвращает собранное количество"""
        if resource_id not in self.resources or self.resources[resource_id] <= 0:
            self.logger.warning("Попытка собрать отсутствующий ресурс {} в локации {}", resource_id, self.id)
            return 0
            
        available = self.resources[resource_id]
        collected = min(available, count)
        self.resources[resource_id] -= collected
        
        # Логируем действие
        self.logger.info("Собрано {} единиц ресурса {} в локации {}", collected, resource_id, self.id)
        
        return collected
    
    def update(self, time_passed):
        """Обновляет состояние локации (например, для респауна ресурсов)"""
        for resource_id, resource_info in self.available_resources.items():
            max_count = resource_info["max_count"]
            current_count = self.resources.get(resource_id, 0)
            
            # Добавляем ресурсы, если их меньше максимума
            if current_count < max_count:
                # Простая формула: каждую секунду восстанавливается часть ресурсов
                restore_speed = max_count / resource_info["respawn_time"]
                new_resources = time_passed * restore_speed
                
                # Округляем до целого числа и добавляем
                to_add = int(new_resources)
                if to_add > 0:
                    new_count = min(current_count + to_add, max_count)
                    self.resources[resource_id] = new_count
                    self.logger.debug("Восстановлено {} единиц ресурса {} в локации {}", 
                                    new_count - current_count, resource_id, self.id)
    
    def get_info(self):
        """Возвращает информацию о локации"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connected_locations": self.connected_locations,
            "resources": self.resources
        }
    
    def describe(self):
        """Возвращает описание локации для вывода игроку"""
        from colorama import Fore, Style
        
        description = f"\n=== {self.name} ===\n"
        if self.description:
            description += f"{self.description}\n\n"
        
        # Список ресурсов
        if self.resources:
            description += "Доступные ресурсы:\n"
            for resource_id, count in self.resources.items():
                if count > 0:
                    # Попробуем получить данные о ресурсе через Game, но это требует рефакторинга
                    # Временное решение - просто показать ресурс
                    description += f"- {resource_id} ({count})\n"
                
        # Список связанных локаций
        if self.connected_locations:
            description += "\nОтсюда можно пойти в:\n"
            for location_id in self.connected_locations:
                description += f"- {location_id}\n"
                
        return description
    