from src.loaders.ItemsLoader import ItemsLoader
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
