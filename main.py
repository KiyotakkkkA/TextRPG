#!/usr/bin/env python
"""
Основной файл запуска игры TextRPG.
"""

import os
import sys
import time
from pathlib import Path

# Добавляем родительскую директорию в пути поиска модулей
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Импорты игровых модулей
from src.render.core import Engine
from src.render.views.MainMenu import MainMenuScreen, UpdateScreen
from src.render.views.Game import GameScreen
from src.GameSystem import GameSystem
from src.utils.PropertiesLoader import get_version_properties

def main():
    """
    Точка входа в игру.
    Инициализирует игровую систему и движок рендеринга, запускает игру.
    """
    # Загружаем информацию о версии
    version_props = get_version_properties()
    game_version = version_props.get("game.version", "0.1.0")
    game_stage = version_props.get("game.stage", "Alpha")
    engine_version = version_props.get("engine.version", "1.0.0")
    engine_name = version_props.get("engine.name", "TextRPG Engine")
    
    # Выводим информацию о запуске
    print(f"\nЗапуск TextRPG Adventure v{game_version} {game_stage}")
    print(f"Powered by {engine_name} v{engine_version}")
    print("=" * 60)
    
    # Инициализация игровой системы
    game_system = GameSystem()
    game_system.preload()
    
    # Устанавливаем начальную локацию для отладки
    try:
        initial_location = game_system.get_location("forest")
        if initial_location:
            game_system.change_location("forest")
            print(f"Установлена начальная локация: {initial_location.name}")
        else:
            print("ВНИМАНИЕ: Начальная локация 'forest' не найдена!")
    except Exception as e:
        print(f"Ошибка при установке начальной локации: {str(e)}")
    
    # Инициализация движка рендеринга
    engine = Engine()
    
    # Настраиваем параметры для уменьшения мерцания
    engine.fps_limit = 10  # Уменьшаем частоту обновления экрана
    engine.update_rate = 20  # Уменьшаем частоту обновления логики
    engine.auto_render = False  # Отключаем автоматический рендеринг
    engine.render_on_update = False  # Рендерим только при необходимости
    
    # Модификация обработчиков меню, чтобы они работали с игровой системой
    def on_new_game():
        """
        Запуск новой игры.
        """
        print("Запуск новой игры...")
        # Проверяем и получаем начальную локацию
        try:
            # Выведем все доступные локации
            locations = game_system.get_all_locations()
            print(f"Доступные локации: {', '.join(locations.keys()) if locations else 'нет'}")
            
            initial_location = game_system.get_location("forest")
            if initial_location is None:
                print("Начальная локация 'forest' не найдена, проверьте файлы локаций!")
                return  # Прерываем запуск игры, если нет локации
            
            # Переходим в начальную локацию
            game_system.change_location("forest")
            
            # Переходим на игровой экран
            engine.set_current_screen("game")
            print(f"Вы начинаете в локации: {initial_location.name}")
        except Exception as e:
            print(f"Ошибка при запуске новой игры: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def on_load_game():
        """
        Загрузка сохраненной игры.
        """
        print("Загрузка игры...")
        # Здесь будет код загрузки
        engine.set_current_screen("game")
        
    # Обновляем информацию о навыках игрока
        
    game_system.player.update_skills()
        
    # Создание и регистрация экранов
    main_menu = MainMenuScreen(engine, "TextRPG Adventure")
    game_screen = GameScreen(engine)
    update_screen = UpdateScreen(engine)
    
    # Устанавливаем ссылку на игровую систему в игровой экран
    game_screen.set_game_system(game_system)
    
    # Назначаем новые обработчики
    main_menu.on_new_game = on_new_game
    main_menu.on_load_game = on_load_game
    
    # Регистрация экранов
    engine.register_screen("main_menu", main_menu)
    engine.register_screen("game", game_screen)
    engine.register_screen("update", update_screen)
    
    # Устанавливаем начальный экран
    engine.set_current_screen("main_menu")
    
    # Запуск движка
    try:
        engine.start()
    except KeyboardInterrupt:
        print("\nПрерывание работы пользователем.")
    except Exception as e:
        print(f"\nОшибка: {str(e)}")
    finally:
        print("\nЗавершение работы игры.")

if __name__ == "__main__":
    main()
