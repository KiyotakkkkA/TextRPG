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
        
    def check_dialogue_condition(self, game, condition):
        """Проверяет выполнение условия для отображения варианта диалога
        
        Args:
            game: Объект игры для доступа к состоянию игрока
            condition: Строка с условием (например, "quest_available_quest1")
            
        Returns:
            bool: True если условие выполнено, False если нет
            str: Описание условия для отображения (или None если условие выполнено)
        """
        if not condition:
            return True, None
            
        player = game.player
        
        # Проверка доступности квеста
        if condition.startswith("quest_available_"):
            quest_id = condition.replace("quest_available_", "")
            quest = game.get_quest(quest_id)
            if quest and not quest.is_started() and not quest.is_completed():
                return True, None
            return False, f"[📜 Нужен квест: {quest_id if not quest else quest.name}]"
            
        # Проверка выполнения квеста
        elif condition.startswith("quest_completed_"):
            quest_id = condition.replace("quest_completed_", "")
            quest = game.get_quest(quest_id)
            if quest and quest.is_completed():
                return True, None
            return False, f"[📜 Нужно завершить: {quest_id if not quest else quest.name}]"
            
        # Проверка уровня навыка
        elif condition.startswith("skill_"):
            # Формат: skill_SKILLID_LEVEL
            parts = condition.split("_")
            if len(parts) >= 3:
                skill_id = parts[1]
                skill_level = int(parts[2])
                
                skill = player.skill_system.get_skill(skill_id)
                if skill and skill.level >= skill_level:
                    return True, None
                    
                skill_name = skill.name if skill else skill_id.capitalize()
                return False, f"[🧠 {skill_name}: {skill_level}]"
                
        # Проверка наличия предмета
        elif condition.startswith("item_"):
            item_id = condition.replace("item_", "")
            
            # Проверяем наличие предмета в инвентаре
            for item in player.inventory.items:
                if item.id.lower() == item_id.lower():
                    return True, None
                    
            # Получаем имя предмета для отображения
            item_data = game.get_item(item_id)
            item_name = item_data.get("name", item_id) if item_data else item_id
            return False, f"[📦 {item_name}]"
            
        # Проверка знакомства с NPC
        elif condition.startswith("npc_known_"):
            npc_id = condition.replace("npc_known_", "")
            
            # Проверяем, есть ли NPC в глоссарии
            glossary_npcs = game.get_glossary_npcs()
            if npc_id in glossary_npcs:
                return True, None
                
            # Получаем имя NPC для отображения
            npc = game.get_npc(npc_id)
            npc_name = npc.name if npc else npc_id
            return False, f"[👤 Знание о: {npc_name}]"
            
        # Проверка посещения локации
        elif condition.startswith("location_visited_"):
            location_id = condition.replace("location_visited_", "")
            
            # Проверяем, есть ли локация в глоссарии (как и для ресурсов, можно создать метод)
            if hasattr(game, "visited_locations") and location_id in game.visited_locations:
                return True, None
                
            # Получаем имя локации для отображения
            location = game.get_location(location_id)
            location_name = location.name if location else location_id
            return False, f"[🗺️ Посещено: {location_name}]"
            
        # Проверка победы над монстром
        elif condition.startswith("monster_defeated_"):
            monster_id = condition.replace("monster_defeated_", "")
            
            # Проверяем, есть ли монстр в глоссарии
            glossary_monsters = game.get_glossary_monsters()
            if monster_id in glossary_monsters:
                return True, None
                
            # Получаем имя монстра для отображения
            monster_data = game.get_monster(monster_id)
            monster_name = monster_data.name if monster_data else monster_id
            return False, f"[⚔️ Побеждено: {monster_name}]"
        
        # Если условие неизвестно, по умолчанию считаем его выполненным
        return True, None 