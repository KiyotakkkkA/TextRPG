from time import time
from colorama import Fore, Style

from src.models.npc.QuestNPC import QuestNPC

def talk_to_npc(self, npc):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Начинает диалог с NPC"""
    if not npc:
        return
    
    # Добавляем NPC в глоссарий
    self.game.add_npc_to_glossary(npc.id)
    
    # Начинаем с приветствия
    current_dialogue_id = "greeting"
    
    # Проверяем квесты, готовые к завершению у этого NPC
    ready_quests = self.game.get_ready_to_complete_quests_for_npc(npc.id)
    
    # Добавляем историю диалога
    dialogue_history = []
    
    while True:
        self.clear_screen()
        self.draw_box(80, f"ДИАЛОГ: {npc.name}")
        
        # Получаем текущий диалог
        dialogue = npc.get_dialogue(current_dialogue_id)
        if not dialogue:
            print(f"{self.error_color}Ошибка: диалог не найден ({current_dialogue_id}){Style.RESET_ALL}")
            self.get_key()
            return
        
        dialogue_text = dialogue.get("text", "...")
        dialogue_options = dialogue.get("options", [])
        
        # Отображаем историю диалога, если она есть
        if dialogue_history:
            last_history_entry = min(len(dialogue_history), 2) # Показываем до 2 последних записей
            
            # Если история длиннее, показываем индикатор
            if len(dialogue_history) > 2:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}↑ История диалога (PgUp/PgDown){Style.RESET_ALL}")
            
            for i in range(len(dialogue_history) - last_history_entry, len(dialogue_history)):
                entry = dialogue_history[i]
                speaker = entry.get("speaker", "???")
                text = entry.get("text", "...")
                
                # Выводим с цветом в зависимости от говорящего
                if speaker == npc.name:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}{speaker}:{Style.RESET_ALL} {text}")
                else:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.normal_color}{speaker}:{Style.RESET_ALL} {text}")
                
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        # Добавляем текущий диалог в историю
        dialogue_history.append({"speaker": npc.name, "text": dialogue_text})
        
        # Отображаем текст NPC с переносами строк
        formatted_text = self.wrap_text(dialogue_text, 70, 0)
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}{npc.name}:{Style.RESET_ALL} {formatted_text}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        # Отображаем варианты ответов
        options = []
        display_options = []
        
        # Добавляем опции завершения квестов в начало списка
        for quest in ready_quests:
            complete_option_text = f"{Fore.GREEN}[Завершить квест: {quest.name}]{Style.RESET_ALL}"
            options.append((None, f"complete_quest_{quest.id}"))
            display_options.append(complete_option_text)
        
        # Если есть квесты для завершения, добавляем разделитель
        if ready_quests:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Доступные действия:{Style.RESET_ALL}")
            self.draw_separator(80)
        
        for option in dialogue_options:
            option_text = option.get("text", "...")
            next_id = option.get("next_id")
            action = option.get("action")
            condition = option.get("condition")
            
            # Проверяем условие квеста и уровень игрока
            if condition and condition.startswith("quest_available_"):
                quest_id = condition[len("quest_available_"):]
                
                # Проверяем, существует ли квест в игре
                if quest_id not in self.game.all_quests:
                    continue
                    
                quest = self.game.all_quests[quest_id]
                
                # Квест найден, проверяем доступность у NPC
                if not isinstance(npc, QuestNPC) or quest_id not in npc.available_quests:
                    continue
                    
                # Проверяем уровень игрока
                if self.game.player.level < quest.requirements["level"]:
                    # Добавляем опцию с сообщением о недостаточном уровне
                    options.append((next_id, None))  # None вместо действия - нельзя начать квест
                    level_warning = f"{Fore.RED}Требуется уровень {quest.requirements['level']} (у вас {self.game.player.level}){Style.RESET_ALL}"
                    display_options.append(f"{level_warning}")
                    continue
            
            # Проверка всех типов условий с использованием NPCManager
            condition_satisfied = True
            condition_text = None
            
            if condition:
                if hasattr(npc, 'check_dialogue_condition'):
                    condition_satisfied, condition_text = npc.check_dialogue_condition(self.game, condition)
                else:
                    # Старый способ проверки
                    condition_satisfied = check_dialogue_condition(self, condition, npc)
            
            if not condition_satisfied:
                # Если условие не выполнено, но у нас есть описание условия,
                # добавляем опцию с пояснением, почему она недоступна
                if condition_text:
                    options.append((None, None))  # Нельзя выбрать эту опцию
                    display_options.append(f"{Fore.LIGHTBLACK_EX}{condition_text} {option_text}{Style.RESET_ALL}")
                continue
            
            # Форматируем текст действия, если оно есть
            display_text = option_text
            if action:
                action_text = get_action_display_text(self, action, npc)
                if action_text:
                    display_text = action_text
            
            options.append((next_id, action))
            display_options.append(display_text)
        
        # Если нет вариантов ответа, добавляем выход
        if not display_options:
            options.append((None, "exit"))
            display_options.append("Уйти")
        
        current_option = 0
        history_view_mode = False
        history_index = len(dialogue_history) - 1
        
        # Максимальное количество отображаемых вариантов за раз
        max_visible_options = 6
        scroll_offset = 0
        
        while True:
            self.clear_screen()
            self.draw_box(80, f"ДИАЛОГ: {npc.name}")
            
            if history_view_mode:
                # Режим просмотра истории диалога
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}История диалога ({history_index + 1}/{len(dialogue_history)}){Style.RESET_ALL}")
                self.draw_separator(80)
                
                # Показываем текущую запись из истории
                if 0 <= history_index < len(dialogue_history):
                    entry = dialogue_history[history_index]
                    speaker = entry.get("speaker", "???")
                    text = entry.get("text", "...")
                    
                    # Выводим с цветом в зависимости от говорящего
                    if speaker == npc.name:
                        formatted_text = self.wrap_text(text, 70, 0)
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}{speaker}:{Style.RESET_ALL} {formatted_text}")
                    else:
                        formatted_text = self.wrap_text(text, 70, 0)
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.normal_color}{speaker}:{Style.RESET_ALL} {formatted_text}")
                
                # Подсказка по навигации
                self.draw_separator(80)
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.normal_color}PgUp/PgDown: Навигация | ESC: Вернуться к диалогу{Style.RESET_ALL}")
                self.draw_bottom_box(80)
                
                # Получаем клавишу
                key = self.get_key()
                
                if key == 'PAGE_UP':
                    history_index = max(0, history_index - 1)
                elif key == 'PAGE_DOWN':
                    history_index = min(len(dialogue_history) - 1, history_index + 1)
                elif key == 'ESC':
                    history_view_mode = False
                    history_index = len(dialogue_history) - 1
                
                continue
            
            # Обычный режим диалога
            # Отображаем текст NPC с переносами строк
            formatted_text = self.wrap_text(dialogue_text, 70, 0)
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}{npc.name}:{Style.RESET_ALL} {formatted_text}")
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
            self.draw_separator(80)
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Герой:{Style.RESET_ALL}")
            
            # Проверяем, нужна ли прокрутка
            total_options = len(display_options)
            need_scroll = total_options > max_visible_options
            
            # Убеждаемся, что текущая опция видима
            if current_option < scroll_offset:
                scroll_offset = current_option
            elif current_option >= scroll_offset + max_visible_options:
                scroll_offset = current_option - max_visible_options + 1
            
            # Показываем индикатор прокрутки вверх, если нужно
            if scroll_offset > 0:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}↑ Еще варианты выше{Style.RESET_ALL}")
            
            # Отображаем опции с учетом прокрутки
            visible_range = min(scroll_offset + max_visible_options, total_options)
            for i in range(scroll_offset, visible_range):
                option_text = display_options[i]
                
                # Добавляем номер варианта (только для доступных опций)
                if options[i][0] is not None or options[i][1] is not None:
                    number_prefix = f"{i+1}. "
                else:
                    number_prefix = "   "
                
                # Форматируем текст ответа, если он длинный
                # Вместо форматирования всего текста сразу, обрабатываем первую строку отдельно
                max_first_line_width = 63  # Уменьшаем ширину для номера
                
                if i == current_option:
                    # Для выбранной опции
                    # Удаляем все цветовые коды из текста
                    clean_option = option_text
                    for color_code in [self.resource_color, self.location_color, Fore.YELLOW, Fore.GREEN, Fore.RED, 
                                      Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTBLUE_EX,
                                      Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX,
                                      Style.BRIGHT, Style.DIM]:
                        clean_option = clean_option.replace(color_code, '')
                    clean_option = clean_option.replace(Style.RESET_ALL, '')
                    
                    # Проверяем наличие условия (текст в квадратных скобках)
                    has_condition = '[' in option_text and ']' in option_text
                    
                    if has_condition:
                        # Находим конец условия
                        condition_end = option_text.find(']') + 1
                        condition_part = option_text[:condition_end]
                        text_part = option_text[condition_end:]
                        
                        # Форматируем только текстовую часть
                        formatted_lines = self.wrap_text(text_part, max_first_line_width, 2).split('\n')
                        
                        # Выводим первую строку с условием
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color} ❯ {number_prefix}{condition_part} {formatted_lines[0]} {Style.RESET_ALL}")
                        
                        # Выводим остальные строки с отступом
                        for line in formatted_lines[1:]:
                            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color}    {' ' * len(number_prefix)}{line} {Style.RESET_ALL}")
                    else:
                        # Если нет условия, форматируем весь текст
                        formatted_lines = self.wrap_text(clean_option, max_first_line_width, 2).split('\n')
                        
                        # Выводим первую строку с номером
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color} ❯ {number_prefix}{formatted_lines[0]} {Style.RESET_ALL}")
                        
                        # Выводим остальные строки с отступом
                        for line in formatted_lines[1:]:
                            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color}    {' ' * len(number_prefix)}{line} {Style.RESET_ALL}")
                else:
                    # Для невыбранных опций
                    # Проверяем наличие условия (текст в квадратных скобках)
                    has_condition = '[' in option_text and ']' in option_text
                    
                    if has_condition:
                        # Находим конец условия
                        condition_end = option_text.find(']') + 1
                        condition_part = option_text[:condition_end]
                        text_part = option_text[condition_end:]
                        
                        # Форматируем только текстовую часть
                        formatted_lines = self.wrap_text(text_part, max_first_line_width, 2).split('\n')
                        
                        # Выводим первую строку с условием
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {number_prefix}{condition_part} {formatted_lines[0]}")
                        
                        # Выводим остальные строки с отступом
                        for line in formatted_lines[1:]:
                            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {' ' * len(number_prefix)}    {line}")
                    else:
                        # Если нет условия, форматируем весь текст
                        formatted_lines = self.wrap_text(option_text, max_first_line_width, 2).split('\n')
                        
                        # Выводим первую строку с номером
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {number_prefix}{formatted_lines[0]}")
                        
                        # Выводим остальные строки с отступом
                        for line in formatted_lines[1:]:
                            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {' ' * len(number_prefix)}    {line}")
            
            # Показываем индикатор прокрутки вниз, если нужно
            if visible_range < total_options:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}↓ Еще варианты ниже{Style.RESET_ALL}")
            
            # Подсказка по навигации
            footer_text = "↑↓: Выбор, 1-9: Быстрый выбор, Enter: Подтвердить, PgUp: История, Esc: Назад"
            self.print_footer(footer_text)
            
            # Получаем нажатую клавишу
            key = self.get_key()
            
            if key == 'UP' or key == 'w' or key == 'W' or key == 'ц' or key == 'Ц':
                current_option -= 1
                # Если вышли за верхнюю границу, переходим в конец списка
                if current_option < 0:
                    current_option = len(options) - 1
            elif key == 'DOWN' or key == 's' or key == 'S' or key == 'ы' or key == 'Ы':
                current_option += 1
                # Если вышли за нижнюю границу, переходим в начало списка
                if current_option >= len(options):
                    current_option = 0
            elif key == 'PAGE_UP':
                # Включаем режим просмотра истории
                history_view_mode = True
                history_index = len(dialogue_history) - 1
            elif key == 'ENTER':
                # Проверяем, что вариант можно выбрать (например, не заблокирован условием)
                if options[current_option] == (None, None):
                    # Это заблокированный вариант, игнорируем его
                    continue
                    
                next_id, action = options[current_option]
                
                # Если выбран вариант с текстом, добавляем его в историю
                if display_options[current_option]:
                    dialogue_history.append({"speaker": "Герой", "text": display_options[current_option]})
                
                # Обработка действий
                if action:
                    handle_dialogue_action(self, action, npc)
                    if action == "exit":
                        return
                    
                    # Обновляем список готовых к завершению квестов
                    ready_quests = self.game.get_ready_to_complete_quests_for_npc(npc.id)
                
                # Переход к следующему диалогу
                if next_id:
                    current_dialogue_id = next_id
                    break
                else:
                    return
            
            elif key == 'ESC':
                return
            # Проверяем, была ли нажата цифровая клавиша для быстрого выбора
            elif key in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                # Преобразуем символ в число (1-9)
                option_index = int(key) - 1
                
                # Проверяем, что такой вариант существует и его можно выбрать
                if 0 <= option_index < len(options) and options[option_index] != (None, None):
                    current_option = option_index
                    
                    # Имитируем нажатие Enter для выбора варианта
                    next_id, action = options[current_option]
                    
                    # Если выбран вариант с текстом, добавляем его в историю
                    if display_options[current_option]:
                        dialogue_history.append({"speaker": "Герой", "text": display_options[current_option]})
                    
                    # Обработка действий
                    if action:
                        handle_dialogue_action(self, action, npc)
                        if action == "exit":
                            return
                        
                        # Обновляем список готовых к завершению квестов
                        ready_quests = self.game.get_ready_to_complete_quests_for_npc(npc.id)
                    
                    # Переход к следующему диалогу
                    if next_id:
                        current_dialogue_id = next_id
                        break
                    else:
                        return

def check_dialogue_condition(self, condition, npc):
    """Проверяет условие для отображения варианта диалога"""
    # Используем метод проверки условий из NPCManager
    if hasattr(npc, 'check_dialogue_condition'):
        is_satisfied, condition_text = npc.check_dialogue_condition(self.game, condition)
        return is_satisfied
    
    # Для обратной совместимости - старая проверка условий
    # Пример условий для квестов
    if condition.startswith("quest_available_"):
        quest_id = condition[len("quest_available_"):]
        
        # Проверяем, существует ли квест в игре
        if quest_id not in self.game.all_quests:
            print(f"Ошибка: Квест '{quest_id}' не найден в игре при проверке условия.")
            return False
        
        # Проверяем доступность у NPC
        if isinstance(npc, QuestNPC):
            return quest_id in npc.available_quests
        return False
    
    return True

def get_action_display_text(self, action, npc):
    """Возвращает текст, описывающий действие для отображения в диалоге"""
    if action == "trade":
        return "Торговля"
    elif action == "exit":
        return "Выход"
    elif action.startswith("start_quest_"):
        quest_id = action[len("start_quest_"):]
        quest = self.game.get_quest(quest_id)
        quest_name = quest.name if quest else quest_id
        return f"{Fore.LIGHTYELLOW_EX}Принять задание: {quest_name}{Style.RESET_ALL}"
    elif action.startswith("complete_quest_"):
        quest_id = action[len("complete_quest_"):]
        quest = self.game.get_quest(quest_id)
        quest_name = quest.name if quest else quest_id
        return f"{Fore.GREEN}Завершить задание: {quest_name}{Style.RESET_ALL}"
    
    return None

def handle_dialogue_action(self, action, npc):
    """Обрабатывает действия в диалоге с NPC"""
    if not action:
        return
    
    # Разбиваем действие на команду и аргументы (если есть)
    parts = action.split('_')
    command = parts[0]
    
    if command == "exit":
        return True
    elif command == "trade":
        return trade_with_npc(self, npc)
    elif command == "start" and len(parts) > 2 and parts[1] == "quest":
        # Действие вида "start_quest_QUEST_ID"
        quest_id = '_'.join(parts[2:])
        print(f"Попытка начать квест: {quest_id}")
        
        # Проверяем, существует ли квест
        quest = self.game.get_quest(quest_id)
        if not quest:
            print(f"Ошибка: Квест '{quest_id}' не найден в игре.")
            print(f"Доступные квесты: {list(self.game.all_quests.keys())}")
            time.sleep(2)  # Пауза, чтобы пользователь увидел сообщение
            return False
            
        return start_quest(self, npc, quest_id)
    elif command == "complete" and len(parts) > 2 and parts[1] == "quest":
        # Действие вида "complete_quest_QUEST_ID"
        quest_id = '_'.join(parts[2:])
        return complete_quest(self, quest_id)
    
    return False

def trade_with_npc(self, npc):
    from src.ui.GameMenu import BOX_CHARS, ICONS, KEY_UP, KEY_DOWN, KEY_ENTER, KEY_ESC
    """Открывает интерфейс торговли с NPC"""
    if npc.type != "trader":
        return False
    
    # Информация о доступных действиях
    # Рассчитываем действительное количество доступных товаров и категорий
    available_items = [(item_id, details) for item_id, details in npc.sells.items() if details.get("count", 0) > 0]
    sells_count = len(available_items)
    
    # Рассчитываем категории предметов, которые может продать игрок
    sellable_items = []
    for item in self.player.inventory.get_items():
        if hasattr(item, 'id') and item.id in npc.buys:
            sellable_items.append(item)
    buys_count = len(set([item.id for item in sellable_items]))
    
    # Создаем меню с опциями
    options = [
        ("buy", f"{ICONS['money']} Купить товары {Fore.CYAN}({sells_count} доступно){Style.RESET_ALL}"),
        ("sell", f"{ICONS['inventory']} Продать предметы {Fore.CYAN}({buys_count} категорий){Style.RESET_ALL}"),
        ("exit", f"{ICONS['back']} Вернуться к разговору")
    ]
    
    # Используем собственную логику выбора вместо show_menu
    current_option = 0
    
    while True:
        self.clear_screen()
        self.draw_box(80, f"ТОРГОВЛЯ {npc.name}")
        
        # Отображаем описание торговца с иконкой
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['npc_trader']} {Fore.LIGHTYELLOW_EX}{npc.name}{Style.RESET_ALL}: {Fore.LIGHTCYAN_EX}{npc.description}{Style.RESET_ALL}")
        
        # Отображаем текущий баланс игрока
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} {Fore.YELLOW}Ваши деньги: {self.player.money} монет{Style.RESET_ALL}")
        self.draw_separator(80)
        
        # Создаем меню с опциями торговли
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Что бы вы хотели сделать?{Style.RESET_ALL}")
        
        # Выводим опции
        for i, (option_id, option_text) in enumerate(options):
            if i == current_option:
                # Очищаем текст от цветовых кодов для выделения
                clean_text = option_text
                for color_code in [Fore.YELLOW, Fore.GREEN, Fore.RED, Fore.BLUE, Fore.MAGENTA, 
                                 Fore.CYAN, Fore.WHITE, Fore.LIGHTBLUE_EX, Fore.LIGHTGREEN_EX, 
                                 Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX,
                                 Style.BRIGHT, Style.DIM]:
                    clean_text = clean_text.replace(color_code, '')
                clean_text = clean_text.replace(Style.RESET_ALL, '')
                
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color} > {clean_text} {Style.RESET_ALL}")
            else:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {option_text}")
        
        self.draw_bottom_box(80)
        self.print_footer("↑↓: Выбор, Enter: Выбрать, Esc: Назад")
        
        # Получаем нажатую клавишу
        key = self.get_key()
        
        # Обрабатываем навигацию
        if key == 'UP' or key == 'w' or key == 'W' or key == 'ц' or key == 'Ц':
            current_option = (current_option - 1) % len(options)
        elif key == 'DOWN' or key == 's' or key == 'S' or key == 'ы' or key == 'Ы':
            current_option = (current_option + 1) % len(options)
        elif key == 'ENTER':
            option_id = options[current_option][0]
            if option_id == "exit":
                return False
            elif option_id == "buy":
                buy_from_npc(self, npc)
                
                # Обновляем данные после покупки
                available_items = [(item_id, details) for item_id, details in npc.sells.items() if details.get("count", 0) > 0]
                sells_count = len(available_items)
                options[0] = ("buy", f"{ICONS['money']} Купить товары {Fore.CYAN}({sells_count} доступно){Style.RESET_ALL}")
            elif option_id == "sell":
                sell_to_npc(self, npc)
                
                # Обновляем данные после продажи
                sellable_items = []
                for item in self.player.inventory.get_items():
                    if hasattr(item, 'id') and item.id in npc.buys:
                        sellable_items.append(item)
                buys_count = len(set([item.id for item in sellable_items]))
                options[1] = ("sell", f"{ICONS['inventory']} Продать предметы {Fore.CYAN}({buys_count} категорий){Style.RESET_ALL}")
        elif key == 'ESC':
            return False
    
    return False

def buy_from_npc(self, npc):
    from src.ui.GameMenu import BOX_CHARS, ICONS, KEY_UP, KEY_DOWN, KEY_ENTER, KEY_ESC
    """Интерфейс для покупки товаров у NPC"""
    self.clear_screen()
    self.draw_box(80, f"ПОКУПКА ТОВАРОВ {npc.name}")
    
    if not npc.sells:
        self.clear_screen()
        self.draw_box(80, f"ПОКУПКА ТОВАРОВ {npc.name}")
        
        # Добавляем информацию о торговце
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['npc_trader']} {Fore.LIGHTYELLOW_EX}{npc.name}{Style.RESET_ALL}: {Fore.LIGHTCYAN_EX}{npc.description}{Style.RESET_ALL}")
        
        # Отображаем текущий баланс игрока
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} {Fore.YELLOW}Ваши деньги: {self.player.money} монет{Style.RESET_ALL}")
        self.draw_separator(80)
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.info_color}У этого торговца нет товаров на продажу.{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
        self.get_key()
        return
    
    # Вместо show_menu реализуем свою логику выбора
    current_option = 0
    
    while True:
        # Создаем список товаров на продажу (только доступные)
        available_items = [(item_id, details) for item_id, details in npc.sells.items() if details.get("count", 0) > 0]
        
        if not available_items:
            self.clear_screen()
            self.draw_box(80, f"ПОКУПКА ТОВАРОВ {npc.name}")
            
            # Добавляем информацию о торговце
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['npc_trader']} {Fore.LIGHTYELLOW_EX}{npc.name}{Style.RESET_ALL}: {Fore.LIGHTCYAN_EX}{npc.description}{Style.RESET_ALL}")
            
            # Отображаем текущий баланс игрока
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} {Fore.YELLOW}Ваши деньги: {self.player.money} монет{Style.RESET_ALL}")
            self.draw_separator(80)
            
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.info_color}У этого торговца закончились все товары.{Style.RESET_ALL}")
            self.draw_bottom_box(80)
            print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
            self.get_key()
            return
        
        # Создаем список товаров для меню
        menu_options = []
        
        for item_id, details in available_items:
            price = details["price"]
            count = details["count"]
            
            item_data = self.game.get_item(item_id)
            if not item_data:
                continue
            
            item_name = item_data.get("name", item_id)
            item_rarity = item_data.get("rarity", "COMMON")
            item_description = item_data.get("description", "")
            
            # Определяем цвет для редкости и иконку
            rarity_color = Fore.WHITE
            rarity_icon = ICONS['common']
            if item_rarity == "UNCOMMON":
                rarity_color = Fore.GREEN
                rarity_icon = ICONS['uncommon']
            elif item_rarity == "RARE":
                rarity_color = Fore.LIGHTBLUE_EX
                rarity_icon = ICONS['rare']
            elif item_rarity == "EPIC":
                rarity_color = Fore.MAGENTA
                rarity_icon = ICONS['epic']
            elif item_rarity == "LEGENDARY":
                rarity_color = Fore.YELLOW
                rarity_icon = ICONS['legendary']
            elif item_rarity == "MYTHIC":
                rarity_color = Fore.RED
                rarity_icon = ICONS['mythic']
            
            # Проверяем, достаточно ли денег у игрока
            can_afford = self.player.money >= price
            
            # Создаем более информативное и визуально приятное отображение товара
            display_text = f"{rarity_icon} {rarity_color}{item_name}{Style.RESET_ALL} "
            
            # Добавляем информацию о количестве
            display_text += f"({Fore.CYAN}{count} шт.{Style.RESET_ALL})"
            
            # Информация о цене с цветовой индикацией доступности
            price_color = Fore.YELLOW if can_afford else Fore.RED
            display_text += f" - {ICONS['money']} {price_color}{price} монет{Style.RESET_ALL}"
            
            # Если игрок не может позволить себе товар, добавляем предупреждение
            if not can_afford:
                display_text += f" {Fore.RED}(недостаточно денег){Style.RESET_ALL}"
            
            # Используем кортеж (item_id, item_data, price, can_afford, description) для доп. информации
            menu_options.append((item_id, display_text, (item_id, item_data, price, can_afford, item_description)))
        
        # Проверяем, нужно ли корректировать current_option после обновления списка
        if menu_options and current_option >= len(menu_options):
            current_option = len(menu_options) - 1
        
        options_data = [data for _, _, data in menu_options]
        
        self.clear_screen()
        self.draw_box(80, f"ПОКУПКА ТОВАРОВ {npc.name}")
        
        # Информация о торговце
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['npc_trader']} {Fore.LIGHTYELLOW_EX}{npc.name}{Style.RESET_ALL}: {Fore.LIGHTCYAN_EX}{npc.description}{Style.RESET_ALL}")
        
        # Отображаем текущий баланс игрока
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} {Fore.YELLOW}Ваши деньги: {self.player.money} монет{Style.RESET_ALL}")
        self.draw_separator(80)
        
        # Показываем меню с товарами
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Выберите товар для покупки:{Style.RESET_ALL}")
        
        # Функция для отображения списка товаров
        def display_options():
            for i, (item_id, display_text, _) in enumerate(menu_options):
                if i == current_option:
                    # Очищаем текст от цветовых кодов для выделения
                    clean_text = display_text
                    for color_code in [Fore.YELLOW, Fore.GREEN, Fore.RED, Fore.BLUE, Fore.MAGENTA, 
                                       Fore.CYAN, Fore.WHITE, Fore.LIGHTBLUE_EX, Fore.LIGHTGREEN_EX, 
                                       Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX,
                                       Style.BRIGHT, Style.DIM]:
                        clean_text = clean_text.replace(color_code, '')
                    clean_text = clean_text.replace(Style.RESET_ALL, '')
                    
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color} > {clean_text} {Style.RESET_ALL}")
                else:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {display_text}")
        
        display_options()
        self.draw_bottom_box(80)
        self.print_footer("↑↓: Выбор, Enter: Купить, Esc: Назад")
        
        # Обработка нажатий клавиш
        key = self.get_key()
    
        
        if key == 'UP' or key == 'w' or key == 'W' or key == 'ц' or key == 'Ц':
            current_option = (current_option - 1) % len(menu_options)
        elif key == 'DOWN' or key == 's' or key == 'S' or key == 'ы' or key == 'Ы':
            current_option = (current_option + 1) % len(menu_options)
        elif key == 'ENTER':
            if menu_options:  # Если есть товары
                result = options_data[current_option]
                item_id, item_data, price, can_afford, item_description = result
                
                # Проверка, может ли игрок позволить себе товар
                if not can_afford:
                    self.clear_screen()
                    self.draw_box(80, f"ОШИБКА ПОКУПКИ ТОВАРОВ {npc.name}")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}У вас недостаточно денег для покупки этого товара!{Style.RESET_ALL}")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Требуется: {Fore.YELLOW}{price} монет{Style.RESET_ALL}, у вас: {Fore.YELLOW}{self.player.money} монет{Style.RESET_ALL}")
                    self.draw_bottom_box(80)
                    print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
                    self.get_key()
                    continue
                
                # Проверяем, не закончился ли товар (на случай, если играем с несколькими экземплярами игры)
                if npc.sells[item_id]["count"] <= 0:
                    self.clear_screen()
                    self.draw_box(80, f"ОШИБКА ПОКУПКИ ТОВАРОВ {npc.name}")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}Этот товар закончился!{Style.RESET_ALL}")
                    self.draw_bottom_box(80)
                    print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
                    self.get_key()
                    continue
                
                # Если нужно выбрать количество (при наличии нескольких)
                quantity = 1
                if npc.sells[item_id]["count"] > 1:
                    quantity = select_quantity(self, npc.sells[item_id]["count"], item_data.get("name", item_id))
                    if quantity <= 0:  # Пользователь отменил выбор
                        continue
                
                # Считаем полную стоимость
                total_price = price * quantity
                
                # Проверяем, хватает ли денег на общую стоимость
                if self.player.money < total_price:
                    self.clear_screen()
                    self.draw_box(80, f"ОШИБКА ПОКУПКИ ТОВАРОВ {npc.name}")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}У вас недостаточно денег для покупки {quantity} единиц товара!{Style.RESET_ALL}")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Требуется: {Fore.YELLOW}{total_price} монет{Style.RESET_ALL}, у вас: {Fore.YELLOW}{self.player.money} монет{Style.RESET_ALL}")
                    self.draw_bottom_box(80)
                    print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
                    self.get_key()
                    continue
                
                # Создаем предметы и добавляем их в инвентарь игрока
                items_added = 0
                total_spent = 0
                
                # Создаем один предмет с нужным количеством
                item = self.game.create_inventory_item(item_id, quantity)
                if item and self.player.spend_money(price * quantity):
                    self.player.add_item(item)
                    npc.sells[item_id]["count"] -= quantity
                    items_added = quantity
                    total_spent = price * quantity
                    
                    # Повышаем навык торговли, если он есть у NPC
                    if hasattr(npc, 'trade_exp'):
                        trade_exp = npc.trade_exp * quantity
                        if hasattr(self.player, 'skill_system') and self.player.skill_system and self.player.skill_system.get_skill("trading"):
                            exp_info = self.player.skill_system.add_experience("trading", trade_exp)
                            if exp_info:
                                skill_name = exp_info["skill_name"]
                                gained_exp = exp_info["gained_exp"]
                
                # Информируем игрока о результате покупки
                self.clear_screen()
                self.draw_box(80, f"УСПЕШНАЯ ПОКУПКА ТОВАРОВ {npc.name}")
                
                item_name = item_data.get("name", item_id)
                
                if items_added > 0:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}✓ Вы успешно приобрели {Fore.LIGHTYELLOW_EX}{item_name} x{items_added}{Fore.GREEN}!{Style.RESET_ALL}")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} Потрачено: {Fore.YELLOW}{total_spent} монет{Style.RESET_ALL}, осталось: {Fore.YELLOW}{self.player.money} монет{Style.RESET_ALL}")
                    
                    # Показываем полученный опыт торговли
                    if hasattr(npc, 'trade_exp'):
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
                        trade_exp = npc.trade_exp * quantity
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['skill']} {Fore.MAGENTA}Опыт торговли:{Style.RESET_ALL} +{trade_exp}")
                    
                    # Если у товара есть описание, выводим его
                    if item_description:
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}Описание:{Style.RESET_ALL} {item_description}")
                else:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}Произошла ошибка при покупке товара.{Style.RESET_ALL}")
                
                self.draw_bottom_box(80)
                print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
                self.get_key()
                
                # Проверяем, остались ли ещё товары для продажи
                if not any(details.get("count", 0) > 0 for _, details in npc.sells.items()):
                    return
                
                # Не делаем return, чтобы обновить список товаров на следующей итерации цикла
            else:
                return
        elif key == 'ESC':
            return

def sell_to_npc(self, npc):
    from src.ui.GameMenu import BOX_CHARS, ICONS, KEY_UP, KEY_DOWN, KEY_ENTER, KEY_ESC
    """Интерфейс для продажи предметов NPC"""
    self.clear_screen()
    self.draw_box(80, f"ПРОДАЖА ПРЕДМЕТОВ {npc.name}")
    if not npc.buys:
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.info_color}Этот торговец не покупает никаких предметов.{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
        self.get_key()
        return
    
    # Вместо show_menu реализуем свою логику выбора
    current_option = 0
    
    while True:
        # Получаем предметы из инвентаря игрока, которые можно продать
        sellable_items = []
        for item in self.player.inventory.get_items():
            if hasattr(item, 'id') and item.id in npc.buys:
                sellable_items.append(item)
        
        if not sellable_items:
            self.clear_screen()
            self.draw_box(80, f"ПРОДАЖА ПРЕДМЕТОВ {npc.name}")
            
            # Добавляем информацию о торговце
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['npc_trader']} {Fore.LIGHTYELLOW_EX}{npc.name}{Style.RESET_ALL}: {Fore.LIGHTCYAN_EX}{npc.description}{Style.RESET_ALL}")
            
            # Отображаем текущий баланс игрока
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} {Fore.YELLOW}Ваши деньги: {self.player.money} монет{Style.RESET_ALL}")
            self.draw_separator(80)
            
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.info_color}У вас нет предметов, которые этот торговец готов купить.{Style.RESET_ALL}")
            self.draw_bottom_box(80)
            print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
            self.get_key()
            return
        
        # Создаем список предметов для продажи
        menu_options = []
        
        for item in sellable_items:
            # Получаем базовую стоимость предмета
            item_data = self.game.get_item(item.id)
            base_price = item_data.get("value", 0) if item_data else 0
            item_description = item_data.get("description", "") if item_data else ""
            
            # Вычисляем цену покупки с учетом модификатора
            buy_price = npc.get_buy_price(item.id, base_price)
            
            # Определяем цвет для редкости и иконку
            rarity_color = Fore.WHITE
            rarity_icon = ICONS['common']
            
            if hasattr(item, 'get_rarity'):
                item_rarity = item.get_rarity()
                if item_rarity == "UNCOMMON":
                    rarity_color = Fore.GREEN
                    rarity_icon = ICONS['uncommon']
                elif item_rarity == "RARE":
                    rarity_color = Fore.LIGHTBLUE_EX
                    rarity_icon = ICONS['rare']
                elif item_rarity == "EPIC":
                    rarity_color = Fore.MAGENTA
                    rarity_icon = ICONS['epic']
                elif item_rarity == "LEGENDARY":
                    rarity_color = Fore.YELLOW
                    rarity_icon = ICONS['legendary']
                elif item_rarity == "MYTHIC":
                    rarity_color = Fore.RED
                    rarity_icon = ICONS['mythic']
            
            # Создаем более информативное и визуально приятное отображение предмета
            display_text = f"{rarity_icon} {rarity_color}{item.name}{Style.RESET_ALL} "
            
            # Добавляем информацию о количестве
            display_text += f"({Fore.CYAN}{item.get_count()} шт.{Style.RESET_ALL})"
            
            # Добавляем цену продажи
            display_text += f" - {ICONS['money']} {Fore.YELLOW}{buy_price} монет/шт.{Style.RESET_ALL}"
            
            # Добавляем общую стоимость
            total_price = buy_price * item.get_count()
            display_text += f" │ {Fore.LIGHTGREEN_EX}Всего: {total_price} монет{Style.RESET_ALL}"
            
            # Используем кортеж (item, buy_price, description) для доп. информации
            menu_options.append((item.id, display_text, (item, buy_price, item_description)))
        
        # Проверяем, нужно ли корректировать current_option после обновления списка
        if menu_options and current_option >= len(menu_options):
            current_option = len(menu_options) - 1
        
        options_data = [data for _, _, data in menu_options]
        
        self.clear_screen()
        self.draw_box(80, f"ПРОДАЖА ПРЕДМЕТОВ {npc.name}")
        
        # Информация о торговце
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['npc_trader']} {Fore.LIGHTYELLOW_EX}{npc.name}{Style.RESET_ALL}: {Fore.LIGHTCYAN_EX}{npc.description}{Style.RESET_ALL}")
        
        # Отображаем текущий баланс игрока
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} {Fore.YELLOW}Ваши деньги: {self.player.money} монет{Style.RESET_ALL}")
        self.draw_separator(80)
        
        # Показываем меню с предметами
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Выберите предмет для продажи:{Style.RESET_ALL}")
        
        # Функция для отображения списка предметов
        def display_options():
            for i, (item_id, display_text, _) in enumerate(menu_options):
                if i == current_option:
                    # Очищаем текст от цветовых кодов для выделения
                    clean_text = display_text
                    for color_code in [Fore.YELLOW, Fore.GREEN, Fore.RED, Fore.BLUE, Fore.MAGENTA, 
                                       Fore.CYAN, Fore.WHITE, Fore.LIGHTBLUE_EX, Fore.LIGHTGREEN_EX, 
                                       Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX,
                                       Style.BRIGHT, Style.DIM]:
                        clean_text = clean_text.replace(color_code, '')
                    clean_text = clean_text.replace(Style.RESET_ALL, '')
                    
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color} > {clean_text} {Style.RESET_ALL}")
                else:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {display_text}")
        
        display_options()
        self.draw_bottom_box(80)
        self.print_footer("↑↓: Выбор, Enter: Продать, Esc: Назад")
        
        # Обработка нажатий клавиш
        key = self.get_key()
    
        
        if key == 'UP' or key == 'w' or key == 'W' or key == 'ц' or key == 'Ц':
            current_option = (current_option - 1) % len(menu_options)
        elif key == 'DOWN' or key == 's' or key == 'S' or key == 'ы' or key == 'Ы':
            current_option = (current_option + 1) % len(menu_options)
        elif key == 'ENTER':
            if menu_options:  # Если есть предметы
                result = options_data[current_option]
                item, buy_price, item_description = result
                
                # Если у игрока несколько единиц этого предмета, спрашиваем количество
                quantity = 1
                if item.get_count() > 1:
                    # Подменю для выбора количества
                    quantity = select_quantity(self, item.get_count(), item.name)
                    if quantity == 0:  # Игрок отменил продажу
                        continue
                
                # Удаляем предмет из инвентаря и добавляем деньги
                total_price = buy_price * quantity
                
                if quantity >= item.get_count():
                    self.player.inventory.remove_item(item)
                else:
                    item.set_count(item.get_count() - quantity)
                
                self.player.add_money(total_price)
                
                # Повышаем навык торговли, если он есть у NPC
                if hasattr(npc, 'trade_exp'):
                    trade_exp = npc.trade_exp * quantity
                    if hasattr(self.player, 'skill_system') and self.player.skill_system and self.player.skill_system.get_skill("trading"):
                        exp_info = self.player.skill_system.add_experience("trading", trade_exp)
                        if exp_info:
                            skill_name = exp_info["skill_name"]
                            gained_exp = exp_info["gained_exp"]
                
                self.clear_screen()
                self.draw_box(80, f"УСПЕШНАЯ ПРОДАЖА {npc.name}")
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}✓ Вы успешно продали {Fore.LIGHTYELLOW_EX}{quantity} {item.name}{Fore.GREEN}!{Style.RESET_ALL}")
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} Получено: {Fore.YELLOW}{total_price} монет{Style.RESET_ALL}, теперь у вас: {Fore.YELLOW}{self.player.money} монет{Style.RESET_ALL}")
                
                # Показываем полученный опыт торговли
                if hasattr(npc, 'trade_exp'):
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
                    trade_exp = npc.trade_exp * quantity
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['skill']} {Fore.MAGENTA}Опыт торговли:{Style.RESET_ALL} +{trade_exp}")
                
                self.draw_bottom_box(80)
                
                print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
                self.get_key()
                
                # После продажи возвращаемся к экрану продажи, если у игрока еще есть что продавать
                if not self.player.inventory.get_items() or all(item.id not in npc.buys for item in self.player.inventory.get_items() if hasattr(item, 'id')):
                    return
            else:
                return
        elif key == 'ESC':
            return

def select_quantity(self, max_quantity, item_name):
    from src.ui.GameMenu import BOX_CHARS, ICONS, KEY_UP, KEY_DOWN, KEY_ENTER, KEY_ESC
    """Позволяет игроку выбрать количество предметов для продажи/покупки
    
    Args:
        max_quantity: Максимальное доступное количество
        item_name: Название предмета
        
    Returns:
        int: Выбранное количество, 0 если операция отменена
    """
    if max_quantity <= 1:
        return 1  # Если только один предмет, возвращаем 1 без выбора
        
    quantity = 1
    presets = [1, max(1, max_quantity // 4), max(1, max_quantity // 2), max_quantity]
    presets = sorted(list(set(presets)))  # Убираем дубликаты и сортируем
    
    menu_options = [
        ("custom", f"{ICONS['item']} Выбрать другое количество"),
        ("cancel", f"{ICONS['back']} Отмена")
    ]
    
    # Добавляем предустановленные значения в начало списка
    for preset in presets:
        percentage = int(preset/max_quantity*100)
        percentage_color = Fore.GREEN
        
        # Цвет для процента в зависимости от значения
        if percentage < 25:
            percentage_color = Fore.CYAN
        elif percentage < 50:
            percentage_color = Fore.GREEN
        elif percentage < 75:
            percentage_color = Fore.YELLOW
        else:
            percentage_color = Fore.RED
            
        menu_options.insert(0, (str(preset), f"{Fore.LIGHTYELLOW_EX}{preset} шт.{Style.RESET_ALL} ({percentage_color}{percentage}%{Style.RESET_ALL})"))
    
    current_option = 0
    
    while True:
        self.clear_screen()
        self.draw_box(80, f"ВЫБОР КОЛИЧЕСТВА")
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['item']} {self.highlight_color}Предмет:{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{item_name}{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Доступно:{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}{max_quantity} шт.{Style.RESET_ALL}")
        
        # Создаем шкалу для наглядного отображения
        progress_bar = self.create_progress_bar(max_quantity, max_quantity, width=40, color=Fore.LIGHTGREEN_EX)
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {progress_bar}")
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        # Вместо show_menu используем собственную логику выбора
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Выберите количество:{Style.RESET_ALL}")
        
        # Выводим опции
        for i, (option_id, option_text) in enumerate(menu_options):
            if i == current_option:
                # Очищаем текст от цветовых кодов для выделения
                clean_text = option_text
                for color_code in [Fore.YELLOW, Fore.GREEN, Fore.RED, Fore.BLUE, Fore.MAGENTA, 
                                  Fore.CYAN, Fore.WHITE, Fore.LIGHTBLUE_EX, Fore.LIGHTGREEN_EX, 
                                  Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX,
                                  Style.BRIGHT, Style.DIM]:
                    clean_text = clean_text.replace(color_code, '')
                clean_text = clean_text.replace(Style.RESET_ALL, '')
                
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color} > {clean_text} {Style.RESET_ALL}")
            else:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {option_text}")
        
        self.draw_bottom_box(80)
        self.print_footer("↑↓: Выбор, Enter: Выбрать, Esc: Отмена")
        
        # Получаем нажатую клавишу
        key = self.get_key()
        
        # Обрабатываем навигацию
        if key == 'UP' or key == 'w' or key == 'W' or key == 'ц' or key == 'Ц':
            current_option = (current_option - 1) % len(menu_options)
        elif key == 'DOWN' or key == 's' or key == 'S' or key == 'ы' or key == 'Ы':
            current_option = (current_option + 1) % len(menu_options)
        elif key == 'ENTER':
            option_id = menu_options[current_option][0]
            
            if option_id == "cancel":
                return 0
            elif option_id == "custom":
                # Запрашиваем ввод пользовательского количества
                self.clear_screen()
                self.draw_box(80, f"ВВОД КОЛИЧЕСТВА")
                
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['item']} {self.highlight_color}Предмет:{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{item_name}{Style.RESET_ALL}")
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Доступно:{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}{max_quantity} шт.{Style.RESET_ALL}")
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Введите количество (от 1 до {max_quantity}):{Style.RESET_ALL}")
                self.draw_bottom_box(80)
                
                # Читаем ввод пользователя
                user_input = ""
                while True:
                    print(f"{self.title_color}> {user_input}{Style.RESET_ALL}", end="\r")
                    key = self.get_key()
                    
                    if key == 'ENTER':
                        if user_input.strip():
                            break
                    elif key == 'ESC':
                        return 0  # Отмена
                    elif key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                        # Разрешаем ввод только цифр
                        user_input += key
                        # Ограничиваем длину до разумного предела
                        if len(user_input) > 10:  
                            user_input = user_input[:10]
                    elif key in ['\b', '\x7f']:  # Backspace
                        user_input = user_input[:-1]
                
                # Преобразуем ввод в число и проверяем границы
                try:
                    custom_quantity = int(user_input)
                    if 1 <= custom_quantity <= max_quantity:
                        return custom_quantity
                    else:
                        # Показываем сообщение об ошибке и продолжаем цикл
                        self.clear_screen()
                        self.draw_box(80, f"ОШИБКА ВВОДА")
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}Количество должно быть от 1 до {max_quantity}!{Style.RESET_ALL}")
                        self.draw_bottom_box(80)
                        print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
                        self.get_key()
                except ValueError:
                    # Если введено не число, показываем сообщение об ошибке
                    self.clear_screen()
                    self.draw_box(80, f"ОШИБКА ВВОДА")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}Пожалуйста, введите число!{Style.RESET_ALL}")
                    self.draw_bottom_box(80)
                    print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
                    self.get_key()
            else:
                try:
                    return int(option_id)
                except ValueError:
                    return 1
        elif key == 'ESC':
            return 0

def start_quest(self, npc, quest_id):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Начинает новый квест от NPC"""
    self.logger.info(f"Попытка начать квест {quest_id} от NPC {npc.id}")
    
    # Получаем объект квеста
    quest = self.game.get_quest(quest_id)
    if not quest:
        self.logger.error(f"Квест {quest_id} не найден!")
        print(f"Ошибка: Квест '{quest_id}' не найден.")
        time.sleep(1)
        return False
    
    # Проверяем, есть ли квест у NPC
    if hasattr(npc, 'available_quests') and quest_id not in npc.available_quests:
        self.logger.warning(f"Квест {quest_id} не доступен у NPC {npc.id}")
        print(f"Этот NPC больше не предлагает квест '{quest.name}'.")
        time.sleep(1)
        return False
    
    # Проверка уровня игрока
    if self.game.player.level < quest.requirements["level"]:
        self.logger.warning(f"Уровень игрока ({self.game.player.level}) недостаточен для квеста {quest_id} (требуется {quest.requirements['level']})")
        self.clear_screen()
        self.draw_box(80, "НЕДОСТАТОЧНЫЙ УРОВЕНЬ")
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}Вы не можете принять этот квест!{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Для квеста '{quest.name}' требуется {quest.requirements['level']} уровень.")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Ваш текущий уровень: {self.game.player.level}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Заработайте больше опыта, выполняя другие задания или собирая ресурсы.")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        self.draw_bottom_box(80)
        print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
        self.get_key()
        return False
    
    # Проверяем, может ли игрок начать квест по другим требованиям
    if hasattr(quest, 'can_be_started') and not quest.can_be_started(self.game.player):
        # Показываем сообщение о невыполненных требованиях
        self.clear_screen()
        self.draw_box(80, "НЕВОЗМОЖНО НАЧАТЬ КВЕСТ")
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}Вы не соответствуете требованиям для начала этого квеста:{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        # Вывод других требований по необходимости
        for skill_id, min_level in quest.requirements.get("skills", {}).items():
            skill = self.game.player.skill_system.get_skill(skill_id)
            if skill:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} - Требуемый навык {skill.name}: {min_level} (у вас {skill.level})")
            else:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} - Требуемый навык {skill_id}: {min_level} (не изучен)")
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
        self.get_key()
        return False
    
    # Запускаем квест
    if self.game.start_quest(quest_id):
        self.logger.info(f"Квест {quest_id} успешно начат")
        
        # Показываем информацию о квесте
        self.clear_screen()
        self.draw_box(80, f"НОВОЕ ЗАДАНИЕ: {quest.name}")
        
        # Описание квеста с переносами строк для красивого отображения
        formatted_description = self.wrap_text(quest.description, 70)
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {formatted_description}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        # Рисуем разделитель перед наградами
        self.draw_separator(80)
        
        # Показываем награды
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Награда:{Style.RESET_ALL}")
        
        if quest.rewards["experience"] > 0:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} - {Fore.YELLOW}Опыт:{Style.RESET_ALL} {quest.rewards['experience']}")
        
        if quest.rewards["money"] > 0:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} - {Fore.YELLOW}Монеты:{Style.RESET_ALL} {quest.rewards['money']}")
        
        if quest.rewards["items"]:
            for item_id, count in quest.rewards["items"].items():
                item_data = self.game.get_item(item_id)
                item_name = item_data.get("name", item_id) if item_data else item_id
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} - {Fore.YELLOW}Предмет:{Style.RESET_ALL} {item_name} x{count}")
        
        if quest.rewards["skills"]:
            for skill_id, exp_amount in quest.rewards["skills"].items():
                skill = self.game.player.skill_system.get_skill(skill_id)
                skill_name = skill.name if skill else skill_id
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} - {Fore.YELLOW}Опыт навыка {skill_name}:{Style.RESET_ALL} {exp_amount}")
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        # Рисуем разделитель перед предложением отслеживать квест
        self.draw_separator(80)
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Хотите отслеживать этот квест? {Fore.GREEN}(Д){Style.RESET_ALL}/{Fore.RED}(Н){Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        
        # Предлагаем отслеживать квест
        key = self.get_key()
        if key.lower() == 'y':
            self.game.track_quest(quest_id)
            self.clear_screen()
            self.draw_box(80, "КВЕСТ ДОБАВЛЕН")
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}Квест '{quest.name}' добавлен в отслеживаемые.{Style.RESET_ALL}")
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
            self.draw_bottom_box(80)
            print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
            self.get_key()
        
        return True
    else:
        self.logger.warning(f"Не удалось начать квест {quest_id}")
        return False

