from src.render.core import Screen, ConsoleHelper, Keys, Color
from src.render.ui import Panel, Label, MenuItem, Menu
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
        pymust_version = self.version_props.get("pymust.version", "0.1.0")
        
        version_text = f"v{game_version} {game_stage}"
        version_label = Label(0, title_y + 1, "", Color.BRIGHT_BLACK)
        version_label.set_text(ConsoleHelper.center_text(version_text, width))
        self.add_child(version_label)
        
        # Информация о движке (опционально)
        engine_text = f"Powered by {engine_name} v{engine_version}"
        engine_label = Label(0, title_y + 2, "", Color.BRIGHT_BLACK)
        engine_label.set_text(ConsoleHelper.center_text(engine_text, width))
        self.add_child(engine_label)
        
        # Информация о скриптере (опционально)
        pymust_text = f"Scripted by Pymust v{pymust_version}"
        pymust_label = Label(0, title_y + 3, "", Color.BRIGHT_BLACK)
        pymust_label.set_text(ConsoleHelper.center_text(pymust_text, width))
        self.add_child(pymust_label)
        
        # Создаем элементы меню
        menu_items = [
            MenuItem("Новая игра", self.on_new_game, key=ord('N')),
            MenuItem("Загрузить игру", self.on_load_game, key=ord('L')),
            MenuItem("Настройки", self.on_settings, key=ord('S')),
            MenuItem("Об игре", self.on_about, key=ord('A')),
            MenuItem("Выход", self.on_exit, key=ord('Q'))
        ]
        
        # Создаем меню
        menu_width = 30
        menu_x = (width - menu_width) // 2
        menu_y = title_y + 5  # Увеличиваем отступ для добавленной информации о движке
        
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
        self.engine.set_current_screen("game")
    
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