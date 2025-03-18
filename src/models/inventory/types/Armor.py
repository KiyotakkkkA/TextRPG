from src.models.inventory.InventoryItem import InventoryItem

class Armor(InventoryItem):
    def __init__(self, name, count=1, description="", value=0, rarity="COMMON", item_id=None, slot=None, characteristics=None):
        """
        Инициализация брони
        name - название брони
        count - количество (по умолчанию 1)
        description - описание
        value - ценность/стоимость брони
        rarity - редкость брони (по умолчанию COMMON)
        item_id - идентификатор предмета (необходим для квестов)
        slot - слот для экипировки (body, head, legs, arms и т.д.)
        characteristics - характеристики брони (defense, weight, durability)
        """
        super().__init__(name, count, description, item_id)
        self.value = value
        self.rarity = rarity
        self.type = "Броня"
        self.slot = slot or "body"
        
        # Инициализация характеристик
        self.characteristics = characteristics or {
            "defense": 0,
            "weight": 1,
            "durability": 100
        }
        
    def get_type(self):
        return self.type
    
    def get_value(self):
        return self.value
    
    def get_rarity(self):
        return self.rarity
    
    def get_slot(self):
        """Возвращает слот, в который экипируется броня"""
        return self.slot
    
    def get_defense(self):
        """Возвращает значение защиты брони"""
        return self.characteristics.get("defense", 0)
    
    def get_weight(self):
        """Возвращает вес брони"""
        return self.characteristics.get("weight", 1)
    
    def get_durability(self):
        """Возвращает текущую прочность брони"""
        return self.characteristics.get("durability", 100)
    
    def decrease_durability(self, amount=1):
        """Уменьшает прочность брони"""
        if "durability" in self.characteristics:
            self.characteristics["durability"] = max(0, self.characteristics["durability"] - amount)
        return self.get_durability()
        
    def copy(self):
        """Создает копию брони"""
        new_armor = Armor(
            self.name, 
            self.count, 
            self.description,
            self.value,
            self.rarity,
            self.id,
            self.slot,
            self.characteristics.copy()  # Важно скопировать словарь характеристик
        )
        return new_armor
