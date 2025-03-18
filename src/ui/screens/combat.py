import os
import time
import random
from colorama import Fore, Back, Style

from src.models.monsters.Monster import Monster
from src.utils.Logger import Logger

def start_combat(menu, monster_id):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Начинает пошаговый бой с монстром
    
    Args:
        menu: Экземпляр GameMenu
        monster_id: ID монстра
    
    Returns:
        bool: True, если игрок победил, False в противном случае
    """
    logger = Logger()
    logger.debug(f"Начинаем бой с монстром ID: {monster_id}")
    
    # Получаем игрока и монстра
    player = menu.player
    game = menu.game
    
    # Создаем экземпляр монстра
    monster = game.get_monster(monster_id)
    if not monster:
        menu.show_message(f"Ошибка: Монстр {monster_id} не найден!", menu.error_color)
        return False
    
    # Создаем копию монстра для боя
    monster = Monster(
        monster.id, 
        monster.name, 
        monster.description, 
        monster.level, 
        monster.health, 
        monster.damage
    )
    
    # Механика пошагового боя
    turn = 1  # Номер хода, начиная с 1
    player_turn = True  # Первый ход за игроком
    combat_log = []  # Лог событий боя
    max_log_entries = 5  # Максимальное количество записей в логе
    
    # Сообщение о начале боя
    combat_log.append(f"Бой начался! Противник: {monster.name} [{monster.health} HP]")
    
    while player.is_alive() and monster.is_alive():
        # Обрабатываем ход
        if player_turn:
            # Ход игрока
            action = handle_player_turn(menu, player, monster)
            
            if action == "flee":
                # Игрок сбежал
                combat_log.append(f"Вы сбежали от {monster.name}!")
                show_combat_screen(menu, player, monster, combat_log, turn, False)
                time.sleep(2)
                return False
            
            elif action == "attack":
                # Игрок атакует
                damage, is_critical, is_dodged = player.attack(monster)
                
                if is_dodged:
                    combat_log.append(f"{monster.name} уклонился от вашей атаки!")
                elif is_critical:
                    combat_log.append(f"{Fore.YELLOW}КРИТИЧЕСКИЙ УДАР!{Style.RESET_ALL} Вы атаковали {monster.name} и нанесли {damage} урона!")
                else:
                    combat_log.append(f"Вы атаковали {monster.name} и нанесли {damage} урона!")
                
                # Проверяем, умер ли монстр
                if not monster.is_alive():
                    combat_log.append(f"{monster.name} побежден!")
                    show_combat_screen(menu, player, monster, combat_log, turn, False)
                    
                    # Награда за победу
                    handle_victory(menu, player, monster)
                    return True
            
            elif action == "use_item":
                # Использование предмета (пока заглушка)
                combat_log.append("Вы использовали предмет!")
                
            elif action == "special":
                # Специальное умение (пока заглушка)
                base_damage, is_crit = player.calculate_damage()
                special_damage = int(base_damage * 1.5)
                died, is_dodged = monster.take_damage(special_damage)
                
                if is_dodged:
                    combat_log.append(f"{monster.name} уклонился от вашей особой атаки!")
                else:
                    combat_log.append(f"{Fore.MAGENTA}ОСОБАЯ АТАКА!{Style.RESET_ALL} Вы нанесли {special_damage} урона!")
                
                # Проверяем, умер ли монстр
                if not monster.is_alive():
                    combat_log.append(f"{monster.name} побежден!")
                    show_combat_screen(menu, player, monster, combat_log, turn, False)
                    
                    # Награда за победу
                    handle_victory(menu, player, monster)
                    return True
        
        else:
            # Ход монстра
            show_combat_screen(menu, player, monster, combat_log, turn, False)
            
            # Монстр атакует
            damage, is_critical, is_dodged = monster.attack(player)
            
            if is_dodged:
                combat_log.append(f"Вы уклонились от атаки {monster.name}!")
            else:
                # Расчитываем блокировку урона
                original_damage = damage
                actual_damage = max(1, damage - player.equipment_bonuses.get("defense", 0))
                blocked_damage = original_damage - actual_damage
                
                # Формируем сообщение о полученном уроне
                if is_critical:
                    if blocked_damage > 0:
                        combat_log.append(f"{Fore.RED}КРИТИЧЕСКИЙ УДАР!{Style.RESET_ALL} {monster.name} атакует вас и наносит {actual_damage} урона! (Блок: {blocked_damage})")
                    else:
                        combat_log.append(f"{Fore.RED}КРИТИЧЕСКИЙ УДАР!{Style.RESET_ALL} {monster.name} атакует вас и наносит {actual_damage} урона!")
                else:
                    if blocked_damage > 0:
                        combat_log.append(f"{monster.name} атакует вас и наносит {actual_damage} урона! (Блок: {blocked_damage})")
                    else:
                        combat_log.append(f"{monster.name} атакует вас и наносит {actual_damage} урона!")
            
            # Проверяем, умер ли игрок
            if not player.is_alive():
                combat_log.append("Вы проиграли бой!")
                show_combat_screen(menu, player, monster, combat_log, turn, False)
                
                # Обработка поражения
                handle_defeat(menu, player)
                return False
        
        # Обновляем счётчик хода и меняем очередь
        if player_turn:
            player_turn = False
        else:
            turn += 1
            player_turn = True
        
        # Ограничиваем размер боевого лога
        if len(combat_log) > max_log_entries:
            combat_log = combat_log[-max_log_entries:]
    
    # Если мы вышли из цикла, значит бой закончился
    if not player.is_alive():
        combat_log.append("Вы проиграли бой!")
        show_combat_screen(menu, player, monster, combat_log, turn, False)
        handle_defeat(menu, player)
        return False
    
    if not monster.is_alive():
        combat_log.append(f"{monster.name} побежден!")
        show_combat_screen(menu, player, monster, combat_log, turn, False)
        handle_victory(menu, player, monster)
        return True
    
    return False

def show_combat_screen(menu, player, monster, combat_log, turn, is_player_turn):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Отображает экран боя
    
    Args:
        menu: Экземпляр GameMenu
        player: Игрок
        monster: Монстр
        combat_log: Лог боя
        turn: Номер хода
        is_player_turn: True, если сейчас ход игрока
    """
    # Если не ход игрока и мы хотим только отобразить состояние боя
    if not is_player_turn:
        menu.clear_screen()
        
        # Рисуем верхнюю часть рамки
        menu.draw_box(80, "ПОШАГОВЫЙ БОЙ")
        
        # Верхняя панель с информацией об участниках
        player_hp_bar = menu.create_progress_bar(player.health, player.max_health, 20, Fore.GREEN)
        monster_hp_bar = menu.create_progress_bar(monster.health, monster.max_health, 20, Fore.RED)
        
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
              f"{Fore.CYAN}Ход: {turn:<3}{Style.RESET_ALL} | " +
              f"Очередь: {Fore.RED}{monster.name:<20}{Style.RESET_ALL}")
        
        menu.draw_separator(80)
        
        # Информация об игроке
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
              f"{Fore.GREEN}Игрок: {player.name:<15}{Style.RESET_ALL} | " +
              f"Уровень: {player.level:<3} | " +
              f"Здоровье: {player_hp_bar} {player.health:>3}/{player.max_health:<3}")
        
        # Информация о монстре
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
              f"{Fore.RED}Монстр: {monster.name:<15}{Style.RESET_ALL} | " +
              f"Уровень: {monster.level:<3} | " +
              f"Здоровье: {monster_hp_bar} {monster.health:>3}/{monster.max_health:<3}")
        
        menu.draw_separator(80)
        
        # Отображаем изображение монстра (ASCII-арт или символ)
        monster_art = get_monster_art(monster.id)
        for line in monster_art.split('\n'):
            print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {line}")
        
        menu.draw_separator(80)
        
        # Отображаем лог боя без правой границы
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
              f"{Fore.YELLOW}═════════════════════ БОЕВОЙ ЖУРНАЛ ═════════════════════{Style.RESET_ALL}")
              
        if len(combat_log) == 0:
            print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
                  f"{Fore.CYAN}Бой начинается...{Style.RESET_ALL}")
        else:
            for log_entry in combat_log:
                # Определяем иконку в зависимости от типа события
                if "уклонились" in log_entry.lower() or "уклонился" in log_entry.lower():
                    icon = "🏃"
                    color = Fore.CYAN
                elif "критический удар" in log_entry.lower():
                    icon = "💥"
                    color = Fore.YELLOW
                elif "атаковали" in log_entry.lower() or "атакует" in log_entry.lower():
                    icon = "⚔️"
                    color = Fore.RED
                elif "блок" in log_entry.lower():
                    icon = "🛡️"
                    color = Fore.BLUE
                elif "побежден" in log_entry.lower():
                    icon = "🏆"
                    color = Fore.GREEN
                elif "особая атака" in log_entry.lower():
                    icon = "✨"
                    color = Fore.MAGENTA
                elif "бой начался" in log_entry.lower():
                    icon = "🔔"
                    color = Fore.YELLOW
                else:
                    icon = "📝"
                    color = Fore.WHITE
                
                # Печатаем запись лога без правой границы
                print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
                      f"{color}{icon}{Style.RESET_ALL} {log_entry}")
        
        # Заполняем пустыми строками, если лог маленький
        for _ in range(max(0, 5 - len(combat_log))):
            print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} ")
        
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
              f"{Fore.YELLOW}═════════════════════════════════════════════════════════{Style.RESET_ALL}")
        
        menu.draw_separator(80)
        
        # Если ход монстра, просто выводим сообщение и ждем
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}Ход монстра...{Style.RESET_ALL}")
        
        # Отображаем характеристики игрока в виде списка
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
              f"{Fore.CYAN}════════════════════ ХАРАКТЕРИСТИКИ ИГРОКА ════════════════════{Style.RESET_ALL}")
        
        player_attack, _ = player.calculate_damage()
        player_defense = player.equipment_bonuses.get("defense", 0)
        total_dodge = player.dodge_chance + player.equipment_bonuses.get("dodge", 0)
        total_crit = player.crit_chance + player.equipment_bonuses.get("crit_chance", 0)
        total_crit_dmg = player.crit_damage + player.equipment_bonuses.get("crit_damage", 0)
        
        # Создаем список характеристик в столбик
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}⚔️ Атака:{Style.RESET_ALL} {player_attack}")
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.BLUE}🛡️ Защита:{Style.RESET_ALL} {player_defense}")
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}🏃 Уклонение:{Style.RESET_ALL} {total_dodge}%")
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.YELLOW}💥 Шанс крита:{Style.RESET_ALL} {total_crit}%")
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.MAGENTA}📈 Множитель крита:{Style.RESET_ALL} x{total_crit_dmg:.1f}")
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.WHITE}📊 Уровень:{Style.RESET_ALL} {player.level}")
        
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
              f"{Fore.CYAN}═══════════════════════════════════════════════════════════{Style.RESET_ALL}")
        
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Нажмите любую клавишу для продолжения...")
        
        # Нижняя часть рамки
        menu.draw_bottom_box(80)
        
        # Ждем нажатия клавиши для продолжения
        menu.get_key()
    # В ходе игрока управление экраном передается в handle_player_turn

