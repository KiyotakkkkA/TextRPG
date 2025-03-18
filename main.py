from src.GameSystem import GameSystem

def main():
    game = GameSystem()
    game.preload()
    
    game.player.add_item_by_id("test_food", 10)
    game.player.take_item_by_id("test_food", 5)
    print(game.player.get_item_by_id("test_food"))

if __name__ == "__main__":
    main()
