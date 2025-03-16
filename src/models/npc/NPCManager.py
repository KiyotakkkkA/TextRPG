import os
import json
from src.utils.Logger import Logger
from src.models.npc.TraderNPC import TraderNPC
from src.models.npc.QuestNPC import QuestNPC
from src.models.npc.DialogueNPC import DialogueNPC

class NPCManager:
    """Класс для управления NPC в игре"""
    
    def __init__(self):
        self.npcs = {}  # {npc_id: npc_object}
        self.logger = Logger()
        
    def load_npcs(self, npcs_directory="resources/npcs"):
        """Загружает всех NPC из указанной директории"""
        if not os.path.exists(npcs_directory):
            self.logger.error(f"Директория NPC не найдена: {npcs_directory}")
            return
        
        for filename in os.listdir(npcs_directory):
            if filename.endswith(".json"):
                npc_path = os.path.join(npcs_directory, filename)
                self.load_npc_from_file(npc_path)
                
    def load_npc_from_file(self, file_path):
        """Загружает NPC из JSON-файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                npc_data = json.load(file)
                
                for npc_id, npc_info in npc_data.items():
                    npc_type = npc_info.get("type", "dialogue")
                    name = npc_info.get("name", npc_id)
                    description = npc_info.get("description", "")
                    location_id = npc_info.get("location_id")
                    
                    # Создаем NPC в зависимости от типа
                    if npc_type == "trader":
                        npc = TraderNPC(npc_id, name, description, location_id)
                        
                        # Загружаем предметы, которые покупает торговец
                        for buy_item, price_mod in npc_info.get("buys", {}).items():
                            npc.add_buy_item(buy_item, price_mod)
                            
                        # Загружаем предметы, которые продает торговец
                        for sell_item, sell_info in npc_info.get("sells", {}).items():
                            price = sell_info.get("price", 0)
                            count = sell_info.get("count", 1)
                            npc.add_sell_item(sell_item, price, count)
                            
                    elif npc_type == "quest":
                        npc = QuestNPC(npc_id, name, description, location_id)
                        
                        # Загружаем доступные квесты
                        for quest_id in npc_info.get("available_quests", []):
                            npc.add_available_quest(quest_id)
                            
                    else:  # dialogue
                        npc = DialogueNPC(npc_id, name, description, location_id)
                        
                        # Загружаем темы для разговора
                        for topic_id, topic_info in npc_info.get("topics", {}).items():
                            topic_name = topic_info.get("name", topic_id)
                            dialogue_id = topic_info.get("dialogue_id", topic_id)
                            npc.add_topic(topic_id, topic_name, dialogue_id)
                    
                    # Загружаем диалоги
                    npc.dialogue_tree = npc_info.get("dialogues", {})
                    
                    # Добавляем NPC в словарь
                    self.npcs[npc_id] = npc
                    self.logger.info(f"Загружен NPC: {name} (тип: {npc_type})")
                    
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке NPC из {file_path}: {str(e)}")
            
    def get_npc(self, npc_id):
        """Возвращает NPC по ID"""
        return self.npcs.get(npc_id)
        
    def get_npcs_at_location(self, location_id):
        """Возвращает список NPC в указанной локации"""
        return [npc for npc in self.npcs.values() if npc.location_id == location_id] 