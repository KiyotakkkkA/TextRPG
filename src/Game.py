from src.models.quests.QuestStage import QuestStage
from src.models.quests.Quest import Quest
from src.models.quests.QuestObjective import QuestObjective
from src.models.quests.objectives.CollectObjective import CollectObjective
from src.models.quests.objectives.TalkObjective import TalkObjective
from src.models.quests.objectives.GotoObjective import GotoObjective
from src.PreLoader import PreLoader
from src.models.Player import Player
from src.utils.Logger import Logger
import time
from src.models.npc.NPCManager import NPCManager
import os
import json


class Game:
    def __init__(self):
        self.preloader = PreLoader()
        self.player = Player()
        self.ATLAS = None  # Будет установлен после загрузки
        self.last_update_time = time.time()  # Для отслеживания времени для обновления локаций
        self.logger = Logger()  # Добавляем логгер
        self.npc_manager = NPCManager()
        self.npc_manager.load_npcs("resources/npcs")
        
        # Добавляем систему квестов
        self.tracked_quest_id = None  # ID отслеживаемого квеста
        self.active_quests = {}  # Активные квесты {quest_id: quest_object}
        self.completed_quests = {}  # Выполненные квесты {quest_id: quest_object}
        
        # Глоссарий для хранения информации о ресурсах и NPC
        self.glossary = {
            "resources": {},  # {resource_id: {"name": name, "description": desc, "locations": [loc1, loc2]}}
            "npcs": {}       # {npc_id: {"name": name, "description": desc, "location": loc}}
        }
        
        # Информация о отслеживаемых целях
        self.tracked_location = None
        self.tracked_target = None
        self.tracked_target_type = None  # "resource" или "npc"
        self.tracked_path = []  # Список локаций для посещения

    def preload(self):
        """Загружает все ресурсы игры"""
        self.preloader.load()
        self.ATLAS = self.preloader.get_atlas()
        
        # Устанавливаем начальную локацию игрока, если есть локации
        if len(self.ATLAS["LOCATIONS"]) > 0:
            first_location_id = next(iter(self.ATLAS["LOCATIONS"].keys()))
            self.player.set_location(self.ATLAS["LOCATIONS"][first_location_id])
        
        # Загружаем квесты из файлов
        self.logger.info("Загрузка квестов...")
        self.load_quests("resources/quests")
        self.logger.info(f"Загружено квестов: {len(self.all_quests)}")

    def get_item(self, item_id):
        """Возвращает данные предмета по его ID"""
        if not item_id:
            return None
        
        # Проверяем регистр
        if item_id.lower() in self.ATLAS["ITEMS"]:
            return self.ATLAS["ITEMS"][item_id.lower()]
        elif item_id in self.ATLAS["ITEMS"]:
            return self.ATLAS["ITEMS"][item_id]
        
        return None

    def create_inventory_item(self, item_id, count=1):
        """
        Создает инвентарный предмет на основе данных из атласа
        """
        # Проверяем регистр
        if item_id and item_id.lower() in self.ATLAS["ITEMS"]:
            item_id = item_id.lower()
        
        # Делегируем создание предмета загрузчику
        inventory_item = self.preloader.ATLAS["ITEMS"].get_inventory_item(item_id, count)
        
        if not inventory_item:
            self.logger.error(f"Не удалось создать предмет инвентаря: {item_id}")
        
        return inventory_item

    def get_location(self, location_id):
        """Получает локацию по ID"""
        if "LOCATIONS" in self.ATLAS and location_id in self.ATLAS["LOCATIONS"]:
            return self.ATLAS["LOCATIONS"][location_id]
        return None

    def get_current_location(self):
        """Возвращает текущую локацию игрока"""
        return self.player.current_location

    def update(self):
        """Обновляет состояние игры"""
        current_time = time.time()
        time_passed = current_time - self.last_update_time
        
        # Обновляем все локации если прошло хотя бы 1 секунда
        if time_passed >= 1.0 and "LOCATIONS" in self.ATLAS:
            for location in self.ATLAS["LOCATIONS"].values():
                location.update(time_passed)
                self.logger.debug(f"Обновление локации {location.name}: прошло {time_passed:.1f} секунд")
        
        self.last_update_time = current_time

    def get_npc(self, npc_id):
        """Возвращает NPC по ID"""
        return self.npc_manager.get_npc(npc_id)
        
    def get_npcs_at_location(self, location_id):
        """Возвращает список NPC в указанной локации"""
        return self.npc_manager.get_npcs_at_location(location_id)

    def get_tracked_quest(self):
        """Возвращает отслеживаемый квест"""
        if self.tracked_quest_id and self.tracked_quest_id in self.active_quests:
            return self.active_quests[self.tracked_quest_id]
        return None
    
    def track_quest(self, quest_id):
        """Устанавливает квест как отслеживаемый"""
        if quest_id in self.active_quests:
            self.tracked_quest_id = quest_id
            self.logger.info(f"Начато отслеживание квеста: {quest_id}")
            return True
        return False
    
    def untrack_quest(self):
        """Отменяет отслеживание квеста"""
        self.tracked_quest_id = None
    
    def get_quest(self, quest_id):
        """Возвращает квест по ID"""
        if quest_id in self.active_quests:
            return self.active_quests[quest_id]
        if quest_id in self.completed_quests:
            return self.completed_quests[quest_id]
        # Ищем среди всех доступных квестов
        if hasattr(self, 'all_quests') and quest_id in self.all_quests:
            return self.all_quests[quest_id]
        return None
    
    def start_quest(self, quest_id):
        """Начинает новый квест"""
        self.logger.info(f"Попытка начать квест: {quest_id}")
        
        # Проверяем, существует ли квест
        if not hasattr(self, 'all_quests'):
            self.logger.error(f"Список all_quests не инициализирован!")
            print(f"Ошибка: система квестов не инициализирована.")
            return False
            
        if quest_id not in self.all_quests:
            self.logger.warning(f"Попытка начать несуществующий квест: {quest_id}")
            print(f"Ошибка: Квест '{quest_id}' не найден в игре.")
            print(f"Доступные квесты: {list(self.all_quests.keys())}")
            return False
            
        # Проверяем, активен ли уже квест
        if quest_id in self.active_quests:
            self.logger.warning(f"Попытка начать уже активный квест: {quest_id}")
            print(f"Квест '{quest_id}' уже активен.")
            return False
        
        # Создаем копию квеста и добавляем в активные
        quest = self.all_quests[quest_id]
        self.logger.info(f"Квест найден: {quest.name}")
        
        if quest.giver_id:
            # Находим NPC, выдающего квест
            npc = self.npc_manager.get_npc(quest.giver_id)
            if npc and hasattr(npc, 'available_quests'):
                # Удаляем квест из списка доступных у NPC
                if quest_id in npc.available_quests:
                    npc.available_quests.remove(quest_id)
                    self.logger.info(f"Квест {quest_id} удален из доступных у NPC {npc.id}")
        
        # Начинаем квест
        quest.start()
        self.active_quests[quest_id] = quest
        
        # Сразу после принятия квеста обновляем его прогресс
        # для учета предметов, которые уже есть у игрока
        self.update_quest_progress(quest_id)
        
        self.logger.info(f"Квест успешно начат: {quest_id}")
        return True
    
    def complete_quest(self, quest_id):
        """Завершает квест и выдает награды"""
        if quest_id in self.active_quests:
            quest = self.active_quests[quest_id]
            
            # Выдаем награды
            self.give_rewards(quest)
            
            # Перемещаем квест в выполненные
            self.completed_quests[quest_id] = quest
            del self.active_quests[quest_id]
            
            # Если это был отслеживаемый квест, снимаем отслеживание
            if self.tracked_quest_id == quest_id:
                self.tracked_quest_id = None
            
            self.logger.info(f"Завершен квест: {quest_id}")
            return True
        return False
        
    def give_rewards(self, quest):
        """Выдает награды за выполнение квеста"""
        # Опыт персонажа
        if quest.rewards["experience"] > 0:
            self.player.add_experience(quest.rewards["experience"])
            
        # Деньги
        if quest.rewards["money"] > 0:
            self.player.add_money(quest.rewards["money"])
            
        # Предметы
        for item_id, count in quest.rewards["items"].items():
            self.player.add_item_by_id(self, item_id, count)
            
        # Опыт навыков
        for skill_id, exp_amount in quest.rewards["skills"].items():
            self.player.skill_system.add_experience(skill_id, exp_amount)

    def get_ready_to_complete_quests_for_npc(self, npc_id):
        """Возвращает список квестов, готовых к завершению у указанного NPC"""
        ready_quests = []
        
        for quest_id, quest in self.active_quests.items():
            # Проверяем, является ли NPC получателем квеста и готов ли квест к завершению
            if quest.taker_id == npc_id and quest.is_ready_to_complete():
                ready_quests.append(quest)
                
        return ready_quests

    def load_quests(self, quests_dir):
        """Загружает квесты из директории"""
        self.all_quests = {}  # {quest_id: quest_object}
        
        if not os.path.exists(quests_dir):
            self.logger.error(f"Директория квестов не найдена: {quests_dir}")
            return
        
        # Получаем список файлов JSON в директории квестов
        quest_files = [os.path.join(quests_dir, f) for f in os.listdir(quests_dir) if f.endswith('.json')]
        
        for quest_file in quest_files:
            try:
                with open(quest_file, 'r', encoding='utf-8') as file:
                    quest_data = json.load(file)
                    
                    # Обрабатываем квесты из файла
                    if 'quests' in quest_data:
                        for quest_info in quest_data['quests']:
                            # Загружаем основную информацию о квесте
                            quest_id = quest_info.get('id', '')
                            name = quest_info.get('name', 'Безымянный квест')
                            description = quest_info.get('description', '')
                            giver_id = quest_info.get('giver_id', '')
                            taker_id = quest_info.get('taker_id', giver_id)
                            completion_text = quest_info.get('completion_text', '')
                            
                            # Создаем объект квеста
                            quest = Quest(quest_id, name, description, giver_id)
                            quest.taker_id = taker_id
                            
                            # Добавляем текст завершения квеста, если он есть
                            if completion_text:
                                quest.completion_text = completion_text
                            
                            # Загружаем требования
                            if 'requirements' in quest_info:
                                reqs = quest_info['requirements']
                                quest.requirements["level"] = reqs.get('level', 1)
                                quest.requirements["skills"] = reqs.get('skills', {})
                                quest.requirements["items"] = reqs.get('items', {})
                                quest.requirements["quests"] = reqs.get('quests', [])
                            
                            # Загружаем награды
                            if 'rewards' in quest_info:
                                rewards = quest_info['rewards']
                                quest.rewards["experience"] = rewards.get('experience', 0)
                                quest.rewards["money"] = rewards.get('money', 0)
                                quest.rewards["items"] = rewards.get('items', {})
                                quest.rewards["skills"] = rewards.get('skills', {})
                            
                            # Загружаем стадии и цели квеста
                            if 'stages' in quest_info:
                                for stage_info in quest_info['stages']:
                                    stage_name = stage_info.get('name', 'Безымянная стадия')
                                    stage_desc = stage_info.get('description', '')
                                    
                                    # Создаем стадию квеста
                                    stage = QuestStage(stage_name, stage_desc)
                                    
                                    # Добавляем цели для стадии
                                    if 'objectives' in stage_info:
                                        for obj_data in stage_info['objectives']:
                                            obj_type = obj_data.get('type', '')
                                            
                                            if obj_type == "gather" or obj_type == "collect":
                                                # Задача на сбор предметов
                                                item_id = obj_data.get("item_id", "")
                                                count = obj_data.get("count", 1)
                                                description = obj_data.get("description", f"Собрать {count} {item_id}")
                                                
                                                # Получаем название предмета для более информативного отображения
                                                if item_id in self.ATLAS["ITEMS"]:
                                                    item_name = self.ATLAS["ITEMS"][item_id].get("name", item_id)
                                                    description = f"Собрать {count} {item_name}"
                                                
                                                objective = CollectObjective(item_id, count, description)
                                                stage.objectives.append(objective)
                                                
                                            elif obj_type == "talk":
                                                # Задача на разговор с NPC
                                                npc_id = obj_data.get("npc_id", "")
                                                description = obj_data.get("description", f"Поговорить с {npc_id}")
                                                
                                                objective = TalkObjective(npc_id, description)
                                                stage.objectives.append(objective)
                                                
                                            elif obj_type == "goto":
                                                # Задача на посещение локации
                                                location_id = obj_data.get("location_id", "")
                                                description = obj_data.get("description", f"Посетить {location_id}")
                                                
                                                objective = GotoObjective(location_id, description)
                                                stage.objectives.append(objective)
                                            
                                            # Здесь можно добавить другие типы задач
                                    
                                    quest.add_stage(stage)
                            
                            # Добавляем квест в словарь всех квестов
                            self.all_quests[quest_id] = quest
                            
                            # Добавляем квест в список доступных квестов у NPC, если указан
                            if giver_id:
                                npc = self.npc_manager.get_npc(giver_id)
                                if npc and hasattr(npc, 'add_available_quest'):
                                    npc.add_available_quest(quest_id)
                            
                            self.logger.info(f"Загружен квест: {quest_id}")
            except Exception as e:
                self.logger.error(f"Ошибка при загрузке квестов из {quest_file}: {e}")
        
        # Выводим список всех загруженных квестов для отладки
        self.logger.info(f"Загружено квестов: {len(self.all_quests)}")
        for quest_id in self.all_quests:
            self.logger.debug(f"- Квест: {quest_id}")
            
        return self.all_quests

    def update_quest_progress(self, quest_id=None):
        """
        Обновляет прогресс указанного квеста или всех активных квестов
        
        Args:
            quest_id: ID квеста для обновления, если None - обновляются все активные квесты
        
        Returns:
            bool: True, если произошли изменения в прогрессе, иначе False
        """
        updated = False
        
        if quest_id:
            # Обновляем только указанный квест
            if quest_id in self.active_quests:
                quest = self.active_quests[quest_id]
                if quest.update_progress(self.player, self):
                    self.logger.info(f"Обновлен прогресс квеста: {quest_id}")
                    updated = True
        else:
            # Обновляем все активные квесты
            for quest_id, quest in self.active_quests.items():
                if quest.update_progress(self.player, self):
                    self.logger.info(f"Обновлен прогресс квеста: {quest_id}")
                    updated = True
        
        return updated
            
    # Методы для работы с глоссарием
    def add_resource_to_glossary(self, resource_id, location_id=None):
        """Добавляет ресурс в глоссарий"""
        if resource_id not in self.glossary["resources"]:
            # Получаем информацию о ресурсе
            item_data = self.get_item(resource_id)
            if not item_data:
                return False
                
            name = item_data.get('name', resource_id)
            description = item_data.get('description', 'Нет описания')
            
            # Создаем запись в глоссарии
            self.glossary["resources"][resource_id] = {
                "name": name,
                "description": description,
                "locations": []
            }
            
        # Добавляем локацию, если она указана и ещё не добавлена
        if location_id and location_id not in self.glossary["resources"][resource_id]["locations"]:
            self.glossary["resources"][resource_id]["locations"].append(location_id)
            
        return True
    
    def add_npc_to_glossary(self, npc_id):
        """Добавляет NPC в глоссарий"""
        if npc_id not in self.glossary["npcs"]:
            # Получаем информацию о NPC
            npc = self.get_npc(npc_id)
            if not npc:
                return False
                
            # Создаем запись в глоссарии
            self.glossary["npcs"][npc_id] = {
                "name": npc.name,
                "description": npc.description,
                "location": npc.location_id
            }
            
        return True
        
    def get_glossary_resources(self):
        """Возвращает список ресурсов в глоссарии"""
        return self.glossary["resources"]
        
    def get_glossary_npcs(self):
        """Возвращает список NPC в глоссарии"""
        return self.glossary["npcs"]

    def track_target(self, target_id, target_type):
        """Устанавливает отслеживаемую цель
        
        Args:
            target_id (str): ID ресурса или NPC для отслеживания
            target_type (str): Тип цели ('resource' или 'npc')
            
        Returns:
            bool: True, если отслеживание установлено успешно
        """
        # Проверяем, что цель есть в глоссарии
        if target_type == "resource" and target_id in self.glossary["resources"]:
            # Если у ресурса нет локаций, нельзя отслеживать
            if not self.glossary["resources"][target_id]["locations"]:
                return False
                
            self.tracked_target = target_id
            self.tracked_target_type = "resource"
            # Берем первую доступную локацию для ресурса
            target_location = self.glossary["resources"][target_id]["locations"][0]
            self.tracked_location = target_location
            
            # Вычисляем маршрут от текущей локации до целевой
            current_location = self.player.current_location.id
            self.tracked_path = self.calculate_path(current_location, target_location)
            
            return True
            
        elif target_type == "npc" and target_id in self.glossary["npcs"]:
            # Если у NPC нет локации, нельзя отслеживать
            if not self.glossary["npcs"][target_id]["location"]:
                return False
                
            self.tracked_target = target_id
            self.tracked_target_type = "npc"
            target_location = self.glossary["npcs"][target_id]["location"]
            self.tracked_location = target_location
            
            # Вычисляем маршрут от текущей локации до целевой
            current_location = self.player.current_location.id
            self.tracked_path = self.calculate_path(current_location, target_location)
            
            return True
            
        return False
    
    def untrack_target(self):
        """Отменяет отслеживание цели"""
        self.tracked_target = None
        self.tracked_target_type = None
        self.tracked_location = None
        self.tracked_path = []
    
    def calculate_path(self, start_location, target_location):
        """Вычисляет кратчайший путь между локациями
        
        Использует простой алгоритм поиска в ширину для нахождения пути
        
        Args:
            start_location (str): ID начальной локации
            target_location (str): ID целевой локации
            
        Returns:
            list: Список ID локаций, которые нужно посетить для достижения цели
        """
        if start_location == target_location:
            return []
            
        # BFS для поиска кратчайшего пути
        queue = [(start_location, [])]
        visited = set([start_location])
        
        while queue:
            (node, path) = queue.pop(0)
            
            # Получаем все соседние локации
            location = self.get_location(node)
            if not location:
                continue
                
            for neighbor in location.connected_locations:
                if neighbor == target_location:
                    # Нашли целевую локацию, возвращаем путь
                    return path + [neighbor]
                    
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
                    
        # Путь не найден
        return []
    
    def get_tracked_target_info(self):
        """Возвращает информацию о отслеживаемой цели
        
        Returns:
            dict: Информация о цели или None, если нет отслеживаемой цели
        """
        if not self.tracked_target:
            return None
            
        result = {
            "target_id": self.tracked_target,
            "target_type": self.tracked_target_type,
            "target_location": self.tracked_location,
            "path": self.tracked_path
        }
        
        # Добавляем информацию о цели
        if self.tracked_target_type == "resource":
            result["name"] = self.glossary["resources"][self.tracked_target]["name"]
        elif self.tracked_target_type == "npc":
            result["name"] = self.glossary["npcs"][self.tracked_target]["name"]
            
        # Добавляем название локации
        location = self.get_location(self.tracked_location)
        if location:
            result["location_name"] = location.name
        else:
            result["location_name"] = self.tracked_location
            
        return result
    
    def update_tracked_path(self):
        """Обновляет путь к отслеживаемой цели после перемещения игрока
        
        Должна вызываться после каждого перемещения игрока
        """
        if not self.tracked_target:
            return
            
        current_location = self.player.current_location.id
        
        # Если игрок уже в целевой локации, путь пустой
        if current_location == self.tracked_location:
            self.tracked_path = []
            return
            
        # Пересчитываем путь от текущей локации
        self.tracked_path = self.calculate_path(current_location, self.tracked_location)
            
    def get_tracked_quest_target_location(self):
        """Определяет целевую локацию для отслеживаемого квеста
        
        Анализирует текущую стадию квеста и определяет локацию, куда должен направиться игрок
        
        Returns:
            tuple: (location_id, target_name, target_type) или (None, None, None), если нет цели
        """
        quest = self.get_tracked_quest()
        if not quest:
            return None, None, None
            
        # Получаем текущую стадию квеста
        current_stage = quest.get_current_stage()
        if not current_stage:
            return None, None, None
            
        # Сперва проверяем задачи в текущей стадии
        for objective in current_stage.objectives:
            # Если найдена незавершенная задача, определяем локацию-цель
            if not objective.is_completed():
                # Задача поговорить с NPC
                if objective.type == "talk":
                    npc_id = objective.npc_id
                    npc = self.get_npc(npc_id)
                    if npc and npc.location_id:
                        return npc.location_id, npc.name, "npc"
                
                # Задача посетить локацию
                elif objective.type == "goto":
                    location_id = objective.location_id
                    location = self.get_location(location_id)
                    if location:
                        return location.id, location.name, "location"
                    
                # Задача собрать ресурсы
                elif objective.type == "collect":
                    item_id = objective.item_id
                    # Ищем локацию, где есть такой ресурс
                    for location in self.ATLAS["LOCATIONS"].values():
                        if item_id in location.resources and location.resources[item_id] > 0:
                            item_data = self.get_item(item_id)
                            item_name = item_data.get("name", item_id) if item_data else item_id
                            return location.id, item_name, "resource"
                            
        # Если текущая стадия завершена, но квест не готов к сдаче,
        # возможно мы должны перейти к следующему этапу
        if current_stage.is_completed() and not quest.is_ready_to_complete():
            # Если есть следующая стадия, попробуем найти там цель
            if quest.current_stage_index < len(quest.stages) - 1:
                next_stage = quest.stages[quest.current_stage_index + 1]
                if next_stage and next_stage.objectives:
                    obj = next_stage.objectives[0]
                    # Аналогично проверяем первую задачу следующей стадии
                    if obj.type == "talk":
                        npc_id = obj.npc_id
                        npc = self.get_npc(npc_id)
                        if npc and npc.location_id:
                            return npc.location_id, npc.name, "npc"
                            
                    elif obj.type == "goto":
                        location_id = obj.location_id
                        location = self.get_location(location_id)
                        if location:
                            return location.id, location.name, "location"
        
        # Если квест готов к завершению, указываем куда нужно идти
        if quest.is_ready_to_complete() and quest.taker_id:
            npc = self.get_npc(quest.taker_id)
            if npc and npc.location_id:
                return npc.location_id, npc.name, "npc"
                
        # Если не нашли цель, возвращаем None
        return None, None, None
        
    def calculate_path_to_quest_target(self):
        """Вычисляет путь к цели текущего отслеживаемого квеста
        
        Returns:
            list: Список ID локаций на пути к цели или пустой список
        """
        target_location, _, _ = self.get_tracked_quest_target_location()
        if not target_location or not self.player.current_location:
            return []
            
        # Если уже в целевой локации, путь пустой
        if target_location == self.player.current_location.id:
            return []
            
        # Ищем путь от текущей локации до цели
        return self.calculate_path(self.player.current_location.id, target_location)
            