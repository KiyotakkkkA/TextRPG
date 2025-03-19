"""
Загрузчик локаций из .desc файлов.
"""

import os
import time
from typing import Dict, List, Any, Optional
from src.loaders.SimpleLoader import SimpleLoader
from src.models.Location import Location
from src.utils.Logger import Logger
from src.loaders.DescLoader import DescLoader

class LocationsLoader(SimpleLoader):
    """
    Класс для загрузки локаций из .desc файлов.
    """
    
    def __init__(self):
        """
        Инициализирует загрузчик локаций.
        """
        self.locations_atlas = {}  # Данные локаций
        self.locations = {}  # Объекты локаций
        self.logger = Logger()
        self.desc_loader = DescLoader()
    
    def load(self):
        """
        Загружает все локации из .desc файлов.
        
        Returns:
            dict: Атлас локаций
        """
        self.logger.info("LocationsLoader: начало загрузки данных...")
        
        # Базовая директория с локациями
        locations_dir = "data/resources/locations"
        
        # Проверка существования директории
        if not os.path.exists(locations_dir):
            self.logger.error("Директория {} не существует!", locations_dir)
            # Создаем директорию, если её нет
            os.makedirs(locations_dir, exist_ok=True)
            self.logger.info("Создана директория для локаций: {}", locations_dir)
        else:
            self.logger.debug("Сканирование директории {}", locations_dir)
        
        # Рекурсивно сканируем все директории и загружаем .desc файлы
        self._scan_directory(locations_dir)
        
        # Создаем объекты локаций после загрузки данных
        self._create_locations()
        
        self.logger.info("LocationsLoader: загружено {} локаций", len(self.locations_atlas))
        return self.locations_atlas
    
    def _create_locations(self):
        """
        Создает объекты локаций на основе загруженных данных.
        """
        created_count = 0
        for location_id, location_data in self.locations_atlas.items():
            # Пропускаем составные ключи, чтобы не создавать дубликаты
            if "." in location_id:
                continue
                
            if isinstance(location_data, dict):
                try:
                    location = Location(location_id, location_data)
                    self.locations[location_id] = location
                    created_count += 1
                except Exception as e:
                    self.logger.error("Ошибка при создании локации {}: {}", location_id, str(e))
        
        self.logger.debug("Создано {} объектов локаций", created_count)
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """
        Возвращает объект локации по её ID.
        
        Args:
            location_id (str): ID локации
            
        Returns:
            Location: Объект локации или None, если локация не найдена
        """
        # Проверяем, есть ли локация в кэше
        if location_id in self.locations:
            # Обновляем ресурсы, если нужно
            self.locations[location_id].respawn_resources(time.time())
            return self.locations[location_id]
        
        # Если локации нет в кэше, но есть в атласе, создаем её
        if location_id in self.locations_atlas:
            try:
                location = Location(location_id, self.locations_atlas[location_id])
                self.locations[location_id] = location
                return location
            except Exception as e:
                self.logger.error("Ошибка при создании локации {}: {}", location_id, str(e))
        
        self.logger.error("Локация с ID {} не найдена!", location_id)
        return None
    
    def get_all_locations(self) -> Dict[str, Location]:
        """
        Возвращает словарь всех локаций.
        
        Returns:
            dict: Словарь с объектами локаций
        """
        return self.locations
    
    def update_all_locations(self):
        """
        Обновляет ресурсы на всех локациях.
        """
        current_time = time.time()
        for location in self.locations.values():
            location.respawn_resources(current_time)
    
    # Магические методы для работы как со словарем
    def __getitem__(self, key):
        """Позволяет обращаться через квадратные скобки: loader['location_id']"""
        return self.locations_atlas[key]
    
    def __setitem__(self, key, value):
        """Позволяет присваивать через квадратные скобки: loader['location_id'] = location_data"""
        self.locations_atlas[key] = value
    
    def __contains__(self, key):
        """Позволяет использовать проверку 'in': 'location_id' in loader"""
        return key in self.locations_atlas
    
    def __len__(self):
        """Позволяет использовать len(): len(loader)"""
        return len(self.locations_atlas)
    
    def keys(self):
        """Возвращает ключи как в словаре"""
        return self.locations_atlas.keys()
    
    def values(self):
        """Возвращает значения как в словаре"""
        return self.locations_atlas.values()
    
    def items(self):
        """Возвращает пары ключ-значение как в словаре"""
        return self.locations_atlas.items()
        
    def _scan_directory(self, directory):
        """
        Рекурсивно сканирует директорию и загружает все .desc файлы с локациями.
        
        Args:
            directory (str): Путь к директории
        """
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            
            if os.path.isdir(path):
                # Рекурсивно обрабатываем поддиректории
                self._scan_directory(path)
            elif item.endswith(".desc"):
                # Загружаем .desc файл с локациями
                self._load_locations_from_file(path)

    def _load_locations_from_file(self, file_path):
        """
        Загружает локации из .desc файла.
        
        Args:
            file_path (str): Путь к файлу
        """
        try:
            # Используем DescLoader для загрузки данных из .desc файла
            locations_data = self.desc_loader.load_file(file_path)
                
            if isinstance(locations_data, dict):
                for location_id, location_data in locations_data.items():
                    # Добавляем локацию в атлас
                    self.locations_atlas[location_id.lower()] = location_data
                        
                self.logger.debug("Загружено {} локаций из файла {}", len(locations_data), file_path)
        except Exception as e:
            self.logger.error("Ошибка при загрузке файла {}: {}", file_path, str(e)) 