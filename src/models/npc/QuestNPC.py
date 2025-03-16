from src.models.npc.NPC import NPC

class QuestNPC(NPC):
    """NPC, который может выдавать и принимать квесты"""
    
    def __init__(self, id, name, description, location_id=None):
        super().__init__(id, name, description, "quest", location_id)
        self.available_quests = []  # ID доступных квестов
        self.completed_quests = []  # ID выполненных квестов
        
    def add_available_quest(self, quest_id):
        """Добавляет квест, который может выдать NPC"""
        if quest_id not in self.available_quests:
            self.available_quests.append(quest_id)
            
    def mark_quest_completed(self, quest_id):
        """Отмечает квест как выполненный"""
        if quest_id in self.available_quests:
            self.available_quests.remove(quest_id)
        if quest_id not in self.completed_quests:
            self.completed_quests.append(quest_id) 