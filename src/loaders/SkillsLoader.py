

from models.skills import Skill


def load_skill(self, skill_data):
    """Загружает навык из JSON-данных"""
    skill_id = skill_data.get("id")
    skill_name = skill_data.get("name", skill_id.capitalize())
    skill_desc = skill_data.get("description", "")
    max_level = skill_data.get("max_level", 100)
    base_exp = skill_data.get("base_exp", 100)
    exp_factor = skill_data.get("exp_factor", 1.5)
    
    # Создаем объект навыка
    skill = Skill(skill_id, skill_name, skill_desc, max_level, base_exp, exp_factor)
    
    # Добавляем информацию о разблокируемых предметах
    if "levels" in skill_data:
        for level_info in skill_data["levels"]:
            level = level_info.get("level", 1)
            unlocks = level_info.get("unlocks", [])
            skill.unlocks_by_level[level] = unlocks
    
    return skill