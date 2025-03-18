from typing import Dict, List, Callable, Any, Optional, Type, TypeVar, Generic
from functools import wraps
from dataclasses import dataclass

E = TypeVar('E')

@dataclass
class EventMetadata:
    """Метаданные события для документации"""
    name: str
    description: str = ""
    params: Dict[str, str] = None
    example: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}
        if self.tags is None:
            self.tags = []

class EventSystem:
    """
    Синглтон для обработки событий и сигналов в игре.
    Реализует паттерн наблюдателя (Observer) для подписки на события.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventSystem, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Инициализация внутренних структур данных"""
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: Dict[str, List[Any]] = {}
        self._is_emitting = False
        self._pending_unsubscribes: List[tuple] = []
        self._event_metadata: Dict[str, EventMetadata] = {}
    
    def subscribe(self, event_name: str, callback: Callable) -> None:
        """
        Подписаться на событие
        
        :param event_name: Имя события
        :param callback: Функция обратного вызова
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """
        Отписаться от события
        
        :param event_name: Имя события
        :param callback: Функция обратного вызова
        """
        if self._is_emitting:
            # Если сейчас идет рассылка событий, откладываем отписку до конца
            self._pending_unsubscribes.append((event_name, callback))
            return
            
        if event_name in self._subscribers and callback in self._subscribers[event_name]:
            self._subscribers[event_name].remove(callback)
            
            # Если подписчиков не осталось, очищаем список
            if not self._subscribers[event_name]:
                del self._subscribers[event_name]
    
    def emit(self, event_name: str, *args, **kwargs) -> None:
        """
        Отправить событие всем подписчикам
        
        :param event_name: Имя события
        :param args: Позиционные аргументы
        :param kwargs: Именованные аргументы
        """
        self._is_emitting = True
        
        # Записываем событие в историю
        if event_name not in self._event_history:
            self._event_history[event_name] = []
        self._event_history[event_name].append((args, kwargs))
        
        # Ограничиваем историю событий
        if len(self._event_history[event_name]) > 10:
            self._event_history[event_name] = self._event_history[event_name][-10:]
        
        # Оповещаем подписчиков
        if event_name in self._subscribers:
            for callback in list(self._subscribers[event_name]):
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Ошибка при обработке события {event_name}: {str(e)}")
        
        self._is_emitting = False
        
        # Обрабатываем отложенные отписки
        for event_name, callback in self._pending_unsubscribes:
            self.unsubscribe(event_name, callback)
        self._pending_unsubscribes.clear()
    
    def get_last_event(self, event_name: str) -> Optional[tuple]:
        """
        Получить последнее событие из истории
        
        :param event_name: Имя события
        :return: Кортеж с аргументами события или None
        """
        if event_name in self._event_history and self._event_history[event_name]:
            return self._event_history[event_name][-1]
        return None
    
    def clear_history(self, event_name: Optional[str] = None) -> None:
        """
        Очистить историю событий
        
        :param event_name: Имя события или None для очистки всей истории
        """
        if event_name:
            if event_name in self._event_history:
                self._event_history[event_name] = []
        else:
            self._event_history.clear()
    
    def has_subscribers(self, event_name: str) -> bool:
        """
        Проверить, есть ли подписчики на событие
        
        :param event_name: Имя события
        :return: True, если есть подписчики
        """
        return event_name in self._subscribers and len(self._subscribers[event_name]) > 0
    
    # Новые методы для работы с метаданными событий
    def register_event(self, event_name: str, description: str = "", params: Dict[str, str] = None, 
                      example: str = "", tags: List[str] = None) -> None:
        """
        Регистрирует новое событие с документацией
        
        :param event_name: Имя события
        :param description: Описание события
        :param params: Словарь параметров события и их описаний
        :param example: Пример использования события
        :param tags: Список тегов для классификации событий
        """
        self._event_metadata[event_name] = EventMetadata(
            name=event_name,
            description=description,
            params=params or {},
            example=example,
            tags=tags or []
        )
    
    def get_event_metadata(self, event_name: str) -> Optional[EventMetadata]:
        """
        Получить метаданные события
        
        :param event_name: Имя события
        :return: Метаданные события или None, если событие не зарегистрировано
        """
        return self._event_metadata.get(event_name)
    
    def get_events_by_tag(self, tag: str) -> List[EventMetadata]:
        """
        Получить список событий с указанным тегом
        
        :param tag: Тег для фильтрации
        :return: Список метаданных событий
        """
        return [metadata for metadata in self._event_metadata.values() if tag in metadata.tags]
    
    def get_all_events(self) -> Dict[str, EventMetadata]:
        """
        Получить все зарегистрированные события
        
        :return: Словарь с метаданными всех событий
        """
        return self._event_metadata


# Удобная функция для получения экземпляра синглтона
def get_event_system() -> EventSystem:
    """Вернуть экземпляр синглтона EventSystem"""
    return EventSystem()


# Декоратор для подписки на события
def on_event(event_name: str):
    """
    Декоратор для подписки метода на событие
    
    Пример использования:
    
    @on_event("player_moved")
    def handle_player_moved(x, y):
        print(f"Игрок переместился на {x}, {y}")
    """
    def decorator(func):
        get_event_system().subscribe(event_name, func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper.unsubscribe = lambda: get_event_system().unsubscribe(event_name, func)
        return wrapper
    return decorator


# Новые декораторы для работы с событиями
def define_event(name: str, description: str = "", params: Dict[str, str] = None, 
                example: str = "", tags: List[str] = None):
    """
    Декоратор для определения события и его метаданных
    
    Пример использования:
    
    @define_event(
        name="player_moved",
        description="Вызывается когда игрок перемещается в новую позицию",
        params={
            "x": "Новая X-координата игрока",
            "y": "Новая Y-координата игрока"
        },
        example="emit('player_moved', 10, 20)",
        tags=["player", "movement"]
    )
    def player_movement_handler(x, y):
        # Обработка события
        pass
    """
    def decorator(func):
        # Регистрируем метаданные события
        get_event_system().register_event(
            event_name=name,
            description=description,
            params=params,
            example=example,
            tags=tags
        )
        
        # Также подписываем функцию на это событие
        get_event_system().subscribe(name, func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper.unsubscribe = lambda: get_event_system().unsubscribe(name, func)
        wrapper.event_name = name
        return wrapper
    return decorator
