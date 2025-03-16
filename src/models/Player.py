from src.models.inventory.Inventory import Inventory
from src.models.inventory.InventoryItem import InventoryItem
from src.models.inventory.types.Material import Material
from src.models.skills.SkillSystem import SkillSystem
from colorama import Fore, Style

class Player:
    def __init__(self):
        self.inventory = Inventory()
        self.current_location = None  # Текущая локация игрока
        self.skill_system = SkillSystem()
        # Путь к навыкам должен быть обновлен
        self.skill_system.load_skills("resources/skills")
        
        # Добавляем основные атрибуты персонажа
        self.name = "Герой"  # Имя персонажа по умолчанию
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100
        
        # Боевые характеристики
        self.health = 100
        self.max_health = 100
        self.mana = 50
        self.max_mana = 50
        self.stamina = 100
        self.max_stamina = 100
        
        # Ресурсы
        self.money = 0

    def add_item(self, item: InventoryItem):
        self.inventory.add_item(item)

    def remove_item(self, item: InventoryItem):
        self.inventory.remove_item(item)
        
    def print_inventory(self):
        self.inventory.print_inventory()

    def add_item_by_id(self, game, item_id, count=1):
        """Добавляет предмет в инвентарь игрока по ID из атласа"""
        # Проверяем регистр
        if item_id and item_id.lower() in game.ATLAS["ITEMS"]:
            item_id = item_id.lower()
        
        item = game.create_inventory_item(item_id, count)
        if item:
            self.add_item(item)
            
            # После добавления предмета обновляем прогресс квестов
            # которые могут требовать этот предмет
            game.update_quest_progress()
            
            return True
        else:
            print(f"Не удалось создать предмет с ID: {item_id}")
        return False
        
    def set_location(self, location):
        """Устанавливает текущую локацию игрока"""
        self.current_location = location
        
    def move_to(self, game, location_id):
        """Перемещает игрока в указанную локацию"""
        # Проверяем, что локация существует
        location = game.get_location(location_id)
        if not location:
            print(f"Локация {location_id} не существует!")
            return False
        
        # Проверяем, что локация доступна из текущей
        if self.current_location and location_id not in self.current_location.connected_locations:
            print(f"Невозможно попасть в локацию {location.name} из текущего места!")
            return False
        
        # Перемещаемся в новую локацию
        self.current_location = location
        
        # Обновляем пути к отслеживаемой цели и целям квеста
        if hasattr(game, 'update_tracked_path'):
            game.update_tracked_path()
        
        # Обновляем прогресс всех активных квестов
        game.update_quest_progress()
        
        print(f"Вы переместились в локацию: {location.name}")
        print(location.describe())
        return True

    def collect_resource(self, game, resource_id, count=1):
        """Собирает ресурс из текущей локации и прокачивает соответствующие навыки"""
        if not self.current_location:
            print("Вы не находитесь ни в одной локации!")
            return False
        
        # Проверяем наличие ресурса в локации
        if resource_id not in self.current_location.resources or self.current_location.resources[resource_id] <= 0:
            print(f"Ресурс {resource_id} отсутствует в текущей локации!")
            return False
        
        # Проверяем, доступен ли ресурс для сбора и существует ли он в игре
        item_data = game.get_item(resource_id)
        if not item_data:
            print(f"ОШИБКА: Ресурс {resource_id} не определен в игре!")
            return False
        
        if item_data.get("collectable", True):
            # Проверяем требования к навыкам
            required_skills = item_data.get("required_skills", {})
            can_collect = True
            
            for skill_id, min_level in required_skills.items():
                skill = self.skill_system.get_skill(skill_id)
                if not skill or skill.level < min_level:
                    print(f"Для сбора ресурса {item_data.get('name', resource_id)} необходим навык {skill_id} уровня {min_level}!")
                    can_collect = False
                    break
            
            if not can_collect:
                return False
        
        # Собираем ресурс
        collected = self.current_location.collect_resource(resource_id, count)
        if collected > 0:
            # Добавляем ресурс в инвентарь
            if not self.add_item_by_id(game, resource_id, collected):
                print(f"ОШИБКА: Не удалось добавить ресурс {resource_id} в инвентарь!")
                # Возвращаем ресурс обратно в локацию
                self.current_location.resources[resource_id] += collected
                return False
            
            # Здесь item_data точно не None, так как мы проверили это выше
            print(f"Вы собрали {collected} единиц ресурса {item_data.get('name', resource_id)}")
            
            # Добавляем ресурс в глоссарий
            game.add_resource_to_glossary(resource_id, self.current_location.id)
            
            # Прокачиваем соответствующие навыки
            if item_data:
                skill_exp = item_data.get("skill_exp", {})
                for skill_id, exp_amount in skill_exp.items():
                    skill = self.skill_system.get_skill(skill_id)
                    if skill:
                        total_exp = exp_amount * collected
                        old_level = skill.level
                        level_up = self.skill_system.add_experience(skill_id, total_exp)
                        
                        # Визуальное отображение получения опыта
                        print(f"+{total_exp} опыта навыка {skill.name}")
                        
                        # Если произошло повышение уровня
                        if level_up:
                            print(f"\n{Fore.YELLOW}🔼 Уровень навыка {skill.name} повышен до {skill.level}!{Style.RESET_ALL}")
                            
                            # Показываем новые разблокированные предметы
                            for lvl in range(old_level + 1, skill.level + 1):
                                unlocked_items = skill.get_unlocked_items_at_level(lvl)
                                if unlocked_items:
                                    print(f"{Fore.GREEN}Разблокированы новые предметы на уровне {lvl}:{Style.RESET_ALL}")
                                    for item_id in unlocked_items:
                                        item_info = game.get_item(item_id)
                                        if item_info and "name" in item_info:
                                            print(f"- {item_info['name']}")
            
            return True
        
        return False

    def look_around(self):
        """Осматривает текущую локацию"""
        if not self.current_location:
            print("Вы не находитесь ни в одной локации!")
            return
        
        print(self.current_location.describe())

    def get_skills(self):
        """Возвращает все навыки игрока"""
        return self.skill_system.get_all_skills()
        
    def can_collect_resource(self, resource_id, item_data):
        """Проверяет, имеет ли игрок необходимый уровень навыка для сбора ресурса"""
        if not item_data:
            return False
        
        required_skills = item_data.get("required_skills", {})
        
        for skill_id, min_level in required_skills.items():
            skill = self.skill_system.get_skill(skill_id)
            if not skill or skill.level < min_level:
                return False
            
        return True
        
    def get_exp_percentage(self):
        """Возвращает процент опыта до следующего уровня в виде числа от 0 до 100"""
        if self.exp_to_next_level == 0:
            return 100
        
        return int((self.experience / self.exp_to_next_level) * 100)

    def get_health_percentage(self):
        """Возвращает процент здоровья персонажа"""
        if self.max_health == 0:
            return 0
        
        return int((self.health / self.max_health) * 100)

    def get_mana_percentage(self):
        """Возвращает процент маны персонажа"""
        if self.max_mana == 0:
            return 0
        
        return int((self.mana / self.max_mana) * 100)

    def get_stamina_percentage(self):
        """Возвращает процент выносливости персонажа"""
        if self.max_stamina == 0:
            return 0
        
        return int((self.stamina / self.max_stamina) * 100)
        
    def add_experience(self, amount):
        """Добавляет опыт персонажу и повышает уровень, если достаточно опыта"""
        if amount <= 0:
            return False
        
        self.experience += amount
        
        # Проверяем, достаточно ли опыта для повышения уровня
        level_up = False
        while self.experience >= self.exp_to_next_level:
            self.level_up()
            level_up = True
        
        return level_up

    def level_up(self):
        """Повышает уровень персонажа и обновляет опыт для следующего уровня"""
        self.level += 1
        self.experience -= self.exp_to_next_level
        
        # Увеличиваем количество опыта, необходимого для следующего уровня
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        
        # Увеличиваем характеристики персонажа
        self.max_health += 10
        self.health = self.max_health
        
        self.max_mana += 5
        self.mana = self.max_mana
        
        self.max_stamina += 5
        self.stamina = self.max_stamina
        
        return True

    def add_money(self, amount):
        """Добавляет деньги игроку"""
        if amount <= 0:
            return False
            
        self.money += amount
        return True
        
    def spend_money(self, amount):
        """Тратит деньги игрока
        
        Args:
            amount: Сумма для списания
            
        Returns:
            bool: True если игрок может позволить себе эту трату, False иначе
        """
        if amount <= 0:
            return True
            
        if self.money < amount:
            return False
            
        self.money -= amount
        return True
        
