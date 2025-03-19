#!/usr/bin/env python3
"""
Транслятор формата .desc в JSON для TextRPG.
Преобразует описания игровых сущностей из удобного формата .desc в JSON.

Использование:
    python desc_to_json.py input.desc output.json
    python desc_to_json.py --dir input_dir output_dir
"""

import os
import sys
import json
import argparse
import re
from typing import Dict, List, Any, Union, Tuple, Optional


class DescParser:
    """
    Парсер для формата .desc
    """
    def __init__(self):
        # Регулярные выражения для различных элементов синтаксиса
        self.entity_start_re = re.compile(r'^([A-Z]+)\s+([a-zA-Z0-9_]+)\s*{$')
        self.property_re = re.compile(r'^([a-zA-Z0-9_]+):\s*(.+)$')
        self.block_start_re = re.compile(r'^([A-Z]+)\s*{$')
        self.block_end_re = re.compile(r'^}$')
        self.array_re = re.compile(r'\[(.*?)\]')
        self.comment_re = re.compile(r'^\s*(#|//).*$')
        self.empty_line_re = re.compile(r'^\s*$')
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Парсит файл .desc и возвращает словарь с данными.
        
        Args:
            file_path: Путь к файлу .desc
            
        Returns:
            Словарь с данными из файла .desc
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip() for line in f.readlines()]
        
        return self.parse_lines(lines)
    
    def parse_lines(self, lines: List[str]) -> Dict[str, Any]:
        """
        Парсит список строк формата .desc.
        
        Args:
            lines: Список строк формата .desc
            
        Returns:
            Словарь с данными
        """
        result = {}
        stack = [(result, None)]  # (текущий_словарь, текущий_ключ)
        i = 0
        
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
                current_dict, _ = stack[-1]
                
                # Создаем словарь для данной сущности
                if entity_type not in current_dict:
                    current_dict[entity_id] = {}
                else:
                    # Если это уже список сущностей
                    if not isinstance(current_dict[entity_type], dict):
                        current_dict[entity_type][entity_id] = {}
                
                # Помещаем новый словарь в стек
                stack.append((current_dict[entity_id], entity_type))
                i += 1
                continue
            
            # Проверяем начало блока (RESOURCES, CONNECTIONS и т.д.)
            block_match = self.block_start_re.match(line)
            if block_match:
                block_type = block_match.group(1)
                current_dict, _ = stack[-1]
                
                if block_type == block_type.upper():  # Это блок верхнего уровня
                    current_dict[block_type.lower()] = {}
                    stack.append((current_dict[block_type.lower()], block_type))
                else:
                    # Для блоков, являющихся списками (напр., RESOURCE в RESOURCES)
                    current_dict[block_type.lower()] = []
                    stack.append((current_dict[block_type.lower()], block_type))
                
                i += 1
                continue
            
            # Проверяем конец блока
            if self.block_end_re.match(line):
                stack.pop()  # Убираем последний словарь из стека
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
            print(f"Предупреждение: непонятная строка в строке {i+1}: {line}")
            i += 1
        
        return result
    
    def _parse_value(self, value: str) -> Any:
        """
        Парсит значение свойства.
        
        Args:
            value: Строка значения
            
        Returns:
            Распарсенное значение: строка, число, булево, null, словарь или список
        """
        value = value.strip()
        
        # Проверяем, является ли значение строкой в кавычках
        if value.startswith('"') and value.endswith('"'):
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
            items = array_match.group(1).split(',')
            parsed_items = [self._parse_value(item.strip()) for item in items]
            
            # Проверяем, если это список JSON-фрагментов, нужно их объединить
            if parsed_items and all(isinstance(item, str) and ("{'id':" in item or "{'name':" in item) for item in parsed_items):
                # Попытаемся реконструировать JSON-объекты из фрагментов
                result = []
                current_obj = ""
                for item in parsed_items:
                    item = item.strip()
                    if "{'id':" in item or "{'name':" in item:
                        if current_obj:
                            # Если начинается новый объект, добавляем предыдущий
                            try:
                                # Заменяем одинарные кавычки на двойные для JSON
                                json_str = current_obj.replace("'", '"')
                                result.append(json.loads(json_str))
                            except json.JSONDecodeError:
                                result.append(current_obj)
                            current_obj = ""
                        current_obj = item
                    else:
                        current_obj += " " + item
                
                # Добавляем последний объект
                if current_obj:
                    try:
                        json_str = current_obj.replace("'", '"')
                        result.append(json.loads(json_str))
                    except json.JSONDecodeError:
                        result.append(current_obj)
                
                return result if result else parsed_items
            
            return parsed_items
        
        # Проверяем, является ли значение объектом JSON
        if value.startswith('{') and value.endswith('}'):
            try:
                json_str = value.replace("'", '"')
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Проверяем специальные значения
        if value.lower() == 'null':
            return None
        elif value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        
        # Если ничего не подошло, возвращаем как строку
        return value


