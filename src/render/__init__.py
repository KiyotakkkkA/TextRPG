"""
Модуль рендеринга для консольной RPG игры.
Предоставляет инструменты для создания и отображения интерфейса пользователя.
"""

from src.render.core import (
    Engine, Screen, UIElement, Renderer, 
    ConsoleHelper, InputHandler, Keys, Color
)
from src.render.ui import (
    Panel, Label, Button, MenuItem, Menu, 
    ProgressBar, TextBox, DialogBox
)
from src.render.screens import (
    MainMenuScreen, GameScreen
)

# Инициализация модуля
__all__ = [
    # Ядро
    'Engine', 'Screen', 'UIElement', 'Renderer', 
    'ConsoleHelper', 'InputHandler', 'Keys', 'Color',
    
    # UI компоненты
    'Panel', 'Label', 'Button', 'MenuItem', 'Menu', 
    'ProgressBar', 'TextBox', 'DialogBox',
    
    # Экраны
    'MainMenuScreen', 'GameScreen'
] 