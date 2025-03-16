import json
import os
from src.loaders.Loader import Loader
from src.models.Location import Location
from src.utils.Logger import Logger

class LocationsLoader(Loader):
    def __init__(self):
        self.locations = {}  # Словарь {location_id: Location}
        self.logger = Logger()
    
    def load(self):
        """Загружает локации из JSON файла"""
        self.logger.info("LocationsLoader: начало загрузки данных...")
        
        # Базовый путь к файлу локаций
        locations_file = "resources/places/main.json"
        
        # Проверка существования файла
        if not os.path.exists(locations_file):
            self.logger.error("Файл локаций {} не существует!", locations_file)
            return self.locations
            
        try:
            with open(locations_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                
                # Загружаем локации
                if "locations" in data:
                    for location_data in data["locations"]:
                        location = self._create_location(location_data)
                        if location:
                            self.locations[location.id] = location
                    
                    self.logger.info("Загружено {} локаций", len(self.locations))
                
                # Загружаем связи между локациями
                if "connections" in data:
                    for connection in data["connections"]:
                        if "from" in connection and "to" in connection:
                            from_id = connection["from"]
                            to_id = connection["to"]
                            
                            if from_id in self.locations and to_id in self.locations:
                                self.locations[from_id].add_connection(to_id)
                                
                                # Если связь двусторонняя
                                if connection.get("bidirectional", True):
                                    self.locations[to_id].add_connection(from_id)
                    
                    self.logger.info("Загружены связи между локациями")
                
                # Загружаем ресурсы для локаций
                if "resources" in data:
                    for resource_data in data["resources"]:
                        if "location_id" in resource_data and "resource_id" in resource_data:
                            location_id = resource_data["location_id"]
                            resource_id = resource_data["resource_id"]
                            max_count = resource_data.get("max_count", 10)
                            respawn_time = resource_data.get("respawn_time", 300)  # в секундах
                            
                            if location_id in self.locations:
                                self.locations[location_id].add_resource(
                                    resource_id, max_count, respawn_time)
                    
                    self.logger.info("Загружены ресурсы для локаций")
                
        except Exception as e:
            self.logger.exception(f"Ошибка при загрузке локаций")
        
        return self.locations
    
    def _create_location(self, location_data):
        """Создает объект Location из данных JSON"""
        try:
            if "id" in location_data and "name" in location_data:
                location = Location(
                    location_data["id"],
                    location_data["name"],
                    location_data.get("description", "")
                )
                
                # Добавляем ресурсы с параметрами респауна
                if "resources" in location_data:
                    for res_id, res_data in location_data["resources"].items():
                        # Проверяем, является ли res_data словарем с параметрами или просто числом
                        if isinstance(res_data, dict):
                            max_count = res_data.get("max_count", 10)
                            respawn_time = res_data.get("respawn_time", 300)  # 5 минут по умолчанию
                        else:
                            # Если просто число, считаем его максимальным количеством
                            max_count = res_data
                            respawn_time = 300  # 5 минут по умолчанию
                            
                        location.add_resource(res_id, max_count, respawn_time)
                        
                # Добавляем действия если есть
                if "actions" in location_data:
                    for action in location_data["actions"]:
                        location.add_action(action)
                        
                return location
        except Exception as e:
            self.logger.exception(f"Ошибка при создании локации {location_data.get('id', 'unknown')}")
        
        return None
    
    def get_location(self, location_id):
        """Возвращает локацию по ID"""
        return self.locations.get(location_id)
    
    def get_all_locations(self):
        """Возвращает все локации"""
        return self.locations
        
    # Магические методы для работы как со словарем
    def __getitem__(self, key):
        """Позволяет обращаться через квадратные скобки: loader['location_id']"""
        return self.locations[key]
    
    def __setitem__(self, key, value):
        """Позволяет присваивать через квадратные скобки: loader['location_id'] = location"""
        self.locations[key] = value
    
    def __contains__(self, key):
        """Позволяет использовать проверку 'in': 'location_id' in loader"""
        return key in self.locations
    
    def __len__(self):
        """Позволяет использовать len(): len(loader)"""
        return len(self.locations)
    
    def keys(self):
        """Возвращает ключи как в словаре"""
        return self.locations.keys()
    
    def values(self):
        """Возвращает значения как в словаре"""
        return self.locations.values()
    
    def items(self):
        """Возвращает пары ключ-значение как в словаре"""
        return self.locations.items() 