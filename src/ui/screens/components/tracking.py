from colorama import Fore, Style


def print_tracked_target(self):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Отображает информацию о текущей отслеживаемой цели в игровом интерфейсе"""
    tracked_info = self.game.get_tracked_target_info()
    if not tracked_info:
        return False
        
    target_name = tracked_info["name"]
    target_type = tracked_info["target_type"]
    location_name = tracked_info["location_name"]
    path = tracked_info["path"]
    
    # Определяем иконку в зависимости от типа
    icon = ICONS['resource'] if target_type == "resource" else ICONS['npc']
    
    # Отображаем название цели в оранжевом цвете
    target_title = f"{Fore.LIGHTYELLOW_EX}{target_name}{Style.RESET_ALL}"
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Отслеживание:{Style.RESET_ALL} {icon} {target_title}")
    
    # Отображаем местоположение цели
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {Fore.LIGHTCYAN_EX}Находится в:{Style.RESET_ALL} {location_name}")
    
    # Отображаем маршрут, если игрок не в той же локации
    if path:
        next_location = self.game.get_location(path[0])
        next_location_name = next_location.name if next_location else path[0]
        
        # Показываем следующую локацию на пути и количество переходов
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {Fore.LIGHTCYAN_EX}Следующий шаг:{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}➤ {next_location_name}{Style.RESET_ALL}")
        
        if len(path) > 1:
            # Отображаем полный маршрут более наглядно
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {Fore.LIGHTCYAN_EX}Полный маршрут:{Style.RESET_ALL}", end="")
            
            # Текущая локация игрока
            current_location = self.game.player.current_location
            print(f" {current_location.name}", end="")
            
            # Промежуточные локации маршрута
            for i, loc_id in enumerate(path):
                loc = self.game.get_location(loc_id)
                loc_name = loc.name if loc else loc_id
                
                # Последняя локация - целевая, отображаем другим цветом
                if i == len(path) - 1:
                    print(f" {Fore.LIGHTYELLOW_EX}➤ {Fore.LIGHTGREEN_EX}{loc_name}{Style.RESET_ALL}")
                else:
                    print(f" {Fore.LIGHTYELLOW_EX}➤{Style.RESET_ALL} {loc_name}", end="")
            
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {Fore.LIGHTCYAN_EX}Всего переходов:{Style.RESET_ALL} {len(path)}")
    else:
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {Fore.GREEN}Вы находитесь в нужной локации!{Style.RESET_ALL}")
        
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
    return True
    
def print_tracked_quest(self):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Отображает информацию о текущем отслеживаемом квесте в игровом интерфейсе"""
    if self.game.tracked_quest_id:
        quest = self.game.active_quests.get(self.game.tracked_quest_id)
        if quest:
            current_stage = quest.get_current_stage()
            if current_stage:
                # Отображаем название квеста в оранжевом цвете
                quest_name = f"{Fore.LIGHTYELLOW_EX}{quest.name}{Style.RESET_ALL}"
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Квест:{Style.RESET_ALL} {quest_name}")
                
                # Отображаем цели текущей стадии
                progress_lines = quest.get_progress_text(self.game).split('\n')
                for line in progress_lines:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {line}")
                
                # Если квест готов к завершению, показываем информацию
                if quest.is_ready_to_complete() and quest.taker_id:
                    npc = self.game.get_npc(quest.taker_id)
                    npc_name = npc.name if npc else quest.taker_id
                    
                    # Получаем имя локации вместо ID
                    location_id = npc.location_id if npc else "неизвестная локация"
                    location = self.game.get_location(location_id)
                    location_name = location.name if location else location_id
                    
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}Квест готов к завершению! Поговорите с {npc_name} в локации {location_name}{Style.RESET_ALL}")
                
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
            
                
                return True
    return False