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
                    display_options.append(f"{option_text} [{level_warning}]")
                    continue
            
            # Стандартная проверка условий для других случаев
            if condition and not check_dialogue_condition(self, condition, npc):
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
        
        while True:
            self.clear_screen()
            self.draw_box(80, f"ДИАЛОГ: {npc.name}")
            
            # Отображаем текст NPC с переносами строк
            formatted_text = self.wrap_text(dialogue_text, 70, 0)
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}{npc.name}:{Style.RESET_ALL} {formatted_text}")
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
            self.draw_separator(80)
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Герой:{Style.RESET_ALL}")
            
            for i, option_text in enumerate(display_options):
                # Форматируем текст ответа, если он длинный
                formatted_option = self.wrap_text(option_text, 65, 2)
                
                if i == current_option:
                    # Удаляем все цветовые коды из текста и делаем его чёрным на сером фоне
                    clean_option = formatted_option
                    for color_code in [self.resource_color, self.location_color, Fore.YELLOW, Fore.GREEN, Fore.RED, 
                                        Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTBLUE_EX,
                                        Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX,
                                        Style.BRIGHT, Style.DIM]:
                        clean_option = clean_option.replace(color_code, '')
                    clean_option = clean_option.replace(Style.RESET_ALL, '')
                    
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color} ❯ {clean_option} {Style.RESET_ALL}")
                else:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {formatted_option}")
            
            self.print_footer()
            
            # Получаем нажатую клавишу
            key = self.get_key()
            
            if key == 'UP' or key == 'W':
                current_option -= 1
                # Если вышли за верхнюю границу, переходим в конец списка
                if current_option < 0:
                    current_option = len(options) - 1
            elif key == 'DOWN' or key == 'S':
                current_option += 1
                # Если вышли за нижнюю границу, переходим в начало списка
                if current_option >= len(options):
                    current_option = 0
            elif key == 'ENTER':
                next_id, action = options[current_option]
                
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
            
            elif key == 'ESC': # Удалили 'or key == 'Q'
                return

def check_dialogue_condition(self, condition, npc):
    """Проверяет условие для отображения варианта диалога"""
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
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Открывает интерфейс торговли с NPC"""
    if npc.type != "trader":
        return False
    
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
        
        # Информация о доступных действиях
        buys_count = len(npc.buys) if npc.buys else 0
        sells_count = sum(1 for item_info in npc.sells.values() if item_info.get("count", 0) > 0)
        
        options = [
            ("buy", f"{ICONS['money']} Купить товары {Fore.CYAN}({sells_count} доступно){Style.RESET_ALL}"),
            ("sell", f"{ICONS['inventory']} Продать предметы {Fore.CYAN}({buys_count} категорий){Style.RESET_ALL}"),
            ("exit", f"{ICONS['back']} Вернуться к разговору")
        ]
        
        choice = self.show_menu("", options, False)
        
        if choice == "exit" or choice is None:
            return False
        elif choice == "buy":
            buy_from_npc(self, npc)
        elif choice == "sell":
            sell_to_npc(self, npc)
    
    return False

def buy_from_npc(self, npc):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Интерфейс для покупки товаров у NPC"""
    self.clear_screen()
    self.draw_box(80, f"ПОКУПКА ТОВАРОВ {npc.name}")
    
    if not npc.sells:
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.info_color}У этого торговца нет товаров на продажу.{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
        self.get_key()
        return
    
    # Создаем список товаров на продажу (только доступные)
    available_items = [(item_id, details) for item_id, details in npc.sells.items() if details.get("count", 0) > 0]
    
    if not available_items:
        self.clear_screen()
        self.draw_box(80, f"ПОКУПКА ТОВАРОВ {npc.name}")
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
    
    while True:
        self.clear_screen()
        self.draw_box(80, f"ПОКУПКА ТОВАРОВ {npc.name}")
        
        # Информация о торговце
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['npc_trader']} {Fore.LIGHTYELLOW_EX}{npc.name}{Style.RESET_ALL}: {Fore.LIGHTCYAN_EX}{npc.description}{Style.RESET_ALL}")
        
        # Отображаем текущий баланс игрока
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} {Fore.YELLOW}Ваши деньги: {self.player.money} монет{Style.RESET_ALL}")
        self.draw_separator(80)
        
        # Показываем меню с товарами с помощью стандартного метода show_menu
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Выберите товар для покупки:{Style.RESET_ALL}")
        
        result = self.show_menu("", menu_options, True)
        
        if result is None:
            return
        
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
        
        for _ in range(quantity):
            item = self.game.create_inventory_item(item_id)
            if item and self.player.spend_money(price):
                self.player.add_item(item)
                npc.sells[item_id]["count"] -= 1
                items_added += 1
                total_spent += price
        
        # Информируем игрока о результате покупки
        self.clear_screen()
        self.draw_box(80, f"УСПЕШНАЯ ПОКУПКА ТОВАРОВ {npc.name}")
        
        item_name = item_data.get("name", item_id)
        
        if items_added > 0:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}✓ Вы успешно приобрели {Fore.LIGHTYELLOW_EX}{item_name} x{items_added}{Fore.GREEN}!{Style.RESET_ALL}")
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} Потрачено: {Fore.YELLOW}{total_spent} монет{Style.RESET_ALL}, осталось: {Fore.YELLOW}{self.player.money} монет{Style.RESET_ALL}")
            
            # Если у товара есть описание, выводим его
            if item_description:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}Описание:{Style.RESET_ALL} {item_description}")
        else:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.RED}Произошла ошибка при покупке товара.{Style.RESET_ALL}")
        
        self.draw_bottom_box(80)
        print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
        self.get_key()

