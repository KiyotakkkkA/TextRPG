class InventoryItem:
    def __init__(self, name, count=1, description="", item_id=None):
        self.name = name
        self.description = description
        self.count = count
        self.id = item_id

    def add(self):
        self.count += 1

    def take(self):
        self.count -= 1

    def remove(self):
        self.count = 0

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

    def set_rarity(self, rarity):
        self.rarity = rarity

    def set_name(self, name):
        self.name = name
    
    def set_description(self, description):
        self.description = description

    def set_count(self, count):
        self.count = count

    def set_id(self, item_id):
        self.id = item_id

    def copy(self):
        """Создает копию предмета"""
        new_item = InventoryItem(self.name, self.count, self.description, self.id)
        return new_item
