from src.models.Inventory import Inventory
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from src.EventSystem import get_event_system
from src.models.interfaces import Serializable
from src.models.SimpleSkill import SimpleSkill
from src.utils.Logger import Logger

if TYPE_CHECKING:
    from src.GameSystem import GameSystem

class Player(Serializable):
    def __init__(self, game: 'GameSystem', name: str):
        self.name = name
        self.inventory = Inventory()
        self.game_system = game
        self.game = game
        self.event_system = get_event_system()
        
        self.level = 1
        self.gold = 0
        
        self.max_health = 100
        self.max_mana = 100
        self.max_stamina = 100
        self.current_health = 100
        self.current_mana = 100
        self.current_stamina = 100
        
        self.current_exp = 0
        self.exp_for_level_up = 100
        self.skills_points = 0
        
        # Навыки игрока (id -> объект)
        self.skills = {}
        
        # Инициализируем базовые навыки
        self._init_skills()
        
        # Подписываемся на событие повышения уровня навыка
        self.event_system.subscribe("skill_level_up", self.on_skill_level_up)

    def _init_skills(self):
        """
        Инициализирует базовые навыки игрока при создании.
        """
        # Получаем загрузчик навыков
        skills_loader = self.game_system.get_skills_loader()
        if not skills_loader:
            return
            
        # Загружаем все доступные навыки
        for skill_id, skill in skills_loader.get_all_skills().items():
            if skill.is_unlocked(self.level):
                self.skills[skill_id] = skill
    
    def update_skills(self):
        """
        Обновляет список доступных навыков на основе текущего уровня игрока.
        """
        # Получаем загрузчик навыков
        skills_loader = self.game_system.get_skills_loader()
        if not skills_loader:
            return
            
        # Проверяем все навыки
        for skill_id, skill in skills_loader.get_all_skills().items():
            # Если навык разблокирован на текущем уровне, но его нет у игрока
            if skill.is_unlocked(self.level) and skill_id not in self.skills:
                self.skills[skill_id] = skill
                self.event_system.emit("player_unlocked_skill", {"skill": skill.get_skill_info()})
    
    def get_skill(self, skill_id: str) -> Optional[SimpleSkill]:
        """
        Возвращает навык по его идентификатору.
        
        Args:
            skill_id (str): Идентификатор навыка
            
        Returns:
            Optional[SimpleSkill]: Объект навыка или None, если навык не найден
        """
        return self.skills.get(skill_id)
    
    def get_skills(self) -> Dict[str, SimpleSkill]:
        """
        Возвращает словарь всех навыков игрока.
        
        Returns:
            Dict[str, SimpleSkill]: Словарь навыков (id -> объект)
        """
        return self.skills
    
    def get_skills_by_group(self, group_id: str) -> List[SimpleSkill]:
        """
        Возвращает список навыков игрока в указанной группе.
        
        Args:
            group_id (str): Идентификатор группы
            
        Returns:
            List[SimpleSkill]: Список объектов навыков
        """
        result = []
        
        for skill_id, skill in self.skills.items():
            if skill.group_id == group_id:
                result.append(skill)
                
        return result
    
    def add_skill_experience(self, skill_id: str, amount: int) -> bool:
        """
        Добавляет опыт указанному навыку.
        
        Args:
            skill_id (str): Идентификатор навыка
            amount (int): Количество опыта
            
        Returns:
            bool: True, если уровень навыка повысился, иначе False
        """
        skill = self.skills.get(skill_id)
        if not skill:
            return False
            
        # Добавляем опыт и проверяем, повысился ли уровень
        level_up = skill.add_experience(amount)
        
        # Если уровень повысился, отправляем событие
        if level_up:
            self.event_system.emit("player_skill_levelup", {
                "skill": skill.get_skill_info(),
                "new_level": skill.level
            })
            
        return level_up
    
    def can_use_skill(self, skill_id: str) -> bool:
        """
        Проверяет, может ли игрок использовать указанный навык.
        
        Args:
            skill_id (str): Идентификатор навыка
            
        Returns:
            bool: True, если навык можно использовать, иначе False
        """
        skill = self.skills.get(skill_id)
        if not skill:
            return False
            
        return skill.can_use(self)
    
    def use_skill(self, skill_id: str, *args, **kwargs) -> bool:
        """
        Использует навык с указанными параметрами.
        
        Args:
            skill_id (str): Идентификатор навыка
            *args, **kwargs: Дополнительные аргументы для навыка
            
        Returns:
            bool: True, если навык был успешно использован, иначе False
        """
        skill = self.skills.get(skill_id)
        if not skill:
            return False
            
        # Проверяем, можно ли использовать навык
        if not self.can_use_skill(skill_id):
            return False
            
        # Используем навык
        result = skill.use(self, *args, **kwargs)
        
        # Если навык был успешно использован, отправляем событие
        if result:
            self.event_system.emit("player_used_skill", {
                "skill": skill.get_skill_info(),
                "args": args,
                "kwargs": kwargs
            })
            
        return result
    
    def get_passive_bonuses(self) -> Dict[str, Any]:
        """
        Возвращает все пассивные бонусы от навыков.
        
        Returns:
            Dict[str, Any]: Словарь бонусов (имя_бонуса: значение)
        """
        bonuses = {}
        
        # Собираем бонусы со всех навыков
        for skill in self.skills.values():
            skill_bonuses = skill.get_passive_bonuses()
            for bonus_name, bonus_value in skill_bonuses.items():
                # Аддитивные бонусы складываем
                if bonus_name in bonuses:
                    bonuses[bonus_name] += bonus_value
                else:
                    bonuses[bonus_name] = bonus_value
                    
        return bonuses

    def get_item_by_id(self, itemID: str):
        """
        Возвращает предмет itemID из инвентаря.
        Предмет возвращается в виде словаря с данными предмета.
        """
        
        data = self.game.get_item(itemID)
        if not data:
            return None
            
        # Создаем копию словаря, чтобы не модифицировать оригинальные данные
        result = dict(data)
        result["count"] = self.inventory.get_item_count_by_id(itemID)
        result["id"] = itemID  # Добавляем ID предмета в результат
        
        return result

    def add_item_by_id(self, itemID: str, count: int = 1) -> bool:
        """
        Добавляет count предметов itemID в инвентарь.
        Возвращает True, если добавление прошло успешно
        Не добавляет предметы, если их нет в игре
        """
        
        item_data = self.game.get_item(itemID)
        if not item_data:
            return False
        
        self.inventory.add_item_by_id(itemID, count)
        
        # Получаем данные предмета с учетом количества для события
        item_with_count = self.get_item_by_id(itemID)
        
        # Вызываем событие player_took_item один раз для всего количества предметов
        self.event_system.emit("player_took_item", item_with_count)
        
        return True

    def take_item_by_id(self, itemID: str, count: int = 1) -> bool:
        """
        Удаляет count предметов itemID из инвентаря.
        Возвращает True, если удаление прошло успешно, и False, если предметов недостаточно.
        Не удаляет предметы, если их нет в инвентаре
        """
        
        if not self.inventory.get_item_count_by_id(itemID):
            return False
        
        return self.inventory.take_item_by_id(itemID, count)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Сериализует игрока в словарь для сохранения.
        
        Returns:
            Dict[str, Any]: Сериализованный игрок
        """
        # Сериализуем навыки
        serialized_skills = {}
        for skill_id, skill in self.skills.items():
            serialized_skills[skill_id] = skill.to_dict()
        
        return {
            "name": self.name,
            "inventory": self.inventory.to_dict(),
            "level": self.level,
            "gold": self.gold,
            "skills": serialized_skills
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], game: 'GameSystem') -> 'Player':
        """
        Создает игрока из словаря (десериализация).
        
        Args:
            data (Dict[str, Any]): Словарь с данными игрока
            game: Игровая система
            
        Returns:
            Player: Созданный игрок
        """
        player = cls(game, data.get("name", "Игрок"))
        
        # Загружаем базовые атрибуты
        player.level = data.get("level", 1)
        player.gold = data.get("gold", 0)
        
        # Загружаем инвентарь
        if "inventory" in data:
            player.inventory = Inventory.from_dict(data["inventory"])
        
        # Загружаем навыки
        if "skills" in data:
            skills_loader = game.get_skills_loader()
            if skills_loader:
                for skill_id, skill_data in data["skills"].items():
                    # Получаем базовый навык из загрузчика
                    base_skill = skills_loader.get_skill(skill_id)
                    if base_skill:
                        # Создаем копию базового навыка
                        skill = type(base_skill)()
                        # Обновляем его данными из сохранения
                        skill.level = skill_data.get("level", 1)
                        skill.current_experience = skill_data.get("current_experience", 0)
                        # Добавляем в навыки игрока
                        player.skills[skill_id] = skill
        
        return player

    def add_experience(self, amount: int) -> bool:
        """
        Добавляет опыт игроку и повышает уровень, если достигнут необходимый опыт.
        Поддерживает повышение на несколько уровней, если получено достаточно опыта.
        
        Args:
            amount (int): Количество опыта для добавления.
            
        Returns:
            bool: True, если уровень был повышен хотя бы на 1, иначе False.
        """
        # Добавляем опыт
        self.current_exp += amount
        
        # Флаг, показывающий, было ли повышение уровня
        level_up_occurred = False
        
        # Проверяем, достаточно ли опыта для повышения уровня
        # Используем цикл, чтобы обработать случай, когда опыта хватает на несколько уровней
        while self.current_exp >= self.exp_for_level_up:
            # Сохраняем старый уровень
            old_level = self.level
            
            # Повышаем уровень
            self.level += 1
            
            # Вычитаем опыт, потраченный на повышение уровня
            self.current_exp -= self.exp_for_level_up
            
            # Увеличиваем требуемый опыт для следующего уровня
            # Формула: базовый_опыт * (1.5 ^ (уровень - 1))
            base_exp = 100
            self.exp_for_level_up = int(base_exp * (1.5 ** (self.level - 1)))
            
            # Увеличиваем очки навыков
            self.skills_points += 1
            
            # Устанавливаем флаг, что было повышение уровня
            level_up_occurred = True
            
            # Отправляем событие о повышении уровня игрока
            self.event_system.emit("player_level_up", {
                "old_level": old_level,
                "new_level": self.level,
                "stats_increase": {"skills_points": 1}
            })
            
            # Логируем информацию о повышении уровня
            logger = Logger()
            logger.info(f"Игрок повысил уровень с {old_level} до {self.level}!")
            logger.info(f"Текущий опыт: {self.current_exp}, опыт до следующего уровня: {self.exp_for_level_up}")
        
        # Если было хотя бы одно повышение уровня, обновляем навыки
        if level_up_occurred:
            # Обновляем доступные навыки
            self.update_skills()
        
        return level_up_occurred
    
    def on_skill_level_up(self, event_data: Dict[str, Any]) -> None:
        """
        Обработчик события повышения уровня навыка.
        Начисляет опыт игроку в зависимости от нового уровня навыка.
        
        Args:
            event_data (Dict[str, Any]): Данные события
        """
        skill_id = event_data.get("skill_id")
        old_level = event_data.get("old_level")
        new_level = event_data.get("new_level")
        skill_name = event_data.get("skill_name")
        
        if not skill_id or not new_level:
            return
        
        # Рассчитываем количество опыта
        # Формула: 10 + (уровень_игрока * 2)
        exp_gain = (10 + (self.level * 2)) * (new_level - old_level)
        
        # Добавляем опыт игроку
        self.add_experience(exp_gain)
