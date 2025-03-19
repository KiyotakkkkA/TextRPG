#!/usr/bin/env python3
"""
Транслятор JSON в формат .desc для TextRPG.
Преобразует JSON файлы в более удобный для чтения формат .desc.

Использование:
    python json_to_desc.py input.json output.desc
    python json_to_desc.py --dir input_dir output_dir
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Union, Tuple, Optional


class JsonToDescConverter:
    """
    Конвертер JSON в формат .desc
    """
    def __init__(self):
        self.indent_size = 4
        
        # Типы сущностей, которые будут обрабатываться специальным образом
        self.entity_types = {
            "LOCATION": ["name", "description", "type"],
            "ITEM": ["name", "description", "value", "type"],
            "NPC": ["name", "description", "level"]
        }
        
        # Блоки со специальной обработкой
        self.special_blocks = {
            "resources": "RESOURCE",
            "connections": "CONNECTION",
            "characters": "CHARACTER"
        }
    
    def convert_file(self, input_path: str, output_path: str) -> bool:
        """
        Конвертирует файл JSON в .desc.
        
        Args:
            input_path: Путь к входному файлу JSON
            output_path: Путь к выходному файлу .desc
            
        Returns:
            True, если конвертация прошла успешно
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Конвертируем данные в формат .desc
            desc_content = self.convert_json_to_desc(data)
            
            # Записываем результат в файл .desc
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(desc_content)
            
            print(f"Успешно сконвертирован: {input_path} -> {output_path}")
            return True
        except Exception as e:
            print(f"Ошибка при конвертации {input_path}: {str(e)}")
            return False
    
    def convert_json_to_desc(self, data: Dict[str, Any], level: int = 0) -> str:
        """
        Рекурсивно конвертирует JSON данные в формат .desc.
        
        Args:
            data: Словарь с данными из JSON
            level: Текущий уровень вложенности для отступов
            
        Returns:
            Строка в формате .desc
        """
        result = []
        
        for key, value in data.items():
            # Определяем, является ли этот ключ идентификатором сущности
            entity_type = self._determine_entity_type(key, value)
            
            if entity_type:
                # Обрабатываем сущность (LOCATION, ITEM и т.д.)
                result.append(self._format_entity(entity_type, key, value, level))
            elif isinstance(value, dict):
                # Проверяем, является ли этот ключ специальным блоком
                if key in self.special_blocks:
                    result.append(self._format_special_block(key, value, level))
                else:
                    # Обычный блок
                    indent = ' ' * (level * self.indent_size)
                    result.append(f"{indent}{key.upper()} {{")
                    result.append(self.convert_json_to_desc(value, level + 1))
                    result.append(f"{indent}}}")
            elif isinstance(value, list):
                # Список значений
                result.append(self._format_list(key, value, level))
            else:
                # Простое свойство
                result.append(self._format_property(key, value, level))
        
        return '\n'.join(result)
    
    def _determine_entity_type(self, key: str, value: Any) -> Optional[str]:
        """
        Определяет тип сущности по данным.
        
        Args:
            key: Ключ объекта
            value: Значение объекта
            
        Returns:
            Тип сущности или None
        """
        if not isinstance(value, dict):
            return None
        
        # Проверяем по ключевым полям
        for entity_type, required_fields in self.entity_types.items():
            if all(field in value for field in required_fields):
                return entity_type
        
        return None
    
    def _format_entity(self, entity_type: str, entity_id: str, data: Dict[str, Any], level: int) -> str:
        """
        Форматирует сущность в формате .desc.
        
        Args:
            entity_type: Тип сущности (LOCATION, ITEM и т.д.)
            entity_id: Идентификатор сущности
            data: Данные сущности
            level: Уровень вложенности
            
        Returns:
            Строка в формате .desc
        """
        indent = ' ' * (level * self.indent_size)
        result = [f"{indent}{entity_type} {entity_id} {{"]
        
        # Сначала выводим основные поля
        for field in self.entity_types[entity_type]:
            if field in data:
                result.append(self._format_property(field, data[field], level + 1))
        
        # Затем остальные поля
        for key, value in data.items():
            if key not in self.entity_types[entity_type]:
                if isinstance(value, dict):
                    if key in self.special_blocks:
                        result.append(self._format_special_block(key, value, level + 1))
                    else:
                        inner_indent = ' ' * ((level + 1) * self.indent_size)
                        result.append(f"{inner_indent}{key.upper()} {{")
                        result.append(self.convert_json_to_desc(value, level + 2))
                        result.append(f"{inner_indent}}}")
                elif isinstance(value, list):
                    # Обработка списков-объектов, таких как connections и characters
                    if key in ["connections", "characters"] and value and isinstance(value[0], dict):
                        result.append(self._format_object_list_as_block(key, value, level + 1))
                    else:
                        result.append(self._format_list(key, value, level + 1))
                else:
                    result.append(self._format_property(key, value, level + 1))
        
        result.append(f"{indent}}}")
        return '\n'.join(result)
    
    def _format_object_list_as_block(self, block_name: str, items: List[Dict[str, Any]], level: int) -> str:
        """
        Форматирует список объектов как блок с подблоками.
        
        Args:
            block_name: Имя блока (connections, characters)
            items: Список объектов
            level: Уровень вложенности
            
        Returns:
            Строка в формате .desc
        """
        indent = ' ' * (level * self.indent_size)
        result = [f"{indent}{block_name.upper()} {{"]
        
        item_type = self.special_blocks.get(block_name)
        
        for item in items:
            item_id = item.get("id", "unknown")
            inner_indent = ' ' * ((level + 1) * self.indent_size)
            result.append(f"{inner_indent}{item_type} {item_id} {{")
            
            for key, value in item.items():
                result.append(self._format_property(key, value, level + 2))
            
            result.append(f"{inner_indent}}}")
        
        result.append(f"{indent}}}")
        return '\n'.join(result)
    
    def _format_special_block(self, block_name: str, data: Dict[str, Any], level: int) -> str:
        """
        Форматирует специальный блок (например, resources, connections).
        
        Args:
            block_name: Имя блока
            data: Данные блока
            level: Уровень вложенности
            
        Returns:
            Строка в формате .desc
        """
        indent = ' ' * (level * self.indent_size)
        result = [f"{indent}{block_name.upper()} {{"]
        
        item_type = self.special_blocks.get(block_name)
        
        for item_id, item_data in data.items():
            inner_indent = ' ' * ((level + 1) * self.indent_size)
            result.append(f"{inner_indent}{item_type} {item_id} {{")
            
            for key, value in item_data.items():
                result.append(self._format_property(key, value, level + 2))
            
            result.append(f"{inner_indent}}}")
        
        result.append(f"{indent}}}")
        return '\n'.join(result)
    
    def _format_list(self, key: str, values: List[Any], level: int) -> str:
        """
        Форматирует список значений.
        
        Args:
            key: Ключ списка
            values: Значения в списке
            level: Уровень вложенности
            
        Returns:
            Строка в формате .desc
        """
        indent = ' ' * (level * self.indent_size)
        
        # Форматируем элементы списка
        items = []
        for item in values:
            if isinstance(item, str):
                # Если строка содержит пробелы или специальные символы, заключаем в кавычки
                if ' ' in item or ',' in item or ':' in item:
                    items.append(f'"{item}"')
                else:
                    items.append(item)
            elif item is None:
                items.append('null')
            else:
                items.append(str(item).lower())
        
        return f"{indent}{key}: [{', '.join(items)}]"
    
    def _format_property(self, key: str, value: Any, level: int) -> str:
        """
        Форматирует простое свойство.
        
        Args:
            key: Ключ свойства
            value: Значение свойства
            level: Уровень вложенности
            
        Returns:
            Строка в формате .desc
        """
        indent = ' ' * (level * self.indent_size)
        
        if isinstance(value, str):
            # Если строка содержит пробелы или специальные символы, заключаем в кавычки
            if ' ' in value or ':' in value:
                return f'{indent}{key}: "{value}"'
            else:
                return f'{indent}{key}: {value}'
        elif value is None:
            return f'{indent}{key}: null'
        elif isinstance(value, bool):
            return f'{indent}{key}: {str(value).lower()}'
        else:
            return f'{indent}{key}: {value}'