def complete_quest(self, npc, quest_id):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Завершает квест и выдает награды"""
    quest = self.game.get_quest(quest_id)
    if not quest:
        return False
    
    # Завершаем квест и выдаем награды
    if self.game.complete_quest(quest_id):
        # Показываем диалог с NPC перед сообщением о завершении квеста
        completion_text = quest.completion_text if hasattr(quest, 'completion_text') and quest.completion_text else f"Спасибо за выполнение задания '{quest.name}'."
        
        # Показываем диалог завершения квеста
        self.clear_screen()
        self.draw_box(80, f"ДИАЛОГ С {npc.name.upper()}")
        
        # Отображаем текст NPC с переносами строк
        formatted_text = self.wrap_text(completion_text, 70, 0)
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}{npc.name}:{Style.RESET_ALL} {formatted_text}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        self.draw_separator(80)
        
        # Добавляем опцию продолжения
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Герой:{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {self.selected_color} ❯ Спасибо за награду. {Style.RESET_ALL}")
        
        self.print_footer()
        self.get_key()
        
        # Показываем сообщение о завершении квеста
        self.clear_screen()
        self.draw_box(80, "КВЕСТ ВЫПОЛНЕН")
        
        # Форматируем название квеста с выделением
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}✓{Style.RESET_ALL} {self.highlight_color}Вы успешно выполнили квест:{Style.RESET_ALL}")
        formatted_name = f"{Fore.CYAN}{quest.name}{Style.RESET_ALL}"
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {formatted_name}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        # Рисуем разделитель перед наградами
        self.draw_separator(80)
        
        # Отображаем полученные награды с небольшой анимацией
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Полученные награды:{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        # Добавляем небольшую задержку для эффекта анимации
        time.sleep(0.3)
        
        # Опыт
        if quest.rewards["experience"] > 0:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {ICONS['experience']} {Fore.LIGHTBLUE_EX}Опыт:{Style.RESET_ALL} {quest.rewards['experience']} XP")
            time.sleep(0.2)
        
        # Деньги
        if quest.rewards["money"] > 0:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {ICONS['money']} {Fore.LIGHTYELLOW_EX}Деньги:{Style.RESET_ALL} {quest.rewards['money']} золота")
            time.sleep(0.2)
        
        # Предметы
        if quest.rewards["items"]:
            for item_id, count in quest.rewards["items"].items():
                item_data = self.game.get_item(item_id)
                item_name = item_data.get("name", item_id) if item_data else item_id
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {ICONS['item']} {Fore.LIGHTGREEN_EX}Предмет:{Style.RESET_ALL} {item_name} x{count}")
                time.sleep(0.2)
        
        # Опыт навыков
        if quest.rewards["skills"]:
            for skill_id, exp_amount in quest.rewards["skills"].items():
                skill = self.game.player.skill_system.get_skill(skill_id)
                skill_name = skill.name if skill else skill_id
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {ICONS['skill']} {Fore.LIGHTMAGENTA_EX}Навык:{Style.RESET_ALL} {skill_name} +{exp_amount} XP")
                time.sleep(0.2)
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        
        print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
        self.get_key()
        
        # Отмечаем квест как выполненный у NPC
        if hasattr(npc, 'mark_quest_completed'):
            npc.mark_quest_completed(quest_id)
        
        return True
    else:
        self.logger.warning(f"Не удалось завершить квест {quest_id}")
        return False