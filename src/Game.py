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
from src.models.monsters.MonsterManager import MonsterManager
import os
import json
import pickle
import signal
import atexit
from datetime import datetime
import logging


class Game:
    def __init__(self):
        self.preloader = PreLoader()
        self.player = Player()
        self.ATLAS = None  # Будет установлен после загрузки
        self.last_update_time = time.time()  # Для отслеживания времени для обновления локаций
        self.logger = Logger()  # Добавляем логгер
        self.npc_manager = NPCManager()
        self.npc_manager.load_npcs("resources/npcs")
        self.monster_manager = MonsterManager()
        self.monster_manager.load_monsters("resources/monsters")
        
        # Флаг для определения, новая это игра или загруженная
        self.is_new_game = True
        
        # Добавляем систему квестов
        self.tracked_quest_id = None  # ID отслеживаемого квеста
        self.active_quests = {}  # Активные квесты {quest_id: quest_object}
        self.completed_quests = {}  # Выполненные квесты {quest_id: quest_object}
        
        # Глоссарий для хранения информации о ресурсах и NPC
        self.glossary = {
            "resources": {},  # {resource_id: {"name": name, "description": desc, "locations": [loc1, loc2]}}
            "npcs": {},      # {npc_id: {"name": name, "description": desc, "location": loc}}
            "monsters": {}   # {monster_id: {"name": name, "description": desc, "locations": [loc1, loc2]}}
        }
        
        # Список посещенных локаций
        self.visited_locations = set()
        
        # Информация о отслеживаемых целях
        self.tracked_location = None
        self.tracked_target = None
        self.tracked_target_type = None  # "resource" или "npc"
        self.tracked_path = []  # Список локаций для посещения
        
        # Регистрируем обработчики для корректного сохранения при выходе
        self._register_exit_handlers()

    def preload(self):
        """Загружает все ресурсы игры"""
        self.preloader.load()
        self.ATLAS = self.preloader.get_atlas()
        
        # Для новой игры выполняем инициализацию
        if self.is_new_game:
            self.initialize_new_game()
        else:
            self.logger.info("Загружена существующая игра, пропускаем инициализацию новой игры")
        
        # Синхронизируем NPC с их локациями - выполняется для всех игр
        self.sync_npcs_with_locations()
        
        # Загружаем квесты из файлов - выполняется для всех игр
        self.logger.info("Загрузка квестов...")
        self.load_quests("resources/quests")
        self.logger.info(f"Загружено квестов: {len(self.all_quests)}")

    def initialize_new_game(self):
        """Инициализирует новую игру: устанавливает начальную локацию и выдает стартовые предметы"""
        self.logger.info("Инициализация новой игры...")

        # Установка начальной локации
        if len(self.ATLAS["LOCATIONS"]) > 0:
            # Сначала ищем локацию с флагом first_spawn_at
            spawn_location = None
            for location_id, location in self.ATLAS["LOCATIONS"].items():
                if location.first_spawn_at:
                    spawn_location = location
                    self.logger.info(f"Найдена локация для начального спавна: {location.name}")
                    break
            
            # Если не нашли локацию с first_spawn_at, используем первую по умолчанию
            if not spawn_location:
                first_location_id = next(iter(self.ATLAS["LOCATIONS"].keys()))
                spawn_location = self.ATLAS["LOCATIONS"][first_location_id]
                self.logger.info(f"Локация для начального спавна не найдена, используем первую: {spawn_location.name}")
            
            # Устанавливаем начальную локацию
            self.player.set_location(spawn_location)
            
            # Отмечаем начальную локацию как посещенную
            self.mark_location_as_visited(spawn_location.id)
        
        # Выдача стартовых предметов
        self.logger.info("Выдаем предметы по умолчанию игроку...")
        default_items_count = 0
        
        # Проходим по всем предметам и проверяем свойство default
        for item_id, item_data in self.ATLAS["ITEMS"].items_atlas.items():
            if item_data.get("default", False) == True:
                # Если у предмета default: true, создаем и добавляем его игроку
                item = self.create_inventory_item(item_id, 1)
                if item:
                    self.player.add_item(item)
                    self.logger.info(f"Выдан предмет по умолчанию: {item.name}")
                    default_items_count += 1
                    
        if default_items_count > 0:
            self.logger.info(f"Выдано {default_items_count} предметов по умолчанию")
        else:
            self.logger.info("Предметы по умолчанию не найдены")

    def sync_npcs_with_locations(self):
        """Синхронизирует NPC с их локациями
        
        Проходит по всем локациям и обновляет поле location_id в объектах NPC,
        если они добавлены в список npcs локации.
        """
        self.logger.info("Синхронизация NPC с локациями...")
        
        # Словарь для отслеживания синхронизированных NPC
        synced_npcs = {}
        
        # Проходим по всем локациям
        for location_id, location in self.ATLAS["LOCATIONS"].items():
            for npc_id in location.npcs:
                # Получаем объект NPC
                npc = self.npc_manager.get_npc(npc_id)
                if npc:
                    # Обновляем поле location_id
                    old_location = npc.location_id
                    npc.location_id = location_id
                    
                    # Обновляем информацию в глоссарии, если NPC уже добавлен
                    if npc_id in self.glossary["npcs"]:
                        self.glossary["npcs"][npc_id]["location"] = location_id
                    
                    # Логируем изменение
                    if old_location != location_id:
                        self.logger.info(f"NPC {npc.name} ({npc_id}) перемещен из локации {old_location} в {location_id}")
                    
                    # Отмечаем NPC как синхронизированный
                    synced_npcs[npc_id] = location_id
        
        # Подсчитываем и выводим статистику
        total_npcs = len(self.npc_manager.npcs)
        synced_count = len(synced_npcs)
        self.logger.info(f"Синхронизировано {synced_count} из {total_npcs} NPC")
        
        # Показываем предупреждение о NPC без локаций
        for npc_id, npc in self.npc_manager.npcs.items():
            if npc_id not in synced_npcs and not npc.location_id:
                self.logger.warning(f"NPC {npc.name} ({npc_id}) не привязан ни к одной локации")

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
        location_id = self.player.current_location
        return self.get_location(location_id)

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
        location = self.get_location(location_id)
        if not location:
            return []
            
        # Получаем список идентификаторов NPC из локации
        npc_ids = location.get_npcs()
        
        # Возвращаем объекты NPC
        return [self.get_npc(npc_id) for npc_id in npc_ids if self.get_npc(npc_id) is not None]

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
        """Загружает квесты из директории и всех её подпапок"""
        self.all_quests = {}  # {quest_id: quest_object}
        
        if not os.path.exists(quests_dir):
            self.logger.error(f"Директория квестов не найдена: {quests_dir}")
            return
        
        # Счетчики для логирования
        total_files_processed = 0
        total_quests_loaded = 0
        
        # Рекурсивно проходим по всем файлам в директории и её подпапках
        for root, dirs, files in os.walk(quests_dir):
            for file in files:
                # Проверяем, что это JSON файл
                if not file.endswith('.json'):
                    continue
                
                file_path = os.path.join(root, file)
                self.logger.info(f"Обрабатываем файл квестов: {file_path}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        quest_data = json.load(file)
                        
                        # Обрабатываем квесты из файла
                        if 'quests' in quest_data:
                            quests_in_file = 0
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
                                quests_in_file += 1
                                
                            total_quests_loaded += quests_in_file
                            self.logger.info(f"Загружено {quests_in_file} квестов из файла {file_path}")
                    
                    total_files_processed += 1
                except Exception as e:
                    self.logger.error(f"Ошибка при загрузке квестов из {file_path}: {e}")
        
        # Суммарная статистика
        self.logger.info(f"Всего обработано файлов квестов: {total_files_processed}")
        self.logger.info(f"Всего загружено квестов: {total_quests_loaded}")
        
        # Выводим список всех загруженных квестов для отладки
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
        """Добавляет NPC в глоссарий
        
        Args:
            npc_id: ID NPC
            
        Returns:
            bool: True, если добавление прошло успешно
        """
        # Получаем NPC
        npc = self.get_npc(npc_id)
        if not npc:
            self.logger.warning(f"Не удалось добавить NPC {npc_id} в глоссарий: NPC не найден")
            return False
        
        # Добавляем NPC в глоссарий
        self.glossary["npcs"][npc_id] = {
            "name": npc.name,
            "description": npc.description,
            "type": npc.type,
            "location": npc.location_id
        }
        
        # Проверяем и обновляем информацию о локации
        self.update_npc_glossary_location(npc_id)
        
        self.logger.info(f"NPC {npc.name} добавлен в глоссарий")
        return True

    def update_npc_glossary_location(self, npc_id):
        """Обновляет информацию о локации NPC в глоссарии
        
        Этот метод проверяет, есть ли у NPC локация. Если нет, пытается найти ее
        в списке локаций, где этот NPC указан, и обновляет информацию.
        
        Args:
            npc_id: ID NPC
            
        Returns:
            bool: True, если локация была обновлена, False в противном случае
        """
        if npc_id not in self.glossary["npcs"]:
            return False
        
        # Если у NPC уже есть локация, ничего не делаем
        if self.glossary["npcs"][npc_id]["location"]:
            return False
        
        # Ищем локацию NPC в списке локаций
        found_location = None
        for location_id, location in self.ATLAS["LOCATIONS"].items():
            if npc_id in location.npcs:
                found_location = location_id
                # Обновляем локацию NPC в глоссарии
                self.glossary["npcs"][npc_id]["location"] = found_location
                # Также обновляем локацию в объекте NPC
                npc = self.get_npc(npc_id)
                if npc:
                    npc.location_id = found_location
                self.logger.info(f"Обновлена локация для NPC {npc_id} в глоссарии: {found_location}")
                return True
            
        # Если локация не найдена
        self.logger.warning(f"Не удалось найти локацию для NPC {npc_id}")
        return False
        
    def add_monster_to_glossary(self, monster_id, location_id=None):
        """Добавляет монстра в глоссарий
        
        Args:
            monster_id: ID монстра
            location_id: ID локации, где встречен монстр (опционально)
            
        Returns:
            bool: True, если добавление прошло успешно
        """
        if "monsters" not in self.glossary:
            self.glossary["monsters"] = {}
            
        # Если монстр еще не в глоссарии, добавляем его
        if monster_id not in self.glossary["monsters"]:
            # Получаем информацию о монстре
            monster = self.get_monster(monster_id)
            if not monster:
                self.logger.warning(f"Не удалось добавить монстра {monster_id} в глоссарий: монстр не найден")
                return False
                
            # Создаем запись в глоссарии
            self.glossary["monsters"][monster_id] = {
                "name": monster.name,
                "description": monster.description,
                "level": monster.level,
                "locations": []
            }
            
            self.logger.info(f"Монстр {monster.name} добавлен в глоссарий")
            
        # Добавляем локацию, если она указана и не была добавлена ранее
        if location_id and location_id not in self.glossary["monsters"][monster_id]["locations"]:
            self.glossary["monsters"][monster_id]["locations"].append(location_id)
            self.logger.debug(f"Локация {location_id} добавлена для монстра {monster_id} в глоссарии")
            
        return True
        
    def get_glossary_resources(self):
        """Возвращает список ресурсов в глоссарии"""
        return self.glossary["resources"]
        
    def get_glossary_npcs(self):
        """Возвращает список NPC в глоссарии"""
        return self.glossary["npcs"]

    def get_glossary_monsters(self):
        """Возвращает список монстров в глоссарии"""
        if "monsters" in self.glossary:
            return self.glossary["monsters"]
        return {}

    def track_target(self, target_id, target_type):
        """Устанавливает отслеживаемую цель
        
        Args:
            target_id (str): ID ресурса, NPC или монстра для отслеживания
            target_type (str): Тип цели ('resource', 'npc' или 'monster')
            
        Returns:
            bool: True, если отслеживание установлено успешно
        """
        # Если цель уже отслеживается, снимаем отслеживание
        if self.tracked_target == target_id and self.tracked_target_type == target_type:
            self.untrack_target()
            return False
            
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
            current_location = self.player.current_location
            self.tracked_path = self.calculate_path(current_location, target_location)
            
            return True
            
        elif target_type == "npc" and target_id in self.glossary["npcs"]:
            # Если у NPC нет локации, нельзя отслеживать
            if not self.glossary["npcs"][target_id]["location"]:
                # Попробуем найти локацию NPC в списке локаций
                found_location = None
                for location_id, location in self.ATLAS["LOCATIONS"].items():
                    if target_id in location.npcs:
                        found_location = location_id
                        # Обновляем локацию NPC в глоссарии и в объекте NPC
                        self.glossary["npcs"][target_id]["location"] = found_location
                        npc = self.get_npc(target_id)
                        if npc:
                            npc.location_id = found_location
                        self.logger.info(f"Найдена локация для NPC {target_id}: {found_location}")
                        break
                
                # Если после поиска локация не найдена, отменяем отслеживание
                if not found_location:
                    self.logger.warning(f"Невозможно отслеживать NPC {target_id}: не указана локация")
                    return False
            
            self.tracked_target = target_id
            self.tracked_target_type = "npc"
            target_location = self.glossary["npcs"][target_id]["location"]
            self.tracked_location = target_location
            
            # Вычисляем маршрут от текущей локации до целевой
            current_location = self.player.current_location
            self.tracked_path = self.calculate_path(current_location, target_location)
            
            return True
            
        elif target_type == "monster" and target_id in self.glossary.get("monsters", {}):
            # Если у монстра нет локаций, нельзя отслеживать
            if not self.glossary["monsters"][target_id]["locations"]:
                return False
                
            self.tracked_target = target_id
            self.tracked_target_type = "monster"
            # Берем первую доступную локацию для монстра
            target_location = self.glossary["monsters"][target_id]["locations"][0]
            self.tracked_location = target_location
            
            # Вычисляем маршрут от текущей локации до целевой
            current_location = self.player.current_location
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
        elif self.tracked_target_type == "monster":
            result["name"] = self.glossary["monsters"][self.tracked_target]["name"]
            
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
            
        current_location = self.player.current_location
        
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
        if target_location == self.player.current_location:
            return []
            
        # Ищем путь от текущей локации до цели
        return self.calculate_path(self.player.current_location, target_location)
            
    def get_monster(self, monster_id):
        """Возвращает шаблон монстра по ID"""
        return self.monster_manager.get_monster(monster_id)
    
    def get_monsters_at_location(self, location_id):
        """Возвращает список монстров в указанной локации"""
        location = self.get_location(location_id)
        if not location:
            return {}
        
        monsters = {}
        for monster_id, count in location.monsters.items():
            if count > 0:
                monster = self.get_monster(monster_id)
                if monster:
                    monsters[monster_id] = {
                        "monster": monster,
                        "count": count
                    }
        
        return monsters
            
    def set_spawn_point(self, location_id):
        """Устанавливает указанную локацию как точку начального спавна
        
        Args:
            location_id: ID локации для спавна
            
        Returns:
            bool: True, если точка спавна успешно установлена
        """
        # Проверяем, существует ли локация
        location = self.get_location(location_id)
        if not location:
            self.logger.error(f"Не удалось установить точку спавна: локация {location_id} не найдена")
            return False
            
        # Сначала сбрасываем флаг у всех локаций
        for loc_id, loc in self.ATLAS["LOCATIONS"].items():
            loc.first_spawn_at = False
            
        # Устанавливаем флаг у новой точки спавна
        location.first_spawn_at = True
        self.logger.info(f"Точка начального спавна установлена: {location.name}")
        
        return True
            
    def mark_location_as_visited(self, location_id):
        """Отмечает локацию как посещенную игроком
        
        Args:
            location_id (str): ID локации
            
        Returns:
            bool: True, если локация была добавлена впервые
        """
        if location_id not in self.visited_locations:
            self.visited_locations.add(location_id)
            self.logger.info(f"Локация {location_id} отмечена как посещенная")
            return True
        return False
        
    def is_location_visited(self, location_id):
        """Проверяет, была ли локация посещена игроком
        
        Args:
            location_id (str): ID локации
            
        Returns:
            bool: True, если локация была посещена
        """
        return location_id in self.visited_locations
            
    def _register_exit_handlers(self):
        """Регистрирует обработчики событий для сохранения при выходе"""
        # При нормальном завершении
        atexit.register(self.auto_save_game)
        
        # Обработка сигналов завершения (CTRL+C и др.)
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            # В Windows нет SIGQUIT
            if hasattr(signal, 'SIGQUIT'):
                signal.signal(signal.SIGQUIT, self._signal_handler)
        except (AttributeError, ValueError) as e:
            self.logger.warning(f"Не удалось зарегистрировать обработчик сигнала: {e}")
    
    def _signal_handler(self, sig, frame):
        """Обработчик сигналов для корректного сохранения при выходе"""
        self.logger.info(f"Получен сигнал {sig}, сохранение игры перед выходом...")
        self.auto_save_game()
        # После сохранения выходим
        exit(0)
    
    def save_game(self, save_name=None):
        """Сохраняет текущее состояние игры
        
        Args:
            save_name: Название сохранения (если None, используется имя игрока)
            
        Returns:
            bool: True если сохранение успешно, False в противном случае
        """
        try:
            # Если имя не передано, используем имя игрока
            if save_name is None:
                save_name = self.player.name
            
            # Создаем директорию saves, если не существует
            base_save_dir = "resources/saves"
            os.makedirs(base_save_dir, exist_ok=True)
            
            # Создаем директорию сохранения
            save_dir = os.path.join(base_save_dir, save_name)
            os.makedirs(save_dir, exist_ok=True)
            
            # Путь к файлам сохранения
            world_file = os.path.join(save_dir, "world.dat")
            meta_file = os.path.join(save_dir, "save_info.json")
            
            # Получаем текущую локацию
            current_location_name = "Неизвестно"
            current_location_id = "unknown"
            if self.player.current_location:
                # Проверяем, является ли current_location строкой или объектом
                if isinstance(self.player.current_location, str):
                    current_location_id = self.player.current_location
                    location = self.get_location(current_location_id)
                    if location:
                        current_location_name = location.name
                else:
                    # Если это объект Location
                    current_location_id = self.player.current_location.id
                    current_location_name = self.player.current_location.name
            
            # Сохраняем метаданные (только простые типы данных)
            meta_data = {
                "playername": self.player.name,
                "player_level": self.player.level,
                "current_location": current_location_name,
                "current_location_id": current_location_id, 
                "worldfile": "world.dat",
                "save_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "game_version": "1.0"  # Версия игры, при необходимости можно обновлять
            }
            
            # Записываем метаданные
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=4)
            
            # Сохраняем состояние игры через pickle (бинарная сериализация)
            with open(world_file, 'wb') as f:
                pickle.dump(self, f)
                
            self.logger.info(f"Игра успешно сохранена в {save_dir}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении игры: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def auto_save_game(self):
        """Автоматически сохраняет игру при выходе"""
        try:
            if hasattr(self, 'player') and self.player:
                # Создаем автосохранение с меткой времени
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_name = f"{self.player.name}_autosave_{timestamp}"
                self.logger.info(f"Выполняется автосохранение: {save_name}")
                result = self.save_game(save_name)
                if result:
                    self.logger.info(f"Автосохранение успешно создано: {save_name}")
                else:
                    self.logger.error("Не удалось создать автосохранение!")
                return result
            else:
                self.logger.warning("Автосохранение не выполнено: player не инициализирован")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка при автосохранении: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def get_saves_list():
        """Получает список всех сохранений
        
        Returns:
            list: Список сохранений с метаданными
        """
        saves_list = []
        base_save_dir = "resources/saves"
        
        # Проверяем, существует ли директория
        if not os.path.exists(base_save_dir):
            return saves_list
        
        # Проходим по всем папкам в директории saves
        for save_folder in os.listdir(base_save_dir):
            save_path = os.path.join(base_save_dir, save_folder)
            
            # Проверяем, что это директория
            if not os.path.isdir(save_path):
                continue
                
            # Путь к файлу с метаданными
            meta_file = os.path.join(save_path, "save_info.json")
            
            # Если файл с метаданными существует, загружаем информацию
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        meta_data = json.load(f)
                        
                    # Проверяем, существует ли файл с сохранением мира
                    worldfile = meta_data.get("worldfile", "world.dat")
                    world_path = os.path.join(save_path, worldfile)
                    
                    if os.path.exists(world_path):
                        # Добавляем полный путь к сохранению
                        meta_data["save_path"] = save_path
                        saves_list.append(meta_data)
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Ошибка при загрузке метаданных сохранения {save_folder}: {str(e)}")
        
        # Сортируем сохранения по времени (от новых к старым)
        saves_list.sort(key=lambda x: x.get("save_time", ""), reverse=True)
        return saves_list
    
    @staticmethod
    def load_game(save_path):
        """Загружает игру из сохранения
        
        Args:
            save_path: Путь к директории с сохранением
            
        Returns:
            Game: Загруженный объект игры или None в случае ошибки
        """
        try:
            # Путь к файлу сохранения мира
            world_file = os.path.join(save_path, "world.dat")
            
            # Проверяем существование файла
            if not os.path.exists(world_file):
                logger = logging.getLogger(__name__)
                logger.error(f"Файл сохранения не найден: {world_file}")
                return None
            
            # Загружаем состояние игры
            with open(world_file, 'rb') as f:
                game = pickle.load(f)
                
            logger = logging.getLogger(__name__)
            logger.info(f"Игра успешно загружена из {save_path}")
            # Перерегистрируем обработчики событий для нового объекта
            game._register_exit_handlers()
            # Помечаем, что это загруженная игра
            game.is_new_game = False
            return game
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка при загрузке игры: {str(e)}")
            return None
            
    def __getstate__(self):
        """Метод для сериализации объекта Game через pickle
        
        Returns:
            dict: Состояние объекта для сериализации
        """
        # Получаем все атрибуты объекта
        state = self.__dict__.copy()
        
        # Удаляем несериализуемые объекты (например, логгер)
        # А также объекты, которые не нужно сохранять
        if 'logger' in state:
            del state['logger']
            
        return state
    
    def __setstate__(self, state):
        """Метод для десериализации объекта Game через pickle
        
        Args:
            state: Состояние объекта из pickle
        """
        # Восстанавливаем состояние объекта
        self.__dict__.update(state)
        
        # Создаем новый логгер
        self.logger = logging.getLogger(__name__)
        
        # Устанавливаем флаг загруженной игры
        self.is_new_game = False
        
        # Перерегистрируем обработчики сигналов
        self._register_exit_handlers()
            