def find_cutoff_position(full_string, clean_string, max_width):
    """Находит позицию для обрезки строки с учетом ANSI-кодов
    
    Args:
        full_string: Строка с ANSI-кодами
        clean_string: Строка без ANSI-кодов
        max_width: Максимальная ширина
        
    Returns:
        int: Позиция для обрезки в строке с ANSI-кодами
    """
    if len(clean_string) <= max_width:
        return len(full_string)
    
    # Позиция в чистой строке
    clean_pos = 0
    # Позиция в полной строке
    full_pos = 0
    
    while clean_pos < max_width and full_pos < len(full_string):
        # Если находим начало ANSI-кода
        if full_string[full_pos] == '\033':
            # Ищем конец кода (символ 'm')
            end_code_pos = full_string.find('m', full_pos)
            if end_code_pos != -1:
                full_pos = end_code_pos + 1
                continue
        
        full_pos += 1
        clean_pos += 1
    
    return full_pos

def handle_player_turn(menu, player, monster):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Обрабатывает ход игрока
    
    Args:
        menu: Экземпляр GameMenu
        player: Игрок
        monster: Монстр
    
    Returns:
        str: Выбранное действие
    """
    valid_actions = {'1': 'attack', '2': 'special', '3': 'use_item', '4': 'flee'}
    action_names = ['attack', 'special', 'use_item', 'flee']
    current_option = 0
    
    # Функция для отображения опций
    def display_options():
        menu.clear_screen()
        
        # Рисуем верхнюю часть рамки
        menu.draw_box(80, "ПОШАГОВЫЙ БОЙ")
        
        # Верхняя панель с информацией об участниках
        player_hp_bar = menu.create_progress_bar(player.health, player.max_health, 20, Fore.GREEN)
        monster_hp_bar = menu.create_progress_bar(monster.health, monster.max_health, 20, Fore.RED)
        
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
            f"{Fore.CYAN}Ход: боевой{Style.RESET_ALL} | " +
            f"Очередь: {Fore.GREEN}Игрок{Style.RESET_ALL}")
        
        menu.draw_separator(80)
        
        # Информация об игроке
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
            f"{Fore.GREEN}Игрок: {player.name:<15}{Style.RESET_ALL} | " +
            f"Уровень: {player.level:<3} | " +
            f"Здоровье: {player_hp_bar} {player.health:>3}/{player.max_health:<3}")
        
        # Информация о монстре
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
            f"{Fore.RED}Монстр: {monster.name:<15}{Style.RESET_ALL} | " +
            f"Уровень: {monster.level:<3} | " +
            f"Здоровье: {monster_hp_bar} {monster.health:>3}/{monster.max_health:<3}")
        
        menu.draw_separator(80)
        
        # Варианты действий
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}Выберите действие:{Style.RESET_ALL}")
        
        # Отображаем варианты с учетом выбранного действия
        for i in range(4):
            if i == 0:  # Атака
                text = f"⚔️ Атаковать"
                color = Fore.RED
            elif i == 1:  # Особая атака
                text = f"✨ Использовать особую атаку"
                color = Fore.MAGENTA
            elif i == 2:  # Предмет
                text = f"🧪 Использовать предмет"
                color = Fore.GREEN
            else:  # Сбежать
                text = f"🏃 Сбежать"
                color = Fore.YELLOW
                
            if i == current_option:
                print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {menu.selected_color} ❯ {text:<40} {Style.RESET_ALL}")
            else:
                print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {color}{text:<40}{Style.RESET_ALL}")
        
        # Нижняя часть рамки
        menu.draw_separator(80)
        
        # Отображаем характеристики игрока в виде списка
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
              f"{Fore.CYAN}════════════════════ ХАРАКТЕРИСТИКИ ИГРОКА ════════════════════{Style.RESET_ALL}")
        
        player_attack, _ = player.calculate_damage()
        player_defense = player.equipment_bonuses.get("defense", 0)
        total_dodge = player.dodge_chance + player.equipment_bonuses.get("dodge", 0)
        total_crit = player.crit_chance + player.equipment_bonuses.get("crit_chance", 0)
        total_crit_dmg = player.crit_damage + player.equipment_bonuses.get("crit_damage", 0)
        
        # Создаем список характеристик в столбик
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}⚔️ Атака:{Style.RESET_ALL} {player_attack}")
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.BLUE}🛡️ Защита:{Style.RESET_ALL} {player_defense}")
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}🏃 Уклонение:{Style.RESET_ALL} {total_dodge}%")
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.YELLOW}💥 Шанс крита:{Style.RESET_ALL} {total_crit}%")
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.MAGENTA}📈 Множитель крита:{Style.RESET_ALL} x{total_crit_dmg:.1f}")
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.WHITE}📊 Уровень:{Style.RESET_ALL} {player.level}")
        
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} " +
              f"{Fore.CYAN}═══════════════════════════════════════════════════════════{Style.RESET_ALL}")
        
        print(f"{menu.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}Используйте стрелки ↑↓ для выбора и Enter для подтверждения{Style.RESET_ALL}")
        menu.draw_bottom_box(80)
    
    # Показываем начальное состояние
    display_options()
    
    # Основной цикл выбора действия
    while True:
        key = menu.get_key()
        
        if key == 'UP':  # Стрелка вверх
            current_option = (current_option - 1) % 4
            display_options()
        elif key == 'DOWN':  # Стрелка вниз
            current_option = (current_option + 1) % 4
            display_options()
        elif key == 'ENTER':  # Ввод
            return action_names[current_option]
        elif key in valid_actions:  # Цифровые клавиши (оставляем для совместимости)
            return valid_actions[key]

def handle_victory(menu, player, monster):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Обрабатывает победу игрока
    
    Args:
        menu: Экземпляр GameMenu
        player: Игрок
        monster: Монстр
    """
    # Расчет опыта за победу
    exp_reward = monster.level * 10
    
    # Расчет награды монетами
    money_reward = monster.level * 5 + random.randint(1, 10)
    
    # Добавляем награду игроку
    player.add_experience(exp_reward)
    player.add_money(money_reward)
    
    # Восстанавливаем часть здоровья после боя
    health_restore = player.max_health * 0.2
    player.heal(int(health_restore))
    
    # Генерируем дроп предметов (пока простой вариант)
    dropped_items = []
    
    # Шанс на выпадение предмета
    drop_chance = min(0.7, 0.3 + (monster.level * 0.05))  # От 30% до 70% в зависимости от уровня
    
    if random.random() < drop_chance:
        # Пока используем заглушку, потом можно сделать более сложную систему дропа
        # connected to your game's item system
        possible_items = ["healing_potion", "mana_potion", "monster_fang", "monster_hide"]
        dropped_item = random.choice(possible_items)
        dropped_items.append(dropped_item)
        player.add_item_by_id(menu.game, dropped_item, 1)
    
    # Добавляем монстра в глоссарий
    if hasattr(menu.game, 'add_monster_to_glossary'):
        menu.game.add_monster_to_glossary(monster.id, player.current_location)
    
    # Сообщение о победе
    victory_message = f"Вы победили {monster.name}!\n\n"
    victory_message += f"{Fore.YELLOW}✨ Получено опыта: {exp_reward}{Style.RESET_ALL}\n"
    victory_message += f"{Fore.YELLOW}💰 Получено монет: {money_reward}{Style.RESET_ALL}\n"
    
    if dropped_items:
        victory_message += f"{Fore.GREEN}📦 Получены предметы:{Style.RESET_ALL}\n"
        for item_id in dropped_items:
            item_data = menu.game.get_item(item_id)
            if item_data:
                item_name = item_data.get('name', item_id)
                victory_message += f"   - {item_name}\n"
    
    menu.show_message(victory_message, Fore.GREEN)
    
    # Обновляем квесты после убийства монстра
    menu.game.update_quest_progress()

