from src.models.interfaces.Serializable import Serializable

class SimpleItem(Serializable):
    def __init__(self, name, description="", item_id=None):
        self.name = name
        self.description = description
        self.id = item_id

    def get_count(self):
        return self.count
    
    def get_name(self):
        return self.name
    
    def get_description(self):
        return self.description
    
    def get_id(self):
        return self.id
    
    def get_rarity(self):
        return "COMMON"

    def get_type(self):
        """Возвращает тип предмета"""
        return "Предмет"

    def set_rarity(self, rarity):
        self.rarity = rarity

    def set_name(self, name):
        self.name = name
    
    def set_description(self, description):
        self.description = description


    def set_id(self, item_id):
        self.id = item_id

    def copy(self):
        """Создает копию предмета"""
        new_item = SimpleItem(self.name, self.description, self.id)
        return new_item
