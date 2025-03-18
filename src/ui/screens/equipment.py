import os
import readchar
from colorama import Fore, Back, Style

# Константы для отображения UI - более красивые рамки
BOX_CHARS = {
    "h_line": "━",
    "v_line": "┃",
    "tl_corner": "┏",
    "tr_corner": "┓",
    "bl_corner": "┗",
    "br_corner": "┛",
    "l_connector": "┣",
    "r_connector": "┫",
    "t_connector": "┳",
    "b_connector": "┻",
    "cross": "╋"
}

# Перевод слотов на русский язык для UI
SLOT_NAMES = {
    "head": "Голова",
    "body": "Тело",
    "legs": "Ноги",
    "feet": "Ступни",
    "hands": "Руки",
    "weapon": "Оружие",
    "offhand": "Левая рука",
    "accessory1": "Аксессуар 1",
    "accessory2": "Аксессуар 2"
}

# Цвета для характеристик
STAT_COLORS = {
    "defense": Fore.BLUE,
    "attack": Fore.RED,
    "magic": Fore.MAGENTA,
    "durability": Fore.GREEN,
    "weight": Fore.YELLOW
}

# Иконки для характеристик
STAT_ICONS = {
    "defense": "🛡️",
    "attack": "⚔️",
    "magic": "✨",
    "durability": "⚒️",
    "weight": "⚖️"
}

# Иконки для слотов
SLOT_ICONS = {
    "head": "👑",
    "body": "👕",
    "legs": "👖",
    "feet": "👢",
    "hands": "🧤",
    "weapon": "🗡️",
    "offhand": "🛡️",
    "accessory1": "💍",
    "accessory2": "📿"
}

def draw_box(width, title=None, color=Fore.CYAN):
    """Рисует красивую рамку с заголовком"""
    # Верхняя граница
    if title:
        title_len = len(title) + 4  # Добавляем отступы для заголовка
        left_padding = (width - title_len) // 2
        right_padding = width - title_len - left_padding
        
        print(f"{color}{BOX_CHARS['tl_corner']}{BOX_CHARS['h_line'] * left_padding} {title} {BOX_CHARS['h_line'] * right_padding}{BOX_CHARS['tr_corner']}{Style.RESET_ALL}")
    else:
        print(f"{color}{BOX_CHARS['tl_corner']}{BOX_CHARS['h_line'] * (width-2)}{BOX_CHARS['tr_corner']}{Style.RESET_ALL}")

def draw_bottom_box(width, color=Fore.CYAN):
    """Рисует нижнюю часть рамки"""
    print(f"{color}{BOX_CHARS['bl_corner']}{BOX_CHARS['h_line'] * (width-2)}{BOX_CHARS['br_corner']}{Style.RESET_ALL}")

def draw_separator(width, color=Fore.CYAN):
    """Рисует разделитель в рамке"""
    print(f"{color}{BOX_CHARS['l_connector']}{BOX_CHARS['h_line'] * (width-2)}{BOX_CHARS['r_connector']}{Style.RESET_ALL}")

def draw_vertical_line(color=Fore.CYAN):
    """Рисует вертикальную линию"""
    return f"{color}{BOX_CHARS['v_line']}{Style.RESET_ALL}"

