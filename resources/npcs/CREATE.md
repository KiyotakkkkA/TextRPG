# Руководство по созданию NPC

Это руководство описывает процесс создания NPC (неигровых персонажей) для игры.

## Содержание

1. [Общая структура NPC](#общая-структура-npc)
2. [Типы NPC](#типы-npc)
   - [Диалоговый NPC](#диалоговый-npc)
   - [Квестовый NPC](#квестовый-npc)
   - [Торговец](#торговец)
3. [Структура диалогов](#структура-диалогов)
4. [Организация файлов](#организация-файлов)
5. [Полные примеры](#полные-примеры)

## Общая структура NPC

Каждый NPC определяется в JSON-файле следующей структурой:

```json
{
  "npc_id": {
    "name": "Имя NPC",
    "description": "Описание NPC",
    "type": "тип_npc", // "dialogue" (по умолчанию), "quest" или "trader"
    "dialogues": {
      // структура диалогов
    }
    // дополнительные поля в зависимости от типа NPC
  }
}
```

Базовые поля для любого NPC:

- **npc_id** - уникальный идентификатор NPC, используется в коде
- **name** - отображаемое имя NPC
- **description** - краткое описание NPC
- **type** - тип NPC: "dialogue" (обычный диалоговый NPC), "quest" (квестовый NPC) или "trader" (торговец)
- **dialogues** - структура диалогов NPC

## Типы NPC

### Диалоговый NPC

Диалоговый NPC (тип "dialogue") используется для предоставления информации игроку через диалоги. Они не выдают квестов и не торгуют.

Дополнительные поля для диалогового NPC:

- **topics** - темы для разговора (опционально)

Пример:

```json
{
  "forest_hermit": {
    "name": "Отшельник Эрмин",
    "description": "Старый отшельник, живущий в лесу много лет.",
    "type": "dialogue",
    "location_id": "forest",
    "topics": {
      "forest_history": {
        "name": "История леса",
        "dialogue_id": "forest_history"
      },
      "magic_essence": {
        "name": "Магические эссенции",
        "dialogue_id": "magic_essence"
      }
    },
    "dialogues": {
      // структура диалогов (описана в разделе "Структура диалогов")
    }
  }
}
```

### Квестовый NPC

Квестовый NPC (тип "quest") может выдавать и принимать квесты.

Дополнительные поля для квестового NPC:

- **available_quests** - список ID квестов, которые может выдать NPC

Пример:

```json
{
  "village_elder": {
    "name": "Старейшина деревни",
    "description": "Мудрый старец, который руководит деревней много лет.",
    "type": "quest",
    "available_quests": ["collect_herbs", "wolves_threat", "missing_child"],
    "dialogues": {
      // структура диалогов с опциями для начала квестов
    }
  }
}
```

### Торговец

Торговец (тип "trader") может покупать и продавать предметы.

Дополнительные поля для торговца:

- **trade_exp** - количество опыта, получаемого за торговлю (по умолчанию 1)
- **buys** - словарь предметов, которые торговец покупает: `{"item_id": price_modifier}`
- **sells** - словарь предметов, которые торговец продает: `{"item_id": {"price": цена, "count": количество}}`

Пример:

```json
{
  "herb_trader": {
    "name": "Травник Миран",
    "description": "Старый травник, который знает все о растениях.",
    "type": "trader",
    "trade_exp": 1,
    "buys": {
      "mushroom": 1,
      "wolfbane": 1,
      "beast_plant": 2
    },
    "sells": {
      "mushroom": {
        "price": 10,
        "count": 5
      },
      "wolfbane": {
        "price": 10,
        "count": 5
      }
    },
    "dialogues": {
      // структура диалогов с опциями для торговли
    }
  }
}
```

## Структура диалогов

Диалоги имеют следующую структуру:

```json
"dialogues": {
  "dialogue_id": {
    "text": "Текст диалога",
    "options": [
      {
        "text": "Текст ответа/вопроса игрока",
        "next_id": "следующий_dialogue_id",  // ID следующего диалога
        "action": "действие",  // опциональное действие
        "condition": "условие" // опциональное условие
      },
      // Другие варианты ответов...
    ]
  },
  // Другие диалоги...
}
```

Основные компоненты:

- **dialogue_id** - уникальный идентификатор диалога
- **text** - текст, произносимый NPC
- **options** - список вариантов ответа, доступных игроку:
  - **text** - текст варианта ответа
  - **next_id** - ID следующего диалога после выбора этого варианта
  - **action** - действие, которое произойдет при выборе (опционально):
    - `"exit"` - выход из диалога
    - `"trade"` - начать торговлю (для торговцев)
    - `"start_quest_QUESTID"` - начать квест с указанным ID (для квестовых NPC)
  - **condition** - условие, при котором вариант ответа будет доступен (опционально):
    - `"quest_available_QUESTID"` - квест с указанным ID доступен
    - `"quest_completed_QUESTID"` - квест с указанным ID выполнен
    - `"skill_SKILLID_LEVEL"` - требуется навык с указанным ID определенного уровня (например, `"skill_ancient_language_3"`)
    - `"item_ITEMID"` - требуется наличие предмета с указанным ID в инвентаре
    - `"npc_known_NPCID"` - требуется знакомство с NPC (NPC должен быть в глоссарии игрока)
    - `"location_visited_LOCATIONID"` - требуется посещение определенной локации
    - `"monster_defeated_MONSTERID"` - требуется победа над определенным монстром

### Визуальное отображение условных опций

В игровом интерфейсе условные опции диалога отображаются со специальными метками слева от текста, показывающими тип требования:

- Требование навыка: `[🧠 Древний язык: 3]` (с уровнем навыка)
- Требование предмета: `[📦 Древний ключ]` (с названием предмета)
- Требование знакомства с NPC: `[👤 Знание о: Старейшина]`
- Требование посещения локации: `[🗺️ Посещено: Древние руины]`
- Требование победы над монстром: `[⚔️ Побеждено: Древний страж]`

Опции, условия которых не выполнены, могут отображаться серым цветом или быть недоступны для выбора, в зависимости от настроек интерфейса.

### Примеры использования условий в диалогах

```json
{
  "npc_dialogue": {
    "text": "Что ты хочешь узнать?",
    "options": [
      {
        "text": "Расскажи о древних рунах",
        "next_id": "ancient_runes_dialogue",
        "condition": "skill_ancient_language_2"
      },
      {
        "text": "Могу ли я войти в храм?",
        "next_id": "temple_access",
        "condition": "item_temple_key"
      },
      {
        "text": "Я слышал о старейшине...",
        "next_id": "elder_dialogue",
        "condition": "npc_known_village_elder"
      }
    ]
  }
}
```

У любого NPC должен быть как минимум диалог с ID "greeting", который используется для начального приветствия.

## Организация файлов

NPC могут быть организованы в JSON-файлах несколькими способами:

1. **По типу** - можно создать отдельные файлы для каждого типа NPC:

   - `dialogue_npcs.json` - для диалоговых NPC
   - `quest_npcs.json` - для квестовых NPC
   - `traders.json` - для торговцев

2. **По региону/локации** - можно организовать NPC по регионам или локациям:

   - `forest_npcs.json` - NPC в лесу
   - `village_npcs.json` - NPC в деревне
   - `city_npcs.json` - NPC в городе

3. **По отдельности** - каждый NPC в отдельном файле (удобно для крупных NPC с большими диалогами)

Файлы NPC могут размещаться как в корневой директории `resources/npcs/`, так и в подпапках для лучшей организации: `resources/npcs/regionName/file.json`.

## Полные примеры

### Диалоговый NPC - Лесной отшельник

```json
{
  "forest_hermit": {
    "name": "Отшельник Эрмин",
    "description": "Старый отшельник, живущий в лесу много лет.",
    "type": "dialogue",
    "topics": {
      "forest_history": {
        "name": "История леса",
        "dialogue_id": "forest_history"
      },
      "magic_essence": {
        "name": "Магические эссенции",
        "dialogue_id": "magic_essence"
      }
    },
    "dialogues": {
      "greeting": {
        "text": "Приветствую тебя, искатель знаний. Мало кто забредает в эту часть леса.",
        "options": [
          {
            "text": "Хочу узнать об истории леса",
            "next_id": "forest_history"
          },
          {
            "text": "Что ты знаешь о магических эссенциях?",
            "next_id": "magic_essence"
          },
          {
            "text": "До свидания",
            "action": "exit"
          }
        ]
      },
      "forest_history": {
        "text": "Этот лес существует с незапамятных времен. В древности его населяли эльфы, которые жили в гармонии с природой. Но они исчезли после Великой Катастрофы тысячу лет назад.",
        "options": [
          {
            "text": "Что еще ты можешь рассказать?",
            "next_id": "greeting"
          }
        ]
      },
      "magic_essence": {
        "text": "Магические эссенции - это концентрированная магия стихий. Воздушная эссенция, которую можно найти в этом лесу, является самой простой для сбора.",
        "options": [
          {
            "text": "Что еще ты можешь рассказать?",
            "next_id": "greeting"
          }
        ]
      }
    }
  }
}
```

### Квестовый NPC - Старейшина деревни

```json
{
  "village_elder": {
    "name": "Старейшина деревни",
    "description": "Мудрый старец, который руководит деревней много лет.",
    "type": "quest",
    "available_quests": ["collect_herbs", "wolves_threat", "missing_child"],
    "dialogues": {
      "greeting": {
        "text": "Приветствую тебя, путешественник. Наша деревня нуждается в помощи.",
        "options": [
          {
            "text": "Чем я могу помочь?",
            "next_id": "help_options"
          },
          {
            "text": "Расскажи о деревне",
            "next_id": "about_village"
          },
          {
            "text": "До свидания",
            "action": "exit"
          }
        ]
      },
      "help_options": {
        "text": "У нас несколько проблем, с которыми ты мог бы помочь.",
        "options": [
          {
            "text": "Нужны травы для лекаря",
            "action": "start_quest_collect_herbs",
            "condition": "quest_available_collect_herbs"
          },
          {
            "text": "Проблема с волками",
            "action": "start_quest_wolves_threat",
            "condition": "quest_available_wolves_threat"
          },
          {
            "text": "Пропавший ребёнок",
            "action": "start_quest_missing_child",
            "condition": "quest_available_missing_child"
          },
          {
            "text": "Вернуться",
            "next_id": "greeting"
          }
        ]
      },
      "about_village": {
        "text": "Наша деревня основана более 200 лет назад. Мы живем в гармонии с лесом и занимаемся в основном земледелием и охотой.",
        "options": [
          {
            "text": "Вернуться",
            "next_id": "greeting"
          }
        ]
      }
    }
  }
}
```

### Торговец - Травник

```json
{
  "herb_trader": {
    "name": "Травник Миран",
    "description": "Старый травник, который знает все о растениях.",
    "type": "trader",
    "trade_exp": 1,
    "buys": {
      "mushroom": 1,
      "wolfbane": 1,
      "beast_plant": 2
    },
    "sells": {
      "mushroom": {
        "price": 10,
        "count": 5
      },
      "wolfbane": {
        "price": 10,
        "count": 5
      }
    },
    "dialogues": {
      "greeting": {
        "text": "Здравствуй, путник! Заинтересован в моих товарах?",
        "options": [
          {
            "text": "Что ты покупаешь?",
            "next_id": "buy_info"
          },
          {
            "text": "Что ты продаешь?",
            "next_id": "sell_info"
          },
          {
            "text": "Давай торговать",
            "action": "trade"
          },
          {
            "text": "До свидания",
            "action": "exit"
          }
        ]
      },
      "buy_info": {
        "text": "Я покупаю любые травы и грибы, особенно интересуюсь редкими растениями.",
        "options": [
          {
            "text": "Вернуться",
            "next_id": "greeting"
          }
        ]
      },
      "sell_info": {
        "text": "У меня есть лечебные зелья и растения.",
        "options": [
          {
            "text": "Вернуться",
            "next_id": "greeting"
          }
        ]
      }
    }
  }
}
```

### Уникальный NPC - Странная статуя

```json
{
  "suspicious_statue": {
    "name": "Странная статуя",
    "description": "Странная статуя, которую вы встретили в руинах.",
    "type": "quest",
    "location_id": "ancient_ruins",
    "dialogues": {
      "greeting": {
        "text": "<Статуя, которая, кажется, внимательно наблюдает за вами>",
        "options": [
          {
            "text": "Подойти ближе и осмотреть",
            "next_id": "examine_statue"
          },
          {
            "text": "Уйти",
            "action": "exit"
          }
        ]
      },
      "examine_statue": {
        "text": "Когда вы подходите ближе, вам кажется, что глаза статуи следят за вами. На статуе есть древние руны.",
        "options": [
          {
            "text": "Прочитать руны",
            "next_id": "read_runes",
            "condition": "skill_ancient_language_3"
          },
          {
            "text": "Попытаться активировать статую",
            "next_id": "activate_statue",
            "condition": "item_ancient_key"
          },
          {
            "text": "Вспомнить рассказ старейшины об этих руинах",
            "next_id": "recall_elder_knowledge",
            "condition": "npc_known_village_elder"
          },
          {
            "text": "Я не могу разобрать эти символы",
            "next_id": "cannot_read"
          },
          {
            "text": "Отойти от статуи",
            "action": "exit"
          }
        ]
      },
      "read_runes": {
        "text": "Благодаря вашим знаниям древнего языка, вы можете прочитать надпись: 'Страж врат, защитник тайн, пробудись от голоса древней крови'.",
        "options": [
          {
            "text": "Произнести фразу на древнем языке",
            "next_id": "speak_ancient_phrase",
            "condition": "skill_ancient_language_5"
          },
          {
            "text": "Вернуться назад",
            "next_id": "examine_statue"
          }
        ]
      },
      "activate_statue": {
        "text": "Вы вставляете древний ключ в скрытое отверстие в основании статуи. Глаза статуи начинают светиться голубым светом, и вы слышите механический звук открывающегося тайного прохода позади статуи.",
        "options": [
          {
            "text": "Исследовать тайный проход",
            "next_id": "secret_passage"
          },
          {
            "text": "Вернуться назад",
            "next_id": "examine_statue"
          }
        ]
      },
      "recall_elder_knowledge": {
        "text": "Вы вспоминаете, что старейшина деревни рассказывал об этой статуе. По его словам, она была создана древней цивилизацией для охраны входа в подземное хранилище знаний.",
        "options": [
          {
            "text": "Поискать механизм, о котором говорил старейшина",
            "next_id": "search_mechanism"
          },
          {
            "text": "Вернуться назад",
            "next_id": "examine_statue"
          }
        ]
      },
      "cannot_read": {
        "text": "Символы выглядят совершенно непонятными. Возможно, если бы вы изучили древние языки, вы смогли бы их расшифровать.",
        "options": [
          {
            "text": "Вернуться назад",
            "next_id": "examine_statue"
          }
        ]
      }
    }
  }
}
```
