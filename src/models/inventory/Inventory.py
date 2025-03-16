from src.models.inventory.InventoryItem import InventoryItem
from src.utils.Logger import Logger
from colorama import Style, Fore

rarity = {
    "COMMON": {
        "color": Fore.WHITE,
        "name": "Обычный",
        "order": 1
    },
    "UNCOMMON": {
        "color": Fore.GREEN,
        "name": "Необычный",
        "order": 2
    },
    "RARE": {
        "color": Fore.LIGHTBLUE_EX,
        "name": "Редкий",
        "order": 3
    },
    "EPIC": {
        "color": Fore.MAGENTA,
        "name": "Эпический",
        "order": 4
    },
    "LEGENDARY": {
        "color": Fore.YELLOW,
        "name": "Легендарный",
        "order": 5
    },
    "MYTHIC": {
        "color": Fore.RED,
        "name": "Мифический",
        "order": 6
    }
}

TYPE_NAME_COLOR = Fore.YELLOW
COUNT_NAME_COLOR = Fore.YELLOW

class Inventory:
    def __init__(self):
        self.items = []
        self.logger = Logger()

    def add_item(self, item: InventoryItem):
        if item is not None:
            self.items.append(item)
            self.logger.debug("Добавлен предмет {} ({})", item.name, item.get_rarity())
        else:
            self.logger.warning("Попытка добавить None в инвентарь")

    def remove_item(self, item: InventoryItem):
        if item in self.items:
            self.items.remove(item)
            self.logger.debug("Удален предмет {} ({})", item.name, item.get_rarity())
        else:
            self.logger.warning("Попытка удалить несуществующий предмет из инвентаря")

    def get_items(self):
        return self.items
    
    def print_inventory(self):
        if not self.items:
            print("ИНВЕНТАРЬ: пусто")
            self.logger.info("Инвентарь пуст")
            return
            
        print("ИНВЕНТАРЬ:")
        self.logger.info("Вывод инвентаря ({} предметов)", len(self.items))
        
        self.items = [item for item in self.items if item is not None]
        
        if not self.items:
            print("  Пусто (были удалены некорректные элементы)")
            self.logger.warning("Инвентарь пуст после фильтрации недействительных элементов")
            return
            
        self.items.sort(key=lambda x: rarity[x.get_rarity()]['order'])
        
        max_name_length = max([len(item.name) for item in self.items], default=0)
        max_count_length = max([len(str(item.get_count())) for item in self.items], default=0)
        max_type_length = max([len(item.get_type()) for item in self.items], default=0)
        max_rarity_length = max([len(rarity[item.get_rarity()]['name']) for item in self.items], default=0)
        
        for item in self.items:
            name_part = f"{item.name:<{max_name_length}}"
            count_part = f"({COUNT_NAME_COLOR}{item.get_count():>{max_count_length}}{Style.RESET_ALL})"
            type_part = f"[{TYPE_NAME_COLOR}{item.get_type():<{max_type_length}}{Style.RESET_ALL}]"
            rarity_color = rarity[item.get_rarity()]['color']
            rarity_name = rarity[item.get_rarity()]['name']
            rarity_part = f"{rarity_color}{rarity_name:<{max_rarity_length}}{Style.RESET_ALL}"
            
            print(f"{name_part} {count_part} {type_part} - {rarity_part}")
            
            # Логируем каждый предмет с детальной информацией
            self.logger.debug("Предмет: {} ({}x) - тип: {}, редкость: {}", 
                             item.name, item.get_count(), item.get_type(), item.get_rarity())

    def count_item(self, item_id):
        """Подсчитывает общее количество предметов с указанным ID в инвентаре
        
        Args:
            item_id: ID предмета для подсчета
            
        Returns:
            int: Общее количество предметов с указанным ID
        """
        count = 0
        for item in self.items:
            # Приведение к нижнему регистру для случаев сравнения разного регистра
            if hasattr(item, 'id') and str(item.id).lower() == str(item_id).lower():
                count += item.get_count()
            # Также проверяем по имени предмета для совместимости
            elif item.name.lower() == str(item_id).lower():
                count += item.get_count()
        return count
        
    def has_item(self, item_id, required_count=1):
        """Проверяет, есть ли в инвентаре необходимое количество предметов с указанным ID
        
        Args:
            item_id: ID предмета для проверки
            required_count: Необходимое количество (по умолчанию 1)
            
        Returns:
            bool: True если нужное количество есть в инвентаре, иначе False
        """
        return self.count_item(item_id) >= required_count
