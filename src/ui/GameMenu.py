import os
import time
import readchar
from colorama import init, Fore, Back, Style
import msvcrt
import logging

from src.models.quests.Quest import Quest
from src.models.npc.QuestNPC import QuestNPC  # Добавляем библиотеку для Windows
from src.ui.screens.components.tracking import print_tracked_quest, print_tracked_target
from src.ui.screens.inventory import format_resource_name, show_inventory
from src.ui.screens.npc import talk_to_npc
from src.ui.screens.quests import show_quests
from src.ui.screens.skills import show_skills
from src.ui.screens.glossary import show_glossary
# Инициализация colorama для работы с цветами в консоли
init()

# Коды клавиш для управления (разные варианты для разных систем)
KEY_UP = ['\x1b[A', '\x1bOA', 'UP']
KEY_DOWN = ['\x1b[B', '\x1bOB', 'DOWN']
KEY_RIGHT = ['\x1b[C', '\x1bOC', 'RIGHT']
KEY_LEFT = ['\x1b[D', '\x1bOD', 'LEFT']
KEY_ENTER = ['\r', '\n', 'ENTER']
KEY_ESC = ['\x1b', 'ESC']
KEY_SPACE = [' ', 'SPACE']

# Unicode-символы для красивых рамок
BOX_CHARS = {
    'h_line': '━',        # горизонтальная линия
    'v_line': '┃',        # вертикальная линия
    'tl_corner': '┏',     # верхний левый угол
    'tr_corner': '┓',     # верхний правый угол
    'bl_corner': '┗',     # нижний левый угол
    'br_corner': '┛',     # нижний правый угол
    'lt_joint': '┣',      # соединение слева
    'rt_joint': '┫',      # соединение справа
    't_joint': '┳',       # соединение сверху
    'b_joint': '┻',       # соединение снизу
    'cross': '╋',         # перекрестие
}

# Символы-иконки для различных элементов
ICONS = {
    'location': '🏠',     # локация
    'travel': '👣',       # перемещение
    'resource': '🌿',     # ресурс
    'collect': '⛏️',      # добыча
    'inventory': '🎒',    # инвентарь
    'quest': '📜',       # квесты
    'skills': '📊',       # навыки
    'mining': '⚒️',       # горное дело
    'herbalism': '🌱',    # травничество
    'elementalism': '🔮', # элементализм
    'alchemy': '⚗️',      # алхимия
    'back': '↩️',         # назад
    'player': '👤',       # игрок
    'common': '⚪',       # обычный предмет
    'uncommon': '🟢',     # необычный предмет
    'rare': '🔵',         # редкий предмет
    'epic': '🟣',         # эпический предмет
    'legendary': '🟡',    # легендарный предмет
    'mythic': '🔴',       # мифический предмет
    'npc': '👤',          # NPC
    'npc_trader': '💰',  # торговец
    'npc_quest': '📝',   # квестовый NPC
    'npc_dialogue': '💬', # диалоговый NPC
    'experience': '✨',    # опыт
    'money': '💰',         # деньги
    'item': '📦',          # предмет
    'skill': '🔧',         # навык
    'book': '📖',          # книга/глоссарий
}

