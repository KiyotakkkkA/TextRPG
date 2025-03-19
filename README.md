# TextRPG Adventure

Текстовая RPG игра с консольной графикой и расширенными возможностями рендеринга.

## Возможности

- Консольный движок рендеринга с поддержкой двойной буферизации
- Система управления событиями
- Система предметов и инвентаря
- Система преднагрузки ресурсов (ATLAS)
- Система управления версиями
- Удобный формат описания игровых сущностей (.desc)
- Расширение VSCode для подсветки синтаксиса .desc файлов

## Установка

```bash
# Клонирование репозитория
git clone <url-репозитория>
cd TextRPG

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Установка расширения VSCode для подсветки .desc файлов (опционально)
python pymust install-extension
```

## Запуск

```bash
python main.py
```

## Формат .desc

Для упрощения разработки игрового контента реализован специальный формат `.desc`, который позволяет описывать игровые сущности в более читаемом и удобном виде, чем JSON. Формат поддерживает:

- Автоматическую компиляцию в JSON при запуске игры
- Комментарии и более понятный синтаксис
- Легкое расширение для новых типов сущностей
- Подсветку синтаксиса в VSCode (через расширение)

### Пример описания локации:

```
LOCATION forest {
    name: "Лес"
    description: "Густой лес с множеством растений и животных."
    type: wilderness

    RESOURCES {
        RESOURCE herb {
            min_amount: 2
            max_amount: 4
        }
    }
}
```

Подробная документация по формату находится в каталоге `desc/README.md`.

## Управление версиями

Версии игры и движка управляются через файл `version.properties`. Для обновления версии используйте утилиту `scripts/update_version.py` или команду `pymust update`:

```bash
# Просмотр информации о текущей версии
python pymust version

# Обновление патч-версии игры (0.1.0 -> 0.1.1)
python pymust update --patch

# Обновление минорной версии игры (0.1.0 -> 0.2.0)
python pymust update --minor

# Обновление мажорной версии игры (0.1.0 -> 1.0.0)
python pymust update --major

# Изменение стадии разработки
python pymust update --stage=Beta

# Обновление версии движка
python pymust update --engine --patch

# Обновление версии pymust
python pymust update --pymust --patch
```

### Формат версий

Игра использует семантическое версионирование:

- **X.Y.Z** (Major.Minor.Patch)
- **Major**: значительные изменения, несовместимые с предыдущими версиями
- **Minor**: добавление новых функций с сохранением обратной совместимости
- **Patch**: исправления ошибок с сохранением обратной совместимости

Стадии разработки:

- **Alpha**: ранняя разработка, функциональность неполная
- **Beta**: тестирование, основные функции работают
- **RC**: релиз-кандидат, готов к выпуску
- **Release**: стабильная версия

## Структура проекта

```
TextRPG/
├── data/               # Данные игры (предметы, существа и т.д.)
├── desc/               # Файлы .desc для описания игровых сущностей
├── logs/               # Логи игры
├── scripts/            # Скрипты для разработки и сборки
├── src/                # Исходный код
│   ├── loaders/        # Загрузчики данных
│   ├── models/         # Модели данных
│   ├── render/         # Движок рендеринга
│   └── utils/          # Утилиты
├── main.py             # Точка входа в игру
├── requirements.txt    # Зависимости проекта
└── version.properties  # Файл версий
```

## Лицензия

[MIT License](https://opensource.org/licenses/MIT)
