import json
from src.utils.Logger import Logger

class NPC:
    """Базовый класс для всех NPC в игре"""
    
    def __init__(self, id, name, description, npc_type, location_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.type = npc_type  # "trader", "quest", "dialog"
        self.location_id = location_id
        self.dialogue_tree = {}
        self.logger = Logger()
        
    def get_greeting(self):
        """Возвращает приветствие NPC, если есть"""
        if "greeting" in self.dialogue_tree:
            return self.dialogue_tree["greeting"]
        return f"Приветствую, путник. Я {self.name}."
        
    def get_dialogue(self, dialogue_id="greeting"):
        """Возвращает диалог по ID"""
        if dialogue_id in self.dialogue_tree:
            return self.dialogue_tree[dialogue_id]
        return None
        
    def get_basic_info(self):
        """Возвращает базовую информацию о NPC"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "location": self.location_id
        } 