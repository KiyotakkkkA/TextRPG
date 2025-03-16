from src.models.inventory.InventoryItem import InventoryItem

class Material(InventoryItem):
    def __init__(self, name, count=1, description="", value=0, rarity="COMMON", item_id=None):
        """
        Инициализация материала
        name - название материала
        count - количество (по умолчанию 1)
        description - описание
        value - ценность/стоимость материала
        rarity - редкость материала (по умолчанию COMMON)
        item_id - идентификатор предмета (необходим для квестов)
        """
        super().__init__(name, count, description, item_id)
        self.value = value
        self.rarity = rarity
        self.type = "Материал"
        
    def get_type(self):
        return self.type
    
    def get_value(self):
        return self.value
    
    def get_rarity(self):
        return self.rarity
        
    def copy(self):
        """Создает копию материала"""
        new_material = Material(
            self.name, 
            self.count, 
            self.description,
            self.value,
            self.rarity,
            self.id
        )
        return new_material
