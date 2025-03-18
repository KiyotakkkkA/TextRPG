from src.models.inventory.Inventory import Inventory
from src.models.inventory.InventoryItem import InventoryItem
from src.models.inventory.types.Material import Material
from src.models.inventory.types.Armor import Armor
from src.models.skills.SkillSystem import SkillSystem
from src.utils.Logger import Logger
from colorama import Fore, Style

class Player:
    def __init__(self):
        self.inventory = Inventory()
        self.current_location = None  # Текущая локация игрока
        self.skill_system = SkillSystem()
        self.logger = Logger()
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
        
        # Дополнительные боевые характеристики
        self.dodge_chance = 10  # Шанс уклонения (в процентах)
        self.crit_chance = 5    # Шанс критического удара (в процентах)
        self.crit_damage = 1.5  # Множитель критического урона (х1.5)
        
        # Ресурсы
        self.money = 0
        
        # Система экипировки
        self.equipment = {
            "head": None,       # Шлем/капюшон
            "body": None,       # Броня/одежда
            "legs": None,       # Штаны/поножи
            "feet": None,       # Ботинки/сапоги
            "hands": None,      # Перчатки/рукавицы
            "weapon": None,     # Оружие
            "offhand": None,    # Щит/второе оружие
            "accessory1": None, # Кольцо/амулет/и т.д.
            "accessory2": None  # Еще одно кольцо/амулет/и т.д.
        }
        
        # Дополнительные бонусы от экипировки
        self.equipment_bonuses = {
            "defense": 0,
            "attack": 0,
            "magic": 0,
            "dodge": 0,        # Бонус к шансу уклонения
            "crit_chance": 0,  # Бонус к шансу крита
            "crit_damage": 0   # Бонус к множителю крит. урона
        }
        
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
        """Устанавливает текущую локацию игрока
        
        Args:
            location: Объект локации или строковый ID локации
        """
        # Если передан объект Location, сохраняем его ID
        if hasattr(location, 'id'):
            self.current_location = location.id
        else:
            # Если передана строка ID или что-то другое, сохраняем как есть
            self.current_location = location
        
    def move_to(self, game, location_id):
        """Перемещает игрока в указанную локацию"""
        # Проверяем, что локация существует
        location = game.get_location(location_id)
        if not location:
            print(f"Локация {location_id} не существует!")
            return False
            
        # Проверяем, можно ли попасть в эту локацию из текущей
        current_loc = self.current_location
        if current_loc:
            current_location = game.get_location(current_loc)
            if current_location and location_id not in current_location.connected_locations:
                print(f"Невозможно попасть в локацию {location.name} из текущей локации!")
                return False
        
        # Устанавливаем новую локацию (используем ID)
        self.current_location = location_id
        
        # Отмечаем локацию как посещенную
        game.mark_location_as_visited(location_id)
        
        # Обновляем пути для отслеживаемых целей
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
        current_location = game.get_location(self.current_location)
        if not current_location:
            print("Ошибка: текущая локация не найдена!")
            return False
            
        if resource_id not in current_location.resources or current_location.resources[resource_id] <= 0:
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
        collected = current_location.collect_resource(resource_id, count)
        if collected > 0:
            # Добавляем ресурс в инвентарь
            if not self.add_item_by_id(game, resource_id, collected):
                print(f"ОШИБКА: Не удалось добавить ресурс {resource_id} в инвентарь!")
                # Возвращаем ресурс обратно в локацию
                current_location.resources[resource_id] += collected
                return False
            
            # Здесь item_data точно не None, так как мы проверили это выше
            print(f"Вы собрали {collected} единиц ресурса {item_data.get('name', resource_id)}")
            
            # Добавляем ресурс в глоссарий
            game.add_resource_to_glossary(resource_id, self.current_location)
            
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

    def look_around(self, game):
        """Осматривает текущую локацию"""
        if not self.current_location:
            print("Вы не находитесь ни в одной локации!")
            return
        
        current_location = game.get_location(self.current_location)
        if current_location:
            print(current_location.describe())
        else:
            print(f"Ошибка: локация с ID {self.current_location} не найдена")

    def get_skills(self):
        """Возвращает все навыки игрока"""
        return self.skill_system.get_all_skills()
        
    def get_skill_bonus(self, bonus_name):
        """Возвращает суммарное значение бонуса по всем навыкам
        
        Args:
            bonus_name (str): Название бонуса
            
        Returns:
            float: Суммарное значение бонуса
        """
        total_bonus = 0
        for skill in self.get_skills():
            total_bonus += skill.get_bonus_value(bonus_name)
        return total_bonus
        
    def get_all_skill_bonuses(self):
        """Возвращает словарь со всеми активными бонусами от навыков
        
        Returns:
            dict: Словарь {bonus_name: total_value}
        """
        all_bonuses = {}
        
        # Собираем все бонусы от навыков
        for skill in self.get_skills():
            skill_bonuses = skill.get_all_bonuses()
            for bonus_name, value in skill_bonuses.items():
                if bonus_name in all_bonuses:
                    all_bonuses[bonus_name] += value
                else:
                    all_bonuses[bonus_name] = value
                    
        return all_bonuses
        
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
        if amount > 0:
            self.money += amount
            return True
        return False
        
    def spend_money(self, amount):
        """Тратит деньги игрока, если их достаточно"""
        if amount > 0 and self.money >= amount:
            self.money -= amount
            return True
        return False
    
    # Методы для управления экипировкой
    def equip_item(self, item):
        """Надевает предмет на персонажа
        
        Args:
            item: Объект надеваемого предмета
        
        Returns:
            bool: True если предмет был надет, False если нет
            str: Сообщение об успехе или ошибке
        """
        # Проверяем, что предмет существует
        if not item:
            return False, "Предмет не найден"
        
        # Проверяем, что предмет можно экипировать
        if not hasattr(item, 'get_slot'):
            return False, "Этот предмет нельзя экипировать"
        
        slot = item.get_slot()
        
        # Проверяем, есть ли такой слот
        if slot not in self.equipment:
            return False, f"Слот {slot} не существует"
        
        # Если слот уже занят, возвращаем старый предмет в инвентарь
        if self.equipment[slot]:
            old_item = self.equipment[slot]
            self.inventory.add_item(old_item)
            self.logger.info(f"Снят предмет {old_item.name} из слота {slot}")
        
        # Удаляем предмет из инвентаря
        self.inventory.remove_item(item)
        
        # Надеваем новый предмет
        self.equipment[slot] = item
        self.logger.info(f"Экипирован предмет {item.name} в слот {slot}")
        
        # Обновляем бонусы от экипировки
        self._update_equipment_bonuses()
        
        return True, f"Предмет {item.name} успешно экипирован"
    
    def unequip_item(self, slot):
        """Снимает предмет из указанного слота
        
        Args:
            slot: Слот, из которого нужно снять предмет
        
        Returns:
            bool: True если предмет был снят, False если нет
            str: Сообщение об успехе или ошибке
        """
        # Проверяем, есть ли такой слот
        if slot not in self.equipment:
            return False, f"Слот {slot} не существует"
        
        # Проверяем, есть ли предмет в слоте
        if not self.equipment[slot]:
            return False, f"Слот {slot} пуст"
        
        # Возвращаем предмет в инвентарь
        item = self.equipment[slot]
        self.inventory.add_item(item)
        
        # Очищаем слот
        self.equipment[slot] = None
        self.logger.info(f"Снят предмет {item.name} из слота {slot}")
        
        # Обновляем бонусы от экипировки
        self._update_equipment_bonuses()
        
        return True, f"Предмет {item.name} снят и возвращен в инвентарь"
    
    def _update_equipment_bonuses(self):
        """Обновляет бонусы от экипировки"""
        # Сбрасываем бонусы
        self.equipment_bonuses = {
            "defense": 0,
            "attack": 0,
            "magic": 0,
            "dodge": 0,
            "crit_chance": 0,
            "crit_damage": 0
        }
        
        # Суммируем бонусы от всех предметов
        for slot, item in self.equipment.items():
            if not item:
                continue
                
            # Для брони считаем защиту
            if hasattr(item, 'get_defense'):
                self.equipment_bonuses["defense"] += item.get_defense()
            
            # Проверяем другие бонусы от предмета
            if hasattr(item, 'get_bonuses'):
                bonuses = item.get_bonuses()
                for bonus_type, value in bonuses.items():
                    if bonus_type in self.equipment_bonuses:
                        self.equipment_bonuses[bonus_type] += value
            
            # Тут можно добавить другие характеристики по мере добавления других типов предметов
        
        self.logger.debug(f"Обновлены бонусы от экипировки: {self.equipment_bonuses}")
    
    def get_equipped_items(self):
        """Возвращает словарь с экипированными предметами"""
        return self.equipment
    
    def get_equipment_bonuses(self):
        """Возвращает бонусы от экипировки"""
        return self.equipment_bonuses
    
    def take_damage(self, damage):
        """Игрок получает урон с учетом защиты от брони
        
        Args:
            damage: Количество урона
            
        Returns:
            bool: True, если игрок умер после получения урона
            bool: Было ли уклонение
        """
        # Проверяем шанс уклонения
        import random
        total_dodge = self.dodge_chance + self.equipment_bonuses.get("dodge", 0)
        is_dodged = random.randint(1, 100) <= total_dodge
        
        if is_dodged:
            self.logger.debug(f"Игрок {self.name} уклонился от атаки")
            return False, True
        
        # Учитываем защиту от брони
        actual_damage = max(1, damage - self.equipment_bonuses.get("defense", 0))
        self.health = max(0, self.health - actual_damage)
        self.logger.debug(f"Игрок {self.name} получил {actual_damage} урона (исходный урон {damage}), осталось {self.health} HP")
        return self.health <= 0, False
    
    def is_alive(self):
        """Проверяет, жив ли игрок"""
        return self.health > 0
    
    def calculate_damage(self):
        """Рассчитывает базовый урон атаки игрока с учетом экипировки и навыков
        
        Returns:
            int: Количество урона
            bool: Критический удар или нет
        """
        # Базовый урон от уровня игрока
        base_damage = 5 + (self.level - 1) * 2
        
        # Добавляем бонус от экипировки
        equipment_bonus = self.equipment_bonuses.get("attack", 0)
        
        # Добавляем бонусы от навыков
        skill_bonuses = self.get_all_skill_bonuses()
        skill_attack_bonus = skill_bonuses.get("attack", 0)
        
        # Учитываем специальные бонусы для разных типов оружия
        weapon_type_bonus = 0
        # Если есть оружие, определяем его тип
        weapon = self.equipment.get("weapon")
        if weapon:
            weapon_type = weapon.get_type()
            weapon_type_bonus = skill_bonuses.get(f"{weapon_type}_damage", 0)
        
        total_damage = base_damage + equipment_bonus + skill_attack_bonus + weapon_type_bonus
        
        # Проверяем, будет ли критический удар
        import random
        base_crit_chance = self.crit_chance + self.equipment_bonuses.get("crit_chance", 0)
        skill_crit_bonus = skill_bonuses.get("critical_chance", 0)
        total_crit_chance = base_crit_chance + skill_crit_bonus
        
        is_critical = random.randint(1, 100) <= total_crit_chance
        
        # Если критический удар, увеличиваем урон
        if is_critical:
            base_crit_multiplier = self.crit_damage + self.equipment_bonuses.get("crit_damage", 0)
            skill_crit_damage_bonus = skill_bonuses.get("critical_damage", 0)
            total_crit_multiplier = base_crit_multiplier + skill_crit_damage_bonus
            
            total_damage = total_damage * total_crit_multiplier
        
        # Добавляем рандомизацию +/- 20%
        variation = random.uniform(0.8, 1.2)
        
        return max(1, int(total_damage * variation)), is_critical
    
    def attack(self, target):
        """Игрок атакует цель
        
        Args:
            target: Цель атаки (обычно монстр)
            
        Returns:
            int: Количество нанесенного урона
            bool: Критический удар или нет
            bool: Было ли уклонение
        """
        # Проверяем, уклонилась ли цель
        import random
        dodge_chance = 5  # Базовый шанс уклонения для монстров
        if hasattr(target, 'dodge_chance'):
            dodge_chance = target.dodge_chance
            
        is_dodged = random.randint(1, 100) <= dodge_chance
        
        if is_dodged:
            self.logger.debug(f"Монстр {target.name} уклонился от атаки игрока {self.name}")
            return 0, False, True
        
        # Расчет урона
        damage, is_critical = self.calculate_damage()
        target.take_damage(damage)
        
        if is_critical:
            self.logger.debug(f"Игрок {self.name} нанес КРИТИЧЕСКИЙ удар {target.name} на {damage} урона")
        else:
            self.logger.debug(f"Игрок {self.name} атаковал {target.name} на {damage} урона")
            
        return damage, is_critical, False
    
    def heal(self, amount):
        """Восстанавливает здоровье игрока
        
        Args:
            amount: Количество восстанавливаемого здоровья
        """
        self.health = min(self.max_health, self.health + amount)
        self.logger.debug(f"Игрок {self.name} восстановил {amount} HP, теперь {self.health} HP")
        
    def show_skills_info(self):
        """Отображает информацию о всех навыках игрока"""
        skills = self.get_skills()
        
        if not skills:
            print("У вас пока нет никаких навыков.")
            return
            
        print(f"\n=== НАВЫКИ ({len(skills)}) ===")
        
        # Сортируем навыки по уровню (от высокого к низкому)
        sorted_skills = sorted(skills, key=lambda x: x.level, reverse=True)
        
        for skill in sorted_skills:
            print("\n" + skill.get_description_text())
            
    def show_skill_info(self, skill_id):
        """Отображает подробную информацию о конкретном навыке"""
        skill = self.skill_system.get_skill(skill_id)
        
        if not skill:
            print(f"Навык '{skill_id}' не найден.")
            return
            
        print("\n" + skill.get_description_text())
            
    def get_skill_info(self, skill_id):
        """Возвращает словарь с информацией о навыке
        
        Args:
            skill_id (str): Идентификатор навыка
            
        Returns:
            dict or None: Словарь с информацией о навыке или None, если навык не найден
        """
        skill = self.skill_system.get_skill(skill_id)
        
        if not skill:
            return None
            
        return skill.get_detail_info()
        
