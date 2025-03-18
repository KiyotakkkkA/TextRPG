"""
Готовые экраны для движка рендеринга.
Включает в себя различные типы экранов: главное меню, игровой экран и т.д.
"""

from typing import List, Dict, Any, Optional, Union, Callable
from src.render.core import Screen, UIElement, ConsoleHelper, InputHandler, Keys, Color
from src.render.ui import Panel, Label, Button, MenuItem, Menu, TextBox
from src.utils.PropertiesLoader import get_version_properties

class MainMenuScreen(Screen):
    """
    Экран главного меню игры.
    """
    def __init__(self, engine, title: str = "TextRPG"):
        super().__init__(engine)
        self.title = title
        # Загружаем свойства версии
        self.version_props = get_version_properties()
        self.setup_ui()
    
    def setup_ui(self):
        """
        Настраивает UI элементы экрана.
        """
        # Очищаем существующие элементы
        self.children = []
        
        # Получаем размеры терминала
        width, height = ConsoleHelper.get_terminal_size()
        
        # Создаем фоновую панель
        background = Panel(0, 0, width, height, "", False, "", Color.BG_BLACK)
        self.add_child(background)
        
        # Заголовок игры
        title_y = height // 4
        title_label = Label(0, title_y, "", Color.BRIGHT_CYAN)
        title_label.set_text(ConsoleHelper.center_text(f"=== {self.title} ===", width))
        self.add_child(title_label)
        
        # Версия игры (из файла свойств)
        game_version = self.version_props.get("game.version", "0.1.0")
        game_stage = self.version_props.get("game.stage", "Alpha")
        engine_version = self.version_props.get("engine.version", "1.0.0")
        engine_name = self.version_props.get("engine.name", "TextRPG Engine")
        
        version_text = f"v{game_version} {game_stage}"
        version_label = Label(0, title_y + 1, "", Color.BRIGHT_BLACK)
        version_label.set_text(ConsoleHelper.center_text(version_text, width))
        self.add_child(version_label)
        
        # Информация о движке (опционально)
        engine_text = f"Powered by {engine_name} v{engine_version}"
        engine_label = Label(0, title_y + 2, "", Color.BRIGHT_BLACK)
        engine_label.set_text(ConsoleHelper.center_text(engine_text, width))
        self.add_child(engine_label)
        
        # Создаем элементы меню
        menu_items = [
            MenuItem("Новая игра", self.on_new_game),
            MenuItem("Загрузить игру", self.on_load_game),
            MenuItem("Настройки", self.on_settings),
            MenuItem("Об игре", self.on_about),
            MenuItem("Выход", self.on_exit)
        ]
        
        # Создаем меню
        menu_width = 30
        menu_x = (width - menu_width) // 2
        menu_y = title_y + 4  # Увеличиваем отступ для добавленной информации о движке
        
        self.menu = Menu(
            menu_x, menu_y, menu_width, menu_items,
            "", True,
            Color.WHITE, Color.BRIGHT_YELLOW,
            Color.BRIGHT_BLACK, Color.CYAN,
            "", Color.BRIGHT_BLUE
        )
        self.add_child(self.menu)
        
        # Подсказки по управлению внизу экрана
        hint_y = height - 2
        hint_text = "↑/↓: Выбор, Enter: Подтвердить, Esc: Выход"
        hint_label = Label(0, hint_y, "", Color.BRIGHT_BLACK)
        hint_label.set_text(ConsoleHelper.center_text(hint_text, width))
        self.add_child(hint_label)
    
    def render(self):
        """
        Рендерит экран.
        """
        # Базовый класс уже рендерит все дочерние элементы
        pass
    
    def handle_input(self, key: int) -> bool:
        """
        Обрабатывает ввод с клавиатуры.
        Возвращает True, если ввод был обработан и требуется перерисовка.
        """
        # Сначала пробуем обработать ввод с помощью меню
        if self.menu.handle_input(key):
            self.needs_redraw = True  # Помечаем, что требуется перерисовка
            return True
        
        # Если меню не обработало ввод, обрабатываем его сами
        if key == Keys.ESCAPE:
            self.on_exit()
            return True
        
        return False
    
    def update(self, dt: float):
        """
        Обновляет состояние экрана.
        """
        # В меню обычно ничего не нужно обновлять
        pass
    
    # Обработчики событий меню
    def on_new_game(self):
        """
        Обработчик выбора пункта "Новая игра".
        """
        print("Запуск новой игры...")
        # self.engine.set_current_screen("game")
    
    def on_load_game(self):
        """
        Обработчик выбора пункта "Загрузить игру".
        """
        print("Загрузка игры...")
        # self.engine.set_current_screen("load_game")
    
    def on_settings(self):
        """
        Обработчик выбора пункта "Настройки".
        """
        print("Открытие настроек...")
        # self.engine.set_current_screen("settings")
    
    def on_about(self):
        """
        Обработчик выбора пункта "Об игре".
        """
        print("Об игре...")
        # self.engine.set_current_screen("about")
    
    def on_exit(self):
        """
        Обработчик выбора пункта "Выход".
        """
        print("Выход из игры...")
        self.engine.stop()

