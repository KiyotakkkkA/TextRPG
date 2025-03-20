from src.render.core import Screen, ConsoleHelper, Keys, Color
from src.render.ui import Panel, Label, MenuItem, Menu
from src.utils.PropertiesLoader import get_version_properties
from src.utils.ChangelogManager import ChangelogManager

class MainMenuScreen(Screen):
    """
    Экран главного меню игры.
    """
    def __init__(self, engine, title: str = "TextRPG"):
        super().__init__(engine)
        self.title = title
        # Загружаем свойства версии
        self.version_props = get_version_properties()
        # Загружаем информацию об обновлении
        self.changelog_manager = ChangelogManager()
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
        
        # Проверяем, есть ли информация об обновлении
        update_info = self.changelog_manager.get_update_info()
        
        # Если есть ASCII-арт, отображаем его вверху
        if update_info["art"]:
            art_lines = update_info["art"].split('\n')
            start_y = 3  # Начинаем с верхнего края
            
            for i, line in enumerate(art_lines):
                art_label = Label(0, start_y + i, "", Color.BRIGHT_CYAN)
                art_label.set_text(ConsoleHelper.center_text(line, width))
                self.add_child(art_label)
                
            # Отступ после арта
            title_y = start_y + len(art_lines) + 2
        else:
            # Если нет арта, стандартное позиционирование
            title_y = height // 4
        
        # Заголовок игры
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
            MenuItem("Загрузить игру", self.on_load_game, key=ord('L'))
        ]
        
        # Если есть информация об обновлении, добавляем пункт меню
        if update_info["has_update"]:
            update_name = update_info["name"] or "Обновление"
            menu_items.insert(0, MenuItem(f"{update_name} NEW!", self.on_update, key=ord('U')))
        
        # Добавляем остальные пункты меню
        menu_items.extend([
            MenuItem("Настройки", self.on_settings, key=ord('S')),
            MenuItem("Об игре", self.on_about, key=ord('A')),
            MenuItem("Выход", self.on_exit, key=ord('Q'))
        ])
        
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
        
    def on_update(self):
        """
        Обработчик выбора пункта "Обновление".
        """
        print("Открытие информации об обновлении...")
        self.engine.set_current_screen("update")


class UpdateScreen(Screen):
    """
    Экран с информацией об обновлении.
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.changelog_manager = ChangelogManager()
        self.current_update_index = 0
        self.update_history = []
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
        
        # Получаем информацию об обновлении
        update_info = self.changelog_manager.get_update_info()
        self.update_history = update_info.get("history", [])
        
        # Если история пуста, используем только текущее обновление
        if not self.update_history:
            self.update_history = [update_info.get("hash")]
        
        # Получаем информацию о текущем обновлении из истории
        current_hash = self.update_history[self.current_update_index]
        current_update = self.changelog_manager.get_update_info_by_hash(current_hash)
        
        # Заголовок экрана
        update_name = current_update.get("name") or "Обновление"
        title_label = Label(0, 1, "", Color.BRIGHT_CYAN)
        title_label.set_text(ConsoleHelper.center_text(f"=== {update_name} ===", width))
        self.add_child(title_label)
        
        # Дата обновления
        date_label = Label(0, 2, "", Color.BRIGHT_BLACK)
        date_label.set_text(ConsoleHelper.center_text(current_update.get("formatted_date", ""), width))
        self.add_child(date_label)
        
        # Индикатор положения в истории обновлений, если есть больше одного обновления
        if len(self.update_history) > 1:
            history_label = Label(0, 3, "", Color.BRIGHT_BLACK)
            history_text = f"Обновление {self.current_update_index + 1} из {len(self.update_history)}"
            history_label.set_text(ConsoleHelper.center_text(history_text, width))
            self.add_child(history_label)
        
        # Текст с изменениями
        changes_text = current_update.get("changes", "Нет информации об изменениях")
        lines = changes_text.split('\n')
        
        # Ограничиваем количество отображаемых строк
        max_lines = min(len(lines), height - 12)  # Уменьшаем для кнопок навигации
        display_panel_height = max_lines + 2
        
        changes_panel = Panel(
            5, 5, width - 10, display_panel_height,
            "", True, "", Color.BG_BLACK, Color.BRIGHT_WHITE
        )
        self.add_child(changes_panel)
        
        # Добавляем строки с изменениями
        for i in range(max_lines):
            if i < len(lines):
                line_color = Color.BRIGHT_GREEN if lines[i].startswith('#') else Color.WHITE
                line_label = Label(7, 6 + i, lines[i], line_color)
                self.add_child(line_label)
        
        # Кнопки навигации между обновлениями (если есть больше одного обновления)
        nav_y = height - 5
        if len(self.update_history) > 1:
            nav_label = Label(0, nav_y, "", Color.BRIGHT_WHITE)
            nav_text = "[ ◄ Предыдущее (←, A, <) ]     [ Следующее (→, D, >) ► ]"
            nav_label.set_text(ConsoleHelper.center_text(nav_text, width))
            self.add_child(nav_label)
        
        # Кнопка "Назад"
        back_label = Label(0, height - 3, "", Color.BRIGHT_YELLOW)
        back_label.set_text(ConsoleHelper.center_text("[ Назад (Enter) ]", width))
        self.add_child(back_label)
    
    def handle_input(self, key: int) -> bool:
        """
        Обрабатывает ввод с клавиатуры.
        """
        # Выход в главное меню
        if key == Keys.ESCAPE or key == Keys.ENTER:
            self.engine.set_current_screen("main_menu")
            return True
        
        # Навигация по истории обновлений
        if len(self.update_history) > 1:
            changed = False
            
            # Предыдущее обновление (стрелка влево)
            if Keys.is_left(key) or key == ord('<'):
                if self.current_update_index > 0:
                    self.current_update_index -= 1
                    changed = True
            
            # Следующее обновление (стрелка вправо)
            elif Keys.is_right(key) or key == ord('>'):
                if self.current_update_index < len(self.update_history) - 1:
                    self.current_update_index += 1
                    changed = True
            
            # Если произошло изменение, обновляем UI и вызываем принудительный рендеринг
            if changed:
                self.setup_ui()  # Перестраиваем UI с новым обновлением
                self.needs_redraw = True  # Явно помечаем для перерисовки
                self.engine.needs_render = True  # Указываем движку о необходимости рендеринга
                
                # Принудительный вызов рендеринга для немедленного обновления экрана
                self.engine.renderer.render(force=True)
                
                return True
        
        return False
    
    def render(self):
        """
        Рендерит экран.
        """
        # Базовый класс уже рендерит все дочерние элементы
        pass
    
    def update(self, dt: float):
        """
        Обновляет состояние экрана.
        """
        # Для экрана обновлений обычно не требуется обновление состояния
        pass