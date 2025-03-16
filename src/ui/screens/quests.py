from colorama import Fore, Style

def show_quests(self):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Отображает список активных и завершенных квестов"""
    current_option = 0
    back_option = False
    
    while self.running:
        self.clear_screen()
        
        self.draw_box(80, "КВЕСТЫ")
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
        
        # Получаем списки квестов
        active_quests = list(self.game.active_quests.values())
        completed_quests = list(self.game.completed_quests.values())
        
        # Формируем общий список опций
        options = []
        
        # Активные квесты
        if active_quests:
            options.append(("header", "АКТИВНЫЕ КВЕСТЫ"))
            for quest in active_quests:
                tracked_text = "📌 " if self.game.tracked_quest_id == quest.id else ""
                options.append(("active", f"{tracked_text}{quest.name}", quest))
        else:
            options.append(("empty", "Нет активных квестов"))
        
        # Разделитель
        options.append(("separator", ""))
        
        # Завершенные квесты
        if completed_quests:
            options.append(("header", "ЗАВЕРШЕННЫЕ КВЕСТЫ"))
            for quest in completed_quests:
                options.append(("completed", f"{quest.name}", quest))
        else:
            options.append(("empty", "Нет завершенных квестов"))
        
        # Добавляем опцию "Назад"
        options.append(("separator", ""))
        options.append(("back", "Назад"))
        
        # Отображаем заголовок
        
        # Отображаем список квестов
        for i, (option_type, option_text, *args) in enumerate(options):
            if option_type == "header":
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}{option_text}{Style.RESET_ALL}")
            elif option_type == "separator":
                self.draw_separator(80)
            elif option_type == "empty":
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.normal_color}{option_text}{Style.RESET_ALL}")
            elif option_type == "back":
                if i == current_option:
                    # Удаляем все цветовые коды из текста
                    clean_text = option_text
                    for color_code in [self.resource_color, self.location_color, Fore.YELLOW, Fore.GREEN, Fore.RED, 
                                        Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTBLUE_EX,
                                        Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX,
                                        Style.BRIGHT, Style.DIM]:
                        clean_text = clean_text.replace(color_code, '')
                    clean_text = clean_text.replace(Style.RESET_ALL, '')
                    
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color} ❯ {clean_text} {Style.RESET_ALL}")
                else:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {option_text}")
            else:  # активные и выполненные квесты
                # Определяем цвет в зависимости от типа и статуса
                quest_color = ""
                if option_type == "active":
                    quest_color = self.action_color
                elif option_type == "completed":
                    quest_color = self.normal_color
                
                if i == current_option:
                    # Очищаем текст от цветов
                    clean_text = option_text
                    for color_code in [self.resource_color, self.location_color, Fore.YELLOW, Fore.GREEN, Fore.RED, 
                                        Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTBLUE_EX,
                                        Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX,
                                        Style.BRIGHT, Style.DIM]:
                        clean_text = clean_text.replace(color_code, '')
                    clean_text = clean_text.replace(Style.RESET_ALL, '')
                    
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color} ❯ {clean_text} {Style.RESET_ALL}")
                else:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {quest_color}{option_text}{Style.RESET_ALL}")
        
        # Отображаем подсказки
        self.draw_separator(80)
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Используйте ↑↓ для выбора, Enter для подробностей, T для отслеживания, Esc для выхода")
        self.draw_bottom_box(80)
        
        # Получаем ввод
        key = self.get_key()
        
        # Навигация по списку
        if key in ['w', 'W', 'UP']:
            current_option -= 1
            # Пропускаем заголовки и разделители
            while True:
                # Если вышли за верхнюю границу, переходим в конец списка
                if current_option < 0:
                    current_option = len(options) - 1
                
                # Если текущая опция не является заголовком/разделителем/пустой строкой, выходим из цикла
                if options[current_option][0] not in ["header", "separator", "empty"]:
                    break
                
                # Иначе продолжаем двигаться вверх
                current_option -= 1
            
        elif key in ['s', 'S', 'DOWN']:
            current_option += 1
            # Пропускаем заголовки и разделители
            while True:
                # Если вышли за нижнюю границу, переходим в начало списка
                if current_option >= len(options):
                    current_option = 0
                
                # Если текущая опция не является заголовком/разделителем/пустой строкой, выходим из цикла
                if options[current_option][0] not in ["header", "separator", "empty"]:
                    break
                
                # Иначе продолжаем двигаться вниз
                current_option += 1
        
        elif key in ['\r', '\n', 'ENTER']:
            option_type = options[current_option][0]
            
            if option_type == "back":
                return  # Выходим из меню квестов
                
            elif option_type in ["active", "completed"]:
                # Показываем подробности о квесте
                quest = options[current_option][2]
                show_quest_details(self, quest)
                
        elif key in ['t', 'T']:
            # Переключаем отслеживание квеста
            option_type = options[current_option][0]
            if option_type == "active":
                quest = options[current_option][2]
                if self.game.tracked_quest_id == quest.id:
                    # Отменяем отслеживание
                    self.game.untrack_quest()
                else:
                    # Начинаем отслеживание
                    self.game.track_quest(quest.id)
                
        elif key in ['\x1b', 'q', 'Q', 'ESC']:
            return  # Выходим из меню квестов при нажатии ESC

def show_quest_details(self, quest):
    from src.ui.GameMenu import BOX_CHARS, ICONS
    """Показывает детальную информацию о квесте"""
    self.clear_screen()
    self.draw_box(80, f"КВЕСТ: {quest.name}")
    
    # Отображаем основную информацию
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Статус:{Style.RESET_ALL} {quest.get_status_text()}")
    
    if quest.giver_id:
        npc = self.game.get_npc(quest.giver_id)
        npc_name = npc.name if npc else "Неизвестный"
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Выдал:{Style.RESET_ALL} {npc_name}")
    
    # Отображаем NPC, которому нужно сдать квест, если он отличается от выдавшего квест
    if quest.taker_id and (quest.taker_id != quest.giver_id or not quest.giver_id):
        npc = self.game.get_npc(quest.taker_id)
        npc_name = npc.name if npc else "Неизвестный"
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Сдать:{Style.RESET_ALL} {Fore.YELLOW}{npc_name}{Style.RESET_ALL}")
    
    # Описание квеста
    if quest.description:
        self.draw_separator(80)
        formatted_description = self.wrap_text(quest.description, 70)
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {formatted_description}")
    
    # Текущий прогресс (для активных квестов)
    if quest.status == quest.STATUS_IN_PROGRESS:
        self.draw_separator(80)
        
        current_stage = quest.get_current_stage()
        if current_stage:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Текущие задачи:{Style.RESET_ALL}")
            progress_lines = quest.get_progress_text(self.game).split('\n')
            for line in progress_lines:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {line}")
            
            # Проверяем, готов ли квест к завершению
            if quest.is_ready_to_complete() and quest.taker_id:
                npc = self.game.get_npc(quest.taker_id)
                npc_name = npc.name if npc else quest.taker_id
                
                # Получаем имя локации вместо ID
                location_id = npc.location_id if npc else "неизвестная локация"
                location = self.game.get_location(location_id)
                location_name = location.name if location else location_id
                
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}✓ Квест готов к завершению!{Style.RESET_ALL}")
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}Для завершения поговорите с {npc_name} в локации {location_name}{Style.RESET_ALL}")
    
    # Награды
    self.draw_separator(80)
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Награды:{Style.RESET_ALL}")
    
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
    
    # Отображаем подсказки и ждем нажатия клавиши
    self.draw_separator(80)
    
    if quest.status == quest.STATUS_IN_PROGRESS:
        if self.game.tracked_quest_id == quest.id:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} [T] - Отменить отслеживание квеста")
        else:
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} [T] - Отслеживать квест")
    
    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Нажмите любую клавишу для возврата...")
    self.draw_bottom_box(80)
    
    # Ждем нажатия клавиши
    key = self.get_key()
    
    # Обработка нажатия T для переключения отслеживания
    if key in ['t', 'T'] and quest.status == quest.STATUS_IN_PROGRESS:
        if self.game.tracked_quest_id == quest.id:
            self.game.untrack_quest()
        else:
            self.game.track_quest(quest.id)
    # Добавляем явную обработку клавиши ESC
    elif key in ['\x1b', 'q', 'Q', 'ESC']:
        return  # Выходим из просмотра деталей квеста