def sell_to_npc(self, npc):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Интерфейс для продажи предметов NPC"""
    self.clear_screen()
    self.draw_box(80, f"ПРОДАЖА ПРЕДМЕТОВ {npc.name}")
    if not npc.buys:
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.info_color}Этот торговец не покупает никаких предметов.{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
        self.get_key()
        return
    
    # Получаем предметы из инвентаря игрока, которые можно продать
    sellable_items = []
    for item in self.player.inventory.get_items():
        if hasattr(item, 'id') and item.id in npc.buys:
            sellable_items.append(item)
    
    if not sellable_items:
        self.clear_screen()
        self.draw_box(80, f"ПРОДАЖА ПРЕДМЕТОВ {npc.name}")
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
    
    while True:
        self.clear_screen()
        self.draw_box(80, f"ПРОДАЖА ПРЕДМЕТОВ {npc.name}")
        
        # Информация о торговце
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['npc_trader']} {Fore.LIGHTYELLOW_EX}{npc.name}{Style.RESET_ALL}: {Fore.LIGHTCYAN_EX}{npc.description}{Style.RESET_ALL}")
        
        # Отображаем текущий баланс игрока
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} {Fore.YELLOW}Ваши деньги: {self.player.money} монет{Style.RESET_ALL}")
        self.draw_separator(80)
        
        # Показываем меню с предметами
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Выберите предмет для продажи:{Style.RESET_ALL}")
        
        result = self.show_menu("", menu_options, True)
        
        if result is None:
            return
        
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
        
        self.clear_screen()
        self.draw_box(80, f"УСПЕШНАЯ ПРОДАЖА {npc.name}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}✓ Вы успешно продали {Fore.LIGHTYELLOW_EX}{quantity} {item.name}{Fore.GREEN}!{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['money']} Получено: {Fore.YELLOW}{total_price} монет{Style.RESET_ALL}, теперь у вас: {Fore.YELLOW}{self.player.money} монет{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        print(f"{self.title_color}Нажмите любую клавишу для продолжения...{Style.RESET_ALL}")
        self.get_key()
        
        # После продажи возвращаемся к экрану продажи, если у игрока еще есть что продавать
        if not self.player.inventory.get_items() or all(item.id not in npc.buys for item in self.player.inventory.get_items() if hasattr(item, 'id')):
            return

def select_quantity(self, max_quantity, item_name):
    from src.ui.GameMenu import BOX_CHARS, ICONS
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
    
    while True:
        self.clear_screen()
        self.draw_box(80, f"ВЫБОР КОЛИЧЕСТВА")
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {ICONS['item']} {self.highlight_color}Предмет:{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{item_name}{Style.RESET_ALL}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Доступно:{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}{max_quantity} шт.{Style.RESET_ALL}")
        
        # Создаем шкалу для наглядного отображения
        progress_bar = self.create_progress_bar(max_quantity, max_quantity, width=40, color=Fore.LIGHTGREEN_EX)
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {progress_bar}")
        
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        result = self.show_menu("Выберите количество:", menu_options, False)
        
        if result == "cancel" or result is None:
            return 0
        elif result == "custom":
            # Здесь можно было бы реализовать ввод произвольного количества,
            # но для простоты будем использовать предустановленные значения
            continue
        else:
            try:
                return int(result)
            except ValueError:
                return 1
            
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
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Для квеста '{quest.name}' требуется {quest.requirements['level']} уровень.")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Ваш текущий уровень: {self.game.player.level}")
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
                skill = self.player.skill_system.get_skill(skill_id)
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
        if key.lower() in ['д', 'y', 'd']:
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