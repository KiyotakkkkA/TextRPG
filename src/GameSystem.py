from src.loaders.ItemsLoader import ItemsLoader
from src.loaders.LocationsLoader import LocationsLoader
from src.utils.Logger import Logger
from src.models.Player import Player
from src.utils.PreLoader import PreLoader
from src.utils.PropertiesLoader import get_version_properties
from src.EventSystem import get_event_system, define_event

class GameSystem:
    def __init__(self):
        self.preloader = PreLoader()
        self.logger = Logger()
        self.player = Player(self, "Player")
        self.ATLAS = None
        self.event_system = get_event_system()
        
        # Загружаем информацию о версии
        self.version_props = get_version_properties()
        self.game_version = self.version_props.get("game.version", "0.1.0")
        self.game_stage = self.version_props.get("game.stage", "Alpha")
        self.engine_version = self.version_props.get("engine.version", "1.0.0")
        self.engine_name = self.version_props.get("engine.name", "TextRPG Engine")
        
        # Текущая локация игрока (по умолчанию: "forest")
        self.current_location_id = "forest"
        
        # Логируем информацию о версии
        self.logger.info(f"Инициализация GameSystem - версия игры: v{self.game_version} {self.game_stage}")
        self.logger.info(f"Используется движок: {self.engine_name} v{self.engine_version}")
        
        # Регистрируем события
        self.register_events()

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

    def preload(self):
        """Загружает все ресурсы игры"""
        self.preloader.load()
        self.ATLAS = self.preloader.get_atlas()
    
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
        Возвращает текущую локацию игрока.
        
        Returns:
            Location: Объект текущей локации
        """
        return self.get_location(self.current_location_id)
    
    def get_location(self, location_id):
        """
        Возвращает локацию по ID.
        
        Args:
            location_id (str): ID локации
            
        Returns:
            Location: Объект локации или None
        """
        if "LOCATIONS" not in self.ATLAS:
            self.logger.error("Атлас локаций не загружен!")
            return None
        
        locations_loader = self.ATLAS["LOCATIONS"]
        return locations_loader.get_location(location_id)
    
    def get_all_locations(self):
        """
        Возвращает словарь всех доступных локаций.
        
        Returns:
            Dict[str, Location]: Словарь с объектами локаций
        """
        if "LOCATIONS" not in self.ATLAS:
            self.logger.error("Атлас локаций не загружен!")
            return {}
        
        locations_loader = self.ATLAS["LOCATIONS"]
        return locations_loader.get_all_locations()
    
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
                    can_move = True
                    break
            
            if not can_move:
                self.logger.error(f"Невозможно перейти из {current_location.id} в {location_id}!")
                return False
        
        # Запоминаем предыдущую локацию для события
        previous_location_id = self.current_location_id
        
        # Меняем текущую локацию
        self.current_location_id = location_id
        
        # Вызываем событие перемещения
        self.event_system.emit(
            "player_entered_location",
            location_id,
            new_location.name,
            previous_location_id
        )
        
        self.logger.info(f"Игрок перешёл в локацию: {new_location.name}")
        return True
    
    def collect_resource(self, resource_id, amount=1):
        """
        Собирает ресурс с текущей локации и добавляет в инвентарь игрока.
        
        Args:
            resource_id (str): ID ресурса
            amount (int): Количество для сбора
            
        Returns:
            int: Фактическое количество собранного ресурса
        """
        current_location = self.get_current_location()
        if not current_location:
            self.logger.error("Текущая локация не определена!")
            return 0
        
        # Получаем данные предмета, чтобы узнать его имя для события
        item_data = self.get_item(resource_id)
        if not item_data:
            self.logger.error(f"Предмет {resource_id} не найден!")
            return 0
        
        # Собираем ресурс с локации
        collected = current_location.collect_resource(resource_id, amount)
        if collected <= 0:
            self.logger.error(f"Ресурс {resource_id} недоступен на локации {current_location.id}!")
            return 0
        
        # Добавляем в инвентарь
        self.player.add_item_by_id(resource_id, collected)
        
        # Вызываем событие сбора ресурса
        self.event_system.emit(
            "player_collected_resource",
            resource_id,
            item_data.get("name", resource_id),
            collected,
            current_location.id
        )
        
        self.logger.info(f"Игрок собрал {collected} {item_data.get('name', resource_id)}")
        return collected
    
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
        
    def get_item(self, itemID: str):
        """Возвращает данные предмета по его ID"""
        if not itemID:
            return None
        
        # Проверяем регистр
        if itemID.lower() in self.ATLAS["ITEMS"]:
            return self.ATLAS["ITEMS"][itemID.lower()]
        elif itemID in self.ATLAS["ITEMS"]:
            return self.ATLAS["ITEMS"][itemID]
        
        return None
    
    def update(self, dt):
        """
        Обновляет состояние игры.
        
        Args:
            dt (float): Время, прошедшее с последнего обновления
        """
        # Обновляем локации (респавн ресурсов)
        if "LOCATIONS" in self.ATLAS:
            self.ATLAS["LOCATIONS"].update_all_locations()
