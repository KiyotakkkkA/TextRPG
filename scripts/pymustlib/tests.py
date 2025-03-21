"""
Тесты для библиотеки pymustlib.
"""

import unittest
import sys
import os
from pathlib import Path
from typing import List

# Добавляем родительскую директорию в sys.path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

# Импортируем библиотеку pymustlib
from pymustlib import registry, run_command, show_help

class MockCommand:
    """Мок-команда для тестирования"""
    
    def __init__(self, name: str, should_succeed: bool = True):
        self.name = name
        self.should_succeed = should_succeed
        self.was_called = False
        self.args = None
    
    def execute(self, args: List[str]) -> int:
        """Эмулирует выполнение команды"""
        self.was_called = True
        self.args = args
        return 0 if self.should_succeed else 1

class PymustlibTests(unittest.TestCase):
    """Тесты для библиотеки pymustlib"""
    
    def test_registry(self):
        """Тестирование реестра команд"""
        # Создаем тестовый реестр
        test_registry = registry.__class__()
        
        # Регистрируем тестовую команду
        test_registry.register("test", "Тестовая команда", lambda args: 0)
        
        # Проверяем, что команда зарегистрирована
        self.assertIn("test", test_registry.commands)
        
        # Проверяем, что можно получить команду по имени
        command = test_registry.get_command("test")
        self.assertIsNotNone(command)
        self.assertEqual(command.name, "test")
        self.assertEqual(command.description, "Тестовая команда")
        
        # Проверяем список команд
        commands = test_registry.list_commands()
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0][0], "test")
        self.assertEqual(commands[0][1], "Тестовая команда")
    
    def test_run_command(self):
        """Тестирование запуска команды"""
        # Создаем тестовый реестр
        test_registry = registry.__class__()
        
        # Создаем мок-команду
        mock_command = MockCommand("test")
        
        # Добавляем команду в реестр
        test_registry.commands["test"] = mock_command
        
        # Сохраняем оригинальный реестр
        original_registry = registry
        
        try:
            # Заменяем глобальный реестр нашим тестовым
            globals()["registry"] = test_registry
            
            # Запускаем команду
            result = run_command("test", ["arg1", "arg2"])
            
            # Проверяем результат
            self.assertEqual(result, 0)
            self.assertTrue(mock_command.was_called)
            self.assertEqual(mock_command.args, ["arg1", "arg2"])
            
            # Проверяем случай с несуществующей командой
            result = run_command("unknown", [])
            self.assertEqual(result, 1)
        
        finally:
            # Восстанавливаем оригинальный реестр
            globals()["registry"] = original_registry
    
    def test_all_commands_registered(self):
        """Проверяет, что все нужные команды зарегистрированы"""
        # Список команд, которые должны быть зарегистрированы
        required_commands = [
            "version",
            "run"
        ]
        
        # Проверяем, что все команды зарегистрированы
        for command in required_commands:
            self.assertIn(command, registry.commands, f"Команда '{command}' не зарегистрирована")

if __name__ == "__main__":
    unittest.main() 