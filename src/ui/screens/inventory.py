from colorama import Fore, Style


def format_resource_name(self, resource_id):
    """Возвращает название ресурса без количества"""
    item_data = self.game.get_item(resource_id)
    if item_data and "name" in item_data:
        return item_data['name']
    return resource_id
    
def show_inventory(self):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Показывает инвентарь игрока и позволяет взаимодействовать с предметами"""
    self.clear_screen()
    self.draw_box(80, "ИНВЕНТАРЬ")
    
    # Добавляем статистику персонажа
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['player']} {self.highlight_color}Статистика персонажа:{Style.RESET_ALL}")
    
    # Статистика в виде таблицы
    hp_bar = self.create_progress_bar(self.player.health, self.player.max_health, 15, Fore.RED)
    mp_bar = self.create_progress_bar(self.player.mana, self.player.max_mana, 15, Fore.BLUE)
    sp_bar = self.create_progress_bar(self.player.stamina, self.player.max_stamina, 15, Fore.GREEN)
    xp_bar = self.create_progress_bar(self.player.experience, self.player.exp_to_next_level, 15, Fore.YELLOW)
    
    # Форматируем строки для выравнивания в таблице
    hp_text = f"{self.player.health}/{self.player.max_health}"
    mp_text = f"{self.player.mana}/{self.player.max_mana}"
    sp_text = f"{self.player.stamina}/{self.player.max_stamina}"
    xp_text = f"{self.player.experience}/{self.player.exp_to_next_level}"
    
    col_width = 25  # Ширина колонки
    
    # Первая строка
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}{'Здоровье:':<10}{Style.RESET_ALL} {hp_bar} {hp_text:<8}", end="")
    print(f"{Fore.BLUE}{'Мана:':<10}{Style.RESET_ALL} {mp_bar} {mp_text:<8}")
    
    # Вторая строка
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}{'Выносл.:':<10}{Style.RESET_ALL} {sp_bar} {sp_text:<8}", end="")
    print(f"{Fore.YELLOW}{'Опыт:':<10}{Style.RESET_ALL} {xp_bar} {xp_text:<8}")
    
    # Третья строка с уровнем и деньгами
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}{'Уровень:':<10}{Style.RESET_ALL} {self.player.level:<23}", end="")
    print(f"{Fore.YELLOW}{'Деньги:':<10}{Style.RESET_ALL} {self.player.money} монет")
    
    # Разделитель
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
    self.draw_separator(80)
    
    # Далее отображаем предметы инвентаря, как и раньше
    items = self.player.inventory.get_items()
    
    if not items:
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.error_color}Инвентарь пуст!{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        self.get_key()
        return
        
    # Сортируем предметы по редкости
    rarity_info = {
        "COMMON": {"order": 1, "color": Fore.WHITE, "name": "Обычный", "icon": ICONS['common']},
        "UNCOMMON": {"order": 2, "color": Fore.GREEN, "name": "Необычный", "icon": ICONS['uncommon']},
        "RARE": {"order": 3, "color": Fore.LIGHTBLUE_EX, "name": "Редкий", "icon": ICONS['rare']},
        "EPIC": {"order": 4, "color": Fore.MAGENTA, "name": "Эпический", "icon": ICONS['epic']},
        "LEGENDARY": {"order": 5, "color": Fore.YELLOW, "name": "Легендарный", "icon": ICONS['legendary']},
        "MYTHIC": {"order": 6, "color": Fore.RED, "name": "Мифический", "icon": ICONS['mythic']}
    }
    
    # Добавим проверку на случай, если get_rarity() не вернет правильное значение
    items.sort(key=lambda x: rarity_info.get(x.get_rarity(), {"order": 999})["order"])
    
    # Определяем максимальную длину для каждого столбца
    max_name_length = max([len(item.name) for item in items], default=0)
    max_count_length = max([len(str(item.get_count())) for item in items], default=0)
    max_type_length = max([len(item.get_type()) for item in items], default=0)
    max_rarity_length = max([len(rarity_info[item.get_rarity()]["name"]) for item in items], default=0)
    
    # Выводим заголовок таблицы
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {'Название':<{max_name_length}} {'Кол-во':>{max_count_length+3}} {'Тип':<{max_type_length+2}} {'Редкость':<{max_rarity_length+2}}")
    self.draw_separator(80)
    
    # Выводим каждый предмет с выравниванием и учетом редкости
    for item in items:
        rarity_color = rarity_info[item.get_rarity()]["color"]
        rarity_name = rarity_info[item.get_rarity()]["name"]
        rarity_icon = rarity_info[item.get_rarity()]["icon"]
        
        # Форматируем части строки
        name_part = f"{item.name:<{max_name_length}}"
        count_part = f"({Fore.YELLOW}{item.get_count():>{max_count_length}}{Style.RESET_ALL})"
        type_part = f"[{Fore.CYAN}{item.get_type():<{max_type_length}}{Style.RESET_ALL}]"
        rarity_part = f"{rarity_icon} {rarity_color}{rarity_name}{Style.RESET_ALL}"
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {name_part} {count_part} {type_part} - {rarity_part}")
    
    self.draw_bottom_box(80)
    print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
    self.get_key()