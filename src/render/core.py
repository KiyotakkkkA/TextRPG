"""
Ядро движка рендеринга для консольной RPG игры.
Содержит базовые классы и функции для рендеринга UI и обработки ввода.
"""

import os
import sys
import msvcrt
import time
import colorama
from typing import List, Dict, Any, Optional, Union, Callable, Tuple
from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass
import threading

# Инициализация colorama для поддержки цветов в Windows
colorama.init()

# Константы для навигации
class Keys:
    UP = 72
    DOWN = 80
    LEFT = 75
    RIGHT = 77
    ENTER = 13
    ESCAPE = 27
    SPACE = 32
    TAB = 9
    BACKSPACE = 8

# Константы для цветов
class Color:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    RESET = '\033[0m'
    
    # Фоновые цвета
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'

class InputHandler:
    """
    Обработчик ввода с клавиатуры.
    Предоставляет методы для считывания нажатий клавиш.
    """
    @staticmethod
    def get_key() -> int:
        """
        Получает код нажатой клавиши.
        Для стрелок и других специальных клавиш сначала идет 0 или 224, затем код клавиши.
        """
        key = ord(msvcrt.getch())
        if key == 0 or key == 224:  # Специальные клавиши (стрелки и др.)
            key = ord(msvcrt.getch())
        return key
    
    @staticmethod
    def get_key_non_blocking() -> Optional[int]:
        """
        Неблокирующее получение кода нажатой клавиши.
        Если ничего не нажато, возвращает None.
        """
        if msvcrt.kbhit():
            return InputHandler.get_key()
        return None

