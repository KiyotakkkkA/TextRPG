from src.models.SimpleItem import SimpleItem

class Food(SimpleItem):
    def __init__(self, name, description="", value=0, rarity="COMMON", item_id=None):
        super().__init__(name, description, item_id)
        self.value = value
        self.rarity = rarity
        self.type = "Food"
        
    def get_type(self):
        return self.type
    
    def get_value(self):
        return self.value
    
    def get_rarity(self):
        return self.rarity
    
    def copy(self):
        """Создает копию еды"""
        new_food = Food(
            self.name, 
            self.description,
            self.value,
            self.rarity,
            self.id
        )
        return new_food

