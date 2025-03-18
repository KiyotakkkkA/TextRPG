from time import time
from colorama import Fore, Style

def show_glossary(self):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Отображает глоссарий игры с разными категориями"""
    current_tab = 0
    tabs = ["Ресурсы", "Персонажи", "Монстры"]
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
        elif current_tab == 1:  # Персонажи
            all_items = self.game.get_glossary_npcs()
        else:  # Монстры
            all_items = self.game.get_glossary_monsters()
        
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
            
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
              f"{search_color}Поиск:{Style.RESET_ALL} {search_query}" + 
              " " * (70 - len(search_query) - 7))
        
        # Отображаем вкладки
        self.draw_separator(80)
        tab_line = f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} "
        for i, tab in enumerate(tabs):
            if i == current_tab:
                tab_line += f"{self.selected_color}{tab}{Style.RESET_ALL} | "
            else:
                tab_line += f"{self.normal_color}{tab}{Style.RESET_ALL} | "
        print(tab_line.rstrip('| '))
        
        self.draw_separator(80)
        
        # Получаем информацию о текущей отслеживаемой цели
        tracked_info = self.game.get_tracked_target_info()
        tracked_target_id = tracked_info["target_id"] if tracked_info else None
        tracked_target_type = tracked_info["target_type"] if tracked_info else None
        
        # Отображаем список элементов
        if not display_items:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
                  f"{self.error_color}Нет доступных записей{Style.RESET_ALL}")
        else:
            for i, (item_id, item_info) in enumerate(display_items.items()):
                # Определяем иконку в зависимости от вкладки
                if current_tab == 0:  # Ресурсы
                    icon = ICONS.get('resource', '📦')
                    current_type = "resource"
                elif current_tab == 1:  # Персонажи
                    icon = ICONS.get('npc', '👤')
                    current_type = "npc"
                else:  # Монстры
                    icon = ICONS.get('monster', '👹')
                    current_type = "monster"
                
                # Добавляем иконку лупы, если эта цель отслеживается
                is_tracked = (tracked_target_id == item_id and tracked_target_type == current_type)
                track_icon = "🔍 " if is_tracked else ""
                
                if i == current_selection:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
                          f"{self.selected_color}❯ {track_icon}{icon} {item_info['name']}{Style.RESET_ALL}")
                else:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   " +
                          f"{track_icon}{icon} {item_info['name']}")
        
        self.draw_separator(80)
        
        # Если есть выбранный элемент, показываем его описание
        if selectable_items and current_selection < len(selectable_items):
            selected_id = selectable_items[current_selection]
            selected_item = display_items[selected_id]
            
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
                  f"{self.highlight_color}{selected_item['name']} ({selected_id}){Style.RESET_ALL}")
            
            # Описание элемента
            description = selected_item.get('description', 'Нет описания')
            # Разбиваем описание на строки по 70 символов
            desc_lines = [description[i:i+70] for i in range(0, len(description), 70)]
            for line in desc_lines:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {line}")
            
            # Дополнительная информация в зависимости от вкладки
            if current_tab == 0:  # Ресурсы
                locations = selected_item.get('locations', [])
                if locations:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} ")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
                          f"{self.highlight_color}Встречается в локациях:{Style.RESET_ALL}")
                    for loc_id in locations:
                        loc = self.game.get_location(loc_id)
                        loc_name = loc.name if loc else loc_id
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   " +
                              f"{ICONS.get('location', '🗺️')} {loc_name}")
            
            elif current_tab == 1:  # Персонажи
                location_id = selected_item.get('location')
                if location_id:
                    loc = self.game.get_location(location_id)
                    loc_name = loc.name if loc else location_id
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} ")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
                          f"{self.highlight_color}Находится в:{Style.RESET_ALL} " +
                          f"{ICONS.get('location', '🗺️')} {loc_name}")
            
            else:  # Монстры
                level = selected_item.get('level', 1)
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} ")
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
                      f"{self.highlight_color}Уровень:{Style.RESET_ALL} {level}")
                
                locations = selected_item.get('locations', [])
                if locations:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} ")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
                          f"{self.highlight_color}Встречается в локациях:{Style.RESET_ALL}")
                    for loc_id in locations:
                        loc = self.game.get_location(loc_id)
                        loc_name = loc.name if loc else loc_id
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   " +
                              f"{ICONS.get('location', '🗺️')} {loc_name}")
        
        self.draw_separator(80)
        
        # Отображаем подсказки управления
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
              f"{self.normal_color}←→: Смена вкладки | " +
              f"↑↓: Навигация | " +
              f"Y: Отслеживать | " +
              f"S: Поиск | " +
              f"Esc: Назад{Style.RESET_ALL}")
        
        # Нижняя часть рамки
        self.draw_bottom_box(80)
        
        # Обрабатываем ввод пользователя
        key = self.get_key()
        
        if key == 'ESC':
            if search_mode:
                search_mode = False
                search_query = ""
            else:
                break
        
        elif key == 'LEFT' and not search_mode:
            current_tab = (current_tab - 1) % len(tabs)
            current_selection = 0
        
        elif key == 'RIGHT' and not search_mode:
            current_tab = (current_tab + 1) % len(tabs)
            current_selection = 0
        
        elif key == 'UP' and not search_mode:
            if selectable_items:
                current_selection = (current_selection - 1) % len(selectable_items)
        
        elif key == 'DOWN' and not search_mode:
            if selectable_items:
                current_selection = (current_selection + 1) % len(selectable_items)
        
        elif (key == 'Y' or key == 'y') and not search_mode:
            # Отслеживание выбранной цели
            if selectable_items and current_selection < len(selectable_items):
                selected_id = selectable_items[current_selection]
                
                # Определяем тип цели в зависимости от вкладки
                if current_tab == 0:  # Ресурсы
                    target_type = "resource"
                elif current_tab == 1:  # Персонажи
                    target_type = "npc"
                else:  # Монстры
                    target_type = "monster"
                
                # Устанавливаем или снимаем отслеживание
                is_currently_tracked = (tracked_target_id == selected_id and tracked_target_type == target_type)
                item_name = display_items[selected_id].get('name', selected_id)
                tracking_result = self.game.track_target(selected_id, target_type)
                
                # Показываем сообщение об успешном отслеживании или снятии отслеживания
                if is_currently_tracked:
                    self.show_message(f"{Fore.CYAN}Отслеживание цели {item_name} отменено!{Style.RESET_ALL}")
                elif tracking_result:
                    self.show_message(f"{Fore.GREEN}Цель {item_name} отслеживается!{Style.RESET_ALL}")
                else:
                    self.show_message(f"{Fore.RED}Невозможно отслеживать цель {item_name}!{Style.RESET_ALL}")
            else:
                self.show_message(f"{Fore.RED}Нет выбранной цели для отслеживания!{Style.RESET_ALL}")
        
        elif key == 'S' or key == 's':
            search_mode = not search_mode
            if not search_mode:
                search_query = ""
        
        elif search_mode:
            if key == 'BACKSPACE':
                search_query = search_query[:-1]
            elif key == 'ENTER':
                search_mode = False
            elif len(key) == 1:  # Если это печатный символ
                search_query += key