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
        """Загружает локации из JSON файлов в директории resources/places и её подпапках"""
        self.logger.info("LocationsLoader: начало загрузки данных...")
        
        # Базовый путь к директории с локациями
        locations_dir = "resources/places"
        
        # Проверка существования директории
        if not os.path.exists(locations_dir):
            self.logger.error(f"Директория локаций {locations_dir} не существует!")
            return self.locations
        
        # Счетчики для логирования
        total_files_processed = 0
        total_locations_loaded = 0
        total_connections_loaded = 0
        total_resources_loaded = 0
        
        # Рекурсивно проходим по всем файлам в директории и её подпапках
        for root, dirs, files in os.walk(locations_dir):
            for file in files:
                # Проверяем, что это JSON файл
                if not file.endswith('.json'):
                    continue
                
                file_path = os.path.join(root, file)
                self.logger.info(f"Обрабатываем файл локаций: {file_path}")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                        # Загружаем локации
                        if "locations" in data:
                            locations_in_file = 0
                            for location_data in data["locations"]:
                                location = self._create_location(location_data)
                                if location:
                                    self.locations[location.id] = location
                                    locations_in_file += 1
                            
                            self.logger.info(f"Загружено {locations_in_file} локаций из файла {file_path}")
                            total_locations_loaded += locations_in_file
                        
                        # Загружаем связи между локациями
                        if "connections" in data:
                            connections_in_file = 0
                            for connection in data["connections"]:
                                if "from" in connection and "to" in connection:
                                    from_id = connection["from"]
                                    to_id = connection["to"]
                                    
                                    if from_id in self.locations and to_id in self.locations:
                                        self.locations[from_id].add_connection(to_id)
                                        connections_in_file += 1
                                        
                                        # Если связь двусторонняя
                                        if connection.get("bidirectional", True):
                                            self.locations[to_id].add_connection(from_id)
                                            connections_in_file += 1
                            
                            self.logger.info(f"Загружено {connections_in_file} связей между локациями из файла {file_path}")
                            total_connections_loaded += connections_in_file
                        
                        # Загружаем ресурсы для локаций
                        if "resources" in data:
                            resources_in_file = 0
                            for resource_data in data["resources"]:
                                if "location_id" in resource_data and "resource_id" in resource_data:
                                    location_id = resource_data["location_id"]
                                    resource_id = resource_data["resource_id"]
                                    max_count = resource_data.get("max_count", 10)
                                    respawn_time = resource_data.get("respawn_time", 300)  # в секундах
                                    
                                    if location_id in self.locations:
                                        self.locations[location_id].add_resource(
                                            resource_id, max_count, respawn_time)
                                        resources_in_file += 1
                            
                            self.logger.info(f"Загружено {resources_in_file} ресурсов для локаций из файла {file_path}")
                            total_resources_loaded += resources_in_file
                        
                        total_files_processed += 1
                        
                except Exception as e:
                    self.logger.exception(f"Ошибка при загрузке локаций из файла {file_path}: {str(e)}")
        
        # Суммарная статистика
        self.logger.info(f"Всего обработано файлов: {total_files_processed}")
        self.logger.info(f"Всего загружено локаций: {total_locations_loaded}")
        self.logger.info(f"Всего загружено связей: {total_connections_loaded}")
        self.logger.info(f"Всего загружено ресурсов: {total_resources_loaded}")
        
        return self.locations
    
    def _create_location(self, location_data):
        """Создает объект Location из данных JSON"""
        try:
            if "id" in location_data and "name" in location_data:
                # Проверяем, есть ли флаг first_spawn_at
                first_spawn_at = location_data.get("first_spawn_at", False)
                
                location = Location(
                    location_data["id"],
                    location_data["name"],
                    location_data.get("description", ""),
                    first_spawn_at
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
                
                # Добавляем монстров с параметрами респауна
                if "monsters" in location_data:
                    for monster_id, monster_data in location_data["monsters"].items():
                        # Проверяем, является ли monster_data словарем с параметрами или просто числом
                        if isinstance(monster_data, dict):
                            max_count = monster_data.get("max_count", 5)
                            respawn_time = monster_data.get("respawn_time", 600)  # 10 минут по умолчанию
                        else:
                            # Если просто число, считаем его максимальным количеством
                            max_count = monster_data
                            respawn_time = 600  # 10 минут по умолчанию
                            
                        location.add_monster(monster_id, max_count, respawn_time)
                
                # Добавляем NPC из поля npcs
                if "npcs" in location_data:
                    # Проверяем, является ли npcs списком или словарем
                    if isinstance(location_data["npcs"], list):
                        # Если это список, просто добавляем каждый NPC
                        for npc_id in location_data["npcs"]:
                            location.add_npc(npc_id)
                    else:
                        # Если это словарь или что-то еще, пытаемся обработать ключи как ID NPC
                        for npc_id in location_data["npcs"].keys():
                            location.add_npc(npc_id)
                        
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