class ConsoleHelper:
    """
    Вспомогательный класс для работы с консолью.
    Предоставляет методы для очистки экрана, позиционирования курсора и т.д.
    """
    @staticmethod
    def clear_screen():
        """Очищает экран консоли."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def hide_cursor():
        """Скрывает курсор консоли."""
        print("\033[?25l", end='')
    
    @staticmethod
    def show_cursor():
        """Показывает курсор консоли."""
        print("\033[?25h", end='')
    
    @staticmethod
    def get_terminal_size() -> Tuple[int, int]:
        """
        Возвращает размеры терминала (ширина, высота).
        """
        try:
            columns, lines = os.get_terminal_size()
            return columns, lines
        except:
            return 80, 24  # Значения по умолчанию
    
    @staticmethod
    def move_cursor(x: int, y: int):
        """
        Перемещает курсор в заданную позицию.
        """
        print(f"\033[{y};{x}H", end='')
    
    @staticmethod
    def colorize(text: str, color: str, bg_color: str = '') -> str:
        """
        Добавляет цвет к тексту.
        """
        return f"{color}{bg_color}{text}{Color.RESET}"
    
    @staticmethod
    def center_text(text: str, width: int) -> str:
        """
        Центрирует текст в пределах заданной ширины.
        """
        return text.center(width)
        
    @staticmethod
    def save_cursor_position():
        """Сохраняет текущую позицию курсора."""
        print("\033[s", end='')
        
    @staticmethod
    def restore_cursor_position():
        """Восстанавливает сохраненную позицию курсора."""
        print("\033[u", end='')
        
    @staticmethod
    def create_buffer(width: int, height: int) -> List[List[str]]:
        """Создает буфер заданного размера."""
        return [[' ' for _ in range(width)] for _ in range(height)]

class UIElement(ABC):
    """
    Базовый абстрактный класс для всех UI элементов.
    """
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.parent = None
        self.children = []
        self.needs_redraw = True
    
    def add_child(self, child: 'UIElement'):
        """
        Добавляет дочерний элемент.
        """
        self.children.append(child)
        child.parent = self
        return child
    
    def remove_child(self, child: 'UIElement'):
        """
        Удаляет дочерний элемент.
        """
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    @abstractmethod
    def render(self):
        """
        Рендерит элемент.
        """
        pass
    
    def render_all(self):
        """
        Рендерит элемент и все его дочерние элементы.
        """
        if not self.visible:
            return
        
        self.render()
        
        for child in self.children:
            child.render_all()
            
    def mark_for_redraw(self):
        """
        Помечает элемент как требующий перерисовки.
        """
        self.needs_redraw = True
        for child in self.children:
            child.mark_for_redraw()

class Renderer:
    """
    Класс для рендеринга UI элементов.
    """
    def __init__(self):
        self.console = ConsoleHelper()
        self.current_screen = None
        self.fps_limit = 30  # Ограничение FPS
        self.frame_time = 1.0 / self.fps_limit
        self.last_render_time = 0
        self.render_lock = threading.Lock()
        
        # Настройки буферизации
        self.use_double_buffer = True  # Включаем двойную буферизацию
        self.buffer = None
        self.width = 0
        self.height = 0
        self._init_buffer()
    
    def _init_buffer(self):
        """Инициализирует буфер для двойной буферизации."""
        self.width, self.height = ConsoleHelper.get_terminal_size()
        if self.use_double_buffer:
            self.buffer = ConsoleHelper.create_buffer(self.width, self.height)
    
    def set_current_screen(self, screen: 'Screen'):
        """
        Устанавливает текущий экран.
        """
        self.current_screen = screen
        if self.current_screen:
            self.current_screen.mark_for_redraw()
            self._do_render(force=True)  # Принудительно рендерим новый экран
    
    def render(self, force=False):
        """
        Рендерит текущий экран с ограничением FPS.
        """
        current_time = time.time()
        elapsed = current_time - self.last_render_time
        
        # Если прошло достаточно времени с последнего рендера или force=True
        if force or elapsed >= self.frame_time:
            self._do_render()
            self.last_render_time = current_time
    
    def _do_render(self, force=False):
        """
        Выполняет рендеринг текущего экрана.
        """
        if not self.current_screen:
            return
            
        # Используем блокировку для безопасного рендеринга из разных потоков
        with self.render_lock:
            # При первом рендере или при изменении размера терминала
            current_width, current_height = ConsoleHelper.get_terminal_size()
            if self.width != current_width or self.height != current_height:
                self.width, self.height = current_width, current_height
                if self.use_double_buffer:
                    self.buffer = ConsoleHelper.create_buffer(self.width, self.height)
                self.console.clear_screen()
                self.console.hide_cursor()
                force = True
                
            if force or self.current_screen.needs_redraw:
                if self.use_double_buffer:
                    # Используем двойную буферизацию
                    # Очищаем буфер
                    self.buffer = ConsoleHelper.create_buffer(self.width, self.height)
                    
                    # Рендерим экран в буфер
                    # TODO: Реализовать рендеринг в буфер
                    
                    # Выводим буфер
                    # TODO: Вывести буфер на экран
                    
                    # В текущей реализации двойная буферизация не реализована полностью,
                    # поэтому просто рендерим напрямую
                    self.console.clear_screen()
                    self.current_screen.render_all()
                    self.current_screen.needs_redraw = False
                else:
                    # Прямой рендеринг без буферизации
                    self.console.clear_screen()
                    self.current_screen.render_all()
                    self.current_screen.needs_redraw = False
                
                sys.stdout.flush()

class Screen(UIElement):
    """
    Базовый класс для всех экранов.
    """
    def __init__(self, engine: 'Engine'):
        columns, lines = ConsoleHelper.get_terminal_size()
        super().__init__(0, 0, columns, lines)
        self.engine = engine
        self.needs_redraw = True
    
    @abstractmethod
    def handle_input(self, key: int) -> bool:
        """
        Обрабатывает ввод с клавиатуры.
        Возвращает True, если ввод был обработан и требуется перерисовка.
        """
        # Базовые реализации следует переопределить
        return False
    
    @abstractmethod
    def update(self, dt: float):
        """
        Обновляет состояние экрана.
        """
        pass

class Engine:
    """
    Основной класс движка.
    Управляет рендерингом и вводом.
    """
    def __init__(self):
        self.renderer = Renderer()
        self.input_handler = InputHandler()
        self.screens = {}
        self.current_screen_name = None
        self.running = False
        self.last_time = time.time()
        
        # Новые настройки для производительности
        self.fps_limit = 10  # Уменьшаем ограничение FPS до 10 кадров в секунду
        self.frame_time = 1.0 / self.fps_limit
        self.update_rate = 20  # Снижаем частоту обновления логики для уменьшения нагрузки
        self.update_interval = 1.0 / self.update_rate
        self.last_update_time = 0
        self.input_check_interval = 0.010  # 10 мс - интервал проверки ввода
        self.render_on_input = True  # Рендерить сразу после ввода
        self.render_on_update = False  # НЕ рендерить после каждого обновления
        self.auto_render = False  # Отключаем автоматический рендеринг по таймеру
        
        # Флаги для отслеживания состояний
        self.input_detected = False
        self.needs_render = False
    
    def register_screen(self, name: str, screen: Screen):
        """
        Регистрирует экран.
        """
        self.screens[name] = screen
    
    def set_current_screen(self, name: str):
        """
        Устанавливает текущий экран.
        """
        if name in self.screens:
            self.current_screen_name = name
            self.renderer.set_current_screen(self.screens[name])
            self.needs_render = True
    
    def start(self):
        """
        Запускает главный цикл движка.
        """
        if not self.current_screen_name:
            raise ValueError("Текущий экран не установлен")
        
        self.running = True
        self.last_time = time.time()
        self.last_update_time = self.last_time
        
        # Скрываем курсор при запуске
        ConsoleHelper.hide_cursor()
        
        try:
            # Главный цикл
            while self.running:
                current_time = time.time()
                
                # Обработка ввода (проверяем часто, но не сразу обрабатываем)
                key = self.input_handler.get_key_non_blocking()
                if key is not None:
                    self.input_detected = True
                    if key == Keys.ESCAPE:
                        self.running = False
                    else:
                        if self.screens[self.current_screen_name].handle_input(key):
                            self.needs_render = True
                
                # Обновление логики с фиксированным интервалом
                update_elapsed = current_time - self.last_update_time
                if update_elapsed >= self.update_interval:
                    dt = update_elapsed
                    self.last_update_time = current_time
                    
                    # Обновляем экран
                    self.screens[self.current_screen_name].update(dt)
                    
                    # Рендерим после обновления, если нужно
                    if self.render_on_update:
                        self.needs_render = True
                
                # Рендеринг с ограничением FPS
                if self.needs_render or (self.auto_render and (current_time - self.renderer.last_render_time >= self.frame_time)):
                    self.renderer.render(force=self.needs_render)
                    self.needs_render = False
                
                # Спим немного, чтобы не нагружать CPU
                time.sleep(0.001)
        
        finally:
            # Показываем курсор перед выходом
            ConsoleHelper.show_cursor()
    
    def stop(self):
        """
        Останавливает главный цикл движка.
        """
        self.running = False 