class GameScreen(Screen):
    """
    Основной игровой экран.
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.setup_ui()
    
    def setup_ui(self):
        """
        Настраивает UI элементы экрана.
        """
        # Очищаем существующие элементы
        self.children = []
        
        # Получаем размеры терминала
        width, height = ConsoleHelper.get_terminal_size()
        
        # Создаем фоновую панель
        background = Panel(0, 0, width, height, "", False, "", Color.BG_BLACK)
        self.add_child(background)
        
        # Панель локации (верхняя часть экрана)
        location_panel_height = height // 3
        location_panel = Panel(0, 0, width, location_panel_height, "ЛОКАЦИЯ: Лес", True, Color.BLUE, "", Color.BRIGHT_WHITE)
        self.add_child(location_panel)
        
        # Описание локации
        location_description = TextBox(
            2, 1, width - 4, location_panel_height - 2,
            "Густой лес с множеством растений и животных.",
            Color.WHITE, "", False
        )
        location_panel.add_child(location_description)
        
        # Список доступных ресурсов
        resources_panel_y = location_panel_height
        resources_panel_height = height // 5
        resources_panel = Panel(0, resources_panel_y, width // 2, resources_panel_height, "Доступные ресурсы:", True, Color.GREEN)
        self.add_child(resources_panel)
        
        # Текст с ресурсами
        resources_text = TextBox(
            2, resources_panel_y + 1, width // 2 - 4, resources_panel_height - 2,
            "Луховир (4)\nВолчья погибель (3)\nВоздушная эссенция (2)\nЗверобой (1)",
            Color.GREEN, "", False
        )
        resources_panel.add_child(resources_text)
        
        # Список соседних локаций
        locations_panel_y = resources_panel_y
        locations_panel = Panel(width // 2, locations_panel_y, width // 2, resources_panel_height, "Отсюда можно пойти в:", True, Color.BLUE)
        self.add_child(locations_panel)
        
        # Текст с локациями
        locations_text = TextBox(
            width // 2 + 2, locations_panel_y + 1, width // 2 - 4, resources_panel_height - 2,
            "Горы\nЦветущий Луг\nДеревня",
            Color.BLUE, "", False
        )
        locations_panel.add_child(locations_text)
        
        # Панель действий
        actions_panel_y = resources_panel_y + resources_panel_height
        actions_panel_height = height - actions_panel_y - 1
        actions_panel = Panel(0, actions_panel_y, width, actions_panel_height, "Доступные действия:", True, Color.YELLOW)
        self.add_child(actions_panel)
        
        # Создаем элементы меню для действий
        action_items = [
            MenuItem("Идти в: Горы", None, True, "🚶", Color.BRIGHT_BLUE),
            MenuItem("Идти в: Цветущий Луг", None, True, "🚶", Color.BRIGHT_BLUE),
            MenuItem("Идти в: Деревня", None, True, "🚶", Color.BRIGHT_BLUE),
            MenuItem("Добыть: Луховир", None, True, "⛏️", Color.BRIGHT_GREEN),
            MenuItem("Добыть: Волчья погибель", None, True, "⛏️", Color.BRIGHT_GREEN),
            MenuItem("Добыть: Воздушная эссенция", None, True, "⛏️", Color.BRIGHT_GREEN),
            MenuItem("Добыть: Зверобой", None, True, "⛏️", Color.BRIGHT_GREEN),
            MenuItem("Навыки", None, True, "📖", Color.BRIGHT_MAGENTA),
            MenuItem("Инвентарь", None, True, "🎒", Color.BRIGHT_RED),
            MenuItem("Квесты", None, True, "📜", Color.BRIGHT_YELLOW),
            MenuItem("Глоссарий", None, True, "📚", Color.BRIGHT_CYAN),
            MenuItem("Поговорить с: Отшельник Эрмин", None, True, "💬", Color.BRIGHT_WHITE),
            MenuItem("Поговорить с: Травник Миран", None, True, "💬", Color.BRIGHT_WHITE)
        ]
        
        # Создаем меню действий
        menu_width = width - 4
        menu_x = 2
        menu_y = actions_panel_y + 1
        
        self.actions_menu = Menu(
            menu_x, menu_y, menu_width, action_items,
            "", False,
            Color.WHITE, Color.BRIGHT_WHITE,
            Color.BRIGHT_BLACK, Color.YELLOW,
            "", Color.BRIGHT_WHITE
        )
        actions_panel.add_child(self.actions_menu)
        
        # Подсказки по управлению внизу экрана
        hint_y = height - 1
        hint_text = "↑/↓: Выбор, Enter: Подтвердить, Esc: Назад"
        hint_label = Label(0, hint_y, "", Color.BRIGHT_BLACK)
        hint_label.set_text(ConsoleHelper.center_text(hint_text, width))
        self.add_child(hint_label)
    
    def render(self):
        """
        Рендерит экран.
        """
        # Базовый класс уже рендерит все дочерние элементы
        pass
    
    def handle_input(self, key: int) -> bool:
        """
        Обрабатывает ввод с клавиатуры.
        Возвращает True, если ввод был обработан и требуется перерисовка.
        """
        # Сначала пробуем обработать ввод с помощью меню действий
        if self.actions_menu.handle_input(key):
            self.needs_redraw = True  # Помечаем, что требуется перерисовка
            return True
        
        # Если меню не обработало ввод, обрабатываем его сами
        if key == Keys.ESCAPE:
            # Возвращаемся в главное меню
            self.engine.set_current_screen("main_menu")
            return True
        
        return False
    
    def update(self, dt: float):
        """
        Обновляет состояние экрана.
        """
        # В игровом экране можно обновлять анимации, таймеры и т.д.
        pass 