import os
import json
from src.utils.Logger import Logger
from src.models.quests.Quest import Quest
from src.models.quests.QuestStage import QuestStage
from src.models.quests.objectives.CollectObjective import CollectObjective
from src.models.quests.objectives.TalkObjective import TalkObjective
from src.models.quests.objectives.GotoObjective import GotoObjective

class QuestManager:
    """Класс для управления квестами в игре"""
    
    def __init__(self):
        self.quests = {}  # {quest_id: quest_object}
        self.active_quests = []  # Список активных квестов (id)
        self.completed_quests = []  # Список выполненных квестов (id)
        self.logger = Logger()
    
    def load_quests(self, quests_directory="resources/quests"):
        """Загружает все квесты из указанной директории"""
        if not os.path.exists(quests_directory):
            self.logger.error(f"Директория квестов не найдена: {quests_directory}")
            return
        
        for filename in os.listdir(quests_directory):
            if filename.endswith(".json"):
                quest_path = os.path.join(quests_directory, filename)
                self.load_quest_from_file(quest_path)
                
    def load_quest_from_file(self, file_path):
        """Загружает квест из JSON-файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                quest_data = json.load(file)
                
                for quest_id, quest_info in quest_data.items():
                    name = quest_info.get("name", quest_id)
                    description = quest_info.get("description", "")
                    giver_id = quest_info.get("giver_id")
                    
                    # Создаем объект квеста
                    quest = Quest(quest_id, name, description, giver_id)
                    
                    # Загружаем принимающего квест NPC, если отличается от выдающего
                    taker_id = quest_info.get("taker_id", giver_id)
                    quest.taker_id = taker_id
                    
                    # Загружаем награды
                    rewards = quest_info.get("rewards", {})
                    quest.rewards["experience"] = rewards.get("experience", 0)
                    quest.rewards["money"] = rewards.get("money", 0)
                    quest.rewards["items"] = rewards.get("items", {})
                    quest.rewards["skills"] = rewards.get("skills", {})
                    
                    # Загружаем требования
                    requirements = quest_info.get("requirements", {})
                    quest.requirements["level"] = requirements.get("level", 1)
                    quest.requirements["skills"] = requirements.get("skills", {})
                    quest.requirements["items"] = requirements.get("items", {})
                    quest.requirements["quests"] = requirements.get("quests", [])
                    
                    # Загружаем стадии квеста
                    stages_data = quest_info.get("stages", [])
                    for stage_index, stage_data in enumerate(stages_data):
                        stage_id = stage_data.get("id", f"stage_{stage_index}")
                        stage_name = stage_data.get("name", f"Этап {stage_index+1}")
                        stage_description = stage_data.get("description", "")
                        
                        # Создаем объект стадии
                        stage = QuestStage(stage_id, stage_name, stage_description)
                        
                        # Загружаем цели стадии
                        objectives_data = stage_data.get("objectives", [])
                        for objective_data in objectives_data:
                            objective_type = objective_data.get("type")
                            
                            if objective_type == "collect":
                                item_id = objective_data.get("item_id")
                                required_count = objective_data.get("count", 1)
                                description = objective_data.get("description")
                                
                                objective = CollectObjective(item_id, required_count, description)
                                stage.add_objective(objective)
                                
                            elif objective_type == "talk":
                                npc_id = objective_data.get("npc_id")
                                description = objective_data.get("description")
                                
                                objective = TalkObjective(npc_id, description)
                                stage.add_objective(objective)
                                
                            elif objective_type == "goto":
                                location_id = objective_data.get("location_id")
                                description = objective_data.get("description")
                                
                                objective = GotoObjective(location_id, description)
                                stage.add_objective(objective)
                        
                        # Добавляем стадию к квесту
                        quest.add_stage(stage)
                    
                    # Добавляем квест в словарь
                    self.quests[quest_id] = quest
                    self.logger.info(f"Загружен квест: {name}")
                    
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке квеста из {file_path}: {str(e)}")
            
    def get_quest(self, quest_id):
        """Возвращает квест по ID"""
        return self.quests.get(quest_id)
        
    def start_quest(self, quest_id, player):
        """Начинает квест для игрока"""
        quest = self.get_quest(quest_id)
        if not quest:
            return False
            
        if quest.status != Quest.STATUS_NOT_STARTED:
            return False
            
        # Проверяем требования для начала квеста
        if not quest.can_be_started(player):
            return False
            
        # Начинаем квест
        if quest.start():
            if quest_id not in self.active_quests:
                self.active_quests.append(quest_id)
            return True
            
        return False
        
    def complete_quest(self, quest_id, player, game):
        """Завершает квест и выдает награды"""
        quest = self.get_quest(quest_id)
        if not quest:
            return False
            
        if quest.status != Quest.STATUS_IN_PROGRESS:
            return False
            
        # Проверяем, готов ли квест к завершению
        if not quest.is_ready_to_complete():
            return False
            
        # Завершаем квест
        if quest.complete():
            # Удаляем из активных и добавляем в выполненные
            if quest_id in self.active_quests:
                self.active_quests.remove(quest_id)
            if quest_id not in self.completed_quests:
                self.completed_quests.append(quest_id)
                
            # Выдаем награды
            self.give_rewards(quest, player, game)
            
            return True
            
        return False
        
    def give_rewards(self, quest, player, game):
        """Выдает награды за выполнение квеста"""
        # Опыт персонажа
        if quest.rewards["experience"] > 0:
            player.add_experience(quest.rewards["experience"])
            
        # Деньги
        if quest.rewards["money"] > 0:
            player.add_money(quest.rewards["money"])
            
        # Предметы
        for item_id, count in quest.rewards["items"].items():
            player.add_item_by_id(game, item_id, count)
            
        # Опыт навыков
        for skill_id, exp_amount in quest.rewards["skills"].items():
            player.skill_system.add_experience(skill_id, exp_amount)
            
    def update_all_quests(self, player, game):
        """Обновляет прогресс всех активных квестов"""
        updated = False
        
        for quest_id in self.active_quests:
            quest = self.get_quest(quest_id)
            if quest and quest.update_progress(player, game):
                updated = True
                
        return updated
        
    def get_active_quests(self):
        """Возвращает список активных квестов"""
        return [self.get_quest(quest_id) for quest_id in self.active_quests if self.get_quest(quest_id)]
        
    def get_completed_quests(self):
        """Возвращает список выполненных квестов"""
        return [self.get_quest(quest_id) for quest_id in self.completed_quests if self.get_quest(quest_id)]
        
    def get_available_quests_for_npc(self, npc_id):
        """Возвращает список доступных квестов для указанного NPC"""
        available_quests = []
        
        for quest in self.quests.values():
            if quest.giver_id == npc_id and quest.status == Quest.STATUS_NOT_STARTED:
                available_quests.append(quest)
                
        return available_quests
        
    def get_ready_to_complete_quests_for_npc(self, npc_id):
        """Возвращает список квестов, готовых к завершению у указанного NPC"""
        ready_quests = []
        
        for quest_id in self.active_quests:
            quest = self.get_quest(quest_id)
            if quest and quest.taker_id == npc_id and quest.is_ready_to_complete():
                ready_quests.append(quest)
                
        return ready_quests
        
    def get_tracked_quest(self):
        """Возвращает отслеживаемый квест (если есть)"""
        for quest_id in self.active_quests:
            quest = self.get_quest(quest_id)
            if quest and quest.tracked:
                return quest
        return None
        
    def track_quest(self, quest_id):
        """Устанавливает квест для отслеживания"""
        # Сначала отключаем отслеживание для всех квестов
        for q in self.quests.values():
            q.set_tracked(False)
            
        # Затем включаем отслеживание для указанного квеста
        quest = self.get_quest(quest_id)
        if quest and quest.status == Quest.STATUS_IN_PROGRESS:
            return quest.set_tracked(True)
            
        return False 