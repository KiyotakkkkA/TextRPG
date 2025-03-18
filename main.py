import os
import logging
from colorama import init, Fore, Style
from src.models.inventory.types.Material import Material
from src.Game import Game
from src.ui.GameMenu import GameMenu

def main():
    # Инициализация colorama
    init()
    
    # Создание и инициализация игры
    game = Game()
    # Явно указываем, что это новая игра
    game.is_new_game = True
    game.preload()
    
    # Создание игрового меню
    menu = GameMenu(game)
    
    # Запускаем главное меню
    menu.main_menu()

if __name__ == "__main__":
    # Настраиваем логирование, если нужно
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        filename=os.path.join(log_dir, "logs.log"),
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Запускаем игру
    main()

