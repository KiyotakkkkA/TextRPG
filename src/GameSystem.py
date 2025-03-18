from src.loaders.ItemsLoader import ItemsLoader
from src.utils.Logger import Logger
from src.models.Player import Player
from src.utils.PreLoader import PreLoader
from src.EventSystem import get_event_system, define_event

class GameSystem:
    def __init__(self):
        self.preloader = PreLoader()
        self.logger = Logger()
        self.player = Player(self, "Player")
        self.ATLAS = None
        self.event_system = get_event_system()
        
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

    def preload(self):
        """Загружает все ресурсы игры"""
        self.preloader.load()
        self.ATLAS = self.preloader.get_atlas()
    
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
