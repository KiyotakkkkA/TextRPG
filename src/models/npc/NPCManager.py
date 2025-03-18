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
        """Загружает всех NPC из указанной директории и её подпапок"""
        if not os.path.exists(npcs_directory):
            self.logger.error(f"Директория NPC не найдена: {npcs_directory}")
            return
        
        # Счетчики для логирования
        total_files_processed = 0
        total_npcs_loaded = 0
        
        # Рекурсивно проходим по всем файлам в директории и её подпапках
        for root, dirs, files in os.walk(npcs_directory):
            for file in files:
                # Проверяем, что это JSON файл
                if not file.endswith('.json'):
                    continue
                
                file_path = os.path.join(root, file)
                self.logger.info(f"Обрабатываем файл NPC: {file_path}")
                
                try:
                    # Загружаем NPC из файла
                    npcs_in_file = self.load_npc_from_file(file_path)
                    
                    # Обновляем счетчики
                    total_files_processed += 1
                    total_npcs_loaded += npcs_in_file
                    
                except Exception as e:
                    self.logger.error(f"Ошибка при загрузке NPC из файла {file_path}: {str(e)}")
        
        # Суммарная статистика
        self.logger.info(f"Всего обработано файлов NPC: {total_files_processed}")
        self.logger.info(f"Всего загружено NPC: {total_npcs_loaded}")
        
    def load_npc_from_file(self, file_path):
        """Загружает NPC из JSON-файла
        
        Returns:
            int: Количество загруженных NPC из файла
        """
        npcs_loaded = 0
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
                            
                        # Загружаем параметр опыта торговли
                        if "trade_exp" in npc_info:
                            npc.trade_exp = npc_info["trade_exp"]
                            
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
                    npcs_loaded += 1
                    
            return npcs_loaded
                    
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке NPC из {file_path}: {str(e)}")
            return 0
        
    def get_npc(self, npc_id):
        """Возвращает NPC по ID"""
        return self.npcs.get(npc_id)
        
    def get_npcs_at_location(self, location_id):
        """Возвращает список NPC в указанной локации"""
        return [npc for npc in self.npcs.values() if npc.location_id == location_id]

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