class GameMenu:
    def __init__(self, game):
        self.game = game
        self.player = game.player
        self.running = True
        self.debug_mode = False  # Временно включаем режим отладки
        
        # Цвета и стили для меню
        self.title_color = Fore.CYAN
        self.selected_color = Fore.BLACK + Back.LIGHTBLACK_EX  # Меняем CYAN на LIGHTBLACK_EX для серого фона
        self.normal_color = Fore.WHITE
        self.highlight_color = Fore.YELLOW
        self.resource_color = Fore.GREEN
        self.location_color = Fore.LIGHTBLUE_EX
        self.error_color = Fore.RED
        self.action_color = Fore.MAGENTA
        self.info_color = Fore.WHITE + Style.BRIGHT
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('game_menu.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def clear_screen(self):
        """Очищает экран консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def draw_box(self, width, title=None, color=None):
        """Рисует красивую рамку с заголовком"""
        if color is None:
            color = self.title_color
            
        # Верхняя граница
        if title:
            title_len = len(title) + 4  # Добавляем отступы для заголовка
            left_padding = (width - title_len) // 2
            right_padding = width - title_len - left_padding
            
            print(f"{color}{BOX_CHARS['tl_corner']}{BOX_CHARS['h_line'] * left_padding} {title} {BOX_CHARS['h_line'] * right_padding}{BOX_CHARS['tr_corner']}{Style.RESET_ALL}")
        else:
            print(f"{color}{BOX_CHARS['tl_corner']}{BOX_CHARS['h_line'] * (width-2)}{BOX_CHARS['tr_corner']}{Style.RESET_ALL}")
            
    def draw_bottom_box(self, width, color=None):
        """Рисует нижнюю часть рамки"""
        if color is None:
            color = self.title_color
            
        print(f"{color}{BOX_CHARS['bl_corner']}{BOX_CHARS['h_line'] * (width-2)}{BOX_CHARS['br_corner']}{Style.RESET_ALL}")
        
    def draw_separator(self, width, color=None):
        """Рисует разделитель в рамке"""
        if color is None:
            color = self.title_color
            
        print(f"{color}{BOX_CHARS['lt_joint']}{BOX_CHARS['h_line'] * (width-2)}{BOX_CHARS['rt_joint']}{Style.RESET_ALL}")
        
    def print_header(self, title):
        """Печатает заголовок меню с красивой рамкой"""
        self.clear_screen()
        self.draw_box(80, title)
        print()
        
    def print_footer(self, help_text="↑↓: Выбор, Enter: Подтвердить, Esc: Назад"):
        """Печатает нижнюю часть меню с подсказками и красивой рамкой"""
        print()
        self.draw_separator(80)
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {help_text:^76} {self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        
        # Убираем вызов show_quest_path_in_footer из этого метода
        # if self.game.tracked_quest_id:
        #     self.show_quest_path_in_footer()
    
    def get_key(self):
        """Получает нажатую клавишу с поддержкой разных систем"""
        try:
            if os.name == 'nt':  # Windows
                # Очищаем буфер ввода
                while msvcrt.kbhit():
                    msvcrt.getch()
                
                # Получаем клавишу
                key = msvcrt.getch()
                
                # Обрабатываем специальные клавиши (стрелки)
                if key == b'\xe0':
                    second_key = msvcrt.getch()
                    
                    # Преобразуем коды в понятные значения
                    if second_key == b'H':
                        return 'UP'
                    elif second_key == b'P':
                        return 'DOWN'
                    elif second_key == b'M':
                        return 'RIGHT'
                    elif second_key == b'K':
                        return 'LEFT'
                    return second_key  # Возвращаем второй байт
                
                # Обрабатываем Enter, Escape и пробел
                if key == b'\r':
                    return 'ENTER'
                elif key == b'\x1b':
                    return 'ESC'
                elif key == b' ':
                    return 'SPACE'
                
                # Для обычных клавиш пробуем декодировать
                try:
                    return key.decode('utf-8')
                except:
                    return key
                
            else:  # Linux/Mac
                key = readchar.readkey()
                
                # Обрабатываем коды стрелок
                if key == '\x1b[A':
                    return 'UP'
                elif key == '\x1b[B':
                    return 'DOWN'
                elif key == '\x1b[C':
                    return 'RIGHT'
                elif key == '\x1b[D':
                    return 'LEFT'
                elif key in ['\r', '\n']:
                    return 'ENTER'
                elif key == '\x1b':
                    return 'ESC'
                
                return key
                
        except Exception as e:
            if self.debug_mode:
                print(f"Ошибка в get_key(): {e}")
            return None
    
    def show_menu(self, title, options, allow_cancel=True):
        """Отображает меню и возвращает выбранный пункт"""
        current_option = 0
        
        while True:
            self.clear_screen()
            self.draw_box(80, title)
            
            for i, option in enumerate(options):
                # Проверяем, является ли опция кортежем
                display_text = option[1] if isinstance(option, (list, tuple)) else option
                
                # Получаем описание, если оно есть
                description = None
                if isinstance(option, (list, tuple)) and len(option) > 2:
                    description = option[2]
                
                # Обработка выбранной опции
                if i == current_option:
                    # Очищаем текст от цветовых кодов
                    clean_text = display_text
                    if isinstance(clean_text, str):
                        for color_code in [self.resource_color, self.location_color, Fore.YELLOW, Fore.GREEN, Fore.RED, 
                                         Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTBLUE_EX,
                                         Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX,
                                         Style.BRIGHT, Style.DIM]:
                            clean_text = clean_text.replace(color_code, '')
                        clean_text = clean_text.replace(Style.RESET_ALL, '')
                    
                    # Отображаем выбранный пункт
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color} > {clean_text:<30} {Style.RESET_ALL}", end="")
                    
                    # Отображаем описание, если оно есть
                    if description:
                        if isinstance(description, str):
                            # Для строкового описания
                            print(f"{self.selected_color}{description}{Style.RESET_ALL}")
                        elif isinstance(description, tuple) and len(description) >= 5:
                            # Для кортежа с данными товара (используем элемент с индексом 4 - описание товара)
                            print(f"{self.selected_color}{description[4]}{Style.RESET_ALL}")
                        else:
                            print()
                    else:
                        print()
                else:
                    # Для невыбранных пунктов просто выводим текст
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {display_text:<30}", end="")
                    
                    # И описание, если оно есть
                    if description:
                        if isinstance(description, str):
                            print(f"{self.info_color}{description}{Style.RESET_ALL}")
                        elif isinstance(description, tuple) and len(description) >= 5:
                            print(f"{self.info_color}{description[4]}{Style.RESET_ALL}")
                        else:
                            print()
                    else:
                        print()
            
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
            
            if allow_cancel:
                self.draw_bottom_box(80, "Выход - ESC")
            else:
                self.draw_bottom_box(80)
            
            key = self.get_key()
            
            if key in KEY_UP:
                current_option -= 1
                # Если вышли за верхнюю границу, переходим в конец списка
                if current_option < 0:
                    current_option = len(options) - 1
            elif key in KEY_DOWN:
                current_option += 1
                # Если вышли за нижнюю границу, переходим в начало списка
                if current_option >= len(options):
                    current_option = 0
            elif key in KEY_ENTER:
                # Возвращаем выбранную опцию
                selected = options[current_option]
                
                # Если выбранный элемент - кортеж с данными товара
                if isinstance(selected, (list, tuple)) and len(selected) > 2 and isinstance(selected[2], tuple):
                    return selected[2]  # Возвращаем кортеж с данными товара
                elif isinstance(selected, (list, tuple)):
                    return selected[0]  # Возвращаем ID
                else:
                    return selected      # Возвращаем саму опцию
            elif key in KEY_ESC and allow_cancel:
                return None
    
    def format_resource(self, resource_id, count):
        """Форматирует название ресурса для отображения с учетом редкости"""
        item_data = self.game.get_item(resource_id)
        if item_data and "name" in item_data:
            # Определяем цвет на основе редкости
            rarity_color = Fore.WHITE  # По умолчанию обычный
            
            if "rarity" in item_data:
                rarity = item_data["rarity"]
                if rarity == "UNCOMMON":
                    rarity_color = Fore.GREEN
                elif rarity == "RARE":
                    rarity_color = Fore.LIGHTBLUE_EX
                elif rarity == "EPIC":
                    rarity_color = Fore.MAGENTA
                elif rarity == "LEGENDARY":
                    rarity_color = Fore.YELLOW
                elif rarity == "MYTHIC":
                    rarity_color = Fore.RED
                
            return f"{rarity_color}{item_data['name']}{Style.RESET_ALL} ({count})"
        return f"{resource_id} ({count})"
    
    def start_game(self):
        """Запускает игровой процесс"""
        # Сюда добавим код для начала игры
        self.game_loop()
    
    def game_loop(self):
        """Основной игровой цикл"""
        while self.running:
            # Обновляем состояние игры
            self.game.update()
            
            # Обновляем прогресс всех активных квестов
            self.game.update_quest_progress()
            
            # Показываем текущую локацию
            self.look_around()
            
            # Проверяем условия выхода из цикла
            if not self.running:
                break
    
    def look_around(self):
        """Показывает информацию о текущей локации и доступных действиях"""
        options = []
        display_options = []
        display_options_disabled = []

        location = self.player.current_location

        # Выводим информацию о локации
        self.clear_screen()
        
        # Рисуем верхнюю часть рамки с названием локации
        self.draw_box(80, f"ЛОКАЦИЯ: {location.name}")
        
        # Описание локации
        formatted_description = self.wrap_text(location.description, 70)
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {formatted_description}")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        # Отображаем информацию о текущем отслеживаемом квесте, если есть
        has_tracked_quest = print_tracked_quest(self)
        
        # Отображаем информацию о текущей отслеживаемой цели, если есть и если нет отслеживаемого квеста
        # Приоритет отдаем квесту
        has_tracked_target = False
        if not has_tracked_quest:
            has_tracked_target = print_tracked_target(self)
        
        # Если есть отслеживаемый квест или цель, добавляем разделитель
        if has_tracked_quest or has_tracked_target:
            self.draw_separator(80)
        
        # Получаем доступные для перехода локации
        connected_locations = []
        for loc_id in location.connected_locations:
            loc = self.game.get_location(loc_id)
            if loc:
                connected_locations.append((loc_id, loc.name))
                
        # Получаем информацию о пути к отслеживаемой цели
        tracked_info = self.game.get_tracked_target_info()
        next_location_on_path = None
        is_quest_target = False
        
        # Проверяем отслеживаемые предметы/NPC
        if tracked_info and tracked_info["path"]:
            next_location_on_path = tracked_info["path"][0]
            
        # Проверяем отслеживаемый квест
        quest_path = []
        if self.game.tracked_quest_id:
            quest_path = self.game.calculate_path_to_quest_target()
            # Если есть путь к цели квеста и нет пути к отслеживаемой цели,
            # или если приоритет отдается квесту
            if quest_path and (not next_location_on_path or not tracked_info):
                next_location_on_path = quest_path[0]
                is_quest_target = True
        
        # Добавляем возможность перехода в другие локации
        for loc_id, loc_name in connected_locations:
            options.append(("travel", loc_id))
            
            # Проверяем, находится ли локация на пути к цели
            if loc_id == next_location_on_path:
                # Выделяем локацию более заметно с иконкой компаса
                compass_icon = "🧭"  # Иконка компаса для навигации
                
                # Разное оформление для цели квеста и отслеживаемой цели
                if is_quest_target:
                    target_info = f"{Fore.LIGHTGREEN_EX}[➜ цель квеста]{Style.RESET_ALL}"
                else:
                    target_info = f"{Fore.LIGHTGREEN_EX}[➜ отслеживаемая цель: {tracked_info['name']}]{Style.RESET_ALL}"
                    
                display_options.append(f"{ICONS['travel']} {compass_icon} {Fore.LIGHTYELLOW_EX}{loc_name} {target_info}")
            else:
                display_options.append(f"{ICONS['travel']} Идти в: {self.location_color}{loc_name}{Style.RESET_ALL}")
        
        # Добавляем варианты сбора ресурсов с проверкой требуемых навыков
        for res_id, count in location.resources.items():
            if count > 0:
                item_data = self.game.get_item(res_id)
                can_collect = True
                required_skills = {}
                
                # Проверяем требуемые навыки
                if item_data and "required_skills" in item_data:
                    required_skills = item_data["required_skills"]
                    for skill_id, min_level in required_skills.items():
                        skill = self.player.skill_system.get_skill(skill_id)
                        if not skill or skill.level < min_level:
                            can_collect = False
                            break
                
                if can_collect:
                    options.append(("collect", res_id))
                    display_options.append(f"{ICONS['collect']} Добыть: {self.resource_color}{format_resource_name(self, res_id)}{Style.RESET_ALL} ({count})")
                else:
                    # Показываем недоступные ресурсы в сером цвете с указанием требуемых навыков
                    missing_skills_info = ""
                    if required_skills:
                        missing_skills = []
                        for skill_id, min_level in required_skills.items():
                            skill = self.player.skill_system.get_skill(skill_id)
                            current_level = skill.level if skill else 0
                            if not skill or current_level < min_level:
                                skill_name = skill.name if skill else skill_id.capitalize()
                                missing_skills.append(f"{Fore.LIGHTRED_EX}[ТРЕБУЕТСЯ {min_level} навык {skill_name}]{Style.RESET_ALL}")
                        missing_skills_info = " ".join(missing_skills)
                    
                    display_options_disabled.append(f"{Fore.LIGHTBLACK_EX}{ICONS['collect']} Добыть: {format_resource_name(self, res_id)} ({count}){Style.RESET_ALL} {missing_skills_info}")
        
        # Добавляем доступ к навыкам
        options.append(("skills", None))
        display_options.append(f"{ICONS['skills']} Навыки (N)")
        
        # Добавляем доступ к инвентарю
        options.append(("inventory", None))
        display_options.append(f"{ICONS['inventory']} Инвентарь (I)")
        
        # Добавляем доступ к квестам
        options.append(("quests", None))
        display_options.append(f"{ICONS['quest']} Квесты (Q)")
        
        # Добавляем доступ к глоссарию
        options.append(("glossary", None))
        display_options.append(f"{ICONS['book']} Глоссарий (G)")
        
        # Добавляем NPC в локации
        npcs = self.game.get_npcs_at_location(location.id)
        if npcs:
            print(f"\n{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Персонажи в локации:{Style.RESET_ALL}")
            for npc in npcs:
                npc_icon = ICONS['npc_trader'] if npc.type == 'trader' else ICONS['npc_quest'] if npc.type == 'quest' else ICONS['npc_dialogue']
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {npc_icon} {npc.name} - {npc.description}")
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        
        # Добавляем возможность поговорить с NPC
        for npc in npcs:
            options.append(("talk", npc.id))
            npc_icon = ICONS['npc_trader'] if npc.type == 'trader' else ICONS['npc_quest'] if npc.type == 'quest' else ICONS['npc_dialogue']
            display_options.append(f"{ICONS['npc_dialogue']} Поговорить с: {self.normal_color}{npc.name} {npc_icon}{Style.RESET_ALL}")
        
        current_option = 0
        
        while True:
            self.clear_screen()
            
            # Рисуем верхнюю часть рамки с названием локации
            self.draw_box(80, f"ЛОКАЦИЯ: {location.name}")
            
            # Выводим описание локации в красивой рамке
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {location.description}")
            
            # Отображаем информацию об отслеживаемом квесте, если есть
            tracked_quest = self.game.get_tracked_quest()
            if tracked_quest:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}📌 Активный квест: {tracked_quest.name}{Style.RESET_ALL}")
                
                # Получаем текущую стадию и отображаем цели
                current_stage = tracked_quest.get_current_stage()
                if current_stage:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.CYAN}Текущий этап: {current_stage.name}{Style.RESET_ALL}")
                    progress_lines = tracked_quest.get_progress_text(self.game).split('\n')
                    for i, line in enumerate(progress_lines, 1):
                        # Применяем цвет в зависимости от статуса задачи
                        colored_line = line
                        if "✅" in line:  # Выполненная задача
                            colored_line = line.replace("✅", f"{Fore.GREEN}✅{Fore.RESET}")
                            colored_line = f"{Fore.GREEN}{colored_line}{Style.RESET_ALL}"
                        elif "❌" in line:  # Невыполненная задача
                            colored_line = line.replace("❌", f"{Fore.RED}❌{Fore.RESET}")
                            colored_line = f"{Fore.YELLOW}{colored_line}{Style.RESET_ALL}"
                        
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {i}. {colored_line}")
                
                # Отображаем информацию о пути к цели квеста
                location_id, target_name, target_type = self.game.get_tracked_quest_target_location()
                if location_id:
                    # Получаем путь к целевой локации
                    path = self.game.calculate_path_to_quest_target()
                    
                    # Получаем название локации
                    target_location = self.game.get_location(location_id)
                    location_name = target_location.name if target_location else location_id
                    
                    # Определяем иконку в зависимости от типа цели
                    icon = ICONS['location']
                    if target_type == "npc":
                        icon = ICONS['npc']
                    elif target_type == "resource":
                        icon = ICONS['resource']
                    
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}Цель квеста:{Style.RESET_ALL} {icon} {Fore.LIGHTYELLOW_EX}{target_name}{Style.RESET_ALL} в {Fore.LIGHTYELLOW_EX}{location_name}{Style.RESET_ALL}")
                    
                    # Отображаем следующий шаг, если игрок не в той же локации
                    if path:
                        next_location = self.game.get_location(path[0])
                        next_location_name = next_location.name if next_location else path[0]
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.LIGHTCYAN_EX}Следующий шаг:{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}➤ {next_location_name}{Style.RESET_ALL} ({len(path)} перех.)")
                    else:
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}Вы находитесь в нужной локации!{Style.RESET_ALL}")
            # Если нет активного квеста, проверяем отслеживаемую цель из глоссария
            elif self.game.tracked_target:
                tracked_info = self.game.get_tracked_target_info()
                if tracked_info:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
                    
                    target_name = tracked_info["name"]
                    target_type = tracked_info["target_type"]
                    target_location = self.game.get_location(tracked_info["target_location"])
                    location_name = target_location.name if target_location else tracked_info["target_location"]
                    path = tracked_info["path"]
                    
                    # Определяем иконку в зависимости от типа
                    icon = ICONS['resource'] if target_type == "resource" else ICONS['npc']
                    
                    # Отображаем название цели
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}📌 Отслеживаемая цель:{Style.RESET_ALL} {icon} {Fore.LIGHTYELLOW_EX}{target_name}{Style.RESET_ALL}")
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.LIGHTCYAN_EX}Находится в:{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{location_name}{Style.RESET_ALL}")
                    
                    # Отображаем маршрут, если игрок не в той же локации
                    if path:
                        next_location = self.game.get_location(path[0])
                        next_location_name = next_location.name if next_location else path[0]
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.LIGHTCYAN_EX}Следующий шаг:{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}➤ {next_location_name}{Style.RESET_ALL} ({len(path)} перех.)")
                    else:
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {Fore.GREEN}Вы находитесь в нужной локации!{Style.RESET_ALL}")
            
            # Рисуем разделитель
            self.draw_separator(80)
            
            # Выводим доступные ресурсы с указанием требуемых навыков
            if location.resources:
                has_resources = False
                for res_id, count in location.resources.items():
                    if count > 0:
                        if not has_resources:
                            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}{ICONS['resource']} Доступные ресурсы:{Style.RESET_ALL}")
                            has_resources = True
                        
                        # Проверяем требуемые навыки для ресурса
                        item_data = self.game.get_item(res_id)
                        can_collect = True
                        missing_skills_info = ""
                        
                        if item_data and "required_skills" in item_data:
                            for skill_id, min_level in item_data["required_skills"].items():
                                skill = self.player.skill_system.get_skill(skill_id)
                                if not skill or skill.level < min_level:
                                    can_collect = False
                                    skill_name = skill.name if skill else skill_id.capitalize()
                                    missing_skills_info = f" {Fore.LIGHTRED_EX}[ТРЕБУЕТСЯ {min_level} навык {skill_name}]{Style.RESET_ALL}"
                                    break
                        
                        if can_collect:
                            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {self.resource_color}{format_resource_name(self, res_id)}{Style.RESET_ALL} ({count})")
                        else:
                            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {Fore.LIGHTBLACK_EX}{format_resource_name(self, res_id)}{Style.RESET_ALL} ({count}){missing_skills_info}")
                
                if has_resources:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
            
            # Выводим связанные локации
            if location.connected_locations:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}{ICONS['location']} Отсюда можно пойти в:{Style.RESET_ALL}")
                for loc_id in location.connected_locations:
                    target_location = self.game.get_location(loc_id)
                    if target_location:
                        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {self.location_color}{target_location.name}{Style.RESET_ALL}")
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
            
            # Рисуем разделитель перед списком действий
            self.draw_separator(80)
            
            # Выводим доступные действия в формате селектора
            print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.highlight_color}Доступные действия:{Style.RESET_ALL}")
            
            # Сначала основные опции
            for i, option in enumerate(display_options):
                if i == current_option:
                    # Удаляем все цветовые коды из текста и делаем его чёрным на сером фоне
                    clean_option = option
                    for color_code in [self.resource_color, self.location_color, Fore.YELLOW, Fore.GREEN, Fore.RED, 
                                      Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTBLUE_EX,
                                      Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX,
                                      Style.BRIGHT, Style.DIM]:
                        clean_option = clean_option.replace(color_code, '')
                    clean_option = clean_option.replace(Style.RESET_ALL, '')
                    
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {self.selected_color} ❯ {clean_option} {Style.RESET_ALL}")
                else:
                    print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {option}")
            
            # Затем отключенные опции
            for option in display_options_disabled:
                print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}   {option}")
            
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
                action_type, action_id = options[current_option]
                
                if action_type == "travel":
                    self.player.move_to(self.game, action_id)
                    location = self.player.current_location
                    return self.look_around()
                    
                elif action_type == "collect":
                    resource_count = location.resources.get(action_id, 0)
                    if resource_count > 0:
                        # Запоминаем активные квесты до сбора ресурса
                        progress_before = {}
                        for quest_id, quest in self.game.active_quests.items():
                            current_stage = quest.get_current_stage()
                            if current_stage:
                                progress_before[quest_id] = current_stage.get_progress_text()
                        
                        # Собираем ресурс
                        self.player.collect_resource(self.game, action_id, resource_count)
                        print(f"{self.highlight_color}Вы собрали {resource_count} {format_resource_name(self, action_id)}{Style.RESET_ALL}")
                        
                        # Обновляем прогресс квестов и проверяем изменения
                        if self.game.update_quest_progress():
                            # Проверяем, связаны ли собранные предметы с квестами
                            for quest_id, quest in self.game.active_quests.items():
                                current_stage = quest.get_current_stage()
                                if current_stage and quest_id in progress_before:
                                    new_progress = current_stage.get_progress_text()
                                    if new_progress != progress_before[quest_id]:
                                        print(f"{Fore.LIGHTYELLOW_EX}✨ Обновлен прогресс квеста: {quest.name}{Style.RESET_ALL}")
                                        # Отображаем обновленные задачи с цветовой маркировкой
                                        progress_lines = new_progress.split('\n')
                                        for line in progress_lines:
                                            if action_id.lower() in line.lower() and "✅" in line:
                                                print(f"  {Fore.GREEN}{line}{Style.RESET_ALL}")
                                            elif action_id.lower() in line.lower():
                                                print(f"  {Fore.YELLOW}{line}{Style.RESET_ALL}")
                        
                        time.sleep(1.5)  # Увеличиваем задержку для отображения сообщений
                        return self.look_around()
                    
                elif action_type == "skills":
                    show_skills(self)
                
                elif action_type == "inventory":
                    show_inventory(self)
                
                elif action_type == "quests":
                    show_quests(self)
                    return self.look_around()
                
                elif action_type == "glossary":
                    show_glossary(self)
                    return self.look_around()
                
                elif action_type == "talk":
                    npc = self.game.get_npc(action_id)
                    if npc:
                        talk_to_npc(self, npc)
                        return self.look_around()
                
            elif key == 'ESC': # Удалили 'or key == 'Q'
                break
            # Добавляем горячие клавиши для быстрого доступа
            elif key == 'N' or key == 'n':  # Навыки
                show_skills(self)
                return self.look_around()
            elif key == 'I' or key == 'i':  # Инвентарь
                show_inventory(self)
                return self.look_around()
            elif key == 'Q' or key == 'q':  # Квесты
                show_quests(self)
                return self.look_around()
            elif key == 'G' or key == 'g':  # Глоссарий
                show_glossary(self)
                return self.look_around()
        
        # Обновление ресурсов перед выходом
        self.game.update()
    
    def exit_game(self):
        """Выход из игры"""
        self.clear_screen()
        self.draw_box(80, "ВЫХОД ИЗ ИГРЫ")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} Вы уверены, что хотите выйти из игры? (Д/Н)")
        print(f"{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL}")
        self.draw_bottom_box(80)
        
        key = self.get_key()
        if key.lower() in ['д', 'y', 'd']:
            self.running = False
            return True
        
        return False
    
    def wrap_text(self, text, max_width=70, indent=0):
        """Разбивает длинный текст на несколько строк для удобного чтения
        
        Args:
            text (str): Исходный текст
            max_width (int): Максимальная ширина строки
            indent (int): Отступ для всех строк, кроме первой
        
        Returns:
            str: Отформатированный текст с переносами строк
        """
        if not text:
            return ""
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            # Если слово добавит больше символов, чем оставшаяся ширина строки
            if current_length + len(word) + (1 if current_line else 0) > max_width:
                # Сохраняем текущую строку и начинаем новую
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                # Добавляем слово к текущей строке
                if current_line:
                    current_length += 1  # Пробел
                current_length += len(word)
                current_line.append(word)
        
        # Добавляем последнюю строку
        if current_line:
            lines.append(" ".join(current_line))
        
        # Формируем результат с отступами
        if not lines:
            return ""
        
        result = lines[0]
        indent_str = " " * indent
        
        for line in lines[1:]:
            result += f"\n{self.title_color}{BOX_CHARS['v_line']}{Style.RESET_ALL} {indent_str}{line}"
        
        return result

    def create_progress_bar(self, current, maximum, width=20, color=Fore.GREEN):
        """Создает индикатор прогресса заданной ширины и цвета
        
        Args:
            current (int): Текущее значение
            maximum (int): Максимальное значение
            width (int): Ширина индикатора в символах
            color (str): Цвет заполненной части индикатора
            
        Returns:
            str: Строка с индикатором прогресса
        """
        if maximum <= 0:
            percent = 100
        else:
            percent = min(100, int((current / maximum) * 100))
        
        filled_width = int(width * percent / 100)
        empty_width = width - filled_width
        
        bar = f"{color}{'█' * filled_width}{Style.RESET_ALL}{'░' * empty_width}"
        return bar 