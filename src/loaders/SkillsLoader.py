"""
Загрузчик навыков и групп навыков.
"""

import os
import importlib
import inspect
import json
from typing import Dict, Any, List, Type, Optional
from src.loaders.SimpleLoader import SimpleLoader
from src.models.SimpleSkill import SimpleSkill
from src.models.skills.SkillGroup import SkillGroup
from src.utils.Logger import Logger

class SkillsLoader(SimpleLoader):
    """
    Класс для загрузки навыков и групп навыков.
    Загружает навыки из Python-файлов и группы из JSON-файлов.
    """
    
    def __init__(self):
        """
        Инициализирует загрузчик навыков.
        """
        self.logger = Logger()
        self.skills = {}  # Словарь навыков: id -> объект навыка
        self.groups = {}  # Словарь групп: id -> объект группы
        
        # Определяем директории для поиска навыков и групп
        self.skills_dir = os.path.join(os.getcwd(), "src", "models", "skills")
        self.groups_data_dir = os.path.join(os.getcwd(), "src", "models", "skills", "data")
        
    def load(self):
        """
        Загружает все навыки и группы навыков.
        """
        self.logger.info("SkillsLoader: Загрузка навыков...")
        
        # Загружаем группы навыков
        self._load_skill_groups()
        
        # Загружаем навыки из Python-файлов
        self._load_skills_from_modules()
        
        # Связываем навыки с группами
        self._link_skills_to_groups()
        
        self.logger.info(f"SkillsLoader: Загружено {len(self.skills)} навыков и {len(self.groups)} групп навыков")
        
    def _load_skill_groups(self):
        """
        Загружает группы навыков из JSON-файлов.
        """
        # Создаем основные группы навыков, если они не определены в файлах
        default_groups = [
            {"id": "combat", "name": "Боевые навыки", "description": "Навыки для сражений и битв", "icon": "⚔️", "order": 1},
            {"id": "magic", "name": "Магические навыки", "description": "Навыки для использования магии", "icon": "🔮", "order": 2},
            {"id": "handcrafting", "name": "Ремесло", "description": "Навыки для создания и сбора предметов", "icon": "🔨", "order": 3},
            {"id": "survival", "name": "Выживание", "description": "Навыки для выживания в дикой природе", "icon": "🏕️", "order": 4},
            {"id": "learning", "name": "Обучаемость", "description": "Навыки для обучения и получения опыта", "icon": "📚", "order": 5},
            {"id": "social", "name": "Социальные навыки", "description": "Навыки для общения с другими игроками", "icon": "👥", "order": 6},
            {"id": "misc", "name": "Разное", "description": "Различные полезные навыки", "icon": "🔄", "order": 7}
        ]
        
        # Добавляем стандартные группы
        for group_data in default_groups:
            group = SkillGroup()
            for key, value in group_data.items():
                setattr(group, key, value)
            self.groups[group.id] = group
            
        # Если директория с данными групп существует, загружаем группы из файлов
        if os.path.exists(self.groups_data_dir):
            for filename in os.listdir(self.groups_data_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(self.groups_data_dir, filename), 'r', encoding='utf-8') as f:
                            group_data = json.load(f)
                            group = SkillGroup.from_dict(group_data)
                            self.groups[group.id] = group
                    except Exception as e:
                        self.logger.error(f"SkillsLoader: Ошибка при загрузке группы навыков из {filename}: {str(e)}")
    
    def _load_skills_from_modules(self):
        """
        Загружает навыки из Python-модулей.
        """
        if not os.path.exists(self.skills_dir):
            self.logger.warning(f"SkillsLoader: Директория {self.skills_dir} не существует")
            return
            
        # Получаем все Python-файлы в директории навыков, исключая __init__.py и SkillGroup.py
        python_files = [f for f in os.listdir(self.skills_dir) 
                      if f.endswith(".py") and f != "__init__.py" and f != "SkillGroup.py"]
        
        for filename in python_files:
            module_name = filename[:-3]  # Удаляем расширение .py
            try:
                # Формируем полное имя модуля
                full_module_name = f"src.models.skills.{module_name}"
                
                # Импортируем модуль
                module = importlib.import_module(full_module_name)
                
                # Ищем в модуле классы, наследующие SimpleSkill
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, SimpleSkill) and obj != SimpleSkill:
                        try:
                            # Создаем экземпляр навыка
                            skill = obj()
                            # Добавляем в словарь
                            self.skills[skill.id] = skill
                        except Exception as e:
                            self.logger.error(f"SkillsLoader: Ошибка при создании навыка {name}: {str(e)}")
                            
            except Exception as e:
                self.logger.error(f"SkillsLoader: Ошибка при загрузке модуля {module_name}: {str(e)}")
    
    def _link_skills_to_groups(self):
        """
        Связывает навыки с соответствующими группами.
        """
        for skill_id, skill in self.skills.items():
            group_id = skill.group_id
            
            # Если группа существует, добавляем навык в группу
            if group_id in self.groups:
                self.groups[group_id].add_skill(skill_id)
            else:
                # Если группа не существует, добавляем в "Разное"
                self.groups["misc"].add_skill(skill_id)
                # Обновляем group_id навыка
                skill.group_id = "misc"
    
    def get_skill(self, skill_id: str) -> Optional[SimpleSkill]:
        """
        Возвращает навык по его идентификатору.
        
        Args:
            skill_id: Идентификатор навыка
            
        Returns:
            Optional[SimpleSkill]: Объект навыка или None, если навык не найден
        """
        return self.skills.get(skill_id)
    
    def get_all_skills(self) -> Dict[str, SimpleSkill]:
        """
        Возвращает словарь всех навыков.
        
        Returns:
            Dict[str, SimpleSkill]: Словарь навыков (id -> объект)
        """
        return self.skills
    
    def get_group(self, group_id: str) -> Optional[SkillGroup]:
        """
        Возвращает группу навыков по ее идентификатору.
        
        Args:
            group_id: Идентификатор группы
            
        Returns:
            Optional[SkillGroup]: Объект группы или None, если группа не найдена
        """
        return self.groups.get(group_id)
    
    def get_all_groups(self) -> Dict[str, SkillGroup]:
        """
        Возвращает словарь всех групп навыков.
        
        Returns:
            Dict[str, SkillGroup]: Словарь групп (id -> объект)
        """
        return self.groups
    
    def get_skills_by_group(self, group_id: str) -> List[SimpleSkill]:
        """
        Возвращает список навыков в указанной группе.
        
        Args:
            group_id: Идентификатор группы
            
        Returns:
            List[SimpleSkill]: Список объектов навыков
        """
        group = self.groups.get(group_id)
        if not group:
            return []
            
        skills = []
        for skill_id in group.get_skills_ids():
            skill = self.skills.get(skill_id)
            if skill:
                skills.append(skill)
                
        return skills
    
    def get_ordered_groups(self) -> List[SkillGroup]:
        """
        Возвращает список групп навыков, отсортированный по порядку отображения.
        
        Returns:
            List[SkillGroup]: Список групп
        """
        return sorted(self.groups.values(), key=lambda g: g.order)
        
    # Реализация интерфейса словаря для удобного доступа к навыкам
    def __getitem__(self, key):
        return self.skills[key]
        
    def __setitem__(self, key, value):
        self.skills[key] = value
        
    def __contains__(self, key):
        return key in self.skills
        
    def __len__(self):
        return len(self.skills)
        
    def keys(self):
        return self.skills.keys()
        
    def values(self):
        return self.skills.values()
        
    def items(self):
        return self.skills.items() 