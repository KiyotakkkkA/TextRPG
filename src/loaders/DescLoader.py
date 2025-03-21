"""
Загрузчик данных из файлов .desc.
Позволяет парсить файлы .desc и получать структурированные данные.
"""

import os
import re
import json
from typing import Dict, List, Any, Union, Tuple, Optional


class DescLoader:
    """
    Класс для загрузки и парсинга файлов .desc.
    """
    
    def __init__(self):
        """
        Инициализирует загрузчик .desc файлов.
        """
        # Регулярные выражения для различных элементов синтаксиса
        self.entity_start_re = re.compile(r'^([A-Z_]+)\s+([a-zA-Z0-9_]+)\s*{$')
        self.property_re = re.compile(r'^([a-zA-Z0-9_]+):\s*(.+)$')
        self.block_start_re = re.compile(r'^([A-Z]+)\s*{$')
        self.block_end_re = re.compile(r'^}$')
        self.array_re = re.compile(r'\[(.*?)\]')
        self.comment_re = re.compile(r'^\s*(#|//).*$')
        self.empty_line_re = re.compile(r'^\s*$')
    
    def load_file(self, file_path: str) -> Dict[str, Any]:
        """
        Загружает и парсит файл .desc, возвращая структурированные данные.
        
        Args:
            file_path: Путь к файлу .desc
            
        Returns:
            Dict[str, Any]: Словарь с данными, полученными из файла
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip() for line in f.readlines()]
        
        result = self.parse_lines(lines)
        return result
    
    def load_directory(self, directory: str) -> Dict[str, Any]:
        """
        Рекурсивно загружает все .desc файлы из указанной директории.
        
        Args:
            directory: Путь к директории
            
        Returns:
            Dict[str, Any]: Объединенный словарь с данными из всех файлов
        """
        result = {}
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.desc'):
                    file_path = os.path.join(root, file)
                    try:
                        data = self.load_file(file_path)
                        # Объединяем данные из файла с общим результатом
                        result.update(data)
                    except Exception as e:
                        print(f"Ошибка при загрузке {file_path}: {str(e)}")
        
        return result
    
    def parse_lines(self, lines: List[str]) -> Dict[str, Any]:
        """
        Парсит список строк формата .desc.
        
        Args:
            lines: Список строк формата .desc
            
        Returns:
            Dict[str, Any]: Словарь с данными
        """
        result = {}
        stack = [(result, None)]  # (текущий_словарь, текущий_ключ)
        i = 0
        
        # Флаги для отслеживания текущего контекста
        in_connections_block = False
        in_characters_block = False
        in_resources_block = False
        in_requires_block = False  # Флаг для блока REQUIRES
        in_improves_block = False  # Флаг для блока IMPROVES
        
        # Счетчики для логирования
        found_skill_improvements = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Пропускаем комментарии и пустые строки
            if self.comment_re.match(line) or self.empty_line_re.match(line):
                i += 1
                continue
            
            # Проверяем начало сущности (LOCATION, ITEM и т.д.)
            entity_match = self.entity_start_re.match(line)
            if entity_match:
                # Проверка на пустоту стека
                if not stack:
                    stack.append((result, None))  # Восстанавливаем стек если он пуст
                    
                entity_type, entity_id = entity_match.groups()
                current_dict, current_key = stack[-1]
                
                # Если мы находимся в корневом словаре, создаем новую сущность на верхнем уровне
                if len(stack) == 1:  # Это корневой уровень
                    # Проверяем, что сущность с таким ID еще не существует
                    
                    current_dict[entity_id] = {}
                    stack.append((current_dict[entity_id], entity_type))
                    
                    # Сбрасываем флаги, так как мы начали новую сущность верхнего уровня
                    in_connections_block = False
                    in_characters_block = False
                    in_resources_block = False
                    in_requires_block = False
                    in_improves_block = False
                
                # Особая обработка CONNECTION внутри блока CONNECTIONS
                elif in_connections_block and entity_type == "CONNECTION":
                    # Проверяем доступ к родительскому элементу
                    if len(stack) < 2:
                        # Если нет родительского элемента, пропускаем операцию
                        i += 1
                        continue
                        
                    current_dict, current_key = stack[-1]
                    entity_parent_dict, _ = stack[-2]  # Словарь-родитель (локация)
                    
                    # Если это первое соединение, создаем список для connections
                    if "connections" not in entity_parent_dict:
                        entity_parent_dict["connections"] = []
                    
                    # Создаем новый словарь для соединения
                    connection_dict = {"id": entity_id}
                    
                    # Добавляем соединение в список
                    entity_parent_dict["connections"].append(connection_dict)
                    
                    # Добавляем в стек для обработки свойств соединения
                    stack.append((connection_dict, entity_type))
                
                # Особая обработка CHARACTER внутри блока CHARACTERS
                elif in_characters_block and entity_type == "CHARACTER":
                    # Проверяем доступ к родительскому элементу
                    if len(stack) < 2:
                        # Если нет родительского элемента, пропускаем операцию
                        i += 1
                        continue
                        
                    current_dict, current_key = stack[-1]
                    entity_parent_dict, _ = stack[-2]  # Словарь-родитель (локация)
                    
                    # Если это первый персонаж, создаем список для characters
                    if "characters" not in entity_parent_dict:
                        entity_parent_dict["characters"] = []
                    
                    # Создаем новый словарь для персонажа
                    character_dict = {"id": entity_id}
                    
                    # Добавляем персонажа в список
                    entity_parent_dict["characters"].append(character_dict)
                    
                    # Добавляем в стек для обработки свойств персонажа
                    stack.append((character_dict, entity_type))
                
                # Особая обработка RESOURCE внутри блока RESOURCES
                elif in_resources_block and entity_type == "RESOURCE":
                    current_dict, current_key = stack[-1]
                    
                    # Создаем новую запись для ресурса
                    if entity_id not in current_dict:
                        current_dict[entity_id] = {}
                    
                    # Добавляем в стек для обработки свойств ресурса
                    stack.append((current_dict[entity_id], entity_type))
                
                # Особая обработка REQ_ITEM внутри блока REQUIRES
                elif in_requires_block and entity_type == "REQ_ITEM":
                    current_dict, current_key = stack[-1]
                    
                    # Если это первый требуемый предмет, создаем словарь player_has_items
                    if "player_has_items" not in current_dict:
                        current_dict["player_has_items"] = {}
                    
                    # Вместо создания промежуточного словаря, добавляем заглушку
                    # Позже заменим эту заглушку на фактическое значение количества
                    current_dict["player_has_items"][entity_id] = 0
                    
                    # Добавляем в стек для обработки свойств требуемого предмета
                    # Ключ будет содержать также ID предмета для последующего обновления
                    stack.append((current_dict["player_has_items"], f"REQ_ITEM:{entity_id}"))
                
                # Особая обработка REQ_SKILL внутри блока REQUIRES
                elif in_requires_block and entity_type == "REQ_SKILL":
                    current_dict, current_key = stack[-1]
                    
                    # Если это первый требуемый навык, создаем словарь player_has_skill_level
                    if "player_has_skill_level" not in current_dict:
                        current_dict["player_has_skill_level"] = {}
                    
                    # Вместо создания промежуточного словаря, добавляем заглушку
                    # Позже заменим эту заглушку на фактическое значение уровня
                    current_dict["player_has_skill_level"][entity_id] = 0
                    
                    # Добавляем в стек для обработки свойств требуемого навыка
                    # Ключ будет содержать также ID навыка для последующего обновления
                    stack.append((current_dict["player_has_skill_level"], f"REQ_SKILL:{entity_id}"))
                
                # Особая обработка IMPROVES_SKILL внутри блока IMPROVES
                elif in_improves_block and entity_type == "IMPROVES_SKILL":
                    current_dict, current_key = stack[-1]
                    
                    # Если это первое улучшение навыка, создаем словарь improves_skills
                    if "improves_skills" not in current_dict:
                        current_dict["improves_skills"] = {}
                    
                    # Вместо создания промежуточного словаря, добавляем заглушку
                    # Позже заменим эту заглушку на фактическое значение опыта
                    current_dict["improves_skills"][entity_id] = 0
                    
                    # Добавляем в стек для обработки свойств улучшаемого навыка
                    # Ключ будет содержать также ID навыка для последующего обновления
                    stack.append((current_dict["improves_skills"], f"IMPROVES_SKILL:{entity_id}"))
                    
                    # Увеличиваем счетчик найденных привязок
                    found_skill_improvements += 1
                    
                    print(f"Найдена привязка улучшения навыка {entity_id}")
                
                # Если мы внутри блока верхнего уровня
                elif len(stack) == 2 and current_key and current_key.isupper():
                    if entity_id not in current_dict:
                        current_dict[entity_id] = {}
                    stack.append((current_dict[entity_id], entity_type))
                else:
                    # Внутри блока другой сущности (например, RESOURCE в RESOURCES)
                    if entity_type.lower() not in current_dict:
                        current_dict[entity_type.lower()] = {}
                    
                    # Добавляем новую сущность в соответствующий блок
                    current_dict[entity_type.lower()][entity_id] = {}
                    stack.append((current_dict[entity_type.lower()][entity_id], entity_type))
                
                i += 1
                continue
            
            # Проверяем начало блока (RESOURCES, CONNECTIONS, REQUIRES и т.д.)
            block_match = self.block_start_re.match(line)
            if block_match:
                # Проверка на пустоту стека
                if not stack:
                    stack.append((result, None))  # Восстанавливаем стек если он пуст
                    
                block_type = block_match.group(1)
                current_dict, _ = stack[-1]
        
                
                # Устанавливаем соответствующий флаг для блока
                if block_type == "CONNECTIONS":
                    in_connections_block = True
                    # Инициализируем пустой список соединений
                    current_dict["connections"] = []
                elif block_type == "CHARACTERS":
                    in_characters_block = True
                    # Инициализируем пустой список персонажей
                    current_dict["characters"] = []
                elif block_type == "RESOURCES":
                    in_resources_block = True
                    # Создаем словарь для ресурсов
                    current_dict[block_type.lower()] = {}
                elif block_type == "REQUIRES":
                    # Новый блок для требований
                    in_requires_block = True
                    # Создаем словарь для требований
                    current_dict["requires"] = {}
                elif block_type == "IMPROVES":
                    # Новый блок для улучшений
                    in_improves_block = True
                    # Создаем словарь для улучшений
                    current_dict["improves"] = {}
                else:
                    # Для других блоков просто создаем обычный словарь
                    current_dict[block_type.lower()] = {}
                
                # Добавляем блок в стек
                stack.append((current_dict[block_type.lower()], block_type))
                
                i += 1
                continue
            
            # Проверяем конец блока или сущности
            if self.block_end_re.match(line):
                # Проверка на пустоту стека
                if not stack:
                    # Если стек пуст, пропускаем эту закрывающую скобку
                    i += 1
                    continue
                    
                # Извлекаем информацию о текущем уровне
                current_dict, current_key = stack[-1]
                
                # Проверяем, завершаем ли мы специальный блок
                if in_connections_block and current_key == "CONNECTIONS":
                    in_connections_block = False
                elif in_characters_block and current_key == "CHARACTERS":
                    in_characters_block = False
                elif in_resources_block and current_key == "RESOURCES":
                    in_resources_block = False
                elif in_requires_block and current_key == "REQUIRES":
                    in_requires_block = False
                elif in_improves_block and current_key == "IMPROVES":
                    in_improves_block = False
                    # Логируем количество найденных привязок улучшений навыков
                    if found_skill_improvements > 0:
                        print(f"Всего найдено привязок улучшений навыков: {found_skill_improvements}")
                        found_skill_improvements = 0
                
                # Убираем последний словарь из стека, но убедимся что в стеке останется как минимум один элемент
                popped = stack.pop() if len(stack) > 1 else None
                
                i += 1
                continue
            
            # Обрабатываем свойства (ключ: значение)
            property_match = self.property_re.match(line)
            if property_match:
                # Проверка на пустоту стека
                if not stack:
                    stack.append((result, None))  # Восстанавливаем стек если он пуст
                    
                key, value = property_match.groups()
                current_dict, current_key = stack[-1]
                
                # Преобразуем ключ level в числовое значение для REQ_SKILL
                if key == "level":
                    try:
                        # Получаем числовое значение уровня
                        level_value = self._parse_value(value)
                        
                        # Извлекаем ID навыка из ключа текущего контекста
                        _, current_key = stack[-1]
                        if current_key and ":" in current_key:
                            _, skill_id = current_key.split(":", 1)
                            
                            # Получаем родительский словарь (requires)
                            parent_dict, _ = stack[-2]
                            
                            # Убедимся, что словарь player_has_skill_level существует
                            if "player_has_skill_level" not in parent_dict:
                                parent_dict["player_has_skill_level"] = {}
                                
                            # Устанавливаем уровень навыка
                            parent_dict["player_has_skill_level"][skill_id] = level_value
                    except Exception as e:
                        print(f"Ошибка при обработке уровня навыка: {e}")
                        
                # Преобразуем ключ amount в числовое значение для REQ_ITEM
                elif key == "amount":
                    try:
                        # Получаем числовое значение количества
                        amount_value = self._parse_value(value)
                        
                        # Извлекаем ID предмета из ключа текущего контекста
                        _, current_key = stack[-1]
                        if current_key and ":" in current_key:
                            _, item_id = current_key.split(":", 1)
                            
                            # Получаем родительский словарь (requires)
                            parent_dict, _ = stack[-2]
                            
                            # Убедимся, что словарь player_has_items существует
                            if "player_has_items" not in parent_dict:
                                parent_dict["player_has_items"] = {}
                                
                            # Устанавливаем количество предмета
                            parent_dict["player_has_items"][item_id] = amount_value
                    
                    except Exception as e:
                        print(f"Ошибка при обработке количества предмета: {e}")
                    
                # Обработка опыта для IMPROVES_SKILL
                elif key == "exp":
                    try:
                        # Получаем числовое значение опыта
                        exp_value = self._parse_value(value)
                        
                        # Извлекаем ID навыка из ключа текущего контекста
                        _, current_key = stack[-1]
                        if current_key and ":" in current_key:
                            _, skill_id = current_key.split(":", 1)
                            
                            # Получаем родительский словарь (improves)
                            parent_dict, _ = stack[-2]
                            
                            # Убедимся, что словарь improves_skills существует
                            if "improves_skills" not in parent_dict:
                                parent_dict["improves_skills"] = {}
                                
                            # Устанавливаем опыт для навыка
                            parent_dict["improves_skills"][skill_id] = exp_value
                    
                    except Exception as e:
                        print(f"Ошибка при обработке опыта для навыка: {e}")
                # Обычная обработка свойств
                else:
                    # Обрабатываем значение
                    parsed_value = self._parse_value(value)
                    current_dict[key] = parsed_value
                
                i += 1
                continue
            
            # Если строка не соответствует ни одному шаблону
            i += 1
        
        return result
    
    def _parse_value(self, value: str) -> Any:
        """
        Парсит значение свойства.
        
        Args:
            value: Строка значения
            
        Returns:
            Any: Распарсенное значение: строка, число, булево, null, словарь или список
        """
        value = value.strip()
        
        # Удаляем запятую в конце значения, если она есть
        if value.endswith(','):
            value = value[:-1].strip()
        
        # Проверяем, является ли значение строкой в кавычках
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        
        # Проверяем, является ли значение числом
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Проверяем, является ли значение массивом
        array_match = self.array_re.match(value)
        if array_match:
            items_str = array_match.group(1).strip()
            
            # Если массив пустой
            if not items_str:
                return []
            
            # Парсим элементы массива
            items = []
            current_item = ""
            in_quotes = False
            quote_char = None
            in_object = 0  # Счетчик глубины вложенных объектов { }
            in_array = 0   # Счетчик глубины вложенных массивов [ ]
            
            for i, char in enumerate(items_str + ','):  # Добавляем запятую, чтобы обработать последний элемент
                if in_quotes:
                    if char == quote_char and (i == 0 or items_str[i-1] != '\\'):
                        in_quotes = False
                    current_item += char
                elif char == '"' or char == "'":
                    in_quotes = True
                    quote_char = char
                    current_item += char
                elif char == '{':
                    in_object += 1
                    current_item += char
                elif char == '}':
                    in_object -= 1
                    current_item += char
                elif char == '[':
                    in_array += 1
                    current_item += char
                elif char == ']':
                    in_array -= 1
                    current_item += char
                elif char == ',' and in_object == 0 and in_array == 0:
                    # Элемент массива завершен
                    if current_item.strip():
                        items.append(self._parse_value(current_item.strip()))
                    current_item = ""
                else:
                    current_item += char
            
            return items
        
        # Проверяем, является ли значение объектом JSON
        if value.startswith('{') and value.endswith('}'):
            try:
                # Заменяем одинарные кавычки на двойные для совместимости с JSON
                json_str = value.replace("'", '"')
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Если не получилось распарсить как JSON
                pass
        
        # Проверяем специальные значения
        if value.lower() == 'null':
            return None
        elif value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        
        # Если ничего не подошло, возвращаем как строку
        # Это особенно важно для значений типа "name: Лес" без кавычек
        return value 