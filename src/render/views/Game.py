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
        
        self.setup_ui()
        self._fix_flex_panel()  # Добавляем метод set_content к FlexPanel
    
    def set_game_system(self, game_system):
        """
        Устанавливает ссылку на игровую систему.
        
        Args:
            game_system: Экземпляр GameSystem
        """
        self.game_system = game_system
        self.update_location_info()
        self.update_actions()
        
        # Инициализируем карту при первой установке системы
        if self.game_system.get_current_location():
            self._draw_location_map(self.game_system.get_current_location())
    
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
        self.tabs = ["Описание", "Персонажи", "Карта"]
        self.tab_keys = [49, 50, 51]  # Коды клавиш '1', '2', '3' для быстрого доступа
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
        
        # Устанавливаем новую активную вкладку
        self.current_tab = new_tab
        
        # Показываем новую вкладку
        if new_tab == 0:
            self.description_text.visible = True
        elif new_tab == 1:
            self.characters_text.visible = True
        
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
                    
                    # Если количество больше нуля, отображаем обычным способом
                    if amount > 0:
                        has_available_resources = True
                        self.resources_text.add_text(f"{resource_name}", resource_color, new_line=True)
                        self.resources_text.add_text(f" × ", Color.WHITE, new_line=False)
                        self.resources_text.add_text(f"{amount}", Color.BRIGHT_YELLOW, new_line=False)
                    else:
                        # Если количество равно нулю, показываем как "исчерпан"
                        self.resources_text.add_text(f"{resource_name}", Color.BRIGHT_BLACK, new_line=True)
                        self.resources_text.add_text(f" - ", Color.WHITE, new_line=False)
                        self.resources_text.add_text("исчерпан", Color.BRIGHT_BLACK, new_line=False)
                    
                    # Каждый ресурс занимает одну строку
                    resource_lines += 1
            
            # Если нет доступных ресурсов вообще, показываем сообщение
            if not has_available_resources:
                self.resources_text.clear()
                self.resources_text.add_text("Нет доступных ресурсов на локации", Color.BRIGHT_BLACK)
                resource_lines = 1
        else:
            self.resources_text.add_text("Нет доступных ресурсов на локации", Color.BRIGHT_BLACK)
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
                
                # Добавляем пункт меню для сбора ресурса
                items.append(MenuItem(
                    f"Добыть: {resource_name}",
                    create_collect_action(resource_id),
                    text_parts=[
                        {"text": "Добыть: ", "color": Color.WHITE},
                        {"text": resource_name, "color": resource_color}
                    ]
                ))
        
        # Добавляем разделитель между ресурсами и персонажами, если есть хотя бы один ресурс
        if has_resources:
            items.append(MenuItem("──────────────", None, enabled=False))
        
        # Добавляем действия диалога с персонажами
        has_characters = False
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
        Обрабатывает ввод с клавиатуры.
        Возвращает True, если ввод был обработан и требуется перерисовка.
        """
        # Проверяем горячие клавиши для вкладок
        if key in self.tab_keys:
            tab_index = self.tab_keys.index(key)
            self.switch_tab(tab_index, True)  # True - указывает, что это прямой переход на вкладку
            return True
            
        # Проверяем регистронезависимые номера клавиш
        # Для случая, когда указаны клавиши 1, 2, 3, но нажаты клавиши с Shift: !, @, #
        # ASCII коды: 1=49, !=33 | 2=50, @=64 | 3=51, #=35
        if key in [33, 64, 35]:  # Символы !, @, #
            shift_key_mapping = {33: 49, 64: 50, 35: 51}  # Маппинг символов с Shift к обычным цифрам
            normalized_key = shift_key_mapping[key]
            if normalized_key in self.tab_keys:
                tab_index = self.tab_keys.index(normalized_key)
                self.switch_tab(tab_index, True)
                return True
            
        # Переключение вкладок по Tab
        if key == Keys.TAB:
            self.switch_tab()
            return True
        
        # Убираем обработку переключения карты по нажатию G
        
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
    
    def update_ui(self):
        """
        Обновляет интерфейс. 
        Функция карты временно отключена.
        """
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