def handle_defeat(menu, player):
    """Обрабатывает поражение игрока
    
    Args:
        menu: Экземпляр GameMenu
        player: Игрок
    """
    # Восстанавливаем некоторое здоровье игрока
    player.health = max(1, int(player.max_health * 0.5))
    
    defeat_message = f"{Fore.RED}Вы проиграли бой!{Style.RESET_ALL}\n\n"
    defeat_message += "Вы без сознания перенесены в безопасное место.\n"
    defeat_message += f"Восстановлено {player.health} HP."
    
    menu.show_message(defeat_message, Fore.RED)

def get_monster_art(monster_id):
    """Возвращает ASCII-арт для монстра
    
    Args:
        monster_id: ID монстра
    
    Returns:
        str: ASCII-арт
    """
    # В будущем можно реализовать загрузку разных артов для разных монстров
    # по ID монстра
    
    # Заглушка по умолчанию
    default_art = '''
        ,     ,
       /(     )\\
      /  \\___/  \\
     /     Y     \\
     |     |     |
     |     |     |
     \\__|__|__   /
        | |  |  /
        | |  | /
    '''
    
    # Можно добавить словарь с разными артами для разных монстров
    monster_arts = {
        "wolf": '''
          /\\      /\\
         ( ◉  .. ◉ )
        /    --    \\
       {     \\v/    }
        \\    ||    /
         \\. ====. /
          \\______/
        ''',
        "skeleton": '''
          .-.
         (o.o)
          |=|
         __|__
       //.=|=.\\\\
      // .=|=. \\\\
      \\\\ .=|=. //
       \\\\(_=_)//
        (:| |:)
         || ||
         () ()
         || ||
         || ||
        ==' '==
        ''',
        "spider": '''
         /\\(,,,)/\\
        /  (o o)  \\
       / ===v=== \\
         /(   )\\
          ^   ^
        ''',
        "slime": '''
           _____
         /       \\
        |  O  O  |
        |    >   |
        \\       /
         ~~^~~~^
        ''',
        "demon": '''
          ^   ^
         / \\ / \\
        (  o o  )
         \\  U  /
          \\+++/
           v-v
        '''
    }
    
    # Если у нас есть специальный арт для этого монстра, используем его
    if monster_id in monster_arts:
        return monster_arts[monster_id]
    
    return default_art 