import os
import datetime
import inspect
import sys
import traceback
from enum import Enum

class LogLevel(Enum):
    DEBUG = (0, "\033[94m", "DEBUG")    # Синий
    INFO = (1, "\033[92m", "INFO")      # Зеленый
    WARNING = (2, "\033[93m", "WARNING") # Желтый
    ERROR = (3, "\033[91m", "ERROR")    # Красный
    CRITICAL = (4, "\033[95m", "CRITICAL") # Фиолетовый

class Logger:
    """
    Класс для логирования сообщений в файл и консоль
    Реализован как Singleton для обеспечения единого экземпляра
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, log_file="logs.log", min_level=LogLevel.INFO, console_output=False):
        if self._initialized:
            return
            
        self.log_file = log_file
        self.min_level = min_level
        self.console_output = console_output
        
        # Создаем директорию для логов, если она не существует
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Проверяем, существует ли файл логов, если нет - создаем его
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Запуск логирования {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        
        self._initialized = True
        self.info("Логирование инициализировано")
    
    def _log(self, level, message, *args):
        """Внутренний метод для записи лога"""
        if level.value[0] < self.min_level.value[0]:
            return
            
        # Форматирование сообщения с аргументами
        if args:
            message = message.format(*args)
            
        # Получение информации о вызывающем коде
        frame = inspect.currentframe().f_back.f_back
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        caller_func = frame.f_code.co_name
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] {level.value[2]:8} | {filename}:{lineno} ({caller_func}) | {message}"
        
        # Запись в файл
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(formatted_message + '\n')
        
        # Вывод в консоль
        if self.console_output:
            color_code = level.value[1]
            print(f"{color_code}{formatted_message}\033[0m")
    
    def debug(self, message, *args):
        """Логирование отладочной информации"""
        self._log(LogLevel.DEBUG, message, *args)
    
    def info(self, message, *args):
        """Логирование информационных сообщений"""
        self._log(LogLevel.INFO, message, *args)
    
    def warning(self, message, *args):
        """Логирование предупреждений"""
        self._log(LogLevel.WARNING, message, *args)
    
    def error(self, message, *args):
        """Логирование ошибок"""
        self._log(LogLevel.ERROR, message, *args)
    
    def critical(self, message, *args):
        """Логирование критических ошибок"""
        self._log(LogLevel.CRITICAL, message, *args)
        
    def exception(self, message, exc_info=None):
        """Логирование исключений с трассировкой стека"""
        if exc_info is None:
            exc_info = sys.exc_info()
        
        if exc_info[0] is not None:
            tb_lines = traceback.format_exception(*exc_info)
            error_message = f"{message}\n{''.join(tb_lines)}"
            self._log(LogLevel.ERROR, error_message)
        else:
            self._log(LogLevel.ERROR, message) 