def convert_directory(input_dir: str, output_dir: str) -> Tuple[int, int]:
    """
    Конвертирует все файлы JSON в директории в .desc.
    
    Args:
        input_dir: Путь к входной директории с файлами JSON
        output_dir: Путь к выходной директории для файлов .desc
        
    Returns:
        (количество успешных конвертаций, общее количество файлов)
    """
    converter = JsonToDescConverter()
    
    # Создаем выходную директорию, если она не существует
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    total_count = 0
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.json'):
                total_count += 1
                
                # Сохраняем структуру директорий
                rel_path = os.path.relpath(root, input_dir)
                out_dir = os.path.join(output_dir, rel_path)
                os.makedirs(out_dir, exist_ok=True)
                
                input_path = os.path.join(root, file)
                output_path = os.path.join(out_dir, file.replace('.json', '.desc'))
                
                if converter.convert_file(input_path, output_path):
                    success_count += 1
    
    return success_count, total_count


def main():
    """
    Основная функция программы.
    """
    parser = argparse.ArgumentParser(description='Конвертирует файлы JSON в .desc')
    
    # Аргументы командной строки
    parser.add_argument('--dir', action='store_true', help='Конвертировать директорию')
    parser.add_argument('input', help='Входной файл JSON или директория')
    parser.add_argument('output', help='Выходной файл .desc или директория')
    
    args = parser.parse_args()
    
    if args.dir:
        success, total = convert_directory(args.input, args.output)
        print(f"Конвертация завершена: {success} из {total} файлов успешно сконвертированы")
    else:
        converter = JsonToDescConverter()
        converter.convert_file(args.input, args.output)


if __name__ == "__main__":
    main() 