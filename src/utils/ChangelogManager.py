"""
Модуль для управления журналом изменений.
"""

import os
import json
import time
from pathlib import Path
import datetime

class ChangelogManager:
    """
    Класс для управления журналом изменений.
    Позволяет получать информацию о текущем обновлении и его изменениях.
    """
    
    def __init__(self):
        """
        Инициализирует менеджер журнала изменений.
        """
        # Определяем пути к директориям
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(self.current_dir, '../..'))
        self.changelog_dir = os.path.join(self.project_root, 'changelog')
        
        # Загружаем информацию о текущем обновлении
        self.head_data = self.load_head()
        self.update_hash = self.head_data.get("current_hash", "")
        self.update_name = self.head_data.get("update_name", "")
        self.update_timestamp = self.head_data.get("timestamp", "")
        
    def load_head(self):
        """
        Загружает информацию о текущем обновлении.
        
        Returns:
            dict: Информация о текущем обновлении
        """
        head_file = os.path.join(self.changelog_dir, 'head.json')
        if not os.path.exists(head_file):
            return {
                "current_hash": None,
                "update_name": None,
                "timestamp": None,
                "history": []
            }
        
        try:
            with open(head_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка при загрузке head.json: {str(e)}")
            return {
                "current_hash": None,
                "update_name": None,
                "timestamp": None,
                "history": []
            }
    
    def get_current_update_hash(self):
        """
        Возвращает хеш текущего обновления.
        
        Returns:
            str: Хеш текущего обновления или None
        """
        return self.head_data.get("current_hash")
    
    def get_update_name(self):
        """
        Возвращает название текущего обновления.
        
        Returns:
            str: Название обновления или None
        """
        return self.head_data.get("update_name")
    
    def get_update_timestamp(self):
        """
        Возвращает временную метку текущего обновления.
        
        Returns:
            int: Временная метка или None
        """
        return self.head_data.get("timestamp")
    
    def get_update_art(self):
        """
        Возвращает ASCII-арт текущего обновления.
        
        Returns:
            str: ASCII-арт или пустая строка
        """
        update_hash = self.get_current_update_hash()
        if not update_hash:
            return ""
        
        art_file = os.path.join(self.changelog_dir, update_hash, 'art.json')
        if not os.path.exists(art_file):
            return ""
        
        try:
            with open(art_file, 'r', encoding='utf-8') as f:
                art_data = json.load(f)
                return art_data.get("art", "")
        except Exception as e:
            print(f"Ошибка при загрузке art.json: {str(e)}")
            return ""
    
    def get_update_changes(self):
        """
        Возвращает текст с изменениями текущего обновления.
        
        Returns:
            str: Текст с изменениями или пустая строка
        """
        update_hash = self.get_current_update_hash()
        if not update_hash:
            return ""
        
        changes_file = os.path.join(self.changelog_dir, update_hash, 'changes.txt')
        if not os.path.exists(changes_file):
            return ""
        
        try:
            with open(changes_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Ошибка при загрузке changes.txt: {str(e)}")
            return ""
    
    def has_update(self):
        """
        Проверяет, есть ли информация о текущем обновлении.
        
        Returns:
            bool: True, если есть информация об обновлении
        """
        return self.get_current_update_hash() is not None
    
    def get_formatted_update_date(self):
        """
        Возвращает форматированную дату обновления.
        
        Returns:
            str: Форматированная дата или пустая строка
        """
        timestamp = self.get_update_timestamp()
        if not timestamp:
            return ""
        
        return time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(timestamp))
    
    def get_update_history(self):
        """
        Возвращает список хэшей предыдущих обновлений.
        
        Returns:
            list: Список хэшей обновлений в хронологическом порядке.
        """
        return self.head_data.get("history", [])
    
    def get_update_info_by_hash(self, update_hash):
        """
        Получает информацию об обновлении по его хэшу.
        
        Args:
            update_hash (str): Хэш обновления.
            
        Returns:
            dict: Словарь с информацией об обновлении.
        """
        if not update_hash:
            return {
                "name": "Неизвестное обновление",
                "hash": "",
                "formatted_date": "",
                "changes": "Информация об обновлении не найдена.",
                "art": "",
                "has_update": False
            }
        
        # Проверяем существование директории обновления
        update_dir = os.path.join(os.getcwd(), "changelog", update_hash)
        if not os.path.exists(update_dir):
            return {
                "name": "Неизвестное обновление",
                "hash": update_hash,
                "formatted_date": "",
                "changes": f"Обновление с хэшем {update_hash} не найдено.",
                "has_update": True
            }
        
        # Пытаемся получить информацию из файлов обновления
        art_file = os.path.join(update_dir, "art.json")
        changes_file = os.path.join(update_dir, "changes.txt")
        
        # Читаем данные из art.json
        art_data = {}
        if os.path.exists(art_file):
            try:
                with open(art_file, 'r', encoding='utf-8') as file:
                    art_data = json.load(file)
            except json.JSONDecodeError:
                pass
        
        # Читаем данные из changes.txt
        changes_text = ""
        if os.path.exists(changes_file):
            try:
                with open(changes_file, 'r', encoding='utf-8') as file:
                    changes_text = file.read()
            except Exception:
                pass
        
        # Формируем информацию об обновлении
        update_info = {
            "name": art_data.get("name", self.update_name if update_hash == self.update_hash else "Обновление"),
            "hash": update_hash,
            "timestamp": art_data.get("timestamp", ""),
            "art": art_data.get("art", ""),
            "changes": changes_text,
            "has_update": True
        }
        
        # Форматируем дату
        timestamp = update_info.get("timestamp")
        if timestamp:
            try:
                dt = datetime.datetime.fromtimestamp(int(timestamp))
                update_info["formatted_date"] = dt.strftime("%d.%m.%Y %H:%M")
            except (ValueError, TypeError):
                update_info["formatted_date"] = ""
        
        return update_info
    
    def get_update_info(self):
        """
        Получает полную информацию о текущем обновлении, включая историю.
        
        Returns:
            dict: Словарь с информацией об обновлении и его историей.
        """
        current_hash = self.head_data.get("current_hash", "")
        history = self.get_update_history()
        
        # Получаем информацию о текущем обновлении
        update_info = self.get_update_info_by_hash(current_hash)
        
        # Добавляем историю
        update_info["history"] = history
        
        return update_info 