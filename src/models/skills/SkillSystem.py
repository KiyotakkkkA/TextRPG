import os
import json
from src.models.skills.Skill import Skill
from src.utils.Logger import Logger

class SkillSystem:
    def __init__(self):
        self.skills = {}
        self.logger = Logger()
        
    def load_skills(self, skills_directory="resources/skills"):
        """Загружает все навыки из указанной директории и её поддиректорий"""
        if not os.path.exists(skills_directory):
            self.logger.error(f"Директория навыков не найдена: {skills_directory}")
            return
        
        # Счетчики для логирования
        total_files_processed = 0
        total_skills_loaded = 0
        
        # Рекурсивно проходим по всем файлам в директории и её поддиректориях
        for root, dirs, files in os.walk(skills_directory):
            for file in files:
                # Проверяем, что это JSON файл
                if not file.endswith('.json'):
                    continue
                
                file_path = os.path.join(root, file)
                self.logger.info(f"Обрабатываем файл навыка: {file_path}")
                
                # Загружаем навык из файла
                skill_loaded = self.load_skill_from_file(file_path)
                
                # Обновляем счетчики
                total_files_processed += 1
                if skill_loaded:
                    total_skills_loaded += 1
        
        # Суммарная статистика
        self.logger.info(f"Всего обработано файлов навыков: {total_files_processed}")
        self.logger.info(f"Всего загружено навыков: {total_skills_loaded}")
    
    def load_skill_from_file(self, file_path):
        """Загружает один навык из JSON-файла
        
        Returns:
            bool: True, если навык успешно загружен, False в противном случае
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                skill_data = json.load(file)
                
                skill_id = skill_data.get("id")
                if not skill_id:
                    self.logger.error(f"В файле {file_path} отсутствует ID навыка")
                    return False
                
                name = skill_data.get("name", skill_id)
                description = skill_data.get("description", "")
                max_level = skill_data.get("max_level", 100)
                base_exp = skill_data.get("base_exp", 100)
                exp_factor = skill_data.get("exp_factor", 1.5)
                
                # Создаем объект навыка с новыми параметрами
                skill = Skill(skill_id, name, description, max_level, base_exp, exp_factor)
                
                # Загружаем информацию о разблокируемых предметах и бонусах
                for level_data in skill_data.get("levels", []):
                    level = level_data.get("level")
                    
                    if not level:
                        continue
                        
                    # Сохраняем разблокируемые предметы для каждого уровня
                    unlocks = level_data.get("unlocks", [])
                    skill.add_unlocks_by_level(level, unlocks)
                    
                    # Сохраняем бонусы, предоставляемые каждым уровнем
                    provides = level_data.get("provides", {})
                    if provides:
                        skill.add_provides_by_level(level, provides)
                
                self.skills[skill_id] = skill
                self.logger.info(f"Загружен навык: {name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке навыка из {file_path}: {str(e)}")
            return False
    
    def get_skill(self, skill_id):
        """Возвращает навык по ID"""
        return self.skills.get(skill_id)
    
    def get_all_skills(self):
        """Возвращает список всех навыков"""
        return list(self.skills.values())
    
    def add_experience(self, skill_id, amount):
        """Добавляет опыт к указанному навыку
        
        Args:
            skill_id (str): Идентификатор навыка
            amount (int): Количество опыта для добавления
            
        Returns:
            bool: True если произошло повышение уровня, иначе False
        """
        skill = self.get_skill(skill_id)
        
        if not skill:
            self.logger.error(f"Невозможно добавить опыт: навык {skill_id} не найден")
            return False
            
        old_level = skill.level
        new_level = skill.add_experience(amount)
        
        # Возвращаем True, если уровень повысился
        return new_level > old_level 