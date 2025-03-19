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
        self.entity_start_re = re.compile(r'^([A-Z]+)\s+([a-zA-Z0-9_]+)\s*{$')
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
        
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Пропускаем комментарии и пустые строки
            if self.comment_re.match(line) or self.empty_line_re.match(line):
                i += 1
                continue
            
            # Проверяем начало сущности (LOCATION, ITEM и т.д.)
            entity_match = self.entity_start_re.match(line)
            if entity_match:
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
                
                # Особая обработка CONNECTION внутри блока CONNECTIONS
                elif in_connections_block and entity_type == "CONNECTION":
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
            
            # Проверяем начало блока (RESOURCES, CONNECTIONS и т.д.)
            block_match = self.block_start_re.match(line)
            if block_match:
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
                else:
                    # Для других блоков просто создаем обычный словарь
                    current_dict[block_type.lower()] = {}
                
                # Добавляем блок в стек
                stack.append((current_dict[block_type.lower()], block_type))
                
                i += 1
                continue
            
            # Проверяем конец блока или сущности
            if self.block_end_re.match(line):
                # Извлекаем информацию о текущем уровне
                current_dict, current_key = stack[-1]
                
                # Проверяем, завершаем ли мы специальный блок
                if in_connections_block and current_key == "CONNECTIONS":
                    in_connections_block = False
                elif in_characters_block and current_key == "CHARACTERS":
                    in_characters_block = False
                elif in_resources_block and current_key == "RESOURCES":
                    in_resources_block = False
                
                # Если мы завершаем блок CONNECTION внутри CONNECTIONS,
                # нам не нужно ничего делать, так как соединение уже добавлено в список
                
                # Убираем последний словарь из стека
                popped = stack.pop()
                
                i += 1
                continue
            
            # Обрабатываем свойства (ключ: значение)
            property_match = self.property_re.match(line)
            if property_match:
                key, value = property_match.groups()
                current_dict, _ = stack[-1]
                
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