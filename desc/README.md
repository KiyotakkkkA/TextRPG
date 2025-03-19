# Документация по формату .desc

## Введение

Формат `.desc` - это упрощенный и более читаемый способ описания игровых сущностей для TextRPG. Он был разработан для замены сложных JSON-файлов и обеспечения более удобного редактирования игрового контента.

## Основные принципы

1. Файлы `.desc` автоматически компилируются в JSON при запуске игры
2. Синтаксис похож на структуру программирования с блоками в фигурных скобках
3. Отсутствие избыточных запятых и кавычек делает файлы более компактными и читаемыми
4. Поддержка комментариев для лучшей документации кода

## Синтаксис

### Комментарии

```
# Это однострочный комментарий

// Это тоже комментарий
```

### Определение сущностей

```
ТИП_СУЩНОСТИ идентификатор {
    свойство1: значение1
    свойство2: значение2

    БЛОК {
        // Содержимое блока
    }
}
```

Поддерживаемые типы сущностей:

- `LOCATION` - игровые локации
- `ITEM` - игровые предметы
- `NPC` - неигровые персонажи

### Типы значений

1. **Строки**: могут быть с кавычками или без (если не содержат пробелов)

   ```
   name: "Лес"
   type: wilderness
   ```

2. **Числа**: целые или с плавающей точкой

   ```
   value: 15
   weight: 2.5
   ```

3. **Булевы значения**: `true` или `false`

   ```
   stackable: true
   ```

4. **Null**: `null`

   ```
   required_tool: null
   ```

5. **Массивы**: в квадратных скобках, элементы через запятую
   ```
   weather: [sunny, rainy, foggy]
   drops: ["Золотая монета", "Серебряная монета"]
   ```

### Вложенные блоки

```
LOCATION forest {
    name: "Лес"

    RESOURCES {
        RESOURCE herb {
            min_amount: 2
            max_amount: 4
        }
    }
}
```

## Специальные блоки

### Для локаций:

- `RESOURCES` - ресурсы, доступные в локации
- `CONNECTIONS` - связи с другими локациями
- `CHARACTERS` - персонажи в локации
- `PROPERTIES` - дополнительные свойства локации

### Для предметов:

- `PROPERTIES` - свойства предмета

## Пример полного файла локации

```
LOCATION forest {
    name: "Лес"
    description: "Густой лес с множеством растений и животных."
    type: wilderness
    color: green

    RESOURCES {
        RESOURCE herb {
            min_amount: 2
            max_amount: 4
            respawn_time: 120
            required_tool: null
        }
    }

    CONNECTIONS {
        CONNECTION mountains {
            id: mountains
            name: "Горы"
            condition: null
        }
    }

    CHARACTERS {
        CHARACTER hermit {
            id: hermit
            name: "Отшельник"
            description: "Старый отшельник, живущий в лесу."
        }
    }

    PROPERTIES {
        danger_level: 1
        weather: [sunny, rainy, foggy]
    }
}
```

## Пример полного файла предмета

```
ITEM healing_potion {
    name: "Зелье лечения"
    description: "Восстанавливает здоровье при использовании."
    type: consumable
    value: 50
    rarity: COMMON

    PROPERTIES {
        healing_power: 25
        effect_duration: 0
        stackable: true
        max_stack: 10
        use_time: 1.5
    }
}
```

## Работа с файлами .desc

### Компиляция файлов .desc в JSON

Файлы `.desc` автоматически компилируются в JSON при запуске игры. Вы также можете вручную скомпилировать их:

```bash
python scripts/compile_resources.py
```

Для принудительной компиляции всех файлов (даже не изменившихся):

```bash
python scripts/compile_resources.py --force
```

### Создание примера файла .desc

```bash
python scripts/compile_resources.py --create-example
```

### Преобразование существующих JSON в .desc

```bash
python scripts/json_to_desc.py input.json output.desc
```

Для преобразования всей директории:

```bash
python scripts/json_to_desc.py --dir data/resources desc
```

## Расширение формата

Формат `.desc` легко расширяется для новых типов сущностей. Добавьте новый тип сущности в класс `JsonToDescConverter` в файле `scripts/json_to_desc.py`.

```python
self.entity_types = {
    "LOCATION": ["name", "description", "type"],
    "ITEM": ["name", "description", "value", "type"],
    "NPC": ["name", "description", "level"],
    "QUEST": ["title", "description", "reward"],  # Новый тип
}
```
