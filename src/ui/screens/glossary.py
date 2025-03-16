from time import time
from colorama import Fore, Style

def show_glossary(self):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Отображает глоссарий игры с разными категориями"""
    current_tab = 0
    tabs = ["Ресурсы", "Персонажи"]
    search_query = ""
    search_mode = False
    
    # Списки элементов для выбора
    selectable_items = []
    current_selection = 0
    
    while self.running:
        self.clear_screen()
        
        # Получаем данные в зависимости от текущей вкладки
        if current_tab == 0:  # Ресурсы
            all_items = self.game.get_glossary_resources()
        else:  # Персонажи
            all_items = self.game.get_glossary_npcs()
        
        # Применяем фильтр поиска, если задан
        filtered_items = {}
        if search_query:
            for item_id, item_info in all_items.items():
                if (search_query.lower() in item_id.lower() or 
                        search_query.lower() in item_info['name'].lower() or
                        search_query.lower() in item_info['description'].lower()):
                    filtered_items[item_id] = item_info
            display_items = filtered_items
        else:
            display_items = all_items
        
        # Обновляем список выбираемых элементов
        selectable_items = list(display_items.keys())
        if selectable_items and current_selection >= len(selectable_items):
            current_selection = len(selectable_items) - 1
        
        # Рисуем заголовок
        self.draw_box(80, "ГЛОССАРИЙ")
        
        # Отображаем поле поиска
        if search_mode:
            search_color = self.highlight_color
        else:
            search_color = self.normal_color
            
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {search_color}Поиск: {search_query + '▌' if search_mode else search_query}{Style.RESET_ALL}")
        
        # Отображаем вкладки
        tab_line = ""
        for i, tab in enumerate(tabs):
            if i == current_tab:
                tab_line += f"{self.selected_color} [{tab}] {Style.RESET_ALL}"
            else:
                tab_line += f" {tab} "
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {tab_line}")
        
        if search_query and not display_items:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.info_color}Ничего не найдено по запросу '{search_query}'{Style.RESET_ALL}")
        
        self.draw_separator(80)
        
        # Отображаем содержимое текущей вкладки
        if not display_items:
            if current_tab == 0:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.normal_color}В глоссарии пока нет ресурсов.{Style.RESET_ALL}")
            else:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.normal_color}В глоссарии пока нет персонажей.{Style.RESET_ALL}")
        else:
            for i, (item_id, item_info) in enumerate(display_items.items()):
                # Определяем цвет и стиль для выбранного элемента
                if i == current_selection and selectable_items:
                    item_style = self.selected_color
                    prefix = "➤ "
                    highlight_box = True
                else:
                    item_style = self.highlight_color
                    prefix = "  "
                    highlight_box = False
                
                # Проверяем, отслеживается ли этот элемент
                is_tracked = (self.game.tracked_target == item_id and 
                                ((current_tab == 0 and self.game.tracked_target_type == "resource") or
                                (current_tab == 1 and self.game.tracked_target_type == "npc")))
                
                track_indicator = "🔍 " if is_tracked else ""
                
                # Создаем мини-рамку для каждого элемента
                if highlight_box:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {prefix}{self.selected_color}┌─{'─' * (len(item_info['name']) + len(track_indicator) + 2)}┐{Style.RESET_ALL}")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {prefix}{self.selected_color}│ {track_indicator}{item_info['name']} │{Style.RESET_ALL}")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {prefix}{self.selected_color}└─{'─' * (len(item_info['name']) + len(track_indicator) + 2)}┘{Style.RESET_ALL}")
                else:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {prefix}{item_style}{track_indicator}{item_info['name']}{Style.RESET_ALL}")
                
                # Описание с отступом и оформлением
                wrapped_desc = self.wrap_text(item_info['description'], 70, 5)
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}     {Fore.LIGHTCYAN_EX}Описание:{Style.RESET_ALL} {wrapped_desc}")
                
                # Отображаем локации с улучшенным оформлением
                if current_tab == 0:  # Для ресурсов
                    if item_info["locations"]:
                        location_names = []
                        
                        # Проверяем, отслеживается ли этот ресурс
                        is_resource_tracked = (self.game.tracked_target == item_id and 
                                                self.game.tracked_target_type == "resource")
                        
                        for loc_id in item_info["locations"]:
                            location = self.game.get_location(loc_id)
                            loc_name = location.name if location else loc_id
                            
                            # Если этот ресурс отслеживается и эта локация текущая цель
                            if is_resource_tracked and loc_id == self.game.tracked_location:
                                loc_name = f"{loc_name} {Fore.LIGHTGREEN_EX}[⟐ текущая цель]{Style.RESET_ALL}"
                            
                            location_names.append(loc_name)
                        
                        location_str = ", ".join(location_names)
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}     {Fore.LIGHTYELLOW_EX}Можно найти в:{Style.RESET_ALL} {location_str}")
                    else:
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}     {Fore.LIGHTYELLOW_EX}Место обнаружения:{Style.RESET_ALL} {Fore.LIGHTRED_EX}Неизвестно{Style.RESET_ALL}")
                else:  # Для NPC
                    if item_info["location"]:
                        location = self.game.get_location(item_info["location"])
                        location_name = location.name if location else item_info["location"]
                        
                        # Если этот NPC отслеживается
                        if (self.game.tracked_target == item_id and 
                            self.game.tracked_target_type == "npc"):
                            location_name = f"{location_name} {Fore.LIGHTGREEN_EX}[⟐ текущая цель]{Style.RESET_ALL}"
                            
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}     {Fore.LIGHTYELLOW_EX}Находится в:{Style.RESET_ALL} {location_name}")
                    else:
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}     {Fore.LIGHTYELLOW_EX}Местоположение:{Style.RESET_ALL} {Fore.LIGHTRED_EX}Неизвестно{Style.RESET_ALL}")
                
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        # Отображаем подсказки и ждем нажатия клавиши
        self.draw_separator(80)
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} [←][→] Вкладки | [↑][↓] Выбор | [Y] Отследить | [/] Поиск | [ESC] Назад")
        self.draw_bottom_box(80)
        
        # Получаем нажатую клавишу
        if search_mode:
            # Используем обычный ввод для поиска
            key = input()
            if key == "":
                # Enter завершает режим поиска
                search_mode = False
                current_selection = 0  # Сбрасываем выбор на первый элемент
            elif key.lower() == "esc" or key == "\x1b":
                # Escape отменяет режим поиска
                search_mode = False
                search_query = ""
            else:
                # Обновляем строку поиска
                search_query = key
            continue
        
        key = self.get_key()
        
        if key == 'LEFT':
            current_tab = (current_tab - 1) % len(tabs)
            current_selection = 0  # Сбрасываем выбор при смене вкладки
        elif key == 'RIGHT':
            current_tab = (current_tab + 1) % len(tabs)
            current_selection = 0  # Сбрасываем выбор при смене вкладки
        elif key == 'UP' and selectable_items:
            current_selection = (current_selection - 1) % len(selectable_items)
        elif key == 'DOWN' and selectable_items:
            current_selection = (current_selection + 1) % len(selectable_items)
        elif key == '/' or key == '?':
            # Включаем режим поиска
            search_mode = True
            search_query = ""
        elif key in ['y', 'Y'] and selectable_items:
            # Отслеживаем выбранный элемент
            selected_id = selectable_items[current_selection]
            target_type = "resource" if current_tab == 0 else "npc"
            
            # Устанавливаем или отменяем отслеживание
            if (self.game.tracked_target == selected_id and 
                ((current_tab == 0 and self.game.tracked_target_type == "resource") or
                    (current_tab == 1 and self.game.tracked_target_type == "npc"))):
                # Если этот элемент уже отслеживается, отменяем отслеживание
                self.game.untrack_target()
            else:
                # Иначе начинаем отслеживать
                success = self.game.track_target(selected_id, target_type)
                if not success:
                    print(f"{self.error_color}Невозможно отследить этот элемент.{Style.RESET_ALL}")
                    time.sleep(1)
        elif key in ['\x1b', 'q', 'Q', 'ESC']:
            return  # Выходим из глоссария при нажатии ESC