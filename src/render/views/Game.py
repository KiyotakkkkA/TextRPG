from src.render.core import Screen, ConsoleHelper, Keys, Color
from src.render.ui import Panel, Label, MenuItem, Menu, FlexPanel, RichText, ProgressBar

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
        
        self.show_global_map = False  # Флаг для отображения глобальной карты регионов
        self.map_initialized = False  # Флаг, указывающий, была ли карта уже проинициализирована
        
        # Состояние для навигации по навыкам
        self.skills_focus = "groups"  # Какая панель в фокусе: "groups" или "skills"
        self.selected_skill_index = 0  # Индекс выбранного навыка
        self.active_skill_items = []  # Список активных навыков в текущей группе
        
        # Управление фокусом для меню
        self.active_menu = None  # Текущее активное меню
        
        # Информация о последнем собранном предмете и полученном опыте
        self.last_collected_item = None
        self.last_skill_improvement = None
        
        self.setup_ui()
        self._fix_flex_panel()  # Добавляем метод set_content к FlexPanel
    
    def set_game_system(self, game_system):
        """
        Устанавливает игровую систему и обновляет интерфейс.
        
        Args:
            game_system: Игровая система
        """
        self.game_system = game_system
        
        # Подключаемся к событиям игровой системы
        self.game_system.event_system.subscribe("player_moved_to_location", self.on_move_to_location)
        self.game_system.event_system.subscribe("player_collected_resource", self.on_collect_resource)
        self.game_system.event_system.subscribe("player_took_item", self.on_player_took_item)
        
        # Подписываемся на события, связанные с навыками
        self.game_system.event_system.subscribe("player_unlocked_skill", lambda skill_data: self.update_skills_info())
        self.game_system.event_system.subscribe("player_skill_levelup", lambda skill_data: self.update_skills_info())
        self.game_system.event_system.subscribe("player_used_skill", lambda skill_data: self.update_skills_info())
        
        # Подписываемся на события, связанные с игроком
        self.game_system.event_system.subscribe("player_level_up", lambda event_data: self.update_ui())
        self.game_system.event_system.subscribe("skill_level_up", lambda event_data: self.update_ui())
        
        # Обновляем интерфейс
        self.update_ui()
        
        # Обновляем действия
        self.update_actions()
        
        # Обновляем информацию о навыках
        self.update_skills_info()
        
        # Отображаем информацию о текущей локации
        self.update_location_info()
    
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
            "ЛОКАЦИЯ И РЕГИОН", True, Color.BRIGHT_BLUE, "", Color.BRIGHT_WHITE
        )
        self.add_child(top_panel)
        
        # Добавляем текст заголовка локации в верхнюю панель
        self.location_title = Label(sidebar_width + 4, 1, "Загрузка...", Color.BRIGHT_WHITE)
        self.add_child(self.location_title)
        
        # Добавляем информацию о регионе
        self.region_info = Label(sidebar_width + 4, 2, "", Color.BRIGHT_CYAN)
        self.add_child(self.region_info)
        
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
        self.tabs = ["Описание", "Персонажи", "Карта", "Навыки"]
        self.tab_keys = [49, 50, 51, 52]  # Коды клавиш '1', '2', '3', '4' для быстрого доступа
        self.current_tab = 0
        
        # Рисуем вкладки
        tab_width = main_content_width // len(self.tabs)
        self.tab_labels = []
        for i, tab in enumerate(self.tabs):
            tab_color = Color.BRIGHT_WHITE if i == self.current_tab else Color.WHITE
            tab_bg = Color.BG_BLUE if i == self.current_tab else ""
            tab_x = sidebar_width + 1 + (i * tab_width)
            # Смещаем метку вкладки на 1 вниз, чтобы она не перекрывала верхнюю панель
            # Добавляем номер вкладки для горячего доступа
            tab_label = Label(tab_x + 2, top_panel_height + 1, f"{i+1}. {tab}", tab_color, tab_bg)
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
        
        # Панель навыков (скрыта изначально)
        self.skills_panel = FlexPanel(
            description_x, description_y, 
            description_width, description_height,
            "minimal", "", 1
        )
        self.skills_panel.visible = False
        self.add_child(self.skills_panel)
        
        # Создаем панель для групп навыков (слева)
        self.skills_groups_panel = Panel(
            description_x, description_y,
            description_width // 3, description_height,
            "Группы навыков", True, Color.BRIGHT_BLUE, "", Color.BRIGHT_WHITE,
            active_border_color=Color.BRIGHT_YELLOW  # Добавляем активный цвет границы
        )
        self.skills_groups_panel.visible = False
        self.add_child(self.skills_groups_panel)
        
        # Создаем меню для групп навыков
        self.skills_groups_menu = Menu(
            description_x + 2, description_y + 2,
            description_width // 3 - 4, [],
            "", False,
            Color.WHITE, Color.BRIGHT_WHITE,
            Color.BRIGHT_BLACK, "",
            "", Color.BRIGHT_WHITE
        )
        self.skills_groups_menu.visible = False
        self.add_child(self.skills_groups_menu)
        
        # Привязываем меню групп навыков к его панели
        self.skills_groups_panel.set_bind_for(self.skills_groups_menu)
        
        # Создаем панель для детальной информации о навыке (справа)
        self.skills_details_panel = Panel(
            description_x + description_width // 3 + 1, description_y,
            description_width - description_width // 3 - 1, description_height,
            "Информация о навыках", True, Color.BRIGHT_BLUE, "", Color.BRIGHT_WHITE,
            active_border_color=Color.BRIGHT_YELLOW  # Добавляем активный цвет границы
        )
        self.skills_details_panel.visible = False
        self.add_child(self.skills_details_panel)
        
        # Создаем меню для выбора конкретных навыков в группе
        self.skills_list_menu = Menu(
            description_x + description_width // 3 + 3, description_y + 2,
            description_width - description_width // 3 - 6, [],
            "", False,
            Color.WHITE, Color.BRIGHT_WHITE,
            Color.BRIGHT_BLACK, "",
            "", Color.BRIGHT_WHITE
        )
        self.skills_list_menu.visible = False
        self.add_child(self.skills_list_menu)
        
        # Привязываем меню списка навыков к панели деталей
        self.skills_details_panel.set_bind_for(self.skills_list_menu)
        
        # Создаем RichText для отображения детальной информации о навыке
        self.skills_details_text = RichText(
            description_x + description_width // 3 + 3, description_y + 2,
            description_width - description_width // 3 - 6, description_height - 4,
            Color.WHITE
        )
        self.skills_details_text.visible = False
        self.add_child(self.skills_details_text)
        
        # Нижняя статусная панель
        status_panel = Panel(
            sidebar_width + 1, height - 3,  # Смещаем на 1 вверх 
            main_content_width, 3,  # Увеличиваем высоту панели для размещения подсказки
            "", True, Color.BRIGHT_BLACK, "", Color.BRIGHT_WHITE
        )
        self.add_child(status_panel)
        
        # Подсказки для управления
        hint_text = "↑/↓: Выбор действия | ←/→: Переключение панелей | Tab: Переключение вкладок | Enter: Подтвердить | Esc: Назад"
        # Поднимаем подсказку, чтобы она была внутри панели
        hint_label = Label(sidebar_width + 3, height - 2, hint_text, Color.BRIGHT_BLACK)
        self.add_child(hint_label)
        
        # ---- БОКОВАЯ ПАНЕЛЬ ----
        
        # Ресурсы на локации
        resources_label = Label(2, 4, "📦 Ресурсы на локации:", Color.YELLOW)
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
            "", True, Color.BRIGHT_BLACK, "", Color.BRIGHT_WHITE,
            active_border_color=Color.BRIGHT_YELLOW  # Добавляем активный цвет границы
        )
        self.add_child(self.actions_panel)
        
        # Создаем меню действий внутри панели
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
        
        player_status_label = Label(2, self.player_status_base_y, "👤 Статус игрока:", Color.YELLOW)
        self.player_status_label = player_status_label
        self.add_child(player_status_label)
        
        # Панель статуса
        status_panel_height = 8
        self.player_status_panel = Panel(
            2, self.player_status_base_y + 1, 
            sidebar_width - 4, status_panel_height,
            "", True, Color.BRIGHT_BLACK, "", Color.BRIGHT_WHITE
        )
        self.add_child(self.player_status_panel)
        
        # Информация о здоровье, мане, выносливости и опыте игрока
        health_bar_width = 30
        
        # Цвета для разных статусов
        self.health_label = Label(4, self.player_status_base_y + 2, "❤️ Здоровье:", Color.RED)
        self.add_child(self.health_label)
        
        # Используем временные значения вместо обращения к self.game_system.player
        self.health_bar = ProgressBar(
            23, self.player_status_base_y + 2, health_bar_width, 
            100, 100, # Временные значения, будут обновлены в update_ui()
            Color.RED, Color.BLACK, True, Color.RED, False
        )
        self.add_child(self.health_bar)
        
        # Выносливость
        self.stamina_label = Label(4, self.player_status_base_y + 3, "⚡ Выносливость:", Color.BRIGHT_GREEN)
        self.add_child(self.stamina_label)
        
        self.stamina_bar = ProgressBar(
            23, self.player_status_base_y + 3, health_bar_width, 
            100, 100, # Временные значения, будут обновлены в update_ui()
            Color.BRIGHT_GREEN, Color.BLACK, True, Color.BRIGHT_GREEN, False
        )
        self.add_child(self.stamina_bar)
        
        # Мана
        self.mana_label = Label(4, self.player_status_base_y + 4, "💧 Мана:", Color.BRIGHT_BLUE)
        self.add_child(self.mana_label)
        
        self.mana_bar = ProgressBar(
            23, self.player_status_base_y + 4, health_bar_width, 
            100, 100, # Временные значения, будут обновлены в update_ui()
            Color.BRIGHT_BLUE, Color.BLACK, True, Color.BRIGHT_BLUE, False
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
        
        self.space_label = Label(4, self.player_status_base_y + 6, " ", Color.YELLOW)
        self.add_child(self.space_label)
        self.level_label = Label(4, self.player_status_base_y + 7, "🏆 Уровень:", Color.YELLOW)
        self.add_child(self.level_label)
        
        # Панель последнего действия сбора ресурсов (добавление новой панели)
        # Добавляем дополнительную пустую строку для разделения (увеличиваем отступ)
        self.last_action_base_y = self.player_status_base_y + status_panel_height + 4  # Увеличиваем отступ на 1
        self.last_action_label = Label(2, self.last_action_base_y, "📝 Последнее действие:", Color.YELLOW)
        self.add_child(self.last_action_label)
        
        # Панель последнего действия
        last_action_panel_height = 4
        self.last_action_panel = Panel(
            2, self.last_action_base_y + 1, 
            sidebar_width - 4, last_action_panel_height,
            "", True, Color.BRIGHT_BLACK, "", Color.BRIGHT_WHITE
        )
        self.add_child(self.last_action_panel)
        
        # Текст последнего действия
        self.last_action_text = RichText(
            4, self.last_action_base_y + 2, 
            sidebar_width - 8, 2,
            Color.WHITE
        )
        self.add_child(self.last_action_text)
        
        # Инициализируем активную вкладку
        self.switch_tab(0, force=True)
        
        # После создания всех меню, устанавливаем начальный фокус
        self.actions_menu.setFocused(True)
        self.skills_groups_menu.setFocused(False)
        self.skills_list_menu.setFocused(False)
        self.active_menu = self.actions_menu
    
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
        self.stamina_label.y = self.player_status_base_y + 3
        self.stamina_bar.y = self.player_status_base_y + 3
        self.mana_label.y = self.player_status_base_y + 4
        self.mana_bar.y = self.player_status_base_y + 4
        self.exp_label.y = self.player_status_base_y + 5
        self.exp_bar.y = self.player_status_base_y + 5
        self.space_label.y = self.player_status_base_y + 6
        self.level_label.y = self.player_status_base_y + 7
        
        # Обновляем позицию панели последнего действия
        status_panel_height = 7
        self.last_action_base_y = self.player_status_base_y + status_panel_height + 3
        self.last_action_label.y = self.last_action_base_y
        self.last_action_panel.y = self.last_action_base_y + 1
        self.last_action_text.y = self.last_action_base_y + 2
    
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
            force (bool): Принудительное переключение, даже если вкладка не изменилась
        """
        old_tab = self.current_tab
        num_tabs = len(self.tabs)
        
        # Вычисляем новую вкладку
        new_tab = (self.current_tab + direction) % num_tabs
        
        # Если вкладка не изменилась и не требуется принудительное переключение, выходим
        if old_tab == new_tab and not force:
            return
        
        # Скрываем текущую вкладку
        if old_tab == 0:
            self.description_text.visible = False
        elif old_tab == 1:
            self.characters_text.visible = False
        elif old_tab == 2:
            self.map_panel.visible = False
        elif old_tab == 3:
            self.skills_panel.visible = False
            self.skills_groups_panel.visible = False
            self.skills_groups_menu.visible = False
            self.skills_details_panel.visible = False
            self.skills_details_text.visible = False
            self.skills_list_menu.visible = False
            
            # Сбрасываем фокус для меню навыков
            self.skills_groups_menu.setFocused(False)
            self.skills_list_menu.setFocused(False)
        
        # Устанавливаем новую активную вкладку
        self.current_tab = new_tab
        
        # Показываем новую вкладку
        if new_tab == 0:
            self.description_text.visible = True
            # Активируем меню действий
            self.active_menu = self.actions_menu
            self.actions_menu.setFocused(True)
        elif new_tab == 1:
            self.characters_text.visible = True
            # Активируем меню действий
            self.active_menu = self.actions_menu
            self.actions_menu.setFocused(True)
        elif new_tab == 2:
            self.map_panel.visible = True
            # Активируем меню действий
            self.active_menu = self.actions_menu
            self.actions_menu.setFocused(True)
            if not self.map_initialized:
                self._draw_location_map(self.game_system.get_current_location())
        elif new_tab == 3:
            self.skills_panel.visible = True
            self.skills_groups_panel.visible = True
            self.skills_groups_menu.visible = True
            self.skills_details_panel.visible = True
            
            # Устанавливаем начальное состояние для вкладки навыков
            if self.skills_focus == "groups":
                # При первом переключении скрываем детали навыков и показываем меню групп
                self.skills_list_menu.visible = False
                self.skills_details_text.visible = True
                self.skills_groups_menu.setFocused(True)
                self.skills_list_menu.setFocused(False)
                self.active_menu = self.skills_groups_menu
            else:
                self.skills_list_menu.visible = True
                self.skills_details_text.visible = False
                self.skills_groups_menu.setFocused(False)
                self.skills_list_menu.setFocused(True)
                self.active_menu = self.skills_list_menu
            
            # Обновляем информацию о навыках
            self.update_skills_info()
        
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
            self.region_info.set_text("")
            return
        
        # Обновляем заголовок локации с иконкой
        self.location_title.set_text(f"{location.icon} {location.name}")
        
        # Обновляем информацию о текущем регионе
        current_region = self.game_system.get_current_region()
        if current_region:
            self.region_info.set_text(f"{current_region.icon} {current_region.name} [{current_region.climate}]")
        else:
            self.region_info.set_text("Регион: не определен")
        
        # Обновляем вкладку описания
        self.description_text.clear()
        self.description_text.add_text(location.description, Color.WHITE)
        self.description_text.add_text("", Color.WHITE)
        
        # Добавляем информацию о соединениях
        if location.connections:
            self.description_text.add_text("\n\nНаправления:", Color.YELLOW)
            for conn in location.connections:
                # Проверяем, является ли соединение словарем или строкой
                if isinstance(conn, dict):
                    conn_id = conn.get("id", "").lower()
                    conn_name = conn.get("name", "Неизвестно")
                    icon = conn.get("icon", "🧭")
                else:
                    # Если это строка или другой тип, используем значение как есть
                    conn_id = str(conn).lower()
                    conn_name = str(conn)
                    icon = "🧭"
                
                # Проверяем, может ли игрок использовать это соединение
                can_use_connection = location.can_use_connection(conn_id, self.game_system.player, self.game_system)
                
                if can_use_connection:
                    conn_text = f"  {icon} {conn_name}"
                    conn_color = Color.WHITE
                else:
                    # Получаем требования для перехода
                    target_location = self.game_system.get_location(conn_id)
                    if target_location:
                        # Проверяем требования локации
                        player_level = self.game_system.player.level
                        
                        if player_level < target_location.requires.get("player_has_level", 0):
                            reason = f"[нужен уровень {target_location.requires.get('player_has_level')}]"
                        elif "player_has_items" in target_location.requires:
                            items_needed = []
                            for item_id, count in target_location.requires["player_has_items"].items():
                                item_data = self.game_system.get_item(item_id)
                                item_name = item_data.get("name", item_id) if item_data else item_id
                                items_needed.append(f"{item_name} x{count}")
                            reason = f"[нужны предметы: {', '.join(items_needed)}]"
                        elif "player_has_gold" in target_location.requires:
                            gold_needed = target_location.requires["player_has_gold"]
                            reason = f"[нужно {gold_needed} золота]"
                        elif "player_has_completed_quest" in target_location.requires:
                            quest_id = target_location.requires["player_has_completed_quest"]
                            reason = f"[нужно завершить квест: {quest_id}]"
                        elif "player_has_skill_level" in target_location.requires:
                            skill_id = target_location.requires["player_has_skill_level"]
                            answer = f"[нужно достичь"
                            count = 0
                            for key in skill_id:
                                answer += f' уровня {skill_id[key]} навыка "{self.game_system.get_skill(key).name}"'
                                count += 1
                                if count > 0 and count < len(skill_id):
                                    answer += " И"
                            answer += "]"
                            reason = answer
                        else:
                            reason = "[недоступно]"
                    else:
                        reason = "[недоступно]"
                    
                    # Полный текст с именем локации и причиной
                    conn_text = f"{icon} {conn_name} "
                    conn_color = Color.BRIGHT_BLACK  # Серый цвет для недоступной локации
                    
                    # Добавляем весь текст сразу, а затем отдельно причину красным цветом
                    self.description_text.add_text(conn_text, conn_color, new_line=True)
                    self.description_text.add_text(reason, Color.BRIGHT_RED, new_line=False)
                    continue  # Переходим к следующему направлению, так как этот уже добавлен
                
                self.description_text.add_text(conn_text, conn_color)
        
        # Обновляем вкладку персонажей
        self.characters_text.clear()
        
        if location.characters:
            self.characters_text.add_text("Персонажи на локации:", Color.BRIGHT_CYAN)
            self.characters_text.add_text("", Color.WHITE)  # Пустая строка
            
            for character in location.characters:
                # Проверяем, является ли персонаж словарем или строкой
                if isinstance(character, dict):
                    char_name = character.get("name", "Неизвестно")
                    char_desc = character.get("description", "")
                else:
                    # Если это строка или другой тип, используем значение как есть
                    char_name = str(character)
                    char_desc = ""
                
                self.characters_text.add_text(f"👤 {char_name}", Color.BRIGHT_WHITE)
                self.characters_text.add_text(f"   {char_desc}", Color.WHITE)
                self.characters_text.add_text("", Color.WHITE)  # Пустая строка
        else:
            self.characters_text.add_text("На этой локации нет персонажей.", Color.BRIGHT_BLACK)
        
        # Обновляем информацию о ресурсах
        self.resources_text.clear()
        
        # Подсчитываем, сколько строк будет занимать текст ресурсов
        resource_lines = 0
        
        if location.available_resources and len(location.available_resources) > 0:
            # Добавляем заголовок
            self.resources_text.add_text("", Color.WHITE)  # Пустая строка
            resource_lines += 2
            
            has_available_resources = False
            
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
                    
                    # Проверяем требования для ресурса, если они есть
                    can_collect = True
                    requirement_text = ""
                    if "requires" in item_data:
                        can_collect = location.check_requirements(item_data["requires"], self.game_system.player, self.game_system)
                        
                        # Формируем текст требований если они не выполнены
                        if not can_collect:
                            requires = item_data["requires"]
                            
                            # Проверяем требование к уровню игрока
                            if "player_has_level" in requires:
                                required_level = requires["player_has_level"]
                                player_level = self.game_system.player.level
                                if player_level < required_level:
                                    requirement_text = f"[Требуется уровень: {required_level}]"
                            
                            # Проверяем требования к предметам
                            elif "player_has_items" in requires:
                                items_needed = []
                                for item_id, count in requires["player_has_items"].items():
                                    item_data = self.game_system.get_item(item_id)
                                    item_name = item_data.get("name", item_id) if item_data else item_id
                                    items_needed.append(f"{item_name} x{count}")
                                requirement_text = f"- [{', '.join(items_needed)}]"
                            
                            # Проверяем требование к золоту
                            elif "player_has_gold" in requires:
                                gold_needed = requires["player_has_gold"]
                                requirement_text = f"- [Золото: {gold_needed}]"
                                
                            # Проверяем требование к завершенным квестам
                            elif "player_has_completed_quest" in requires:
                                quest_id = requires["player_has_completed_quest"]
                                requirement_text = f"- [Квест: {quest_id}]"
                                
                            # Проверяем требования к навыкам
                            elif "player_has_skill_level" in requires:
                                skill_reqs = []
                                for skill_id, required_level in requires["player_has_skill_level"].items():
                                    skill = self.game_system.get_skill(skill_id)
                                    skill_name = skill.name if skill else skill_id
                                    skill_reqs.append(f"{skill_name} ур. {required_level}")
                                requirement_text = f"- [{', '.join(skill_reqs)}]"
                                
                            # Если не определено конкретное требование
                            elif not requirement_text:
                                requirement_text = "- [Недоступно]"
                    
                    # Если количество больше нуля, отображаем в зависимости от доступности
                    if amount > 0:
                        has_available_resources = True
                        
                        if can_collect:
                            # Ресурс доступен для сбора
                            self.resources_text.add_text(f"{resource_name}", resource_color, new_line=True)
                            self.resources_text.add_text(f" × ", Color.WHITE, new_line=False)
                            self.resources_text.add_text(f"{amount}", Color.BRIGHT_YELLOW, new_line=False)
                        else:
                            # Ресурс недоступен из-за требований
                            self.resources_text.add_text(f"{resource_name}", Color.BRIGHT_BLACK, new_line=True)
                            self.resources_text.add_text(f" × ", Color.WHITE, new_line=False)
                            self.resources_text.add_text(f"{amount}", Color.BRIGHT_BLACK, new_line=False)
                            self.resources_text.add_text("", Color.WHITE, new_line=True)
                            self.resources_text.add_text(requirement_text, Color.BRIGHT_RED, new_line=False)
                    else:
                        # Если количество равно нулю, показываем как "исчерпан"
                        self.resources_text.add_text(f"{resource_name}", Color.BRIGHT_BLACK, new_line=True)
                        self.resources_text.add_text(f" - ", Color.WHITE, new_line=False)
                        self.resources_text.add_text("исчерпан", Color.BRIGHT_BLACK, new_line=False)
                    
                    # Каждый ресурс занимает две строки: сам ресурс и пустая строка после него
                    resource_lines += 2
            
            # Если нет доступных ресурсов вообще, показываем сообщение
            if not has_available_resources:
                self.resources_text.clear()
                self.resources_text.add_text("Нет ресурсов на локации", Color.BRIGHT_BLACK)
                resource_lines = 1
        else:
            self.resources_text.add_text("Нет ресурсов на локации", Color.BRIGHT_BLACK)
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
        
        # Очищаем меню действий
        items = []
        
        # Добавляем действия перемещения в другие локации
        for connection in location.connections:
            # Проверяем, является ли соединение словарем или строкой
            conn_id = ""
            conn_name = ""
            if isinstance(connection, dict):
                conn_id = connection.get("id", "").lower()
                conn_name = connection.get("name", conn_id)
            else:
                conn_id = str(connection).lower()
                conn_name = conn_id
            
            # Создаем функцию для перемещения в указанную локацию
            def create_move_action(target_id):
                return lambda: self.on_move_to_location(target_id)
            
            # Проверяем, может ли игрок использовать это соединение
            can_use_connection = location.can_use_connection(conn_id, self.game_system.player, self.game_system)
            
            # Добавляем пункт меню для перемещения
            items.append(MenuItem(
                f"Идти в: {conn_name}",
                create_move_action(conn_id),
                enabled=can_use_connection,  # Делаем пункт меню неактивным, если переход недоступен
                text_parts=[
                    {"text": "Идти в: ", "color": Color.WHITE},
                    {"text": conn_name, "color": Color.BRIGHT_YELLOW if can_use_connection else Color.BRIGHT_BLACK}
                ]
            ))
        
        # Добавляем разделитель, если есть хотя бы одна локация для перемещения
        if items:
            items.append(MenuItem("──────────────", None, enabled=False))
        
        # Добавляем действия для сбора ресурсов
        has_resources = False
        
        for resource_id, amount in location.available_resources.items():
            # Пропускаем ресурсы с количеством 0
            if amount <= 0:
                continue
                
            # Получаем данные ресурса
            item_data = self.game_system.get_item(resource_id)
            if item_data:
                has_resources = True
                resource_name = item_data.get("name", resource_id)
                resource_color = Color.GREEN
                
                # Определяем цвет в зависимости от редкости
                rarity = item_data.get("rarity", "COMMON").upper()
                if rarity == "COMMON":
                    resource_color = Color.WHITE
                elif rarity == "UNCOMMON":
                    resource_color = Color.BRIGHT_GREEN
                elif rarity == "RARE":
                    resource_color = Color.BRIGHT_BLUE
                elif rarity == "EPIC":
                    resource_color = Color.BRIGHT_MAGENTA
                elif rarity == "LEGENDARY":
                    resource_color = Color.BRIGHT_YELLOW
                
                # Создаем функцию для сбора ресурса
                def create_collect_action(res_id):
                    return lambda: self.on_collect_resource(res_id)
                
                # Проверяем требования для ресурса, если они есть
                can_collect = True
                requirement_text = ""
                if "requires" in item_data:
                    can_collect = location.check_requirements(item_data["requires"], self.game_system.player, self.game_system)
                    
                    # Если требования не выполнены, формируем текст требований
                    if not can_collect:
                        requires = item_data["requires"]
                        
                        # Проверяем требование к уровню игрока
                        if "player_has_level" in requires:
                            required_level = requires["player_has_level"]
                            player_level = self.game_system.player.level
                            if player_level < required_level:
                                requirement_text = f"Требуется уровень: {required_level}"
                        
                        # Проверяем требования к предметам
                        elif "player_has_items" in requires:
                            items_needed = []
                            for item_id, count in requires["player_has_items"].items():
                                item_data = self.game_system.get_item(item_id)
                                item_name = item_data.get("name", item_id) if item_data else item_id
                                items_needed.append(f"{item_name} x{count}")
                            requirement_text = f"Требуются: {', '.join(items_needed)}"
                        
                        # Проверяем требование к золоту
                        elif "player_has_gold" in requires:
                            gold_needed = requires["player_has_gold"]
                            requirement_text = f"Требуется золото: {gold_needed}"
                            
                        # Проверяем требование к завершенным квестам
                        elif "player_has_completed_quest" in requires:
                            quest_id = requires["player_has_completed_quest"]
                            requirement_text = f"Требуется квест: {quest_id}"
                            
                        # Проверяем требования к навыкам
                        elif "player_has_skill_level" in requires:
                            skill_reqs = []
                            for skill_id, required_level in requires["player_has_skill_level"].items():
                                skill = self.game_system.get_skill(skill_id)
                                skill_name = skill.name if skill else skill_id
                                skill_reqs.append(f"{skill_name} ур. {required_level}")
                            requirement_text = f"Требуется: {', '.join(skill_reqs)}"
                            
                        # Проверяем требования к навыкам в формате REQ_SKILL
                        elif "REQ_SKILL" in requires:
                            skill_reqs = []
                            for skill_id, skill_req in requires["REQ_SKILL"].items():
                                skill_level = skill_req.get("level", 1)
                                skill = self.game_system.get_skill(skill_id)
                                skill_name = skill.name if skill else skill_id
                                skill_reqs.append(f"{skill_name} ур. {skill_level}")
                            requirement_text = f"Требуется: {', '.join(skill_reqs)}"
                            
                        # Если не определено конкретное требование
                        elif not requirement_text:
                            requirement_text = "Недоступно"
                
                # Определяем цвет текста в зависимости от доступности
                resource_name_color = resource_color if can_collect else Color.BRIGHT_BLACK
                
                # Создаем текстовые части для отображения
                text_parts = [
                    {"text": "Добыть: ", "color": Color.WHITE},
                    {"text": resource_name, "color": resource_name_color}
                ]
                
                # Добавляем пункт меню для сбора ресурса
                items.append(MenuItem(
                    f"Добыть: {resource_name}",
                    create_collect_action(resource_id) if can_collect else None,
                    enabled=can_collect,
                    text_parts=text_parts
                ))
        
        # Добавляем разделитель между ресурсами и персонажами, если есть хотя бы один ресурс
        if has_resources:
            items.append(MenuItem("──────────────", None, enabled=False))
        
        # Добавляем действия диалога с персонажами
        has_characters = False
        
        # Проверяем наличие персонажей в локации
        if hasattr(location, 'characters') and location.characters:
            for character in location.characters:
                has_characters = True
                
                # Проверяем формат персонажа (словарь или строка)
                if isinstance(character, dict):
                    character_id = character.get("id", "unknown")
                    character_name = character.get("name", character_id)
                else:
                    character_id = str(character)
                    character_name = character_id
                
                # Создаем функцию для разговора с персонажем
                def create_talk_action(char_id):
                    return lambda: self.on_talk_to_character(char_id)
                
                # Добавляем пункт меню для разговора
                items.append(MenuItem(
                    f"Говорить с: {character_name}",
                    create_talk_action(character_id),
                    text_parts=[
                        {"text": "Говорить с: ", "color": Color.WHITE},
                        {"text": character_name, "color": Color.BRIGHT_CYAN}
                    ]
                ))
        
        # Добавляем разделитель между персонажами и стандартными действиями, если есть хотя бы один персонаж
        if has_characters:
            items.append(MenuItem("──────────────", None, enabled=False))
        
        # Добавляем стандартные действия
        items.append(MenuItem(
            "Навыки",
            self.on_skills,
            key=Keys.from_char('k'),
            text_parts=[
                {"text": "Навыки", "color": Color.WHITE},
            ]
        ))
        
        items.append(MenuItem(
            "Инвентарь",
            self.on_inventory,
            key=Keys.from_char('i'),
            text_parts=[
                {"text": "Инвентарь", "color": Color.WHITE},
            ]
        ))
        
        items.append(MenuItem(
            "Квесты",
            self.on_quests,
            key=Keys.from_char('j'),
            text_parts=[
                {"text": "Квесты", "color": Color.WHITE},
            ]
        ))
        
        items.append(MenuItem(
            "Глоссарий",
            self.on_glossary,
            key=Keys.from_char('g'),
            text_parts=[
                {"text": "Глоссарий", "color": Color.WHITE},
            ]
        ))
        
        # Обновляем меню действий
        self.actions_menu.items = items
        
        # Рассчитываем необходимую высоту для меню действий
        # Учитываем, что каждый пункт занимает одну строку, а разделители тоже занимают по строке
        action_lines = len(items)
        
        # Добавляем дополнительные строки для многострочных элементов меню
        for item in items:
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
    
    def _draw_regions_map(self, current_region):
        """
        Отображает заглушку вместо карты регионов.
        """
        # Очищаем контент карты
        map_content = []
        
        # Заголовок
        map_content.append("╔══════════════════════════════════════════╗")
        map_content.append("║              🗺️ КАРТА МИРА               ║")
        map_content.append("╚══════════════════════════════════════════╝")
        map_content.append("")
        map_content.append("   Функция карты временно отключена.")
        map_content.append("   Карта будет реализована в следующих версиях.")
        map_content.append("")
        map_content.append("   Пожалуйста, воспользуйтесь вкладками")
        map_content.append("   \"Описание\" и \"Персонажи\" для навигации.")
        
        # Устанавливаем содержимое в панель карты
        self.map_panel.set_content(map_content)
        self.map_panel.needs_redraw = True
        self.needs_redraw = True

    def _draw_location_map(self, location):
        """
        Отображает заглушку вместо карты локации.
        """
        # Очищаем контент карты
        map_content = []
        
        # Заголовок
        map_content.append("╔══════════════════════════════════════════╗")
        map_content.append("║              🗺️ ЛОКАЛЬНАЯ КАРТА          ║")
        map_content.append("╚══════════════════════════════════════════╝")
        map_content.append("")
        map_content.append("   Функция карты временно отключена.")
        map_content.append("   Карта будет реализована в следующих версиях.")
        map_content.append("")
        map_content.append("   Пожалуйста, воспользуйтесь описанием локации")
        map_content.append("   для навигации и информации о соседних локациях.")
        
        # Устанавливаем содержимое в панель карты
        self.map_panel.set_content(map_content)
        self.map_panel.needs_redraw = True
        self.needs_redraw = True
    
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
        Обрабатывает ввод для игрового экрана.
        
        Args:
            key (int): Код нажатой клавиши
            
        Returns:
            bool: True, если ввод был обработан
        """
        # Обрабатываем выход из игры
        if key == Keys.ESCAPE:
            self.engine.set_current_screen("main_menu")
            return True
            
        # Обрабатываем переключение вкладок клавишей Tab
        if key == Keys.TAB:
            self.switch_tab(1)
            return True
            
        # Обрабатываем быстрое переключение по цифрам
        if key in self.tab_keys:
            tab_index = self.tab_keys.index(key)
            if tab_index != self.current_tab:
                self.switch_tab(tab_index - self.current_tab)
            return True
            
        # Обрабатываем навигацию в режиме навыков
        if self.current_tab == 3:
            # Переключение между панелями левой и правой с помощью стрелок влево/вправо
            if Keys.is_left(key) and self.skills_focus == "skills":
                # Переключаемся на левую панель (группы навыков)
                self.skills_focus = "groups"
                self.skills_list_menu.visible = False
                self.skills_details_text.visible = True
                
                # Переключаем фокус
                self.skills_groups_menu.setFocused(True)
                self.skills_list_menu.setFocused(False)
                self.active_menu = self.skills_groups_menu
                
                self.needs_redraw = True
                return True
            
            if Keys.is_right(key) and self.skills_focus == "groups":
                # Переключаемся на правую панель (список навыков)
                self.skills_focus = "skills"
                self.skills_list_menu.visible = True
                self.skills_details_text.visible = False
                
                # Переключаем фокус
                self.skills_groups_menu.setFocused(False)
                self.skills_list_menu.setFocused(True)
                self.active_menu = self.skills_list_menu
                
                self.update_skills_list()
                self.needs_redraw = True
                return True
        
        # Обрабатываем ввод для текущего активного меню
        if self.active_menu and self.active_menu.visible and self.active_menu.handle_input(key):
            self.needs_redraw = True
            return True
        
        return False
    
    def update_ui(self):
        """
        Обновляет все элементы интерфейса, такие как здоровье, опыт, золото и т.д.
        """
        if not self.game_system:
            return
        
        # Обновляем значения статуса игрока из объекта Player
        player = self.game_system.player
        
        # Обновляем показатели здоровья
        self.health_bar.set_value(player.current_health)
        self.health_bar.max_value = player.max_health
        
        # Обновляем показатели выносливости
        self.stamina_bar.set_value(player.current_stamina)
        self.stamina_bar.max_value = player.max_stamina
        
        # Обновляем показатели маны
        self.mana_bar.set_value(player.current_mana)
        self.mana_bar.max_value = player.max_mana
        
        self.exp_bar.set_value(player.current_exp)
        self.exp_bar.max_value = player.exp_for_level_up
        
        # Обновляем уровень игрока
        self.level_label.set_text(f"🏆 Уровень: {player.level}")
        
        # Обновляем остальные UI элементы
        self.update_location_info()
        self.update_skills_info()
        
        self.needs_redraw = True
    
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
                self._draw_location_map(self.game_system.get_current_location())
            
            # Проверяем, изменились ли действия
            if self.actions_changed:
                self.update_actions()
    
    # Вспомогательные методы
    def _fix_flex_panel(self):
        """
        Расширяет функциональность FlexPanel, добавляя метод set_content,
        если он ещё не существует в классе.
        """
        if not hasattr(self.map_panel, 'set_content'):
            def set_content(panel, content):
                panel._content = []
                if content:
                    panel._content.extend(content)
                panel.needs_redraw = True
            
            # Добавляем метод set_content динамически
            import types
            self.map_panel.set_content = types.MethodType(set_content, self.map_panel)
            print("Добавлен метод set_content для FlexPanel")
    
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
                # Обновляем карту
                self._draw_location_map(self.game_system.get_current_location())
    
    def on_player_took_item(self, item_data):
        """
        Обработчик события получения предмета игроком.
        Используется для отслеживания улучшений навыков.
        
        Args:
            item_data (dict): Данные предмета со счетчиком количества
        """
        if not self.game_system:
            return
        
        # Сохраняем информацию о последнем собранном предмете
        self.last_collected_item = item_data
        
        # Получаем полные данные о предмете
        item_id = item_data.get("id")
        count = item_data.get("count", 1)
        
        item_full_data = self.game_system.get_item(item_id)
        if not item_full_data:
            return
        
        # Проверяем наличие блока улучшений
        improves = item_full_data.get("improves")
        if not improves:
            return
        
        # Получаем информацию об улучшении навыков
        skill_improvements = improves.get("improves_skills", {})
        
        # Если есть улучшения навыков, обновляем панель последнего действия
        if skill_improvements:
            self.update_last_action_panel(item_full_data, count, skill_improvements)
    
    def update_last_action_panel(self, item_data, count, skill_improvements):
        """
        Обновляет панель последнего действия с информацией о собранном предмете и улучшении навыков.
        
        Args:
            item_data (dict): Данные предмета
            count (int): Количество собранных предметов
            skill_improvements (dict): Словарь с улучшениями навыков (skill_id -> exp)
        """
        if not self.game_system:
            return
        
        # Очищаем текст последнего действия
        self.last_action_text.clear()
        
        # Получаем название предмета
        item_name = item_data.get("name", "Неизвестный предмет")
        
        # Определяем цвет в зависимости от редкости
        item_color = Color.WHITE
        rarity = item_data.get("rarity", "COMMON").upper()
        if rarity == "COMMON":
            item_color = Color.WHITE
        elif rarity == "UNCOMMON":
            item_color = Color.BRIGHT_GREEN
        elif rarity == "RARE":
            item_color = Color.BRIGHT_BLUE
        elif rarity == "EPIC":
            item_color = Color.BRIGHT_MAGENTA
        elif rarity == "LEGENDARY":
            item_color = Color.BRIGHT_YELLOW
        
        # Добавляем информацию о собранном предмете
        self.last_action_text.add_text("Собрано ", Color.WHITE, new_line=False)
        self.last_action_text.add_text(item_name, item_color, new_line=False)
        self.last_action_text.add_text(" x ", Color.WHITE, new_line=False)
        self.last_action_text.add_text(str(count), Color.BRIGHT_YELLOW, new_line=False)
        
        # Для каждого улучшенного навыка добавляем информацию
        for skill_id, exp_amount in skill_improvements.items():
            # Получаем навык игрока
            skill = self.game_system.player.get_skill(skill_id)
            if skill:
                skill_name = skill.name
                # Общее количество опыта (exp_amount * count)
                total_exp = exp_amount * count
                
                # Добавляем информацию о улучшении навыка
                self.last_action_text.add_text(skill_name, Color.BRIGHT_GREEN, new_line=True)
                self.last_action_text.add_text(" увеличено на ", Color.WHITE, new_line=False)
                self.last_action_text.add_text(str(total_exp), Color.BRIGHT_YELLOW, new_line=False)
                self.last_action_text.add_text(" опыта", Color.WHITE)
    
    def on_collect_resource(self, resource_id, resource_name=None, amount=0, location_id=None):
        """
        Обработчик сбора ресурса.
        
        Args:
            resource_id (str, dict): ID ресурса или словарь с данными события
            resource_name (str, optional): Название ресурса
            amount (int, optional): Количество собранного ресурса
            location_id (str, optional): ID локации, где был собран ресурс
        """
        # Проверяем, получили ли мы данные в виде словаря (новый формат)
        if isinstance(resource_id, dict):
            event_data = resource_id
            resource_id = event_data.get("resource_id")
            resource_name = event_data.get("resource_name")
            amount = event_data.get("amount", 0)
            location_id = event_data.get("location_id")
        
        if self.game_system:
            # Получаем данные о ресурсе
            item_data = self.game_system.get_item(resource_id)
            location = self.game_system.get_current_location()
            
            # Проверяем требования для ресурса, если они есть
            if item_data and "requires" in item_data:
                can_collect = location.check_requirements(item_data["requires"], self.game_system.player, self.game_system)
                if not can_collect:
                    # Если требования не выполнены, не собираем ресурс
                    return
            
            # Передаём None в качестве количества, чтобы собрать всё доступное количество
            collected = self.game_system.collect_resource(resource_id, None)
            if collected > 0:
                # Ресурс собран, обновляем информацию
                self.location_changed = True
                self.actions_changed = True
                self.needs_redraw = True
    
    def on_skills(self):
        """
        Обработчик нажатия на кнопку 'Навыки'.
        Переключает на вкладку с навыками.
        """
        # Получаем индекс вкладки "Навыки"
        skills_tab_index = self.tabs.index("Навыки")
        
        # Если мы уже не на этой вкладке, переключаемся на неё
        if self.current_tab != skills_tab_index:
            self.switch_tab(skills_tab_index - self.current_tab)
        
        # Обновляем информацию о навыках
        self.update_skills_info()
    
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

    def _wrap_text(self, text, width):
        """
        Разбивает текст на строки с максимальной длиной width.
        
        Args:
            text: Исходный текст
            width: Максимальная ширина строки
            
        Returns:
            list: Список строк
        """
        # Если текст пустой, возвращаем пустой список
        if not text:
            return []
            
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            # Проверка, поместится ли слово в текущую строку
            if current_length + len(word) + len(current_line) <= width:
                current_line.append(word)
                current_length += len(word)
            else:
                # Если текущая строка не пуста, добавляем ее в результат
                if current_line:
                    lines.append(" ".join(current_line))
                # Начинаем новую строку с текущего слова
                current_line = [word]
                current_length = len(word)
        
        # Добавляем последнюю строку, если она не пуста
        if current_line:
            lines.append(" ".join(current_line))
            
        return lines

    def update_skills_info(self):
        """
        Обновляет информацию о навыках игрока и формирует меню групп навыков.
        """
        if not self.game_system:
            return
        
        # Очищаем текст с деталями навыка
        self.skills_details_text.clear()
        
        # Получаем все группы навыков в порядке отображения
        groups = self.game_system.get_ordered_skill_groups()
        if not groups:
            self.skills_details_text.add_text("Нет доступных групп навыков", Color.BRIGHT_RED)
            return
        
        # Формируем элементы меню для групп навыков
        menu_items = []
        for group in groups:
            # Получаем навыки в этой группе
            skills = self.game_system.get_skills_by_group(group.id)
            # Считаем количество доступных игроку навыков в группе
            player_skills = [skill for skill in skills if skill.id in self.game_system.player.skills]
            
            # Создаем элемент меню
            menu_item_text = f"{group.icon} {group.name} ({len(player_skills)}/{len(skills)})"
            
            # Создаем функцию для отображения навыков группы
            def make_select_group_action(group_id):
                return lambda: self.show_group_skills(group_id)
            
            # Добавляем элемент в меню
            menu_items.append(MenuItem(
                menu_item_text,
                make_select_group_action(group.id),
                enabled=len(player_skills) > 0
            ))
        
        # Обновляем меню групп
        self.skills_groups_menu.items = menu_items
        
        # При первом переключении на вкладку навыков сбрасываем состояние
        if self.current_tab == 3 and not self.skills_details_text.visible:
            # Очищаем текст с деталями и скрываем список навыков
            self.skills_details_text.clear()
            self.skills_list_menu.visible = False
            self.skills_details_text.visible = True
        
        # Если есть элементы, выбираем первый по умолчанию
        if menu_items:
            # Активируем первую доступную группу
            for i, item in enumerate(menu_items):
                if item.enabled:
                    self.skills_groups_menu.selected_index = i
                    # Если мы на вкладке навыков и в фокусе группы, активируем элемент
                    if self.current_tab == 3 and self.skills_focus == "groups" and self.active_menu == self.skills_groups_menu:
                        item.activate()
                    break
    
    def show_group_skills(self, group_id):
        """
        Отображает навыки выбранной группы.
        
        Args:
            group_id (str): ID группы навыков
        """
        if not self.game_system:
            return
            
        # Получаем группу навыков
        group = self.game_system.get_skill_group(group_id)
        if not group:
            self.skills_details_text.clear()
            self.skills_details_text.add_text(f"Группа навыков с ID {group_id} не найдена", Color.BRIGHT_RED)
            return
            
        # Устанавливаем режим фокуса на группы
        self.skills_focus = "groups"
        self.skills_groups_menu.setFocused(True)
        self.skills_list_menu.setFocused(False)
        self.active_menu = self.skills_groups_menu
        
        # Скрываем список навыков и показываем детали группы
        self.skills_list_menu.visible = False
        self.skills_details_text.visible = True
        
        # Очищаем текст с деталями
        self.skills_details_text.clear()
        
        # Отображаем заголовок группы
        self.skills_details_text.add_text(f"{group.icon} {group.name}", Color.BRIGHT_CYAN)
        self.skills_details_text.add_text(group.description, Color.WHITE)
        self.skills_details_text.add_text("", Color.WHITE)  # Пустая строка
        
        # Получаем навыки этой группы
        skills = self.game_system.get_skills_by_group(group_id)
        
        # Сохраняем текущую выбранную группу
        self.current_group_id = group_id
        
        # Обновляем список навыков для меню
        self.update_skills_list()
        
        # Отображаем навыки
        if not skills:
            self.skills_details_text.add_text("В этой группе нет навыков", Color.BRIGHT_RED)
            return
            
        # Отображаем каждый навык
        for skill in skills:
            # Проверяем, есть ли у игрока этот навык
            player_skill = self.game_system.player.get_skill(skill.id)
            
            if player_skill:
                # Отображаем навык, доступный игроку
                skill_name = f"{skill.icon} {skill.name} [{player_skill.level}/{player_skill.max_level}]"
                self.skills_details_text.add_text(skill_name, Color.BRIGHT_GREEN)
                
                # Отображаем прогресс навыка
                progress_percent = player_skill.get_experience_percent() * 100
                progress_bar = self._create_progress_bar(
                    20, 
                    progress_percent, 
                    player_skill.current_experience, 
                    player_skill.max_level_experience
                )
                progress_text = f"Прогресс: {progress_bar}"
                self.skills_details_text.add_text(progress_text, Color.YELLOW)
                
                # Отображаем описание навыка
                self.skills_details_text.add_text(skill.description, Color.WHITE)
                
                # Отображаем бонусы навыка, если они есть
                passive_bonuses = player_skill.get_passive_bonuses()
                if passive_bonuses:
                    self.skills_details_text.add_text("Пассивные бонусы:", Color.BRIGHT_MAGENTA)
                    for bonus_name, bonus_value in passive_bonuses.items():
                        bonus_text = f"  • {bonus_name}: +{bonus_value}"
                        self.skills_details_text.add_text(bonus_text, Color.MAGENTA)
                
                # Отображаем разблокированные способности, если они есть
                unlocked_abilities = player_skill.get_unlocked_abilities()
                if unlocked_abilities:
                    self.skills_details_text.add_text("Разблокированные способности:", Color.BRIGHT_CYAN)
                    for ability in unlocked_abilities:
                        ability_text = f"  • {ability}"
                        self.skills_details_text.add_text(ability_text, Color.CYAN)
                        
                # Добавляем пустую строку между навыками
                self.skills_details_text.add_text("", Color.WHITE)
            elif skill.is_unlocked(self.game_system.player.level):
                # Навык доступен для изучения, но не изучен
                skill_name = f"🔓 {skill.name} (Доступен)"
                self.skills_details_text.add_text(skill_name, Color.BRIGHT_YELLOW)
                self.skills_details_text.add_text(skill.description, Color.WHITE)
                self.skills_details_text.add_text("", Color.WHITE)  # Пустая строка
            else:
                # Навык недоступен
                skill_name = f"🔒 {skill.name} (Требуется уровень {skill.unlocked_at_level})"
                self.skills_details_text.add_text(skill_name, Color.BRIGHT_BLACK)
                self.skills_details_text.add_text("", Color.WHITE)  # Пустая строка
    
    def update_skills_list(self):
        """
        Обновляет список навыков для конкретной группы в меню выбора.
        """
        if not hasattr(self, 'current_group_id') or not self.game_system:
            return
        
        # Получаем навыки текущей группы
        skills = self.game_system.get_skills_by_group(self.current_group_id)
        
        # Формируем элементы меню для навыков
        menu_items = []
        self.active_skill_items = []
        
        for skill in skills:
            # Проверяем, есть ли у игрока этот навык
            player_skill = self.game_system.player.get_skill(skill.id)
            
            # Создаем функцию для отображения деталей навыка
            def make_show_skill_action(skill_index):
                return lambda: self.show_skill_details(skill_index)
            
            if player_skill:
                # Доступный навык
                skill_name = f"{skill.icon} {skill.name} [{player_skill.level}/{player_skill.max_level}]"
                menu_color = Color.BRIGHT_GREEN
                enabled = True
                self.active_skill_items.append(skill)
            elif skill.is_unlocked(self.game_system.player.level):
                # Навык доступен, но не изучен
                skill_name = f"🔓 {skill.name}"
                menu_color = Color.BRIGHT_YELLOW
                enabled = False
            else:
                # Навык недоступен
                skill_name = f"🔒 {skill.name}"
                menu_color = Color.BRIGHT_BLACK
                enabled = False
            
            # Добавляем элемент в меню
            menu_items.append(MenuItem(
                skill_name,
                make_show_skill_action(len(self.active_skill_items) - 1) if enabled else None,
                enabled=enabled,
                text_parts=[{"text": skill_name, "color": menu_color}]
            ))
        
        # Обновляем меню навыков
        self.skills_list_menu.items = menu_items
        
        # Если есть активные элементы, выбираем первый по умолчанию
        if self.active_skill_items:
            # Находим первый активный навык
            for i, item in enumerate(menu_items):
                if item.enabled:
                    self.skills_list_menu.selected_index = i
                    self.selected_skill_index = 0  # Первый активный навык
                    break

    def show_skill_details(self, skill_index):
        """
        Показывает детальную информацию о выбранном навыке.
        
        Args:
            skill_index (int): Индекс навыка в списке активных навыков
        """
        # Сохраняем выбранный индекс
        self.selected_skill_index = skill_index
        
        # Если нет активных навыков, выходим
        if not self.active_skill_items or skill_index >= len(self.active_skill_items):
            return
            
        # Получаем выбранный навык
        skill = self.active_skill_items[skill_index]
        
        # Получаем навык игрока
        player_skill = self.game_system.player.get_skill(skill.id)
        if not player_skill:
            return
            
        # Очищаем панель с деталями
        self.skills_details_text.clear()
        
        # Отображаем заголовок навыка
        skill_name = f"{skill.icon} {skill.name} [{player_skill.level}/{player_skill.max_level}]"
        self.skills_details_text.add_text(skill_name, Color.BRIGHT_CYAN)
        
        # Отображаем прогресс навыка
        progress_percent = player_skill.get_experience_percent() * 100
        progress_bar = self._create_progress_bar(
            30, 
            progress_percent, 
            player_skill.current_experience, 
            player_skill.max_level_experience
        )
        progress_text = f"Прогресс: {progress_bar}"
        self.skills_details_text.add_text(progress_text, Color.YELLOW)
        
        # Отображаем описание навыка
        self.skills_details_text.add_text(skill.description, Color.WHITE)
        
        # Отображаем информацию о разблокировке
        if hasattr(skill, 'unlocked_at_level'):
            unlock_text = f"Разблокируется на уровне игрока: {skill.unlocked_at_level}"
            self.skills_details_text.add_text(unlock_text, Color.BRIGHT_CYAN)
        
        # Отображаем пассивные бонусы
        passive_bonuses = player_skill.get_passive_bonuses()
        if passive_bonuses:
            self.skills_details_text.add_text("", Color.WHITE)  # Пустая строка
            self.skills_details_text.add_text("Пассивные бонусы:", Color.BRIGHT_MAGENTA)
            for bonus_name, bonus_value in passive_bonuses.items():
                bonus_text = f"  • {bonus_name}: +{bonus_value}"
                self.skills_details_text.add_text(bonus_text, Color.MAGENTA)
        
        # Отображаем разблокированные способности
        unlocked_abilities = player_skill.get_unlocked_abilities()
        if unlocked_abilities:
            self.skills_details_text.add_text("", Color.WHITE)  # Пустая строка
            self.skills_details_text.add_text("Разблокированные способности:", Color.BRIGHT_CYAN)
            for ability in unlocked_abilities:
                self.skills_details_text.add_text(f"  • {ability}", Color.CYAN)
        
        # Отображаем будущие улучшения
        self.skills_details_text.add_text("", Color.WHITE)  # Пустая строка
        self.skills_details_text.add_text("Будущие улучшения:", Color.BRIGHT_YELLOW)
        
        # Показываем бонусы на следующих уровнях
        for level in range(player_skill.level + 1, player_skill.max_level + 1):
            # Проверяем наличие пассивных бонусов на этом уровне
            level_bonuses = player_skill.passive_bonuses.get(level, {})
            # Проверяем наличие способностей на этом уровне
            level_abilities = player_skill.unlocked_abilities.get(level, [])
            
            if level_bonuses or level_abilities:
                self.skills_details_text.add_text(f"Уровень {level}:", Color.BRIGHT_YELLOW)
                
                # Отображаем пассивные бонусы этого уровня
                if level_bonuses:
                    for bonus_name, bonus_value in level_bonuses.items():
                        self.skills_details_text.add_text(f"  • {bonus_name}: +{bonus_value}", Color.YELLOW)
                
                # Отображаем способности этого уровня
                if level_abilities:
                    for ability in level_abilities:
                        self.skills_details_text.add_text(f"  • Способность: {ability}", Color.YELLOW)
        
        # Обновляем видимость и фокус
        self.skills_details_text.visible = True
        self.skills_list_menu.visible = True
        
        # Устанавливаем фокус на список навыков и переходим в режим выбора навыка
        if self.skills_focus != "skills":
            self.skills_focus = "skills"
            self.skills_groups_menu.setFocused(False)
            self.skills_list_menu.setFocused(True)
            self.active_menu = self.skills_list_menu
    
    def _create_progress_bar(self, width, percent, current_exp=None, max_level_exp=None):
        """
        Создает текстовый прогресс-бар в виде 10 квадратов, где каждый квадрат представляет 10% прогресса.
        
        Args:
            width (int): Этот параметр больше не используется, но сохранен для совместимости
            percent (float): Процент заполнения (0.0 - 100.0)
            current_exp (int, optional): Текущий опыт
            max_level_exp (int, optional): Максимальный опыт для уровня
            
        Returns:
            str: Текстовый прогресс-бар с квадратами и числовыми значениями
        """
        # Преобразуем процент в количество заполненных квадратов (от 0 до 10)
        filled_squares = int(percent / 10)
        
        # Создаем строку с заполненными и пустыми квадратами
        progress_squares = "■" * filled_squares + "□" * (10 - filled_squares)
        
        # Если предоставлены данные об опыте, добавляем их справа от квадратов
        if current_exp is not None and max_level_exp is not None:
            return f"{progress_squares} [{current_exp} / {max_level_exp}]"
        else:
            return progress_squares