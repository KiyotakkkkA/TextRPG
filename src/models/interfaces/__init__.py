"""
Пакет interfaces содержит абстрактные классы и интерфейсы
для определения общего поведения различных игровых сущностей.
"""

from src.models.interfaces.Require import Require
from src.models.interfaces.Serializable import Serializable

__all__ = ['Require', 'Serializable'] 