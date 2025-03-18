from src.models.npc.NPC import NPC

class TraderNPC(NPC):
    """NPC торговец, который может покупать и продавать предметы"""
    
    def __init__(self, id, name, description, location_id=None):
        super().__init__(id, name, description, "trader", location_id)
        self.buys = {}  # {item_id: price_modifier}
        self.sells = {}  # {item_id: {price: X, count: Y}}
        self.trade_exp = 1  # Опыт торговли за единицу товара (по умолчанию)
        
    def add_buy_item(self, item_id, price_modifier=1.0):
        """Добавляет предмет, который торговец будет покупать"""
        self.buys[item_id] = price_modifier
        
    def add_sell_item(self, item_id, price, count=1):
        """Добавляет предмет, который торговец будет продавать"""
        self.sells[item_id] = {"price": price, "count": count}
        
    def get_buy_price(self, item_id, base_price):
        """Возвращает цену, по которой торговец купит предмет"""
        if item_id in self.buys:
            return int(base_price * self.buys[item_id])
        return 0  # Торговец не покупает этот предмет
        
    def get_sell_price(self, item_id):
        """Возвращает цену, по которой торговец продаст предмет"""
        if item_id in self.sells:
            return self.sells[item_id]["price"]
        return 0 