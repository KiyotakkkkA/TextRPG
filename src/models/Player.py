from src.models.Inventory import Inventory
from typing import TYPE_CHECKING
from src.EventSystem import get_event_system
from src.models.interfaces import Serializable

if TYPE_CHECKING:
    from src.GameSystem import GameSystem

class Player(Serializable):
    def __init__(self, game: 'GameSystem', name: str):
        self.name = name
        self.inventory = Inventory()
        self.game_system = game
        self.game = game
        self.event_system = get_event_system()
        
        self.level = 1
        self.gold = 0

    def get_item_by_id(self, itemID: str):
        """
        Возвращает предмет itemID из инвентаря.
        Предмет возвращается в виде словаря с данными предмета.
        """
        
        data = self.game.get_item(itemID)
        data["count"] = self.inventory.get_item_count_by_id(itemID)
        
        return data

    def add_item_by_id(self, itemID: str, count: int = 1) -> bool:
        """
        Добавляет count предметов itemID в инвентарь.
        Возвращает True, если добавление прошло успешно
        Не добавляет предметы, если их нет в игре
        """
        
        item_data = self.game.get_item(itemID)
        if not item_data:
            return False
        
        self.inventory.add_item_by_id(itemID, count)
        
        item_with_count = self.get_item_by_id(itemID)
        
        self.event_system.emit("player_took_item", item_with_count)
        
        return True

    def take_item_by_id(self, itemID: str, count: int = 1) -> bool:
        """
        Удаляет count предметов itemID из инвентаря.
        Возвращает True, если удаление прошло успешно, и False, если предметов недостаточно.
        Не удаляет предметы, если их нет в инвентаре
        """
        
        if not self.inventory.get_item_count_by_id(itemID):
            return False
        
        return self.inventory.take_item_by_id(itemID, count)