def convert_file(input_path: str, output_path: str) -> bool:
    """
    Конвертирует файл .desc в JSON.
    
    Args:
        input_path: Путь к входному файлу .desc
        output_path: Путь к выходному файлу JSON
        
    Returns:
        True, если конвертация прошла успешно
    """
    try:
        parser = DescParser()
        data = parser.parse_file(input_path)
        
        # Постобработка специальных структур
        for entity_id, entity in data.items():
            # Обрабатываем список connections
            if 'connections' in entity and isinstance(entity['connections'], list):
                processed_connections = []
                current_obj = {}
                for item in entity['connections']:
                    if isinstance(item, dict):
                        processed_connections.append(item)
                    elif isinstance(item, str):
                        # Пытаемся восстановить JSON-объект
                        if item.startswith("{'id':"):
                            # Новый объект начался
                            if current_obj:
                                processed_connections.append(current_obj)
                                current_obj = {}
                            
                            # Извлекаем id
                            id_match = re.search(r"'id':\s*'([^']+)'", item)
                            if id_match:
                                current_obj['id'] = id_match.group(1)
                        
                        elif item.startswith("'name':"):
                            # Извлекаем name
                            name_match = re.search(r"'name':\s*'([^']+)'", item)
                            if name_match:
                                current_obj['name'] = name_match.group(1)
                        
                        elif item.startswith("'condition':"):
                            # Извлекаем condition
                            condition_match = re.search(r"'condition':\s*([^}]+)", item)
                            if condition_match:
                                condition = condition_match.group(1).strip()
                                if condition == 'none':
                                    current_obj['condition'] = None
                                elif condition.startswith("'") and condition.endswith("'"):
                                    current_obj['condition'] = condition[1:-1]
                                else:
                                    current_obj['condition'] = condition
                        
                        elif item.endswith("}"):
                            # Конец объекта
                            if current_obj:
                                processed_connections.append(current_obj)
                                current_obj = {}
                
                # Добавляем последний объект, если есть
                if current_obj:
                    processed_connections.append(current_obj)
                
                entity['connections'] = processed_connections
            
            # Аналогично обрабатываем characters
            if 'characters' in entity and isinstance(entity['characters'], list):
                processed_chars = []
                current_obj = {}
                for item in entity['characters']:
                    if isinstance(item, dict):
                        processed_chars.append(item)
                    elif isinstance(item, str):
                        # Пытаемся восстановить JSON-объект
                        if item.startswith("{'id':"):
                            # Новый объект начался
                            if current_obj:
                                processed_chars.append(current_obj)
                                current_obj = {}
                            
                            # Извлекаем id
                            id_match = re.search(r"'id':\s*'([^']+)'", item)
                            if id_match:
                                current_obj['id'] = id_match.group(1)
                        
                        elif item.startswith("'name':"):
                            # Извлекаем name
                            name_match = re.search(r"'name':\s*'([^']+)'", item)
                            if name_match:
                                current_obj['name'] = name_match.group(1)
                        
                        elif item.startswith("'description':"):
                            # Извлекаем description
                            desc_match = re.search(r"'description':\s*'([^']+)'", item)
                            if desc_match:
                                current_obj['description'] = desc_match.group(1)
                            else:
                                # Если description содержит несколько строк
                                current_obj['description'] = item.replace("'description': '", "").rstrip("'")
                        
                        elif "живущий" in item or "который" in item or "знает" in item or "собиратель" in item:
                            # Продолжение description
                            if 'description' in current_obj:
                                current_obj['description'] += " " + item.rstrip("'}")
                            else:
                                current_obj['description'] = item.rstrip("'}")
                        
                        elif item.endswith("}"):
                            # Конец объекта
                            if current_obj:
                                processed_chars.append(current_obj)
                                current_obj = {}
                
                # Добавляем последний объект, если есть
                if current_obj:
                    processed_chars.append(current_obj)
                
                entity['characters'] = processed_chars
        
        # Записываем результат в JSON файл
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Успешно сконвертирован: {input_path} -> {output_path}")
        return True
    except Exception as e:
        print(f"Ошибка при конвертации {input_path}: {str(e)}")
        return False


def convert_directory(input_dir: str, output_dir: str) -> Tuple[int, int]:
    """
    Конвертирует все файлы .desc в директории в JSON.
    
    Args:
        input_dir: Путь к входной директории с файлами .desc
        output_dir: Путь к выходной директории для файлов JSON
        
    Returns:
        (количество успешных конвертаций, общее количество файлов)
    """
    # Создаем выходную директорию, если она не существует
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    total_count = 0
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.desc'):
                total_count += 1
                
                # Сохраняем структуру директорий
                rel_path = os.path.relpath(root, input_dir)
                out_dir = os.path.join(output_dir, rel_path)
                os.makedirs(out_dir, exist_ok=True)
                
                input_path = os.path.join(root, file)
                output_path = os.path.join(out_dir, file.replace('.desc', '.json'))
                
                if convert_file(input_path, output_path):
                    success_count += 1
    
    return success_count, total_count


def main():
    """
    Основная функция программы.
    """
    parser = argparse.ArgumentParser(description='Конвертирует файлы .desc в JSON')
    
    # Аргументы командной строки
    parser.add_argument('--dir', action='store_true', help='Конвертировать директорию')
    parser.add_argument('input', help='Входной файл .desc или директория')
    parser.add_argument('output', help='Выходной файл JSON или директория')
    
    args = parser.parse_args()
    
    if args.dir:
        success, total = convert_directory(args.input, args.output)
        print(f"Конвертация завершена: {success} из {total} файлов успешно сконвертированы")
    else:
        convert_file(args.input, args.output)


if __name__ == "__main__":
    main() 