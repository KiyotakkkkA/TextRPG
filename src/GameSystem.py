from src.loaders.ItemsLoader import ItemsLoader
from src.loaders.LocationsLoader import LocationsLoader
from src.loaders.SkillsLoader import SkillsLoader
from src.utils.Logger import Logger
from src.models.Player import Player
from src.utils.PreLoader import PreLoader
from src.utils.PropertiesLoader import get_version_properties
from src.EventSystem import get_event_system, define_event
from src.models.interfaces import Serializable

class GameSystem(Serializable):
    def __init__(self):
        """
        Инициализирует игровую систему.
        """
        # Устанавливаем логгер
        self.logger = Logger()
        
        # Создаем систему событий
        self.event_system = get_event_system()
        self.register_events()
        
        # Создаем преднагрузчик данных (ATLAS)
        self.preloader = PreLoader()
        
        # Инициализируем игровой мир
        self.current_location_id = None
        self.current_region_id = None  # Текущий регион
        
        # Создаем загрузчик навыков
        self.skills_loader = SkillsLoader()
        
        # Создаем игрока
        self.player = Player(self, "Player")
        
        # Загружаем информацию о версии
        self.version_props = get_version_properties()
        self.game_version = self.version_props.get("game.version", "0.1.0")
        self.game_stage = self.version_props.get("game.stage", "Alpha")
        self.engine_version = self.version_props.get("engine.version", "1.0.0")
        self.engine_name = self.version_props.get("engine.name", "TextRPG Engine")
        
        # Логируем информацию о версии
        self.logger.info(f"Инициализация GameSystem - версия игры: v{self.game_version} {self.game_stage}")
        self.logger.info(f"Используется движок: {self.engine_name} v{self.engine_version}")

    def register_events(self):
        """Регистрирует все события в системе с их документацией"""
        self.event_system.register_event(
            event_name="player_took_item",
            description="Вызывается когда игрок получает предмет в инвентарь",
            params={
                "item_data": "Данные предмета со счетчиком количества (словарь)"
            },
            tags=["player", "inventory", "items"]
        )
        
        # Подписываемся на событие получения предмета для обработки улучшений навыков
        self.event_system.subscribe("player_took_item", self.process_item_skill_improvements)
        
        # Другие события
        self.event_system.register_event(
            event_name="player_dropped_item",
            description="Вызывается когда игрок выбрасывает предмет из инвентаря",
            params={
                "item_id": "ID предмета",
                "count": "Количество выброшенных предметов"
            },
            tags=["player", "inventory", "items"]
        )
        
        # Добавляем событие обновления версии
        self.event_system.register_event(
            event_name="game_version_check",
            description="Вызывается для проверки актуальности версии игры",
            params={
                "current_version": "Текущая версия игры",
                "latest_version": "Последняя доступная версия игры",
                "is_update_required": "Требуется ли обновление"
            },
            tags=["system", "version"]
        )
        
        # Новые события для локаций
        self.event_system.register_event(
            event_name="player_entered_location",
            description="Вызывается когда игрок входит в новую локацию",
            params={
                "location_id": "ID локации",
                "location_name": "Название локации",
                "previous_location_id": "ID предыдущей локации"
            },
            tags=["player", "location", "movement"]
        )
        
        self.event_system.register_event(
            event_name="player_collected_resource",
            description="Вызывается когда игрок собирает ресурс",
            params={
                "resource_id": "ID ресурса",
                "resource_name": "Название ресурса",
                "amount": "Количество собранного ресурса",
                "location_id": "ID локации, где собран ресурс"
            },
            tags=["player", "resources", "collecting"]
        )
        
        self.event_system.register_event(
            event_name="location_resources_respawned",
            description="Вызывается когда ресурсы на локации обновляются",
            params={
                "location_id": "ID локации",
                "resources": "Список доступных ресурсов"
            },
            tags=["location", "resources"]
        )
        
        # События для системы навыков
        self.event_system.register_event(
            event_name="player_unlocked_skill",
            description="Вызывается, когда игрок разблокирует новый навык",
            params={
                "skill": "Информация о навыке (словарь)"
            },
            tags=["player", "skills", "progression"]
        )
        
        self.event_system.register_event(
            event_name="player_skill_levelup",
            description="Вызывается, когда навык игрока повышает уровень",
            params={
                "skill": "Информация о навыке (словарь)",
                "new_level": "Новый уровень навыка"
            },
            tags=["player", "skills", "progression"]
        )
        
        self.event_system.register_event(
            event_name="player_used_skill",
            description="Вызывается, когда игрок использует навык",
            params={
                "skill": "Информация о навыке (словарь)",
                "args": "Позиционные аргументы для навыка",
                "kwargs": "Именованные аргументы для навыка"
            },
            tags=["player", "skills", "action"]
        )
        
    def preload(self):
        """
        Загружает все необходимые данные для игры.
        """
        self.logger.info("GameSystem: Загрузка данных игры...")
        
        # Загружаем навыки
        self.logger.info("GameSystem: Загрузка навыков...")
        self.skills_loader.load()
        
        # Загружаем остальные данные
        self.preloader.load()
        
        self.logger.info("GameSystem: Загрузка данных завершена!")
    
    def get_skills_loader(self) -> SkillsLoader:
        """
        Возвращает загрузчик навыков.
        
        Returns:
            SkillsLoader: Загрузчик навыков
        """
        return self.skills_loader
    
    def get_skill(self, skill_id: str):
        """
        Возвращает навык по его ID.
        
        Args:
            skill_id (str): ID навыка
            
        Returns:
            SimpleSkill: Навык или None, если навык не найден
        """
        return self.skills_loader.get_skill(skill_id)
    
    def get_all_skills(self):
        """
        Возвращает словарь всех навыков.
        
        Returns:
            dict: Словарь всех навыков (id -> навык)
        """
        return self.skills_loader.get_all_skills()
    
    def get_skill_group(self, group_id: str):
        """
        Возвращает группу навыков по её ID.
        
        Args:
            group_id (str): ID группы
            
        Returns:
            SkillGroup: Группа навыков или None, если группа не найдена
        """
        return self.skills_loader.get_group(group_id)
    
    def get_all_skill_groups(self):
        """
        Возвращает словарь всех групп навыков.
        
        Returns:
            dict: Словарь всех групп навыков (id -> группа)
        """
        return self.skills_loader.get_all_groups()
    
    def get_skills_by_group(self, group_id: str):
        """
        Возвращает список навыков в указанной группе.
        
        Args:
            group_id (str): ID группы
            
        Returns:
            list: Список навыков в группе
        """
        return self.skills_loader.get_skills_by_group(group_id)
    
    def get_ordered_skill_groups(self):
        """
        Возвращает список групп навыков, отсортированный по порядку отображения.
        
        Returns:
            list: Отсортированный список групп
        """
        return self.skills_loader.get_ordered_groups()
    
    def get_version_info(self):
        """Возвращает словарь с информацией о версии игры и движка"""
        return {
            "game_version": self.game_version,
            "game_stage": self.game_stage,
            "engine_version": self.engine_version,
            "engine_name": self.engine_name,
            "full_game_version": f"v{self.game_version} {self.game_stage}",
            "full_engine_version": f"{self.engine_name} v{self.engine_version}"
        }
    
    def get_current_location(self):
        """
        Возвращает текущую локацию.
        
        Returns:
            Location: Текущая локация или None, если локация не задана
        """
        if not self.current_location_id:
            return None
        
        return self.get_location(self.current_location_id)
    
    def get_current_region(self):
        """
        Возвращает текущий регион.
        
        Returns:
            Region: Текущий регион или None, если регион не задан
        """
        if not self.current_region_id:
            # Пытаемся определить регион по текущей локации
            if self.current_location_id:
                return self.get_region_for_location(self.current_location_id)
            return None
        
        return self.get_region(self.current_region_id)
    
    def get_skill(self, skill_id):
        """
        Возвращает навык по его ID.
        
        Args:
            skill_id (str): ID навыка
            
        Returns:
            SimpleSkill: Навык или None, если навык не найден
        """
        return self.skills_loader.get_skill(skill_id)
    
    def get_location(self, location_id):
        """
        Возвращает локацию по её ID.
        
        Args:
            location_id (str): ID локации
            
        Returns:
            Location: Локация или None, если локация не найдена
        """
        locations = self.preloader.ATLAS["LOCATIONS"]
        return locations.get_location(location_id)
    
    def get_region(self, region_id):
        """
        Возвращает регион по его ID.
        
        Args:
            region_id (str): ID региона
            
        Returns:
            Region: Регион или None, если регион не найден
        """
        regions = self.preloader.ATLAS["REGIONS"]
        return regions.get_region(region_id)
    
    def get_region_for_location(self, location_id):
        """
        Возвращает регион, в котором находится указанная локация.
        
        Args:
            location_id (str): ID локации
            
        Returns:
            Region: Регион, в котором находится локация, или None
        """
        regions = self.preloader.ATLAS["REGIONS"]
        return regions.get_region_for_location(location_id)
    
    def get_all_locations(self):
        """
        Возвращает словарь всех локаций.
        
        Returns:
            dict: Словарь всех локаций
        """
        locations = self.preloader.ATLAS["LOCATIONS"]
        return locations.get_all_locations()
    
    def get_all_regions(self):
        """
        Возвращает словарь всех регионов.
        
        Returns:
            dict: Словарь всех регионов
        """
        regions = self.preloader.ATLAS["REGIONS"]
        return regions.get_all_regions()
    
    def change_location(self, location_id):
        """
        Перемещает игрока в новую локацию.
        
        Args:
            location_id (str): ID новой локации
            
        Returns:
            bool: True, если перемещение успешно
        """
        # Проверяем, существует ли локация
        new_location = self.get_location(location_id)
        if not new_location:
            self.logger.error(f"Локация {location_id} не найдена!")
            return False
        
        # Проверяем, можно ли переместиться из текущей локации
        current_location = self.get_current_location()
        if current_location:
            # Проверяем, есть ли соединение между локациями
            can_move = False
            for connection in current_location.connections:
                # Проверяем, является ли соединение словарем или строкой
                if isinstance(connection, dict):
                    conn_id = connection.get("id", "").lower()
                else:
                    conn_id = str(connection).lower()
                    
                if conn_id == location_id.lower():
                    # Проверяем требования для использования соединения
                    if current_location.can_use_connection(location_id, self.player, self):
                        can_move = True
                        break
                    else:
                        self.logger.error(f"Вы не соответствуете требованиям для перехода в {new_location.name}!")
                        return False
            
            if not can_move:
                self.logger.error(f"Невозможно перейти из {current_location.id} в {location_id}!")
                return False
        
        # Проверяем, есть ли требования для доступа к новой локации
        if not new_location.can_access(self.player, self):
            self.logger.error(f"Вы не соответствуете требованиям для доступа в {new_location.name}!")
            return False
        
        # Запоминаем предыдущую локацию для события
        previous_location_id = self.current_location_id
        
        # Меняем текущую локацию
        self.current_location_id = location_id
        
        # Определяем и устанавливаем текущий регион
        new_region = self.get_region_for_location(location_id)
        if new_region:
            previous_region_id = self.current_region_id
            self.current_region_id = new_region.id
            
            # Если сменился регион, вызываем событие
            if previous_region_id != self.current_region_id:
                self.event_system.emit(
                    "player_entered_region",
                    self.current_region_id,
                    new_region.name,
                    previous_region_id
                )
        
        # Вызываем событие перемещения
        self.event_system.emit(
            "player_entered_location",
            location_id,
            new_location.name,
            previous_location_id
        )
        
        self.logger.info(f"Игрок перешёл в локацию: {new_location.name}")
        return True
    
    def change_region(self, region_id):
        """
        Изменяет текущий регион и перемещает игрока в стартовую локацию региона.
        
        Args:
            region_id (str): ID нового региона
            
        Returns:
            bool: True, если изменение региона прошло успешно
        """
        # Проверяем существование региона
        new_region = self.get_region(region_id)
        if not new_region:
            self.logger.error(f"Регион {region_id} не найден!")
            return False
        
        # Проверяем требования для доступа к региону
        if not new_region.can_access(self.player, self):
            self.logger.error(f"Вы не соответствуете требованиям для доступа в регион {new_region.name}!")
            return False
            
        # Проверяем существование стартовой локации
        starting_location_id = new_region.starting_location
        if not starting_location_id:
            # Если стартовая локация не указана, берем первую локацию из списка
            if new_region.locations:
                starting_location_id = new_region.locations[0]
            else:
                self.logger.error(f"В регионе {region_id} нет локаций!")
                return False
        
        # Проверяем, существует ли стартовая локация
        starting_location = self.get_location(starting_location_id)
        if not starting_location:
            self.logger.error(f"Стартовая локация {starting_location_id} в регионе {region_id} не найдена!")
            return False
            
        # Меняем текущий регион и перемещаем игрока в стартовую локацию
        old_region_id = self.current_region_id
        self.current_region_id = region_id
        self.current_location_id = starting_location_id
        
        # Вызываем событие смены региона
        self.event_system.emit("region_changed", {
            "old_region_id": old_region_id,
            "new_region_id": region_id,
            "player": self.player
        })
        
        # Вызываем событие входа в новую локацию
        self.event_system.emit("enter_location", {
            "location": starting_location,
            "player": self.player
        })
        
        self.logger.info(f"Игрок перемещен в регион {new_region.name}, локация: {starting_location.name}")
        return True
    
    def collect_resource(self, resource_id, amount=None):
        """
        Собирает ресурс с текущей локации.
        
        Args:
            resource_id: ID ресурса для сбора
            amount: Количество ресурса для сбора (если None, собирает всё доступное количество)
            
        Returns:
            int: Количество собранного ресурса
        """
        try:
            # Получаем текущую локацию
            location = self.get_current_location()
            if not location:
                return 0
                
            # Получаем данные о ресурсе
            item_data = self.get_item(resource_id)
            if not item_data:
                return 0
                
            # Проверяем требования для сбора ресурса
            if not self.check_resource_requirements(resource_id):
                self.logger.info(f"Не удалось собрать ресурс {resource_id} - не выполнены требования")
                return 0
                
            # Определяем количество для сбора
            if amount is None:
                # Если количество не указано, собираем все доступные ресурсы
                amount = location.available_resources.get(resource_id, 0)
            
            # Собираем ресурс
            collected = location.collect_resource(resource_id, amount)
            if collected <= 0:
                return 0
                
            # Получаем название ресурса
            resource_name = item_data.get("name", resource_id)
            
            # Добавляем ресурс в инвентарь игрока
            self.player.add_item_by_id(resource_id, collected)
            
            # Отправляем событие сбора ресурса
            self.event_system.emit("player_collected_resource", {
                "resource_id": resource_id,
                "resource_name": resource_name,
                "amount": collected,
                "location_id": location.id
            })
            
            # Обрабатываем навыки, связанные с этим предметом
            self.process_item_skill_improvements(item_data)
            return collected
            
        except Exception as e:
            self.logger.error(f"Ошибка при сборе ресурса {resource_id}: {str(e)}", exc_info=True)
            return 0
    
    @define_event(
        name="player_level_up",
        description="Вызывается при повышении уровня игрока",
        params={
            "old_level": "Предыдущий уровень игрока",
            "new_level": "Новый уровень игрока",
            "stats_increase": "Увеличение характеристик (словарь)"
        },
        example="emit('player_level_up', 1, 2, {'strength': 1, 'vitality': 2})",
        tags=["player", "progression"]
    )
    def handle_player_level_up(self, old_level, new_level, stats_increase):
        """Обработчик события повышения уровня игрока"""
        self.logger.info(f"Игрок повысил уровень с {old_level} до {new_level}!")
        # Логика обработки повышения уровня
        
        # Обновляем доступные навыки
        self.player.update_skills()
        
    def get_item(self, itemID: str):
        """Возвращает данные предмета по его ID"""
        if not itemID:
            return None
        
        # Проверяем регистр
        if itemID.lower() in self.preloader.ATLAS["ITEMS"]:
            return self.preloader.ATLAS["ITEMS"][itemID.lower()]
        elif itemID in self.preloader.ATLAS["ITEMS"]:
            return self.preloader.ATLAS["ITEMS"][itemID]
        
        return None

    def update(self, dt):
        """
        Обновляет состояние игры.
        
        Args:
            dt (float): Время, прошедшее с последнего обновления
        """
        # Обновляем локации (респавн ресурсов)
        if "LOCATIONS" in self.preloader.ATLAS:
            self.preloader.ATLAS["LOCATIONS"].update_all_locations()
    
    def save_game(self, save_name: str) -> bool:
        """
        Сохраняет текущее состояние игры в файл.
        
        Args:
            save_name (str): Имя сохранения (без расширения)
            
        Returns:
            bool: True, если сохранение прошло успешно
        """
        try:
            # Отсоединяем некоторые несериализуемые объекты перед сохранением
            
            # Сохраняем ссылки на несериализуемые объекты, чтобы потом восстановить
            original_logger = self.logger
            original_event_system = self.event_system
            original_skills_loader = self.skills_loader
            
            # Временно устанавливаем None для несериализуемых объектов
            self.logger = None
            self.event_system = None
            self.skills_loader = None
            
            # Также отключаем ссылки на game_system в объектах
            original_player_game = self.player.game
            original_player_game_system = self.player.game_system
            self.player.game = None
            self.player.game_system = None
            
            # Используем метод serialize из Serializable для сохранения
            save_path = f"saves/{save_name}.pickle"
            self.serialize(save_path)
            
            # Восстанавливаем ссылки
            self.logger = original_logger
            self.event_system = original_event_system
            self.skills_loader = original_skills_loader
            self.player.game = original_player_game
            self.player.game_system = original_player_game_system
            
            self.logger.info(f"Игра успешно сохранена в {save_path}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при сохранении игры: {str(e)}")
            return False
    
    @classmethod
    def load_game(cls, save_name: str) -> 'GameSystem':
        """
        Загружает игру из файла сохранения.
        
        Args:
            save_name (str): Имя сохранения (без расширения)
            
        Returns:
            GameSystem: Загруженное состояние игры или None, если загрузка не удалась
        """
        try:
            # Десериализуем объект из файла
            save_path = f"saves/{save_name}.pickle"
            game_system = cls.deserialize(filename=save_path)
            
            # Восстанавливаем ссылки на несериализуемые объекты
            game_system.logger = Logger()
            game_system.event_system = get_event_system()
            game_system.skills_loader = SkillsLoader()
            game_system.skills_loader.load()
            
            # Восстанавливаем ссылки в объектах
            game_system.player.game = game_system
            game_system.player.game_system = game_system
            
            # Регистрируем события
            game_system.register_events()
            
            # Инициализация окончена
            game_system.logger.info(f"Игра успешно загружена из {save_path}")
            return game_system
        except Exception as e:
            print(f"Ошибка при загрузке игры: {str(e)}")
            return None

    def process_item_skill_improvements(self, item_data):
        """
        Обрабатывает улучшения навыков при получении предмета.
        Если предмет имеет блок IMPROVES с указанием навыков и опыта,
        то добавляет соответствующее количество опыта каждому навыку.
        
        Args:
            item_data: Данные предмета со счетчиком количества
        """
        if not item_data or not isinstance(item_data, dict):
            return
        
        # Получаем ID предмета и количество
        item_id = item_data.get("id")
        count = item_data.get("count", 1)
        
        if not item_id:
            return
        
        # Получаем полные данные о предмете
        item_full_data = self.get_item(item_id)
        if not item_full_data:
            return
        
        # Проверяем наличие блока улучшений
        improves = item_full_data.get("improves")
        if not improves:
            return
        
        # Обрабатываем улучшения навыков
        skill_improvements = improves.get("improves_skills")
        if not skill_improvements:
            return
        
        self.logger.info(f"Обрабатываем улучшения навыков для предмета {item_id} (x{count})")
        
        # Для каждого навыка добавляем опыт
        for skill_id, exp_amount in skill_improvements.items():
            # Умножаем опыт на количество предметов
            total_exp = exp_amount * count
            
            # Добавляем опыт навыку
            level_up = self.player.add_skill_experience(skill_id, total_exp)
            
            skill_name = skill_id
            skill = self.player.get_skill(skill_id)
            if skill:
                skill_name = skill.name
            
            self.logger.info(f"Добавлено {total_exp} опыта навыку {skill_name}")
            
            # Если произошло повышение уровня, логируем это
            if level_up:
                self.logger.info(f"Повышен уровень навыка {skill_name} до {skill.level}")

    def check_resource_requirements(self, resource_id: str) -> bool:
        """
        Проверяет, выполняются ли требования для сбора ресурса.
        
        Args:
            resource_id (str): ID ресурса
            
        Returns:
            bool: True, если требования выполнены, иначе False
        """
        # Получаем данные о ресурсе
        item_data = self.get_item(resource_id)
        if not item_data:
            return False
            
        # Получаем текущую локацию
        location = self.get_current_location()
        if not location:
            return False
            
        # Проверяем требования, если они есть
        if "requires" in item_data:
            return location.check_requirements(item_data["requires"], self.player, self)
            
        # Если требования не указаны, считаем их выполненными
        return True