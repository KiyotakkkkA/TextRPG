from src.models.npc.NPC import NPC

class DialogueNPC(NPC):
    """NPC, который предоставляет только диалоги и информацию о мире"""
    
    def __init__(self, id, name, description, location_id=None):
        super().__init__(id, name, description, "dialogue", location_id)
        self.topics = {}  # Темы для разговора
        
    def add_topic(self, topic_id, topic_name, dialogue_id):
        """Добавляет тему для разговора"""
        self.topics[topic_id] = {
            "name": topic_name,
            "dialogue_id": dialogue_id
        }
    
    def get_available_topics(self):
        """Возвращает доступные темы для разговора"""
        return self.topics 