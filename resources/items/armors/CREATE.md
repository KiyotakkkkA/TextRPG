# Руководство по созданию доспехов и экипировки

Это руководство описывает процесс создания доспехов и экипировки для игры.

## Содержание

1. [Общая структура предмета экипировки](#общая-структура-предмета-экипировки)
2. [Типы слотов экипировки](#типы-слотов-экипировки)
3. [Характеристики доспехов](#характеристики-доспехов)
4. [Редкость и качество](#редкость-и-качество)
5. [Особые эффекты и свойства](#особые-эффекты-и-свойства)
6. [Требования для надевания](#требования-для-надевания)
7. [Организация файлов](#организация-файлов)
8. [Полные примеры](#полные-примеры)

## Общая структура предмета экипировки

Каждый предмет экипировки определяется в JSON-файле следующей структурой:

```json
{
  "item_id": {
    "name": "Название предмета",
    "description": "Описание предмета",
    "type": "armor",
    "slot": "тип_слота",
    "rarity": "COMMON",
    "level": 1,
    "characteristics": {
      "defense": 5,
      "weight": 2.0,
      "durability": 100
      // Другие характеристики
    },
    "requirements": {
      // Требования для надевания
    },
    "effects": {
      // Особые эффекты
    },
    "materials": {
      // Материалы для создания
    },
    "visual": {
      // Визуальное отображение
    }
  }
}
```

Базовые поля для любого предмета экипировки:

- **item_id** - уникальный идентификатор предмета, используется в коде
- **name** - отображаемое название предмета
- **description** - описание предмета
- **type** - тип предмета ("armor", "weapon", "accessory" и т.д.)
- **slot** - слот, в который экипируется предмет
- **rarity** - редкость предмета (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHIC)
- **level** - уровень предмета, влияет на его характеристики

## Типы слотов экипировки

Предметы экипировки размещаются в определенных слотах на персонаже:

- **head** - голова (шлемы, короны и т.д.)
- **body** - тело (нагрудные доспехи, робы и т.д.)
- **legs** - ноги (поножи, набедренники и т.д.)
- **feet** - ступни (сапоги, ботинки и т.д.)
- **hands** - руки (перчатки, рукавицы и т.д.)
- **weapon** - оружие (мечи, посохи, луки и т.д.)
- **offhand** - левая рука (щиты, книги, жезлы и т.д.)
- **accessory1** - аксессуар 1 (кольца, ожерелья, амулеты и т.д.)
- **accessory2** - аксессуар 2 (дополнительный слот для аксессуаров)

## Характеристики доспехов

Доспехи могут иметь различные характеристики, влияющие на персонажа:

- **defense** - защита от физического урона
- **magic_resist** - защита от магического урона
- **weight** - вес предмета, влияет на скорость и маневренность
- **durability** - прочность предмета, определяет сколько использований до ремонта
- **health_bonus** - бонус к максимальному здоровью
- **stamina_bonus** - бонус к максимальной выносливости
- **mana_bonus** - бонус к максимальной мане
- **attack_bonus** - бонус к силе атаки
- **magic_bonus** - бонус к силе магии
- **speed_bonus** - бонус к скорости передвижения

Оружие имеет следующие дополнительные характеристики:

- **damage** - базовый урон
- **damage_type** - тип урона (physical, magic, fire, ice и т.д.)
- **attack_speed** - скорость атаки
- **critical_chance** - шанс критического удара
- **critical_multiplier** - множитель критического урона
- **range** - дальность атаки

## Редкость и качество

Предметы экипировки имеют разную редкость, которая влияет на их характеристики:

- **COMMON** (обычный) - базовые характеристики
- **UNCOMMON** (необычный) - улучшенные характеристики, может иметь 1 особый эффект
- **RARE** (редкий) - значительно улучшенные характеристики, 1-2 особых эффекта
- **EPIC** (эпический) - высокие характеристики, 2-3 особых эффекта
- **LEGENDARY** (легендарный) - очень высокие характеристики, 3-4 особых эффекта, уникальные свойства
- **MYTHIC** (мифический) - исключительные характеристики, 4-5 особых эффектов, уникальные свойства

Цветовая кодировка редкости для отображения в интерфейсе:

- **COMMON** - белый
- **UNCOMMON** - зеленый
- **RARE** - синий
- **EPIC** - фиолетовый
- **LEGENDARY** - оранжевый
- **MYTHIC** - красный или золотой

## Особые эффекты и свойства

Предметы экипировки могут иметь особые эффекты и свойства:

```json
"effects": {
  "passive": {
    "fire_resistance": 20,
    "poison_immunity": true
  },
  "on_hit": {
    "fire_damage": {
      "damage": 5,
      "chance": 0.2
    }
  },
  "on_kill": {
    "health_restore": {
      "amount": 10,
      "chance": 0.3
    }
  },
  "set_bonus": {
    "set_id": "dragon_armor",
    "bonuses": [
      {
        "pieces": 2,
        "effects": {
          "fire_resistance": 30
        }
      },
      {
        "pieces": 4,
        "effects": {
          "fire_damage_aura": {
            "damage": 10,
            "radius": 3
          }
        }
      }
    ]
  }
}
```

Типы эффектов:

- **passive** - постоянные эффекты при ношении предмета
- **on_hit** - эффекты, срабатывающие при нанесении удара противнику
- **on_kill** - эффекты, срабатывающие при убийстве противника
- **set_bonus** - бонусы за ношение нескольких предметов из одного набора

## Требования для надевания

Предметы экипировки могут иметь требования, которые должны быть выполнены для их использования:

```json
"requirements": {
  "level": 10,
  "strength": 15,
  "dexterity": 0,
  "intelligence": 0,
  "skills": {
    "heavy_armor": 3
  },
  "quests": ["dragon_slayer"]
}
```

Типы требований:

- **level** - минимальный уровень персонажа
- **strength**, **dexterity**, **intelligence** - минимальные значения характеристик
- **skills** - требуемые навыки и их уровни
- **quests** - квесты, которые должны быть выполнены

## Организация файлов

Предметы экипировки могут быть организованы в JSON-файлах несколькими способами:

1. **По типу слота** - организация предметов по слоту экипировки:

   - `head_armor.json` - шлемы, короны и т.д.
   - `body_armor.json` - нагрудные доспехи, робы и т.д.
   - `weapons.json` - оружие
   - `accessories.json` - кольца, амулеты и т.д.

2. **По набору** - организация предметов по комплектам:

   - `iron_set.json` - железный комплект доспехов
   - `dragon_set.json` - драконий комплект доспехов
   - `mage_set.json` - комплект мага

3. **По редкости** - организация предметов по редкости:
   - `common_items.json` - обычные предметы
   - `rare_items.json` - редкие предметы
   - `legendary_items.json` - легендарные предметы

Файлы экипировки могут размещаться как в корневой директории `resources/armors/` или `resources/weapons/`, так и в подпапках для лучшей организации: `resources/armors/sets/dragon_set.json`.

## Полные примеры

### Шлем - Железный шлем

```json
{
  "iron_helmet": {
    "name": "Железный шлем",
    "description": "Простой железный шлем, обеспечивающий базовую защиту.",
    "type": "armor",
    "slot": "head",
    "rarity": "COMMON",
    "level": 5,
    "characteristics": {
      "defense": 5,
      "weight": 2.0,
      "durability": 100
    },
    "requirements": {
      "level": 5,
      "strength": 8
    },
    "effects": {
      "passive": {
        "physical_resistance": 5
      }
    },
    "materials": {
      "iron_ingot": 3,
      "leather": 1
    },
    "visual": {
      "model": "models/armors/iron_helmet.obj",
      "icon": "icons/armors/iron_helmet.png"
    }
  }
}
```

### Нагрудный доспех - Драконья броня

```json
{
  "dragon_chestplate": {
    "name": "Драконья броня",
    "description": "Нагрудный доспех, выкованный из чешуи древнего дракона. Сохраняет тепло владельца и защищает от огня.",
    "type": "armor",
    "slot": "body",
    "rarity": "LEGENDARY",
    "level": 30,
    "characteristics": {
      "defense": 25,
      "magic_resist": 15,
      "weight": 8.0,
      "durability": 500,
      "health_bonus": 50
    },
    "requirements": {
      "level": 30,
      "strength": 25,
      "quests": ["dragon_slayer"]
    },
    "effects": {
      "passive": {
        "fire_resistance": 50,
        "fire_immunity": true
      },
      "on_hit": {
        "fire_reflect": {
          "damage": 10,
          "chance": 0.3
        }
      },
      "set_bonus": {
        "set_id": "dragon_armor",
        "bonuses": [
          {
            "pieces": 2,
            "effects": {
              "fire_resistance": 75
            }
          },
          {
            "pieces": 4,
            "effects": {
              "fire_breath": {
                "damage": 50,
                "cooldown": 60,
                "range": 5
              }
            }
          }
        ]
      }
    },
    "materials": {
      "dragon_scale": 10,
      "fire_essence": 5,
      "star_metal_ingot": 3
    },
    "visual": {
      "model": "models/armors/dragon_chestplate.obj",
      "icon": "icons/armors/dragon_chestplate.png",
      "effects": {
        "glow": {
          "color": "#FF4500",
          "intensity": 0.5
        }
      }
    }
  }
}
```

### Оружие - Клинок бури

```json
{
  "storm_blade": {
    "name": "Клинок бури",
    "description": "Древний магический меч, наполненный энергией молний и ветра.",
    "type": "weapon",
    "slot": "weapon",
    "rarity": "EPIC",
    "level": 25,
    "characteristics": {
      "damage": 35,
      "damage_type": "lightning",
      "attack_speed": 1.2,
      "critical_chance": 15,
      "critical_multiplier": 2.5,
      "weight": 3.5,
      "durability": 300
    },
    "requirements": {
      "level": 25,
      "strength": 15,
      "dexterity": 20,
      "skills": {
        "swordsmanship": 5
      }
    },
    "effects": {
      "passive": {
        "lightning_damage_bonus": 20,
        "movement_speed": 10
      },
      "on_hit": {
        "chain_lightning": {
          "damage": 15,
          "targets": 3,
          "chance": 0.2,
          "cooldown": 10
        }
      },
      "on_kill": {
        "lightning_explosion": {
          "damage": 30,
          "radius": 4,
          "chance": 0.4
        }
      }
    },
    "materials": {
      "enchanted_steel": 5,
      "lightning_essence": 3,
      "air_essence": 3,
      "magical_gem": 1
    },
    "visual": {
      "model": "models/weapons/storm_blade.obj",
      "icon": "icons/weapons/storm_blade.png",
      "effects": {
        "trail": {
          "color": "#00BFFF",
          "length": 1.0
        },
        "particles": {
          "type": "lightning",
          "intensity": 0.7
        }
      }
    }
  }
}
```

### Аксессуар - Кольцо архимага

```json
{
  "archmage_ring": {
    "name": "Кольцо архимага",
    "description": "Древнее кольцо, принадлежавшее могущественному архимагу. Усиливает магические способности и регенерацию маны.",
    "type": "accessory",
    "slot": "accessory1",
    "rarity": "RARE",
    "level": 20,
    "characteristics": {
      "weight": 0.1,
      "durability": 200,
      "mana_bonus": 50,
      "magic_bonus": 15
    },
    "requirements": {
      "level": 20,
      "intelligence": 25,
      "skills": {
        "elementalism": 7
      }
    },
    "effects": {
      "passive": {
        "mana_regeneration": 2,
        "spell_cost_reduction": 15,
        "spell_critical_chance": 10
      },
      "on_hit": {
        "mana_drain": {
          "amount": 5,
          "chance": 0.2
        }
      }
    },
    "materials": {
      "enchanted_gold": 2,
      "sapphire": 1,
      "mana_crystal": 1
    }
  }
}
```

Эти примеры демонстрируют структуру различных типов экипировки и показывают, как определять их характеристики, требования, эффекты и визуальное отображение. При создании новых предметов экипировки важно учитывать баланс игры и согласованность с другими системами, такими как боевая система, крафтинг и развитие персонажа.
