# Руководство по созданию материалов

Это руководство описывает процесс создания материалов и ресурсов для игры.

## Содержание

1. [Общая структура материала](#общая-структура-материала)
2. [Типы материалов](#типы-материалов)
3. [Свойства материалов](#свойства-материалов)
4. [Источники получения](#источники-получения)
5. [Использование материалов](#использование-материалов)
6. [Организация файлов](#организация-файлов)
7. [Полные примеры](#полные-примеры)

## Общая структура материала

Каждый материал определяется в JSON-файле следующей структурой:

```json
{
  "material_id": {
    "name": "Название материала",
    "description": "Описание материала",
    "type": "тип_материала",
    "rarity": "COMMON",
    "value": 10,
    "weight": 0.5,
    "stackable": true,
    "max_stack": 99,
    "properties": {
      // Дополнительные свойства материала
    },
    "sources": {
      // Источники получения материала
    },
    "uses": {
      // Возможные применения материала
    }
  }
}
```

Базовые поля для любого материала:

- **material_id** - уникальный идентификатор материала, используется в коде
- **name** - отображаемое название материала
- **description** - описание материала
- **type** - тип материала (herb, ore, essence и т.д.)
- **rarity** - редкость материала (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY)
- **value** - базовая стоимость материала
- **weight** - вес единицы материала
- **stackable** - может ли материал складываться в стопки
- **max_stack** - максимальное количество в стопке (если stackable: true)

## Типы материалов

Материалы могут быть различных типов, которые определяют их свойства и способы использования:

### Травы (herb)

Растения и грибы, используемые для алхимии и зелий.

```json
{
  "wolfbane": {
    "name": "Волчья погибель",
    "description": "Редкое растение с фиолетовыми цветами, обладает целебными свойствами.",
    "type": "herb",
    "rarity": "UNCOMMON",
    "value": 15,
    "weight": 0.1,
    "stackable": true,
    "max_stack": 50,
    "properties": {
      "healing_power": 2,
      "poison_resistance": 5
    },
    "sources": {
      "locations": ["forest", "meadow"],
      "required_skill": "herbalism",
      "required_skill_level": 3
    },
    "uses": {
      "crafting": ["healing_potion", "antidote"],
      "alchemy_exp": 5
    }
  }
}
```

### Руды и минералы (ore, mineral)

Материалы, добываемые в шахтах и пещерах.

```json
{
  "iron_ore": {
    "name": "Железная руда",
    "description": "Кусок породы, содержащий железо.",
    "type": "ore",
    "rarity": "COMMON",
    "value": 20,
    "weight": 2.0,
    "stackable": true,
    "max_stack": 20,
    "properties": {
      "purity": 0.7,
      "hardness": 6
    },
    "sources": {
      "locations": ["mountains", "cave"],
      "required_skill": "mining",
      "required_skill_level": 5
    },
    "uses": {
      "smelting": ["iron_ingot"],
      "crafting": ["crude_weapon"],
      "mining_exp": 10
    }
  }
}
```

### Эссенции (essence)

Магические материалы, используемые для зачарования и создания артефактов.

```json
{
  "air_essence": {
    "name": "Воздушная эссенция",
    "description": "Кристаллизованная энергия воздуха.",
    "type": "essence",
    "rarity": "RARE",
    "value": 50,
    "weight": 0.1,
    "stackable": true,
    "max_stack": 10,
    "properties": {
      "magic_power": 10,
      "element": "air",
      "stability": 0.8
    },
    "sources": {
      "locations": ["forest", "mountains"],
      "monster_drops": ["air_elemental"],
      "required_skill": "elementalism",
      "required_skill_level": 10
    },
    "uses": {
      "enchanting": ["wind_enchant", "speed_enchant"],
      "crafting": ["air_talisman", "wind_staff"],
      "magic_exp": 20
    }
  }
}
```

### Обработанные материалы (processed)

Материалы, полученные после обработки сырья.

```json
{
  "iron_ingot": {
    "name": "Железный слиток",
    "description": "Очищенное железо, готовое для создания предметов.",
    "type": "processed",
    "rarity": "COMMON",
    "value": 30,
    "weight": 1.0,
    "stackable": true,
    "max_stack": 20,
    "properties": {
      "quality": 1.0,
      "durability": 30
    },
    "sources": {
      "crafting": {
        "recipe": "smelting_iron_ore",
        "ingredients": {
          "iron_ore": 2,
          "coal": 1
        }
      }
    },
    "uses": {
      "crafting": ["iron_sword", "iron_armor", "tools"]
    }
  }
}
```

## Свойства материалов

Материалы могут иметь различные свойства, которые влияют на их использование:

- **healing_power** - целебная сила (для трав)
- **poison_resistance** - сопротивление яду (для трав)
- **purity** - чистота руды (для руд)
- **hardness** - твердость материала (для руд и минералов)
- **magic_power** - магическая сила (для эссенций)
- **element** - стихийный элемент (для эссенций)
- **quality** - качество материала (для обработанных материалов)
- **durability** - прочность материала (для обработанных материалов)

## Источники получения

Материалы могут быть получены из различных источников:

- **locations** - локации, где можно найти материал
- **monster_drops** - монстры, которые могут дропнуть материал
- **required_skill** - навык, необходимый для сбора материала
- **required_skill_level** - уровень навыка, необходимый для сбора
- **crafting** - рецепт для создания материала из других ингредиентов

## Использование материалов

Материалы могут иметь различные применения:

- **crafting** - предметы, которые можно создать из материала
- **alchemy_exp** - опыт алхимии, получаемый при использовании материала
- **mining_exp** - опыт горного дела, получаемый при добыче материала
- **magic_exp** - опыт магии, получаемый при использовании материала
- **enchanting** - зачарования, для которых можно использовать материал
- **cooking** - блюда, которые можно приготовить из материала

## Организация файлов

Материалы могут быть организованы в JSON-файлах несколькими способами:

1. **По типу материала** - организация материалов по их типу:

   - `herbs.json` - травы и растения
   - `ores.json` - руды и минералы
   - `essences.json` - магические эссенции
   - `processed_materials.json` - обработанные материалы

2. **По источнику** - организация материалов по источнику их получения:

   - `forest_materials.json` - материалы из леса
   - `mountain_materials.json` - материалы из гор
   - `crafted_materials.json` - созданные материалы

3. **По редкости** - организация материалов по их редкости:
   - `common_materials.json` - обычные материалы
   - `rare_materials.json` - редкие материалы
   - `legendary_materials.json` - легендарные материалы

Файлы материалов могут размещаться как в корневой директории `resources/materials/`, так и в подпапках для лучшей организации: `resources/materials/type/file.json`.

## Полные примеры

### Трава - Зверобой

```json
{
  "beast_plant": {
    "name": "Зверобой",
    "description": "Растение с яркими желтыми цветами, известное своими лечебными свойствами.",
    "type": "herb",
    "rarity": "UNCOMMON",
    "value": 25,
    "weight": 0.1,
    "stackable": true,
    "max_stack": 50,
    "properties": {
      "healing_power": 3,
      "stamina_boost": 5
    },
    "sources": {
      "locations": ["forest", "meadow"],
      "required_skill": "herbalism",
      "required_skill_level": 5,
      "seasons": ["summer", "autumn"]
    },
    "uses": {
      "crafting": ["strong_healing_potion", "stamina_elixir"],
      "cooking": ["herbal_tea"],
      "alchemy_exp": 10
    }
  }
}
```

### Руда - Медная руда

```json
{
  "copper_ore": {
    "name": "Медная руда",
    "description": "Зеленоватый камень с прожилками меди.",
    "type": "ore",
    "rarity": "COMMON",
    "value": 15,
    "weight": 1.5,
    "stackable": true,
    "max_stack": 20,
    "properties": {
      "purity": 0.6,
      "hardness": 4
    },
    "sources": {
      "locations": ["mountains", "cave"],
      "required_skill": "mining",
      "required_skill_level": 1
    },
    "uses": {
      "smelting": ["copper_ingot"],
      "crafting": ["copper_wire", "crude_jewelry"],
      "mining_exp": 5
    }
  }
}
```

### Эссенция - Кристалл маны

```json
{
  "mana_crystal": {
    "name": "Кристалл маны",
    "description": "Кристалл, содержащий чистую магическую энергию.",
    "type": "essence",
    "rarity": "EPIC",
    "value": 200,
    "weight": 0.2,
    "stackable": true,
    "max_stack": 5,
    "properties": {
      "magic_power": 50,
      "stability": 0.9,
      "purity": 0.95
    },
    "sources": {
      "locations": ["ancient_ruins", "magic_cave"],
      "monster_drops": {
        "crystal_golem": { "chance": 0.1, "min": 1, "max": 1 },
        "arcane_elemental": { "chance": 0.3, "min": 1, "max": 2 }
      },
      "required_skill": "elementalism",
      "required_skill_level": 20
    },
    "uses": {
      "enchanting": ["mana_regeneration", "spell_power_boost"],
      "crafting": ["staff_of_power", "arcane_focus", "mana_potion"],
      "magic_exp": 100
    }
  }
}
```

Эти примеры демонстрируют структуру материалов для разных типов и показывают, как определять их свойства, источники получения и возможные применения. При создании новых материалов важно учитывать баланс игры и интеграцию с другими системами, такими как крафтинг, зачарование и навыки.
