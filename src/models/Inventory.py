class Inventory:
    def __init__(self, items: dict[str, int] = {}):
        self.items = items
    
    def add_item_by_id(self, itemID: str, count: int = 1) -> bool:
        """
        Добавляет count предметов itemID в инвентарь.
        Возвращает True, если добавление прошло успешно
        """
        
        if itemID in self.items:
            self.items[itemID] += count
        else:
            self.items[itemID] = count
            
        return True

    def take_item_by_id(self, itemID: str, count: int = 1) -> bool:
        """
        Удаляет count предметов itemID из инвентаря.
        Возвращает True, если удаление прошло успешно, и False, если предметов недостаточно.
        """
        
        if self.items[itemID] >= count:
            self.items[itemID] -= count
            if self.items[itemID] == 0:
                del self.items[itemID]
            return True
        return False
    
    def get_item_count_by_id(self, itemID: str) -> int:
        """
        Возвращает количество предметов itemID в инвентаре.
        """
        
        return self.items[itemID] if itemID in self.items else 0
