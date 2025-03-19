"""
Загрузчик предметов из .desc файлов.
"""

import os
from src.loaders.SimpleLoader import SimpleLoader
from src.models import SimpleItem
from src.models.items.Food import Food
from src.models.items.Material import Material
from src.utils.Logger import Logger
from src.loaders.DescLoader import DescLoader

class ItemsLoader(SimpleLoader):
    """
    Класс для загрузки предметов из .desc файлов.
    """
    
    def __init__(self):
        """
        Инициализирует загрузчик предметов.
        """
        self.items_atlas = {}  # Данные предметов
        self.inventory_items = {}  # Объекты инвентаря
        self.logger = Logger()
        self.desc_loader = DescLoader()

    def load(self):
        """
        Загружает все предметы из .desc файлов.
        
        Returns:
            dict: Атлас предметов
        """
        self.logger.info("ItemsLoader: начало загрузки данных...")
        
        # Базовая директория с предметами
        items_dir = "data/resources/items"
        
        # Проверка существования директории
        if not os.path.exists(items_dir):
            self.logger.error("Директория {} не существует!", items_dir)
            # Создаем директорию, если её нет
            os.makedirs(items_dir, exist_ok=True)
            self.logger.info("Создана директория для предметов: {}", items_dir)
        else:
            self.logger.debug("Сканирование директории {}", items_dir)
        
        # Рекурсивно сканируем все директории и загружаем .desc файлы
        self._scan_directory(items_dir)
        
        # Создаем объекты инвентаря после загрузки данных
        self._create_inventory_items()
        
        self.logger.info("ItemsLoader: загружено {} сущностей", len(self.items_atlas))
        return self.items_atlas
        
    def _create_inventory_items(self):
        """
        Создает объекты инвентаря на основе загруженных данных.
        """
        created_count = 0
        for item_id, item_data in self.items_atlas.items():
            # Пропускаем составные ключи, чтобы не создавать дубликаты
            if "." in item_id:
                continue
                
            if isinstance(item_data, dict) and "item_type" in item_data:
                inventory_item = self._create_inventory_item(item_data)
                if inventory_item:
                    self.inventory_items[item_id] = inventory_item
                    created_count += 1
        
        self.logger.debug("Создано {} объектов инвентаря", created_count)
    
    def _create_inventory_item(self, item_data, count=1, item_id=None):
        """
        Создает объект предмета инвентаря из данных.
        
        Args:
            item_data (dict): Данные предмета
            count (int): Количество предметов
            item_id (str): ID предмета
            
        Returns:
            object: Объект предмета
        """
        try:
            item_type = item_data.get("type", "")
            
            if item_type == "material":
                # Создаем материал
                material = Material(
                    item_data.get("name", "Неизвестный материал"),
                    item_data.get("description", ""),
                    item_data.get("value", 0),
                    item_data.get("rarity", "COMMON"),
                    item_id  # Передаем ID предмета
                )
                return material
            
            elif item_type == "food":
                # Создаем еду
                food = Food(
                    item_data.get("name", "Неизвестная еда"),
                    item_data.get("description", ""),
                    item_data.get("value", 0),
                    item_data.get("rarity", "COMMON"),
                    item_id  # Передаем ID предмета
                )
                return food
            
            # Если тип неизвестен, создаем базовый предмет инвентаря
            return SimpleItem(
                item_data.get("name", "Неизвестный предмет"),
                item_data.get("description", ""),
                item_id  # Передаем ID предмета
            )
        except Exception as e:
            self.logger.exception(f"Ошибка при создании предмета инвентаря: {str(e)}")
            return None
        
    # Получить объект инвентаря
    def get_inventory_item(self, item_id, count=1):
        """
        Возвращает объект инвентарного предмета по его ID.
        
        Args:
            item_id (str): ID предмета
            count (int): Количество предметов
            
        Returns:
            object: Объект предмета
        """
        # Предмет в кэше - создаем новый с заданным количеством
        if item_id in self.inventory_items:
            item_data = self.items_atlas[item_id]
            return self._create_inventory_item(item_data, count, item_id)
        
        # Предмет не найден в кэше, пробуем создать его заново
        if item_id in self.items_atlas:
            item_data = self.items_atlas[item_id]
            inventory_item = self._create_inventory_item(item_data, count, item_id)
            if inventory_item:
                # Сохраняем шаблон предмета (с количеством 1) в кэш
                template_item = self._create_inventory_item(item_data, 1, item_id)
                if template_item:
                    self.inventory_items[item_id] = template_item
                return inventory_item
        
        self.logger.error(f"Предмет с ID {item_id} не найден!")
        return None
    
    # Магические методы для работы как со словарем
    def __getitem__(self, key):
        """Позволяет обращаться через квадратные скобки: loader['item_id']"""
        return self.items_atlas[key]
    
    def __setitem__(self, key, value):
        """Позволяет присваивать через квадратные скобки: loader['item_id'] = item_data"""
        self.items_atlas[key] = value
    
    def __contains__(self, key):
        """Позволяет использовать проверку 'in': 'item_id' in loader"""
        return key in self.items_atlas
    
    def __len__(self):
        """Позволяет использовать len(): len(loader)"""
        return len(self.items_atlas)
    
    def keys(self):
        """Возвращает ключи как в словаре"""
        return self.items_atlas.keys()
    
    def values(self):
        """Возвращает значения как в словаре"""
        return self.items_atlas.values()
    
    def items(self):
        """Возвращает пары ключ-значение как в словаре"""
        return self.items_atlas.items()
        
    def _scan_directory(self, directory):
        """
        Рекурсивно сканирует директорию и загружает все .desc файлы с предметами.
        
        Args:
            directory (str): Путь к директории
        """
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            
            if os.path.isdir(path):
                # Рекурсивно обрабатываем поддиректории
                self._scan_directory(path)
            elif item.endswith(".desc"):
                # Загружаем .desc файл с предметами
                self._load_items_from_file(path)

    def _load_items_from_file(self, file_path):
        """
        Загружает предметы из .desc файла.
        
        Args:
            file_path (str): Путь к файлу
        """
        try:
            # Используем DescLoader для загрузки данных из .desc файла
            items_data = self.desc_loader.load_file(file_path)
            
            if isinstance(items_data, dict):
                for item_id, item_data in items_data.items():
                    # Пропускаем элементы, которые не являются предметами
                    if not isinstance(item_data, dict):
                        self.logger.warning(f"Пропускаю не-словарь: {item_id} в {file_path}")
                        continue
                        
                    # Проверяем, что это объект ITEM или другой подходящий тип
                    if "type" in item_data:
                        # Добавляем предмет в атлас
                        self.items_atlas[item_id.lower()] = item_data
                        
                        # Сразу создаем шаблон объекта инвентаря для кэша
                        try:
                            template_item = self._create_inventory_item(item_data, 1, item_id.lower())
                            if template_item:
                                self.inventory_items[item_id.lower()] = template_item
                        except Exception as e:
                            self.logger.error(f"Ошибка при создании шаблона предмета {item_id}: {str(e)}")
                            
                        self.logger.debug(f"Загружен предмет: {item_id}")
                    else:
                        self.logger.warning(f"Пропускаю объект без поля 'type': {item_id} в {file_path}")
                        
                self.logger.debug(f"Загружено {len(items_data)} предметов из файла {file_path}")
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке файла {file_path}: {str(e)}")
