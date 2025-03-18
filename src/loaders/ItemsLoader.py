import json
import os
import sys
from src.models.inventory.InventoryItem import InventoryItem
from src.loaders.Loader import Loader
from src.models.inventory.types.Material import Material
from src.models.inventory.types.Armor import Armor
from src.utils.Logger import Logger
# Импортируйте здесь другие типы предметов по мере необходимости

class ItemsLoader(Loader):
    def __init__(self):
        self.items_atlas = {}  # JSON данные предметов
        self.inventory_items = {}  # Объекты инвентаря
        self.logger = Logger()

    def load(self):
        self.logger.info("ItemsLoader: начало загрузки данных...")
        # Базовая директория с предметами
        items_dir = "resources/items"
        
        # Проверка существования директории
        if not os.path.exists(items_dir):
            self.logger.error("Директория {} не существует!", items_dir)
        else:
            self.logger.debug("Сканирование директории {}", items_dir)
        
        # Рекурсивно сканируем все директории
        self._scan_directory(items_dir)
        
        # Создаем объекты инвентаря после загрузки JSON
        self._create_inventory_items()
        
        self.logger.info("ItemsLoader: загружено {} сущностей", len(self.items_atlas))
        return self.items_atlas
        
    def _create_inventory_items(self):
        """Создает объекты инвентаря на основе загруженных JSON данных"""
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
        """Создает объект предмета инвентаря из JSON данных"""
        try:
            item_type = item_data.get("type", "")
            
            if item_type == "material":
                # Создаем материал
                material = Material(
                    item_data.get("name", "Неизвестный материал"),
                    count,
                    item_data.get("description", ""),
                    item_data.get("value", 0),
                    item_data.get("rarity", "COMMON"),
                    item_id  # Передаем ID предмета
                )
                return material
            
            elif item_type == "armor":
                # Создаем броню
                armor = Armor(
                    item_data.get("name", "Неизвестная броня"),
                    count,
                    item_data.get("description", ""),
                    item_data.get("value", 0),
                    item_data.get("rarity", "COMMON"),
                    item_id,  # Передаем ID предмета
                    item_data.get("slot", "body"),  # Слот экипировки
                    item_data.get("characteristics", None)  # Характеристики брони
                )
                return armor
            # Здесь можно добавить другие типы предметов
            
            # Если тип неизвестен, создаем базовый предмет инвентаря
            return InventoryItem(
                item_data.get("name", "Неизвестный предмет"),
                count,
                item_data.get("description", ""),
                item_id  # Передаем ID предмета
            )
        except Exception as e:
            self.logger.exception(f"Ошибка при создании предмета инвентаря: {str(e)}")
            return None
        
    # Получить объект инвентаря
    def get_inventory_item(self, item_id, count=1):
        """Возвращает объект инвентарного предмета по его ID"""
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
        """Рекурсивно сканирует директорию и загружает все JSON файлы с предметами"""
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            
            if os.path.isdir(path):
                # Рекурсивно обрабатываем поддиректории
                self._scan_directory(path)
            elif item.endswith(".json"):
                # Загружаем JSON файл с предметами
                self._load_items_from_file(path)

    def _load_items_from_file(self, file_path):
        """Загружает предметы из JSON файла"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                items_data = json.load(file)
                
                if isinstance(items_data, dict):
                    for item_id, item_data in items_data.items():
                        # Добавляем ID предмета в его данные
                        if isinstance(item_data, dict):
                            # Добавляем предмет в атлас
                            self.items_atlas[item_id.lower()] = item_data
                            
                            # Сразу создаем шаблон объекта инвентаря для кэша
                            if "type" in item_data:
                                try:
                                    template_item = self._create_inventory_item(item_data, 1, item_id.lower())
                                    if template_item:
                                        self.inventory_items[item_id.lower()] = template_item
                                except Exception as e:
                                    self.logger.error(f"Ошибка создания шаблона предмета {item_id}: {str(e)}")
                            
                self.logger.debug("Загружено {} предметов из файла {}", len(items_data), file_path)
        except Exception as e:
            self.logger.error("Ошибка при загрузке файла {}: {}", file_path, str(e))

# Код для тестирования при прямом запуске файла
if __name__ == "__main__":
    # Добавляем корень проекта в путь поиска модулей
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(base_path)
    
    # Теперь можно импортировать из src
    from src.loaders.Loader import Loader
    
    # Тестируем загрузчик
    loader = ItemsLoader()
    loader.load()
    print(f"Загружено {len(loader)} сущностей")
    
    # Вывести названия нескольких предметов для проверки
    for item_id in list(loader.keys())[:3]:
        print(f"Сущность: {item_id} - {loader[item_id]['name'] if 'name' in loader[item_id] else 'Без имени'}")
