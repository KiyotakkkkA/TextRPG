import os
import json
import random
from src.models.monsters.Monster import Monster
from src.utils.Logger import Logger

class MonsterManager:
    """Класс для управления монстрами в игре"""
    
    def __init__(self):
        self.monsters = {}  # Словарь шаблонов монстров {monster_id: monster_template}
        self.active_monsters = {}  # Словарь активных монстров по локациям {location_id: {monster_id: count}}
        self.logger = Logger()
    
    def load_monsters(self, monsters_directory="resources/monsters"):
        """Загружает всех монстров из указанной директории и её подпапок"""
        if not os.path.exists(monsters_directory):
            self.logger.error(f"Директория монстров не найдена: {monsters_directory}")
            return
        
        # Счетчики для логирования
        total_files_processed = 0
        total_monsters_loaded = 0
        
        # Рекурсивно проходим по всем файлам в директории и её подпапках
        for root, dirs, files in os.walk(monsters_directory):
            for file in files:
                # Проверяем, что это JSON файл
                if not file.endswith('.json'):
                    continue
                
                file_path = os.path.join(root, file)
                self.logger.info(f"Обрабатываем файл монстров: {file_path}")
                
                try:
                    # Загружаем монстров из файла
                    monsters_in_file = self.load_monster_from_file(file_path)
                    
                    # Обновляем счетчики
                    total_files_processed += 1
                    total_monsters_loaded += monsters_in_file
                    
                except Exception as e:
                    self.logger.error(f"Ошибка при загрузке монстров из файла {file_path}: {str(e)}")
        
        # Суммарная статистика
        self.logger.info(f"Всего обработано файлов монстров: {total_files_processed}")
        self.logger.info(f"Всего загружено монстров: {total_monsters_loaded}")
        
    def load_monster_from_file(self, file_path):
        """Загружает монстра из JSON-файла
        
        Returns:
            int: Количество загруженных монстров из файла
        """
        monsters_loaded = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                monster_data = json.load(file)
                
                for monster_id, monster_info in monster_data.items():
                    name = monster_info.get("name", monster_id)
                    description = monster_info.get("description", "")
                    level = monster_info.get("level", 1)
                    health = monster_info.get("health", 10)
                    damage = monster_info.get("damage", 2)
                    
                    monster = Monster(monster_id, name, description, level, health, damage)
                    self.monsters[monster_id] = monster
                    self.logger.info(f"Загружен монстр: {name} (уровень: {level})")
                    monsters_loaded += 1
                    
            return monsters_loaded
                    
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке монстра из {file_path}: {str(e)}")
            return 0
    
    def init_monsters_for_location(self, location_id, monster_data):
        """Инициализирует монстров для указанной локации
        
        Args:
            location_id: ID локации
            monster_data: Словарь {monster_id: {max_count: X, respawn_time: Y}}
        """
        if location_id not in self.active_monsters:
            self.active_monsters[location_id] = {}
            
        for monster_id, monster_info in monster_data.items():
            max_count = monster_info.get("max_count", 5)
            initial_count = random.randint(1, max_count)
            
            if monster_id in self.monsters:
                self.active_monsters[location_id][monster_id] = initial_count
                self.logger.debug(f"Инициализировано {initial_count} монстров типа {monster_id} в локации {location_id}")
            else:
                self.logger.warning(f"Монстр {monster_id} не найден при инициализации локации {location_id}")
    
    def get_monster(self, monster_id):
        """Возвращает шаблон монстра по ID"""
        return self.monsters.get(monster_id)
    
    def get_monsters_at_location(self, location_id):
        """Возвращает словарь монстров в указанной локации {monster_id: count}"""
        return self.active_monsters.get(location_id, {})
    
    def reduce_monster_count(self, location_id, monster_id, count=1):
        """Уменьшает количество монстров указанного типа в локации
        
        Returns:
            bool: True, если операция выполнена успешно
        """
        if location_id in self.active_monsters and monster_id in self.active_monsters[location_id]:
            current_count = self.active_monsters[location_id][monster_id]
            if current_count >= count:
                self.active_monsters[location_id][monster_id] -= count
                self.logger.debug(f"Уменьшено количество монстров {monster_id} в локации {location_id} на {count}")
                return True
        return False
    
    def update_monsters(self, time_passed):
        """Обновляет состояние монстров (восстановление количества со временем)
        
        Args:
            time_passed: Прошедшее время в секундах
        """
        # В будущем здесь может быть логика восстановления количества монстров
        pass 