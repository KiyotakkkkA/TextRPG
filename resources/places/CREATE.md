# Руководство по созданию локаций

Это руководство описывает процесс создания локаций (мест) для игры.

## Содержание

1. [Общая структура файла локаций](#общая-структура-файла-локаций)
2. [Структура локации](#структура-локации)
3. [Связи между локациями](#связи-между-локациями)
4. [Ресурсы и монстры в локациях](#ресурсы-и-монстры-в-локациях)
5. [Организация файлов](#организация-файлов)
6. [Полные примеры](#полные-примеры)

## Общая структура файла локаций

Файлы локаций обычно содержат два основных раздела: список локаций и их связи между собой.

```json
{
  "locations": [
    // Массив объектов локаций
  ],
  "connections": [
    // Массив связей между локациями
  ]
}
```

## Структура локации

Каждая локация имеет следующую структуру:

```json
{
  "id": "location_id",
  "name": "Название локации",
  "description": "Описание локации",
  "resources": {
    // Ресурсы, доступные в локации
  },
  "monsters": {
    // Монстры, обитающие в локации
  }
  // Дополнительные свойства локации
}
```

Базовые поля для любой локации:

- **id** - уникальный идентификатор локации, используется в коде
- **name** - отображаемое название локации
- **description** - описание локации, которое видит игрок

Дополнительные поля для локаций:

- **resources** - словарь ресурсов, которые можно собирать в локации
- **monsters** - словарь монстров, которые обитают в локации
- **is_safe** - флаг, указывающий, является ли локация безопасной (нет монстров)
- **required_level** - минимальный уровень персонажа для посещения локации
- **required_quest** - ID квеста, который должен быть выполнен для доступа
- **required_item** - ID предмета, который должен быть у игрока для доступа
- **background** - путь к файлу фонового изображения для локации
- **effects** - особые эффекты, действующие на игрока в этой локации

## Связи между локациями

Связи определяют, как локации соединяются между собой. Игрок может перемещаться только между соединенными локациями.

```json
{
  "from": "location_id_1",
  "to": "location_id_2",
  "bidirectional": true,
  "required_level": 5,
  "required_quest": "quest_id",
  "required_item": "item_id",
  "path_name": "Через горный перевал"
}
```

Поля для связей:

- **from** - ID локации, откуда начинается путь
- **to** - ID локации, куда ведет путь
- **bidirectional** - флаг, указывающий, можно ли идти в обоих направлениях (по умолчанию true)
- **required_level** - минимальный уровень персонажа для прохода
- **required_quest** - ID квеста, который должен быть выполнен для прохода
- **required_item** - ID предмета, который должен быть у игрока для прохода
- **path_name** - название пути, отображаемое игроку (опционально)

## Ресурсы и монстры в локациях

Ресурсы и монстры в локациях определяются следующим образом:

### Ресурсы

```json
"resources": {
  "resource_id": {
    "max_count": 10,
    "respawn_time": 60
  },
  // Другие ресурсы
}
```

Поля для ресурсов:

- **resource_id** - ID ресурса
- **max_count** - максимальное количество ресурса, доступное в локации
- **respawn_time** - время в секундах, через которое ресурс восстанавливается

### Монстры

```json
"monsters": {
  "monster_id": {
    "max_count": 5,
    "respawn_time": 180
  },
  // Другие монстры
}
```

Поля для монстров:

- **monster_id** - ID монстра
- **max_count** - максимальное количество монстров в локации
- **respawn_time** - время в секундах, через которое монстры появляются заново

## Организация файлов

Локации могут быть организованы в JSON-файлах несколькими способами:

1. **Основной файл** - все локации и их связи могут быть определены в одном файле `main.json`:

```
resources/places/main.json
```

2. **По регионам** - локации могут быть организованы по регионам в отдельных файлах:

```
resources/places/Eldaria/forest_region.json
resources/places/Eldaria/mountain_region.json
resources/places/DarkLands/caves.json
```

Для больших игровых миров рекомендуется организация по регионам, где каждый регион содержит свой набор связанных локаций.

## Полные примеры

### Пример основного файла локаций

```json
{
  "locations": [
    {
      "id": "forest",
      "name": "Лес",
      "description": "Густой лес с множеством растений и животных.",
      "resources": {
        "mushroom": { "max_count": 10, "respawn_time": 60 },
        "wolfbane": { "max_count": 5, "respawn_time": 120 },
        "air_essence": { "max_count": 3, "respawn_time": 180 },
        "beast_plant": { "max_count": 4, "respawn_time": 180 }
      },
      "monsters": {
        "forest_wolf": { "max_count": 5, "respawn_time": 180 }
      }
    },
    {
      "id": "mountains",
      "name": "Горы",
      "description": "Высокие горы с пещерами и залежами руд.",
      "resources": {
        "iron_ore": { "max_count": 8, "respawn_time": 180 },
        "copper_ore": { "max_count": 12, "respawn_time": 120 }
      }
    },
    {
      "id": "village",
      "name": "Деревня",
      "description": "Маленькая деревня с жителями и магазином.",
      "is_safe": true
    }
  ],
  "connections": [
    {
      "from": "forest",
      "to": "mountains",
      "bidirectional": true
    },
    {
      "from": "village",
      "to": "forest",
      "bidirectional": true
    },
    {
      "from": "village",
      "to": "mountains",
      "bidirectional": true
    }
  ]
}
```

### Пример файла локаций с дополнительными условиями

```json
{
  "locations": [
    {
      "id": "ancient_ruins",
      "name": "Древние руины",
      "description": "Руины древней цивилизации, полные опасностей и сокровищ.",
      "required_level": 10,
      "required_quest": "find_ruins_map",
      "monsters": {
        "skeleton": { "max_count": 8, "respawn_time": 120 },
        "ancient_guardian": { "max_count": 1, "respawn_time": 600 }
      },
      "resources": {
        "ancient_fragment": { "max_count": 5, "respawn_time": 300 }
      },
      "effects": {
        "magic_amplification": {
          "description": "Усиливает магические способности",
          "stat_boost": {
            "magic": 10
          }
        }
      }
    },
    {
      "id": "hidden_temple",
      "name": "Скрытый храм",
      "description": "Древний храм, скрытый глубоко в руинах.",
      "required_item": "temple_key",
      "is_safe": true
    }
  ],
  "connections": [
    {
      "from": "forest",
      "to": "ancient_ruins",
      "bidirectional": true
    },
    {
      "from": "ancient_ruins",
      "to": "hidden_temple",
      "required_item": "temple_key"
    }
  ]
}
```

Эти примеры показывают, как можно организовать локации, их ресурсы, монстров и связи между ними для создания интересного и последовательного игрового мира.