def show_equipment(game_menu):
    """Отображает экран экипировки и позволяет управлять ею"""
    
    # Получаем ссылки на нужные объекты
    player = game_menu.game.player
    equipment = player.get_equipped_items()
    bonuses = player.get_equipment_bonuses()
    
    # Список слотов для навигации
    slots = list(equipment.keys())
    current_slot_index = 0
    
    # Флаг для отображения инвентаря при нажатии Enter на пустом слоте
    show_inventory_items = False
    current_item_index = 0
    
    # Главный цикл экрана экипировки
    while True:
        # Обновляем список экипировки и бонусы для корректного отображения
        equipment = player.get_equipped_items()
        bonuses = player.get_equipment_bonuses()
        
        game_menu.clear_screen()
        
        # Отображаем заголовок
        draw_box(80, "Экипировка", Fore.CYAN)
        
        # Создаем два столбца для экрана
        if not show_inventory_items:
            # Левая часть с информацией о слотах
            print(f"{draw_vertical_line()} {Fore.CYAN}Слоты экипировки:{Style.RESET_ALL}")
            
            for i, slot in enumerate(slots):
                slot_name = SLOT_NAMES.get(slot, slot)
                item = equipment[slot]
                slot_icon = SLOT_ICONS.get(slot, "📦")
                
                # Отображаем слот и предмет, если он есть
                if i == current_slot_index:
                    slot_marker = f"{Fore.YELLOW}>{Style.RESET_ALL}"
                else:
                    slot_marker = " "
                
                if item:
                    rarity_color = game_menu.get_rarity_color(item.get_rarity())
                    print(f"{draw_vertical_line()} {slot_marker} {slot_icon} {slot_name}: {rarity_color}{item.name}{Style.RESET_ALL}")
                else:
                    print(f"{draw_vertical_line()} {slot_marker} {slot_icon} {slot_name}: {Fore.LIGHTBLACK_EX}Пусто{Style.RESET_ALL}")
            
            print(f"{draw_vertical_line()}")
            draw_separator(80)
            
            # Бонусы от экипировки
            print(f"{draw_vertical_line()} {Fore.CYAN}Бонусы от экипировки:{Style.RESET_ALL}")
            
            for stat, value in bonuses.items():
                color = STAT_COLORS.get(stat, Fore.WHITE)
                stat_name = stat.capitalize()
                stat_icon = STAT_ICONS.get(stat, "🔹")
                
                # Добавляем цветную полоску для визуального отображения
                if value > 0:
                    bar = color + "■" * min(value, 10) + Style.RESET_ALL
                else:
                    bar = Fore.LIGHTBLACK_EX + "□" * 5 + Style.RESET_ALL
                
                print(f"{draw_vertical_line()} {stat_icon} {stat_name}: {color}+{value}{Style.RESET_ALL} {bar}")
            
            print(f"{draw_vertical_line()}")
            draw_separator(80)
            
            # Информация о выбранном предмете
            current_slot = slots[current_slot_index]
            item = equipment[current_slot]
            
            print(f"{draw_vertical_line()} {Fore.CYAN}Информация о слоте:{Style.RESET_ALL}")
            print(f"{draw_vertical_line()} {SLOT_ICONS.get(current_slot, '📦')} {Fore.CYAN}{SLOT_NAMES.get(current_slot, current_slot)}{Style.RESET_ALL}")
            
            if item:
                # Детали выбранного предмета
                rarity_color = game_menu.get_rarity_color(item.get_rarity())
                rarity_name = get_rarity_name(item.get_rarity())
                
                print(f"{draw_vertical_line()}")
                print(f"{draw_vertical_line()} {Fore.CYAN}Информация о предмете:{Style.RESET_ALL}")
                print(f"{draw_vertical_line()} {rarity_color}{item.name}{Style.RESET_ALL} - {rarity_color}{rarity_name}{Style.RESET_ALL}")
                print(f"{draw_vertical_line()} {Fore.WHITE}{item.get_description()}{Style.RESET_ALL}")
                
                # Отображаем характеристики, если они есть
                if hasattr(item, 'characteristics') and item.characteristics:
                    print(f"{draw_vertical_line()}")
                    print(f"{draw_vertical_line()} {Fore.CYAN}Характеристики:{Style.RESET_ALL}")
                    
                    for stat, value in item.characteristics.items():
                        color = STAT_COLORS.get(stat, Fore.WHITE)
                        stat_name = stat.capitalize()
                        stat_icon = STAT_ICONS.get(stat, "🔹")
                        
                        print(f"{draw_vertical_line()} {stat_icon} {stat_name}: {color}{value}{Style.RESET_ALL}")
            else:
                print(f"{draw_vertical_line()} {Fore.LIGHTBLACK_EX}Слот пуст{Style.RESET_ALL}")
                print(f"{draw_vertical_line()}")
                
                # Проверяем, есть ли в инвентаре предметы для этого слота
                all_items = player.inventory.get_items()
                equippable_items = [item for item in all_items if hasattr(item, 'get_slot') and item.get_slot() == current_slot]
                
                if equippable_items:
                    print(f"{draw_vertical_line()} {Fore.YELLOW}Нажмите Enter, чтобы просмотреть доступные предметы{Style.RESET_ALL}")
                else:
                    print(f"{draw_vertical_line()} {Fore.LIGHTBLACK_EX}У вас нет предметов для этого слота{Style.RESET_ALL}")
            
            # Нижняя часть с кнопками
            print(f"{draw_vertical_line()}")
            draw_separator(80)
            print(f"{draw_vertical_line()} {Fore.CYAN}Управление:{Style.RESET_ALL}")
            
            if item:
                print(f"{draw_vertical_line()} {Fore.GREEN}[Пробел]{Style.RESET_ALL} Снять предмет   {Fore.YELLOW}[↑/↓]{Style.RESET_ALL} Выбрать слот   {Fore.RED}[Esc]{Style.RESET_ALL} Выход")
            else:
                # Проверяем, можно ли надеть предмет в этот слот
                all_items = player.inventory.get_items()
                equippable_items = [item for item in all_items if hasattr(item, 'get_slot') and item.get_slot() == current_slot]
                
                if equippable_items:
                    print(f"{draw_vertical_line()} {Fore.GREEN}[Enter]{Style.RESET_ALL} Надеть предмет   {Fore.YELLOW}[↑/↓]{Style.RESET_ALL} Выбрать слот   {Fore.RED}[Esc]{Style.RESET_ALL} Выход")
                else:
                    print(f"{draw_vertical_line()} {Fore.YELLOW}[↑/↓]{Style.RESET_ALL} Выбрать слот   {Fore.RED}[Esc]{Style.RESET_ALL} Выход")
        else:
            # Инвентарь с экипируемыми предметами для выбранного слота
            all_items = player.inventory.get_items()
            current_slot = slots[current_slot_index]
            equippable_items = [item for item in all_items if hasattr(item, 'get_slot') and item.get_slot() == current_slot]
            
            print(f"{draw_vertical_line()} {Fore.CYAN}Доступные предметы для слота {SLOT_NAMES.get(current_slot, current_slot)}:{Style.RESET_ALL}")
            
            if not equippable_items:
                print(f"{draw_vertical_line()} {Fore.YELLOW}В инвентаре нет предметов для этого слота.{Style.RESET_ALL}")
                print(f"{draw_vertical_line()}")
                print(f"{draw_vertical_line()} {Fore.GREEN}Нажмите любую клавишу, чтобы вернуться...{Style.RESET_ALL}")
                draw_bottom_box(80)
                
                # Ожидаем нажатия клавиши и затем возвращаемся к экрану экипировки
                readchar.readkey()
                show_inventory_items = False
                continue
            
            # Отображаем предметы из инвентаря для выбранного слота
            for i, item in enumerate(equippable_items):
                rarity_color = game_menu.get_rarity_color(item.get_rarity())
                
                if i == current_item_index:
                    print(f"{draw_vertical_line()} {Fore.YELLOW}>{Style.RESET_ALL} {rarity_color}{item.name}{Style.RESET_ALL}")
                else:
                    print(f"{draw_vertical_line()}   {rarity_color}{item.name}{Style.RESET_ALL}")
            
            print(f"{draw_vertical_line()}")
            draw_separator(80)
            
            # Отображаем детали выбранного предмета
            if equippable_items and current_item_index >= 0 and current_item_index < len(equippable_items):
                selected_item = equippable_items[current_item_index]
                
                rarity_color = game_menu.get_rarity_color(selected_item.get_rarity())
                rarity_name = get_rarity_name(selected_item.get_rarity())
                
                print(f"{draw_vertical_line()} {Fore.CYAN}Информация о предмете:{Style.RESET_ALL}")
                print(f"{draw_vertical_line()} {rarity_color}{selected_item.name}{Style.RESET_ALL} - {rarity_color}{rarity_name}{Style.RESET_ALL}")
                print(f"{draw_vertical_line()} {Fore.WHITE}{selected_item.get_description()}{Style.RESET_ALL}")
                
                # Отображаем характеристики, если они есть
                if hasattr(selected_item, 'characteristics') and selected_item.characteristics:
                    print(f"{draw_vertical_line()}")
                    print(f"{draw_vertical_line()} {Fore.CYAN}Характеристики:{Style.RESET_ALL}")
                    
                    for stat, value in selected_item.characteristics.items():
                        color = STAT_COLORS.get(stat, Fore.WHITE)
                        stat_name = stat.capitalize()
                        stat_icon = STAT_ICONS.get(stat, "🔹")
                        
                        print(f"{draw_vertical_line()} {stat_icon} {stat_name}: {color}{value}{Style.RESET_ALL}")
            
            # Нижняя часть с кнопками
            print(f"{draw_vertical_line()}")
            draw_separator(80)
            print(f"{draw_vertical_line()} {Fore.CYAN}Управление:{Style.RESET_ALL}")
            print(f"{draw_vertical_line()} {Fore.GREEN}[Enter]{Style.RESET_ALL} Экипировать   {Fore.YELLOW}[↑/↓]{Style.RESET_ALL} Выбрать предмет   {Fore.RED}[Esc]{Style.RESET_ALL} Вернуться")
        
        # Вывод всего интерфейса
        print(f"{draw_vertical_line()}")
        
        # Подсказки для пользователя
        text_color = Fore.CYAN
        if not show_inventory_items:
            draw_separator(80)
            print(f"{draw_vertical_line()} {text_color}Управление:{Style.RESET_ALL}")
            print(f"{draw_vertical_line()} {text_color}↑/↓{Style.RESET_ALL} - Выбор слота")
            print(f"{draw_vertical_line()} {text_color}Enter{Style.RESET_ALL} - Выбрать/заменить экипировку")
            print(f"{draw_vertical_line()} {text_color}Пробел{Style.RESET_ALL} - Снять экипировку")
            print(f"{draw_vertical_line()} {text_color}ESC{Style.RESET_ALL} - Выход")
        else:
            draw_separator(80)
            print(f"{draw_vertical_line()} {text_color}Управление:{Style.RESET_ALL}")
            print(f"{draw_vertical_line()} {text_color}↑/↓{Style.RESET_ALL} - Выбор предмета")
            print(f"{draw_vertical_line()} {text_color}Enter{Style.RESET_ALL} - Экипировать выбранный предмет")
            print(f"{draw_vertical_line()} {text_color}ESC{Style.RESET_ALL} - Вернуться к списку слотов")
            
        # Нижняя рамка
        draw_bottom_box(80)
        
        # Обрабатываем пользовательский ввод
        key = game_menu.get_key()
        
        # Обработка нажатия клавиш
        if key == "ESC":
            if show_inventory_items:
                # Возвращаемся к просмотру экипировки
                show_inventory_items = False
            else:
                # Выход из экрана экипировки
                return
        
        elif not show_inventory_items:
            # Навигация по слотам экипировки
            if key == "UP":
                # Перемещаемся вверх по списку слотов
                current_slot_index = (current_slot_index - 1) % len(slots)
            
            elif key == "DOWN":
                # Перемещаемся вниз по списку слотов
                current_slot_index = (current_slot_index + 1) % len(slots)
            
            elif key == "ENTER":
                # Показываем предметы для слота, независимо от того, пуст он или нет
                current_slot = slots[current_slot_index]
                all_items = player.inventory.get_items()
                equippable_items = [item for item in all_items if hasattr(item, 'get_slot') and item.get_slot() == current_slot]
                
                if equippable_items:
                    # Показываем предметы инвентаря для выбранного слота
                    show_inventory_items = True
                    current_item_index = 0
                else:
                    # Нет предметов для этого слота - показываем сообщение
                    game_menu.show_message(f"У вас нет предметов для слота {SLOT_NAMES.get(current_slot, current_slot)}", Fore.YELLOW)
            
            elif (key == " " or key == "SPACE") and equipment[slots[current_slot_index]]:
                # Снимаем предмет
                success, message = player.unequip_item(slots[current_slot_index])
                if success:
                    game_menu.show_message(message, Fore.GREEN)
                    # Обновляем бонусы после снятия предмета
                    bonuses = player.get_equipment_bonuses()
                else:
                    game_menu.show_message(message, Fore.RED)
        
        else:
            # Навигация по предметам инвентаря
            all_items = player.inventory.get_items()
            current_slot = slots[current_slot_index]
            equippable_items = [item for item in all_items if hasattr(item, 'get_slot') and item.get_slot() == current_slot]
            
            if not equippable_items:
                show_inventory_items = False
                continue
            
            if key == "UP" and equippable_items:
                # Перемещаемся вверх по списку предметов
                current_item_index = (current_item_index - 1) % len(equippable_items)
            
            elif key == "DOWN" and equippable_items:
                # Перемещаемся вниз по списку предметов
                current_item_index = (current_item_index + 1) % len(equippable_items)
            
            elif key == "ENTER" and equippable_items and current_item_index < len(equippable_items):
                # Экипируем выбранный предмет
                selected_item = equippable_items[current_item_index]
                success, message = player.equip_item(selected_item)
                
                if success:
                    game_menu.show_message(message, Fore.GREEN)
                    # Обновляем бонусы после экипировки предмета
                    bonuses = player.get_equipment_bonuses()
                    # Возвращаемся к просмотру экипировки
                    show_inventory_items = False
                else:
                    game_menu.show_message(message, Fore.RED)

def get_rarity_name(rarity):
    """Возвращает название редкости на русском"""
    rarity_names = {
        "COMMON": "Обычный",
        "UNCOMMON": "Необычный",
        "RARE": "Редкий",
        "EPIC": "Эпический",
        "LEGENDARY": "Легендарный",
        "MYTHIC": "Мифический"
    }
    return rarity_names.get(rarity, "Неизвестно") 