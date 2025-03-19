# Формат DESC для TextRPG

DESC (Description Language) - это формат для описания игровых ресурсов в TextRPG. Он разработан для простого и удобного создания и редактирования игрового контента.

## Основные принципы

1. Синтаксис DESC основан на блоках, ключах и значениях
2. Блоки обозначаются фигурными скобками `{}`
3. Ключи и значения разделяются двоеточием `:`
4. Идентификаторы и названия блоков используются для указания типа и идентификации ресурса
5. Комментарии начинаются с символа `#` или `//`

## Типы данных

- **Строки**: заключаются в двойные кавычки `"строка"`
- **Числа**: целые и с плавающей точкой `123`, `45.67`
- **Булевы значения**: `true` или `false`
- **Null**: `null`
- **Массивы**: заключаются в квадратные скобки `["элемент1", "элемент2"]`
- **Блоки**: заключаются в фигурные скобки и могут содержать другие элементы

## Структура ресурсов

### Локации (LOCATION)

```
LOCATION location_id {
    name: "Название локации"
    description: "Описание локации"
    type: location_type
    color: "color_name"

    RESOURCES {
        RESOURCE resource_id {
            min_amount: 1
            max_amount: 3
            respawn_time: 600
            required_tool: "tool_id"
            rarity: "COMMON"
        }
        # Другие ресурсы...
    }

    CONNECTIONS {
        CONNECTION connection_id {
            id: "target_location_id"
            name: "Название соединения"
            condition: "condition_id"
            icon: "🌲"
        }
        # Другие соединения...
    }

    CHARACTERS {
        CHARACTER character_id {
            id: "character_id"
            name: "Имя персонажа"
            description: "Описание персонажа"
            dialogue: [
                "Реплика 1",
                "Реплика 2"
            ]
        }
        # Другие персонажи...
    }

    PROPERTIES {
        # Дополнительные свойства
        danger_level: 2
        ambient_sound: "sound.mp3"
        weather: ["sunny", "rainy"]
    }
}
```

### Предметы (ITEM)

```
ITEM item_id {
    name: "Название предмета"
    description: "Описание предмета"
    type: item_type
    icon: "🔪"
    value: 100
    weight: 0.5
    rarity: "UNCOMMON"
    usable: true

    PROPERTIES {
        # Дополнительные свойства
        damage: 15
        durability: 100
    }

    EFFECTS {
        EFFECT effect_id {
            type: "buff"
            stat: "strength"
            value: 5
            duration: 60
        }
        # Другие эффекты...
    }
}
```

### Персонажи (CHARACTER)

```
CHARACTER character_id {
    name: "Имя персонажа"
    description: "Описание персонажа"
    type: character_type
    icon: "👨"

    STATS {
        health: 100
        strength: 5
        agility: 6
        intelligence: 4
    }

    DIALOGUE {
        TOPIC topic_id {
            text: "О чем вы хотите поговорить?"
            responses: [
                {
                    id: "response1",
                    text: "Расскажи о себе",
                    next_topic: "about_self"
                },
                {
                    id: "response2",
                    text: "Что здесь происходит?",
                    next_topic: "whats_happening"
                }
            ]
        }
        # Другие темы диалога...
    }

    INVENTORY {
        ITEM item_id {
            id: "sword"
            quantity: 1
        }
        # Другие предметы...
    }
}
```

## Специальные значения

- **Идентификаторы**: могут содержать буквы, цифры и символ подчеркивания, начинаются с буквы или подчеркивания
- **Перечисления**: используются для типов и редкости, например `COMMON`, `UNCOMMON`, `RARE`, `EPIC`, `LEGENDARY`
- **Null**: используется для указания отсутствия значения

## Комментарии

```
# Это однострочный комментарий

/*
 * Это многострочный
 * комментарий
 */
```

## Расширение VSCode

Для удобства редактирования файлов DESC в Visual Studio Code разработано специальное расширение, которое обеспечивает подсветку синтаксиса. Установить его можно с помощью команды:

```
python pymust install-extension
```
