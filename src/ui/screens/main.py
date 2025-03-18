from colorama import Fore, Style

def main_menu(self):
    """Главное меню игры"""
    self.running = True
    current_option = 0
    options = ["Начать игру", 'Загрузить игру', "Настройки", "Выход"]
    
    while self.running:
        self.clear_screen()
        
        # Выводим заголовок
        print(f"\n{self.title_color}╭───────────────────────────────────────────────────────────────╮{Style.RESET_ALL}")
        print(f"{self.title_color}│{Style.RESET_ALL}                        {self.highlight_color}ТЕКСТОВАЯ RPG{Style.RESET_ALL}                        {self.title_color}│{Style.RESET_ALL}")
        print(f"{self.title_color}╰───────────────────────────────────────────────────────────────╯{Style.RESET_ALL}")
        
        # Отображаем информацию об активном квесте, если есть
        tracked_quest = self.game.get_tracked_quest()
        if tracked_quest:
            print(f"\n {Fore.LIGHTYELLOW_EX}📌 Активный квест: {tracked_quest.name}{Style.RESET_ALL}")
            
            # Получаем текущую стадию и отображаем задачи
            current_stage = tracked_quest.get_current_stage()
            if current_stage:
                progress_lines = tracked_quest.get_progress_text(self.game).split('\n')
                for i, line in enumerate(progress_lines, 1):
                    # Применяем цвет в зависимости от статуса задачи
                    if "✅" in line:
                        line = line.replace("✅", f"{Fore.GREEN}✅{Style.RESET_ALL}")
                    elif "❌" in line:
                        line = line.replace("❌", f"{Fore.RED}❌{Style.RESET_ALL}")
                    print(f" {i}. {line}")
            print("")
        
        # Выводим варианты меню с цифрами для выбора
        print("\n")
        for i, option in enumerate(options):
            if i == current_option:
                print(f"{self.selected_color}   [{i+1}] {option} {Style.RESET_ALL}")
            else:
                print(f"     [{i+1}] {option}")
        
        print("\n")
        print(f"{self.normal_color}Используйте цифры 1-{len(options)} для выбора или W/S для навигации и Enter для подтверждения{Style.RESET_ALL}")
        
        # Если включен режим отладки, выводим подсказку
        if self.debug_mode:
            print(f"\n{self.error_color}Режим отладки включен. Введенные клавиши будут отображаться здесь.{Style.RESET_ALL}")
        
        # Получаем ввод от пользователя
        key = self.get_key()
        
        # Отладочная информация
        if self.debug_mode:
            print(f"Нажата клавиша: {repr(key)} (тип: {type(key)})")
            input("Нажмите Enter для продолжения...")
        
        # Обработка цифровых клавиш
        if key in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            option_num = int(key) - 1
            if 0 <= option_num < len(options):
                if option_num == 0:  # Начать игру
                    self.start_game()
                elif option_num == 1:  # Настройки
                    self.show_settings()
                elif option_num == 2:  # Выход
                    self.running = False
                    print("Спасибо за игру!")
                    return
        
        # Обработка клавиш навигации
        elif key in ['w', 'W'] or key == b'H' or key == 'UP':
            current_option -= 1
            # Если вышли за верхнюю границу, переходим в конец списка
            if current_option < 0:
                current_option = len(options) - 1
        elif key in ['s', 'S'] or key == b'P' or key == 'DOWN':
            current_option += 1
            # Если вышли за нижнюю границу, переходим в начало списка
            if current_option >= len(options):
                current_option = 0
        elif key in ['\r', '\n', b'\r', b'\n'] or key == 'ENTER':
            if current_option == 0:  # Начать игру
                self.start_game()
            elif current_option == 1:  # Настройки
                self.show_settings()
            elif current_option == 2:  # Выход
                self.running = False
                print("Спасибо за игру!")
                return
        elif key in ['\x1b', 'q', 'Q'] or key == 'ESC':
            self.running = False
            print("Спасибо за игру!")
            return