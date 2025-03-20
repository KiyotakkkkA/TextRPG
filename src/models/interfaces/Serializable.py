"""
Интерфейс Serializable для поддержки сериализации объектов игры.
Этот интерфейс обеспечивает базовую функциональность для сохранения и загрузки объектов
с помощью модуля pickle или других инструментов сериализации.
"""

from abc import ABC, abstractmethod
import pickle
from typing import Any, Dict, Optional

class Serializable(ABC):
    """
    Абстрактный класс для объектов, которые можно сериализовать.
    Все игровые объекты, которые нужно сохранять, должны наследоваться от этого класса.
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует объект в словарь для сериализации.
        
        Returns:
            Dict[str, Any]: Словарь с данными объекта
        """
        # Базовая реализация возвращает словарь из всех атрибутов объекта,
        # которые не начинаются с '_'
        return {
            key: value for key, value in self.__dict__.items() 
            if not key.startswith('_') and not callable(value)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Serializable':
        """
        Создает объект из словаря с данными.
        
        Args:
            data (Dict[str, Any]): Словарь с данными объекта
            
        Returns:
            Serializable: Новый экземпляр класса
        """
        instance = cls.__new__(cls)
        for key, value in data.items():
            setattr(instance, key, value)
        return instance
    
    def serialize(self, filename: Optional[str] = None) -> Optional[bytes]:
        """
        Сериализует объект в байты или в файл, если указано имя файла.
        
        Args:
            filename (Optional[str]): Имя файла для сохранения объекта
            
        Returns:
            Optional[bytes]: Сериализованный объект в виде байтов, если filename не указан
        """
        if filename:
            with open(filename, 'wb') as f:
                pickle.dump(self, f)
            return None
        else:
            return pickle.dumps(self)
    
    @classmethod
    def deserialize(cls, data: bytes = None, filename: str = None) -> 'Serializable':
        """
        Десериализует объект из байтов или из файла.
        
        Args:
            data (bytes): Байты сериализованного объекта
            filename (str): Имя файла с сериализованным объектом
            
        Returns:
            Serializable: Десериализованный объект
            
        Raises:
            ValueError: Если не указаны ни data, ни filename
        """
        if data is not None:
            return pickle.loads(data)
        elif filename is not None:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        else:
            raise ValueError("Необходимо указать либо data, либо filename для десериализации")
    
    def __getstate__(self) -> Dict[str, Any]:
        """
        Метод для настройки сериализации pickle.
        Возвращает словарь с состоянием объекта для сериализации.
        
        Returns:
            Dict[str, Any]: Состояние объекта
        """
        return self.to_dict()
    
    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Метод для настройки десериализации pickle.
        Восстанавливает состояние объекта из словаря.
        
        Args:
            state (Dict[str, Any]): Состояние объекта
        """
        for key, value in state.items():
            setattr(self, key, value) 