import os
import json
from src.models.skills.Skill import Skill
from src.utils.Logger import Logger

class SkillSystem:
    def __init__(self):
        self.skills = {}
        self.logger = Logger()
        
    def load_skills(self, skills_directory="resources/skills"):
        """Загружает все навыки из указанной директории"""
        if not os.path.exists(skills_directory):
            self.logger.error(f"Директория навыков не найдена: {skills_directory}")
            return
        
        for filename in os.listdir(skills_directory):
            if filename.endswith(".json"):
                skill_path = os.path.join(skills_directory, filename)
                self.load_skill_from_file(skill_path)
    
    def load_skill_from_file(self, file_path):
        """Загружает один навык из JSON-файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                skill_data = json.load(file)
                
                skill_id = skill_data.get("id")
                if not skill_id:
                    self.logger.error(f"В файле {file_path} отсутствует ID навыка")
                    return
                
                name = skill_data.get("name", skill_id)
                description = skill_data.get("description", "")
                max_level = skill_data.get("max_level", 100)
                base_exp = skill_data.get("base_exp", 100)
                exp_factor = skill_data.get("exp_factor", 1.5)
                
                # Создаем объект навыка с новыми параметрами
                skill = Skill(skill_id, name, description, max_level, base_exp, exp_factor)
                
                # Загружаем информацию о разблокируемых предметах
                for level_data in skill_data.get("levels", []):
                    level = level_data.get("level")
                    unlocks = level_data.get("unlocks", [])
                    
                    if level:
                        # Сохраняем разблокируемые предметы для каждого уровня
                        skill.add_unlocks_by_level(level, unlocks)
                
                self.skills[skill_id] = skill
                self.logger.info(f"Загружен навык: {name}")
                
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке навыка из {file_path}: {str(e)}")
    
    def get_skill(self, skill_id):
        """Возвращает навык по ID"""
        return self.skills.get(skill_id)
    
    def get_all_skills(self):
        """Возвращает список всех навыков"""
        return list(self.skills.values())
    
    def add_experience(self, skill_id, amount):
        """Добавляет опыт к навыку и возвращает информацию о прогрессе"""
        skill = self.get_skill(skill_id)
        if not skill:
            self.logger.warning(f"Попытка добавить опыт к несуществующему навыку: {skill_id}")
            return None
        
        old_level = skill.level
        new_level = skill.add_experience(amount)
        
        # Подготавливаем информацию о прогрессе
        result = {
            "skill_id": skill_id,
            "skill_name": skill.name,
            "old_level": old_level,
            "new_level": new_level,
            "gained_exp": amount,
            "total_exp": skill.experience,
            "level_up": new_level > old_level
        }
        
        # Если был повышен уровень, добавляем информацию о новых разблокированных элементах
        if result["level_up"]:
            result["unlocked_items"] = []
            for level in range(old_level + 1, new_level + 1):
                if level in skill.unlocks_by_level:
                    result["unlocked_items"].extend(skill.unlocks_by_level[level])
        
        return result 