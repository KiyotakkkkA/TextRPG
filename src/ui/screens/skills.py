from colorama import Fore, Style

def show_skills(self):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Отображает навыки игрока с информацией о прогрессе и разблокированных предметах"""
    self.clear_screen()
    self.draw_box(80, "НАВЫКИ")
    
    skills = self.player.get_skills()
    
    if not skills:
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.error_color}У вас пока нет навыков!{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        self.get_key()
        return
    
    # Определяем максимальную длину для каждого столбца
    max_name_length = max([len(skill.name) for skill in skills], default=0)
    max_level_length = max([len(str(skill.level)) for skill in skills], default=0)
    
    # Выводим заголовок таблицы
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {'Навык':<{max_name_length}} {'Уровень':>{max_level_length+2}} {'Прогресс':<15} {'До следующего':<15}")
    self.draw_separator(80)
    
    # Выводим каждый навык с выравниванием
    for skill in skills:
        # Иконка навыка
        skill_icon = ICONS.get(skill.id, '📊')
        
        name_part = f"{skill_icon} {skill.name:<{max_name_length-2}}"
        level_part = f"{skill.level:>{max_level_length}}"
        
        # Создаем прогресс-бар
        progress = skill.get_progress_to_next_level()
        progress_bar_length = 10
        filled_length = int(progress_bar_length * progress)
        progress_bar = f"[{Fore.GREEN}{'■' * filled_length}{Style.RESET_ALL}{'□' * (progress_bar_length - filled_length)}]"
        progress_percent = f"{int(progress * 100)}%"
        
        # Информация о следующем уровне
        next_level = skill.get_next_level()
        exp_to_next = skill.get_exp_to_next_level()
        
        # Добавляем информацию о формуле расчета опыта
        base_exp = skill.base_exp
        exp_factor = skill.exp_factor
        exp_formula = f"Формула: {base_exp} × {exp_factor}^(уровень-1)"
        
        next_level_info = f"{exp_to_next} опыта" if next_level else "Макс. уровень"
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {name_part} {level_part} {progress_bar} {progress_percent} {next_level_info}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {Fore.CYAN}Описание:{Style.RESET_ALL} {skill.description}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {Fore.CYAN}Расчет XP:{Style.RESET_ALL} {exp_formula}")
        
        # Выводим разблокированные предметы текущего уровня
        current_unlocks = skill.get_unlocked_items_at_level(skill.level)
        if current_unlocks:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {Fore.GREEN}Доступно сейчас:{Style.RESET_ALL}")
            # Выводим по 3 предмета в строке
            items_shown = 0
            item_line = f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}     "
            for item_id in current_unlocks:
                item_data = self.game.get_item(item_id)
                if item_data and "name" in item_data:
                    item_name = item_data["name"]
                    if items_shown > 0 and items_shown % 3 == 0:
                        print(item_line)
                        item_line = f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}     "
                    item_line += f"{item_name}, "
                    items_shown += 1
            if item_line != f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}     ":
                print(item_line.rstrip(", "))
        
        # Выводим предметы, которые будут разблокированы на следующем уровне
        if next_level:
            next_unlocks = skill.get_unlocked_items_at_level(next_level)
            if next_unlocks:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {Fore.YELLOW}На уровне {next_level}:{Style.RESET_ALL}")
                items_shown = 0
                item_line = f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}     "
                for item_id in next_unlocks:
                    item_data = self.game.get_item(item_id)
                    if item_data and "name" in item_data:
                        item_name = item_data["name"]
                        if items_shown > 0 and items_shown % 3 == 0:
                            print(item_line)
                            item_line = f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}     "
                        item_line += f"{item_name}, "
                        items_shown += 1
                if item_line != f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}     ":
                    print(item_line.rstrip(", "))
        
        # Если это не последний навык, добавляем разделитель
        if skill != skills[-1]:
            self.draw_separator(80)
    
    # Выводим уведомление о получении опыта
    self.draw_separator(80)
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}Совет:{Style.RESET_ALL} Собирайте ресурсы для получения опыта и повышения уровня навыков.")
    
    self.draw_bottom_box(80)
    print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
    self.get_key()