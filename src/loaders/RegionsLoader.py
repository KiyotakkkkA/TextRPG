"""
Загрузчик регионов из файлов .desc.
Отвечает за загрузку и управление регионами в игре.
"""

import os
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.loaders.SimpleLoader import SimpleLoader
from src.loaders.DescLoader import DescLoader
from src.models.Region import Region
from src.utils.Logger import Logger

class RegionsLoader(SimpleLoader):
    """
    Загрузчик регионов из .desc файлов.
    """
    
    def __init__(self):
        """Инициализирует загрузчик регионов."""
        self.logger = Logger()
        self.desc_loader = DescLoader()
        
        # Словарь регионов, ключ - ID региона, значение - объект Region
        self.regions = {}
        
        # Словарь, сопоставляющий локации с их регионами
        self.location_to_region = {}
    
    def load(self):
        """
        Загружает все регионы из директории data/resources/regions.
        
        Returns:
            dict: Словарь загруженных регионов
        """
        self.logger.info("RegionsLoader: Загрузка регионов...")
        
        # Путь к директории с данными регионов
        regions_dir = Path("data/resources/regions")
        
        # Создаем директорию, если её нет
        if not regions_dir.exists():
            regions_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"RegionsLoader: Создана директория {regions_dir}")
        
        # Сканируем директорию для поиска .desc файлов
        regions_data = self._scan_directory(regions_dir)
        
        # Создаем объекты Region из загруженных данных
        self._create_regions(regions_data)
        
        self.logger.info(f"RegionsLoader: Загружено {len(self.regions)} регионов")
        return self.regions
    
    def _create_regions(self, regions_data):
        """
        Создает объекты Region из загруженных данных.
        """
        for region_id, data in regions_data.items():
            # Добавляем region_id в словарь data
            data_copy = data.copy()
            data_copy["id"] = region_id
            
            # Создаем объект Region с одним параметром
            region = Region(data_copy)
            
            # Добавляем в словарь регионов
            self.regions[region_id] = region
            
            # Обновляем словарь соответствия локаций регионам
            for location_id in region.locations:
                self.location_to_region[location_id] = region_id
    
    def get_region(self, region_id: str) -> Optional[Region]:
        """
        Возвращает регион по его ID.
        
        Args:
            region_id (str): ID региона
            
        Returns:
            Optional[Region]: Объект региона или None, если регион не найден
        """
        return self.regions.get(region_id)
    
    def get_all_regions(self) -> Dict[str, Region]:
        """
        Возвращает словарь всех регионов.
        
        Returns:
            Dict[str, Region]: Словарь всех регионов
        """
        return self.regions
    
    def get_region_for_location(self, location_id: str) -> Optional[Region]:
        """
        Возвращает регион, в котором находится указанная локация.
        
        Args:
            location_id (str): ID локации
            
        Returns:
            Optional[Region]: Регион, в котором находится локация, или None
        """
        region_id = self.location_to_region.get(location_id)
        if region_id:
            return self.regions.get(region_id)
        return None
    
    def _scan_directory(self, directory: Path) -> Dict[str, Any]:
        """
        Сканирует указанную директорию на наличие .desc файлов с регионами.
        
        Args:
            directory (Path): Путь к директории
            
        Returns:
            Dict[str, Any]: Словарь с данными регионов
        """
        regions_data = {}
        
        # Проверяем, существует ли директория
        if not directory.exists():
            return regions_data
        
        # Список всех .desc файлов в директории
        desc_files = list(directory.glob("*.desc"))
        
        for file_path in desc_files:
            try:
                # Загружаем данные из .desc файла
                file_data = self.desc_loader.load_file(str(file_path))
                
                # Обрабатываем данные регионов из файла
                for entity_id, entity_data in file_data.items():
                    # Проверяем, что это определение региона (по ключевым атрибутам)
                    if "name" in entity_data and "locations" in entity_data:
                        # Добавляем в общий словарь
                        regions_data[entity_id] = entity_data
            except Exception as e:
                self.logger.error(f"RegionsLoader: Ошибка при загрузке файла {file_path}: {e}")
        
        return regions_data
    
    # Магические методы для работы как со словарем
    def __getitem__(self, key):
        """Позволяет обращаться через квадратные скобки: loader['region_id']"""
        return self.regions.get(key)
    
    def __setitem__(self, key, value):
        """Позволяет присваивать через квадратные скобки: loader['region_id'] = region"""
        self.regions[key] = value
    
    def __contains__(self, key):
        """Позволяет использовать проверку 'in': 'region_id' in loader"""
        return key in self.regions
    
    def __len__(self):
        """Позволяет использовать len(): len(loader)"""
        return len(self.regions)
    
    def keys(self):
        """Возвращает ключи словаря регионов"""
        return self.regions.keys()
    
    def values(self):
        """Возвращает значения словаря регионов"""
        return self.regions.values()
    
    def items(self):
        """Возвращает пары (ключ, значение) словаря регионов"""
        return self.regions.items() 