"""
Готовые экраны для движка рендеринга.
Включает в себя различные типы экранов: главное меню, игровой экран и т.д.
"""

from typing import List, Dict, Any, Optional, Union, Callable
from src.render.core import Screen, UIElement, ConsoleHelper, InputHandler, Keys, Color
from src.render.ui import Panel, Label, Button, MenuItem, Menu, TextBox, FlexPanel, RichText, SidebarLayout, ProgressBar
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
            MenuItem("Новая игра", self.on_new_game),
            MenuItem("Загрузить игру", self.on_load_game),
            MenuItem("Настройки", self.on_settings),
            MenuItem("Об игре", self.on_about),
            MenuItem("Выход", self.on_exit)
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

class GameScreen(Screen):
    """
    Основной игровой экран.
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.game_system = None  # Будет установлен позже
        
        # Элементы интерфейса
        self.layout = None
        self.location_title = None
        self.description_text = None
        self.resources_text = None
        self.actions_menu = None
        
        # Флаги состояния
        self.location_changed = True
        self.actions_changed = True
        
        self.setup_ui()
    
    def set_game_system(self, game_system):
        """
        Устанавливает ссылку на игровую систему.
        
        Args:
            game_system: Экземпляр GameSystem
        """
        self.game_system = game_system
        self.update_location_info()
        self.update_actions()
    
    def setup_ui(self):
        """
        Настраивает UI элементы экрана, используя современную структуру интерфейса.
        """
        # Очищаем существующие элементы
        self.children = []
        
        # Получаем размеры терминала
        width, height = ConsoleHelper.get_terminal_size()
        
        # Создаем фоновую панель для всего экрана
        background = Panel(0, 0, width, height, "", False, "", Color.BG_BLACK)
        self.add_child(background)
        
        # Определение размеров основных панелей
        sidebar_width = min(40, width // 3)  # Увеличиваем ширину боковой панели
        top_panel_height = 3  # Высота верхней панели
        
        # Создаем стилизованную боковую панель слева
        sidebar_panel = Panel(
            0, 0, 
            sidebar_width, height,
            "НАВИГАЦИЯ", True, Color.BRIGHT_BLUE, "", Color.BRIGHT_WHITE
        )
        self.add_child(sidebar_panel)
        
        # Создаем верхнюю панель для информации о локации
        top_panel = Panel(
            sidebar_width, 0, 
            width - sidebar_width, top_panel_height,
            "ЛОКАЦИЯ:", True, Color.BRIGHT_BLUE, "", Color.BRIGHT_WHITE
        )
        self.add_child(top_panel)
        
        # Добавляем текст заголовка локации в верхнюю панель
        self.location_title = Label(sidebar_width + 12, 1, "Загрузка...", Color.BRIGHT_WHITE)
        self.add_child(self.location_title)
        
        # Главная панель контента
        main_content_width = width - sidebar_width - 2
        main_content_height = height - top_panel_height - 3  # -3 для нижней панели
        
        content_panel = Panel(
            sidebar_width + 1, top_panel_height + 1, 
            main_content_width, main_content_height,
            "", True, Color.BRIGHT_BLACK, "", Color.BRIGHT_WHITE
        )
        self.add_child(content_panel)
        
        # Создаем вкладки для основного контента
        self.tabs = ["Описание", "Персонажи", "Карта"]
        self.current_tab = 0
        
        # Рисуем вкладки
        tab_width = main_content_width // len(self.tabs)
        self.tab_labels = []
        for i, tab in enumerate(self.tabs):
            tab_color = Color.BRIGHT_WHITE if i == self.current_tab else Color.WHITE
            tab_bg = Color.BG_BLUE if i == self.current_tab else ""
            tab_x = sidebar_width + 1 + (i * tab_width)
            # Смещаем метку вкладки на 1 вниз, чтобы она не перекрывала верхнюю панель
            tab_label = Label(tab_x + 2, top_panel_height + 1, tab, tab_color, tab_bg)
            self.tab_labels.append(tab_label)
            self.add_child(tab_label)
        
        # Создаем контейнер для описания локации
        description_x = sidebar_width + 3
        description_y = top_panel_height + 3  # Увеличиваем отступ от верха для размещения под вкладками
        description_width = main_content_width - 4
        description_height = main_content_height - 4  # Уменьшаем высоту, чтобы оставить место для вкладок
        
        self.description_text = RichText(
            description_x, description_y, 
            description_width, description_height, 
            Color.WHITE
        )
        self.add_child(self.description_text)
        
        # Панель персонажей (скрыта изначально)
        self.characters_text = RichText(
            description_x, description_y, 
            description_width, description_height, 
            Color.WHITE
        )
        self.characters_text.visible = False
        self.add_child(self.characters_text)
        
        # Панель карты (скрыта изначально)
        self.map_panel = FlexPanel(
            description_x, description_y, 
            description_width, description_height,
            "double", "", 1
        )
        self.map_panel.visible = False
        self.add_child(self.map_panel)
        
        # Нижняя статусная панель
        status_panel = Panel(
            sidebar_width + 1, height - 3,  # Смещаем на 1 вверх 
            main_content_width, 3,  # Увеличиваем высоту панели для размещения подсказки
            "", True, Color.BRIGHT_BLACK, "", Color.BRIGHT_WHITE
        )
        self.add_child(status_panel)
        
        # Подсказки для управления
        hint_text = "↑/↓: Выбор действия | Tab: Переключение вкладок | Enter: Подтвердить | Esc: Назад"
        # Поднимаем подсказку, чтобы она была внутри панели
        hint_label = Label(sidebar_width + 3, height - 2, hint_text, Color.BRIGHT_BLACK)
        self.add_child(hint_label)
        
        # ---- БОКОВАЯ ПАНЕЛЬ ----
        
        # Доступные ресурсы
        resources_label = Label(2, 4, "📦 Доступные ресурсы:", Color.YELLOW)
        self.add_child(resources_label)
        
        # Создаем отдельную панель для ресурсов с четкими границами
        # Начальная минимальная высота для панели ресурсов
        self.resources_min_height = 5
        self.resources_panel_height = self.resources_min_height
        
        # Создаем панель ресурсов, высота будет динамически обновляться
        self.resources_panel = Panel(
            2, 5, 
            sidebar_width - 4, self.resources_panel_height,
            "", True, Color.BRIGHT_BLACK, "", Color.BRIGHT_WHITE
        )
        self.add_child(self.resources_panel)
        
        # RichText внутри панели ресурсов
        self.resources_text = RichText(
            4, 6, 
            sidebar_width - 8, self.resources_panel_height - 2, 
            Color.GREEN
        )
        self.add_child(self.resources_text)
        
        # Позиция метки действий зависит от высоты панели ресурсов
        self.actions_base_y = 6 + self.resources_panel_height
        actions_label = Label(2, self.actions_base_y, "⚔️ Действия:", Color.YELLOW)
        self.actions_label = actions_label
        self.add_child(actions_label)
        
        # Минимальная высота для панели действий
        self.actions_min_height = 5
        
        # Начальная высота для панели действий (будет динамически обновляться)
        self.actions_panel_height = self.actions_min_height
        self.actions_panel = Panel(
            2, self.actions_base_y + 1, 
            sidebar_width - 4, self.actions_panel_height,
            "", True, Color.BRIGHT_BLACK, "", Color.BRIGHT_WHITE
        )
        self.add_child(self.actions_panel)
        
        # Меню действий внутри панели
        self.actions_menu = Menu(
            4, self.actions_base_y + 2, 
            sidebar_width - 8, [],
            "", False,
            Color.WHITE, Color.BRIGHT_WHITE,
            Color.BRIGHT_BLACK, "",
            "", Color.BRIGHT_WHITE
        )
        self.add_child(self.actions_menu)
        
        # Статус игрока - его позиция будет зависеть от высоты панелей ресурсов и действий
        # Начальное значение, которое будет обновляться
        self.player_status_base_y = self.actions_base_y + self.actions_panel_height + 2
        
        player_status_label = Label(2, self.player_status_base_y, "👤 Статус игрока:", Color.BRIGHT_MAGENTA)
        self.player_status_label = player_status_label
        self.add_child(player_status_label)
        
        # Панель статуса
        status_panel_height = 7
        self.player_status_panel = Panel(
            2, self.player_status_base_y + 1, 
            sidebar_width - 4, status_panel_height,
            "", True, Color.BRIGHT_BLACK, "", Color.BRIGHT_WHITE
        )
        self.add_child(self.player_status_panel)
        
        # Здоровье
        self.health_label = Label(4, self.player_status_base_y + 2, "❤️ Здоровье:", Color.BRIGHT_RED)
        self.add_child(self.health_label)
        
        # Увеличиваем ширину прогресс-бара, чтобы лучше вместить информацию
        health_bar_width = sidebar_width - 22
        self.health_bar = ProgressBar(
            23, self.player_status_base_y + 2, health_bar_width, 
            100, 100, Color.RED, Color.BLACK, True, Color.RED, False
        )
        self.add_child(self.health_bar)
        
        # Энергия
        self.energy_label = Label(4, self.player_status_base_y + 3, "⚡ Выносливость:", Color.BRIGHT_GREEN)
        self.add_child(self.energy_label)
        
        self.energy_bar = ProgressBar(
            23, self.player_status_base_y + 3, health_bar_width, 
            100, 100, Color.BRIGHT_GREEN, Color.BLACK, True, Color.BRIGHT_GREEN, False
        )
        self.add_child(self.energy_bar)
        
        # Мана
        self.mana_label = Label(4, self.player_status_base_y + 4, "💙 Мана:", Color.BRIGHT_BLUE)
        self.add_child(self.mana_label)
        
        self.mana_bar = ProgressBar(
            23, self.player_status_base_y + 4, health_bar_width, 
            100, 100, Color.BRIGHT_BLUE, Color.BLACK, True, Color.BRIGHT_BLUE, False
        )
        self.add_child(self.mana_bar)
        
        # Опыт
        self.exp_label = Label(4, self.player_status_base_y + 5, "✨ Опыт:", Color.BRIGHT_YELLOW)
        self.add_child(self.exp_label)
        
        self.exp_bar = ProgressBar(
            23, self.player_status_base_y + 5, health_bar_width, 
            0, 100, Color.BRIGHT_YELLOW, Color.BLACK, True, Color.BRIGHT_YELLOW, False
        )
        self.add_child(self.exp_bar)
        
        # Инициализируем активную вкладку
        self.switch_tab(0, force=True)
    
    def _update_ui_positions(self):
        """
        Обновляет позиции элементов UI в зависимости от высоты панелей.
        """
        # Обновляем позицию метки действий
        self.actions_base_y = 6 + self.resources_panel_height
        self.actions_label.y = self.actions_base_y
        
        # Обновляем позицию панели действий
        self.actions_panel.y = self.actions_base_y + 1
        self.actions_menu.y = self.actions_base_y + 2
        
        # Обновляем позицию панели статуса игрока
        self.player_status_base_y = self.actions_base_y + self.actions_panel_height + 2
        self.player_status_label.y = self.player_status_base_y
        self.player_status_panel.y = self.player_status_base_y + 1
        
        # Обновляем позицию всех элементов статуса
        self.health_label.y = self.player_status_base_y + 2
        self.health_bar.y = self.player_status_base_y + 2
        self.energy_label.y = self.player_status_base_y + 3
        self.energy_bar.y = self.player_status_base_y + 3
        self.mana_label.y = self.player_status_base_y + 4
        self.mana_bar.y = self.player_status_base_y + 4
        self.exp_label.y = self.player_status_base_y + 5
        self.exp_bar.y = self.player_status_base_y + 5
    
    def _update_tab_labels(self):
        """
        Обновляет внешний вид вкладок в соответствии с активной.
        """
        for i, label in enumerate(self.tab_labels):
            if i == self.current_tab:
                label.color = Color.BRIGHT_WHITE
                label.bg_color = Color.BG_BLUE
            else:
                label.color = Color.WHITE
                label.bg_color = ""
    
    def switch_tab(self, direction=1, force=False):
        """
        Переключает активную вкладку.
        
        Args:
            direction (int): 1 для перехода вправо, -1 для перехода влево
            force (bool): Если True, переключает на заданный индекс вкладки без сдвига
        """
        old_tab = self.current_tab
        
        if force:
            # В режиме force направление трактуется как индекс вкладки
            new_tab = direction if 0 <= direction < len(self.tabs) else 0
        else:
            # Обычное переключение со сдвигом
            new_tab = (self.current_tab + direction) % len(self.tabs)
        
        # Если вкладка не изменилась, ничего не делаем
        if old_tab == new_tab and not force:
            return
        
        # Скрываем текущую вкладку
        if old_tab == 0:
            self.description_text.visible = False
        elif old_tab == 1:
            self.characters_text.visible = False
        elif old_tab == 2:
            self.map_panel.visible = False
        
        # Устанавливаем новую активную вкладку
        self.current_tab = new_tab
        
        # Показываем новую вкладку
        if new_tab == 0:
            self.description_text.visible = True
        elif new_tab == 1:
            self.characters_text.visible = True
        elif new_tab == 2:
            self.map_panel.visible = True
        
        # Обновляем внешний вид вкладок
        self._update_tab_labels()
        
        # Перерисовываем
        self.needs_redraw = True
    
    def update_location_info(self):
        """
        Обновляет информацию о текущей локации и подстраивает размер панели ресурсов.
        """
        if not self.game_system:
            return
            
        location = self.game_system.get_current_location()
        if not location:
            self.location_title.set_text("Локация не найдена")
            self.description_text.clear()
            self.description_text.add_text("Локация не найдена. Проверьте конфигурацию игры.", Color.BRIGHT_RED)
            self.resources_text.clear()
            return
        
        # Обновляем заголовок локации с иконкой
        self.location_title.set_text(f"{location.icon} {location.name}")
        
        # Обновляем вкладку описания
        self.description_text.clear()
        self.description_text.add_text(location.description, Color.WHITE)
        self.description_text.add_text("", Color.WHITE)
        
        # Добавляем информацию о соединениях
        if location.connections:
            self.description_text.add_text("\n\nНаправления:", Color.YELLOW)
            for conn in location.connections:
                conn_name = conn.get("name", "Неизвестно")
                icon = conn.get("icon", "🧭")
                condition = conn.get("condition", None)
                
                # Проверяем доступность направления по условию
                if condition:
                    conn_text = f"  {icon} {conn_name} (требуется: {condition})"
                    conn_color = Color.BRIGHT_BLACK  # Недоступно - тусклый цвет
                else:
                    conn_text = f"  {icon} {conn_name}"
                    conn_color = Color.WHITE
                
                self.description_text.add_text(conn_text, conn_color)
        
        # Обновляем вкладку персонажей
        self.characters_text.clear()
        
        if location.characters:
            self.characters_text.add_text("Персонажи на локации:", Color.BRIGHT_CYAN)
            self.characters_text.add_text("", Color.WHITE)  # Пустая строка
            
            for character in location.characters:
                char_name = character.get("name", "Неизвестно")
                char_desc = character.get("description", "")
                
                self.characters_text.add_text(f"👤 {char_name}", Color.BRIGHT_WHITE)
                self.characters_text.add_text(f"   {char_desc}", Color.WHITE)
                self.characters_text.add_text("", Color.WHITE)  # Пустая строка
        else:
            self.characters_text.add_text("На этой локации нет персонажей.", Color.BRIGHT_BLACK)
        
        # Обновляем вкладку карты
        self._draw_location_map(location)
        
        # Обновляем информацию о ресурсах
        self.resources_text.clear()
        
        # Подсчитываем, сколько строк будет занимать текст ресурсов
        resource_lines = 0
        
        if location.available_resources:
            for resource_id, amount in location.available_resources.items():
                # Получаем данные ресурса
                item_data = self.game_system.get_item(resource_id)
                if item_data:
                    resource_name = item_data.get("name", resource_id)
                    resource_color = Color.GREEN
                    
                    # Определяем цвет в зависимости от редкости
                    rarity = item_data.get("rarity", "COMMON").upper()
                    if rarity == "COMMON":
                        resource_color = Color.LIGHT_GRAY
                    elif rarity == "UNCOMMON":
                        resource_color = Color.BRIGHT_GREEN
                    elif rarity == "RARE":
                        resource_color = Color.BRIGHT_BLUE
                    elif rarity == "EPIC":
                        resource_color = Color.BRIGHT_MAGENTA
                    elif rarity == "LEGENDARY":
                        resource_color = Color.BRIGHT_YELLOW
                    
                    self.resources_text.add_text(f"{resource_name}", resource_color, new_line=True)
                    self.resources_text.add_text(f" × ", Color.WHITE, new_line=False)
                    self.resources_text.add_text(f"{amount}", Color.BRIGHT_YELLOW, new_line=False)
                    
                    # Каждый ресурс занимает одну строку
                    resource_lines += 1
        else:
            self.resources_text.add_text("На этой локации нет доступных ресурсов.", Color.BRIGHT_BLACK)
            resource_lines = 1
        
        # Обновляем высоту панели ресурсов в зависимости от их количества
        # Минимальная высота + количество строк + 1 строка отступа сверху и снизу
        new_resources_height = max(self.resources_min_height, resource_lines + 2)
        
        # Проверяем, изменилась ли высота
        if new_resources_height != self.resources_panel_height:
            # Обновляем высоту панели
            self.resources_panel_height = new_resources_height
            self.resources_panel.height = new_resources_height
            self.resources_text.height = new_resources_height - 2  # -2 для рамки
            
            # Обновляем позиции всех элементов, которые зависят от высоты панели ресурсов
            self._update_ui_positions()
        
        # Отмечаем, что информация о локации обновлена
        self.location_changed = False
        self.needs_redraw = True
    
    def update_actions(self):
        """
        Обновляет список доступных действий и подстраивает размер панели действий.
        """
        if not self.game_system:
            return
            
        location = self.game_system.get_current_location()
        if not location:
            self.actions_menu.items = []
            return
        
        action_items = []
        
        # Добавляем действия перемещения с более коротким префиксом
        if location.connections:
            for conn in location.connections:
                conn_id = conn.get("id", "unknown")
                conn_name = conn.get("name", conn_id)
                
                # Создаем действие перемещения с коротким префиксом
                action = lambda loc_id=conn_id: self.on_move_to_location(loc_id)
                action_items.append(MenuItem(f"Идти: {conn_name}", action, True, "", Color.BRIGHT_BLUE, text_parts=[{
                    "text": f"Идти в: ",
                    "color": Color.WHITE,
                }, {
                    "text": f"{conn_name}",
                    "color": Color.BRIGHT_YELLOW,
                }]))
        
        # Добавляем разделитель, если есть ресурсы
        if location.available_resources:
            action_items.append(MenuItem("", None, False))
        
        # Добавляем действия сбора ресурсов с более коротким префиксом
        if location.available_resources:
            for resource_id, amount in location.available_resources.items():
                # Получаем данные ресурса
                item_data = self.game_system.get_item(resource_id)
                if item_data:
                    resource_name = item_data.get("name", resource_id)
                    
                    # Создаем действие сбора ресурса
                    action = lambda res_id=resource_id: self.on_collect_resource(res_id)
                    # Укорачиваем префикс для экономии места
                    action_items.append(MenuItem(f"Добыть: {resource_name}", action, True, "", Color.BRIGHT_GREEN, text_parts=[{
                        "text": f"Добыть: ",
                        "color": Color.WHITE,
                    }, {
                        "text": f"{resource_name}",
                        "color": Color.YELLOW,
                    }]))
        
        # Добавляем персонажей для диалогов
        if location.characters:
            action_items.append(MenuItem("", None, False))
            for character in location.characters:
                char_id = character.get("id", "unknown")
                char_name = character.get("name", char_id)
                
                # Создаем действие разговора с коротким префиксом
                action = lambda c_id=char_id: self.on_talk_to_character(c_id)
                action_items.append(MenuItem(f"Говорить с: {char_name.split()[0]}", action, True, "", Color.BRIGHT_WHITE, text_parts=[{
                    "text": f"Говорить с: ",
                    "color": Color.WHITE,
                }, {
                    "text": f"{char_name.split()[0]}",
                    "color": Color.CYAN,
                }]))
        
        # Добавляем разделитель и основные действия
        action_items.append(MenuItem("", None, False))
        action_items.extend([
            MenuItem("Навыки", self.on_skills, True),
            MenuItem("Инвентарь", self.on_inventory, True),
            MenuItem("Квесты", self.on_quests, True),
            MenuItem("Глоссарий", self.on_glossary, True)
        ])
        
        # Обновляем меню
        self.actions_menu.items = action_items
        
        # Рассчитываем необходимую высоту для меню действий
        # Учитываем, что каждый пункт занимает одну строку, а разделители тоже занимают по строке
        action_lines = len(action_items)
        
        # Добавляем дополнительные строки для многострочных элементов меню
        for item in action_items:
            if item.text and len(item.text) > (self.actions_menu.width - 4):
                # Примерно оцениваем количество дополнительных строк для длинного текста
                text_width = self.actions_menu.width - 4
                additional_lines = (len(item.text) - 1) // text_width
                action_lines += additional_lines
        
        # Обновляем высоту панели действий
        # Минимальная высота + количество строк + 1 строка отступа сверху и снизу
        new_actions_height = max(self.actions_min_height, action_lines + 2)
        
        # Проверяем, изменилась ли высота
        if new_actions_height != self.actions_panel_height:
            # Обновляем высоту панели
            self.actions_panel_height = new_actions_height
            self.actions_panel.height = new_actions_height
            
            # Обновляем позиции всех элементов, которые зависят от высоты панели действий
            self._update_ui_positions()
        
        # Отмечаем, что действия обновлены
        self.actions_changed = False
        self.needs_redraw = True
    
    def _draw_location_map(self, location):
        """
        Рисует карту текущей локации и её соединений.
        """
        # Очищаем панель карты
        self.map_panel._content = []
        
        # Добавляем заголовок
        self.map_panel._content.append("КАРТА ЛОКАЦИЙ")
        self.map_panel._content.append("")
        
        # Простая ASCII карта с текущей локацией в центре
        center_x = 15
        center_y = 7
        
        # Матрица карты
        map_width = 30
        map_height = 15
        map_matrix = [[" " for _ in range(map_width)] for _ in range(map_height)]
        
        # Помещаем текущую локацию в центр
        map_matrix[center_y][center_x] = location.icon
        
        # Отмечаем соединения (для упрощения - только первая буква локации)
        if location.connections:
            directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # Вверх, вправо, вниз, влево
            
            for i, conn in enumerate(location.connections[:4]):  # Берем только первые 4 соединения
                dx, dy = directions[i % len(directions)]
                conn_name = conn.get("name", "?")
                icon = conn.get("icon", "🧭")
                
                # Ставим символ стрелки направления
                arrow_x = center_x + (dx // 2)
                arrow_y = center_y + (dy // 2)
                
                if dx < 0:
                    map_matrix[arrow_y][arrow_x] = "←"
                elif dx > 0:
                    map_matrix[arrow_y][arrow_x] = "→"
                elif dy < 0:
                    map_matrix[arrow_y][arrow_x] = "↑"
                elif dy > 0:
                    map_matrix[arrow_y][arrow_x] = "↓"
                
                # Ставим иконку локации
                map_matrix[center_y + dy][center_x + dx] = icon
        
        # Преобразуем матрицу в строки для отображения
        for row in map_matrix:
            self.map_panel._content.append("".join(row))
    
    def render(self):
        """
        Рендерит экран.
        """
        # Обновляем информацию о локации, если нужно
        if self.location_changed and self.game_system:
            self.update_location_info()
        
        # Обновляем действия, если нужно
        if self.actions_changed and self.game_system:
            self.update_actions()
        
        # Базовый класс уже рендерит все дочерние элементы
        pass
    
    def handle_input(self, key: int) -> bool:
        """
        Обрабатывает ввод с клавиатуры.
        Возвращает True, если ввод был обработан и требуется перерисовка.
        """
        # Переключение вкладок по Tab
        if key == Keys.TAB:
            self.switch_tab()
            return True
        
        # Сначала пробуем обработать ввод с помощью меню действий
        if self.actions_menu.handle_input(key):
            self.needs_redraw = True
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
        # В игровом экране обновляем игровую систему
        if self.game_system:
            self.game_system.update(dt)
            
            # Проверяем, изменилась ли локация
            if self.location_changed:
                self.update_location_info()
            
            # Проверяем, изменились ли действия
            if self.actions_changed:
                self.update_actions()
    
    # Обработчики действий
    def on_move_to_location(self, location_id):
        """
        Обработчик перемещения в локацию.
        
        Args:
            location_id (str): ID локации
        """
        if self.game_system:
            if self.game_system.change_location(location_id):
                # Локация изменилась, обновляем информацию
                self.location_changed = True
                self.actions_changed = True
                self.needs_redraw = True
    
    def on_collect_resource(self, resource_id):
        """
        Обработчик сбора ресурса.
        
        Args:
            resource_id (str): ID ресурса
        """
        if self.game_system:
            collected = self.game_system.collect_resource(resource_id)
            if collected > 0:
                # Ресурс собран, обновляем информацию
                self.location_changed = True
                self.actions_changed = True
                self.needs_redraw = True
                
    def on_skills(self):
        """
        Обработчик открытия навыков.
        """
        print("Открытие навыков...")
        # TODO: Реализовать экран навыков
    
    def on_inventory(self):
        """
        Обработчик открытия инвентаря.
        """
        print("Открытие инвентаря...")
        # TODO: Реализовать экран инвентаря
    
    def on_quests(self):
        """
        Обработчик открытия журнала квестов.
        """
        print("Открытие журнала квестов...")
        # TODO: Реализовать экран квестов
    
    def on_glossary(self):
        """
        Обработчик открытия глоссария.
        """
        print("Открытие глоссария...")
        # TODO: Реализовать экран глоссария
    
    def on_talk_to_character(self, character_id):
        """
        Обработчик разговора с персонажем.
        
        Args:
            character_id (str): ID персонажа
        """
        print(f"Разговор с персонажем {character_id}...")
        # TODO: Реализовать диалоговый экран 