const vscode = require("vscode");

/**
 * Активация расширения
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  console.log("Расширение DESC Language Support активировано");

  // Общие ключевые слова DESC
  const KEYWORDS = [
    "LOCATION",
    "ITEM",
    "CHARACTER",
    "RESOURCE",
    "CONNECTION",
    "EFFECT",
    "DIALOGUE",
    "PROPERTIES",
    "RESOURCES",
    "CONNECTIONS",
    "CHARACTERS",
    "STATS",
    "INVENTORY",
    "EFFECTS",
    "TOPIC",
  ];

  // Типы блоков и их свойства
  const BLOCK_PROPERTIES = {
    LOCATION: [
      { name: "name", detail: "Название локации", type: "string" },
      { name: "description", detail: "Описание локации", type: "string" },
      {
        name: "type",
        detail: "Тип локации (wilderness, dungeon, settlement)",
        type: "string",
      },
      { name: "color", detail: "Цвет отображения локации", type: "string" },
      { name: "icon", detail: "Иконка локации", type: "string" },
    ],
    ITEM: [
      { name: "name", detail: "Название предмета", type: "string" },
      { name: "description", detail: "Описание предмета", type: "string" },
      {
        name: "type",
        detail: "Тип предмета (weapon, armor, consumable)",
        type: "string",
      },
      { name: "icon", detail: "Иконка предмета", type: "string" },
      { name: "value", detail: "Ценность предмета", type: "number" },
      { name: "weight", detail: "Вес предмета", type: "number" },
      {
        name: "rarity",
        detail: "Редкость предмета (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY)",
        type: "enum",
      },
    ],
    RESOURCE: [
      {
        name: "min_amount",
        detail: "Минимальное количество ресурса",
        type: "number",
      },
      {
        name: "max_amount",
        detail: "Максимальное количество ресурса",
        type: "number",
      },
      {
        name: "respawn_time",
        detail: "Время восстановления ресурса (в секундах)",
        type: "number",
      },
      {
        name: "required_tool",
        detail: "Необходимый инструмент для сбора",
        type: "string",
      },
      { name: "rarity", detail: "Редкость ресурса", type: "enum" },
    ],
    CONNECTION: [
      {
        name: "id",
        detail: "ID локации, на которую ведет соединение",
        type: "string",
      },
      { name: "name", detail: "Название соединения", type: "string" },
      { name: "condition", detail: "Условие для прохода", type: "string" },
      { name: "icon", detail: "Иконка соединения", type: "string" },
    ],
    CHARACTER: [
      { name: "id", detail: "ID персонажа", type: "string" },
      { name: "name", detail: "Имя персонажа", type: "string" },
      { name: "description", detail: "Описание персонажа", type: "string" },
      { name: "dialogue", detail: "Реплики персонажа", type: "array" },
    ],
    PROPERTIES: [
      { name: "danger_level", detail: "Уровень опасности", type: "number" },
      { name: "ambient_sound", detail: "Фоновый звук", type: "string" },
      { name: "weather", detail: "Погода", type: "array" },
    ],
    REGION: [
      { name: "name", detail: "Название региона", type: "string" },
      { name: "description", detail: "Описание региона", type: "string" },
      { name: "color", detail: "Цвет отображения региона", type: "string" },
      { name: "icon", detail: "Иконка региона", type: "string" },
      { name: "difficulty", detail: "Уровень сложности", type: "number" },
      { name: "climate", detail: "Климат", type: "string" },
      { name: "locations", detail: "Локации в регионе", type: "array" },
      { name: "x", detail: "Координата X", type: "number" },
      { name: "y", detail: "Координата Y", type: "number" },
      {
        name: "adjacent_regions",
        detail: "Приграничные регионы",
        type: "array",
      },
    ],
  };

  // Определение значений для перечислений
  const ENUM_VALUES = {
    rarity: ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY", "MYTHIC"],
    type: [
      "wilderness",
      "dungeon",
      "settlement",
      "weapon",
      "armor",
      "consumable",
      "resource",
    ],
  };

  // Определяет тип текущего блока на основе контекста
  function determineCurrentBlockType(document, position) {
    // Ищем последний открытый блок перед текущей позицией
    for (let i = position.line; i >= 0; i--) {
      const line = document.lineAt(i).text.trim();

      // Ищем определение блока (LOCATION, ITEM и т.д.)
      for (const keyword of KEYWORDS) {
        if (line.startsWith(keyword) && line.includes("{")) {
          return keyword;
        }
      }

      // Если нашли закрывающую скобку, ищем соответствующую открывающую
      if (line === "}") {
        let braceCount = 1;
        for (let j = i - 1; j >= 0; j--) {
          const braceLine = document.lineAt(j).text.trim();
          if (braceLine === "}") {
            braceCount++;
          } else if (braceLine.endsWith("{")) {
            braceCount--;
            if (braceCount === 0) {
              // Нашли соответствующую открывающую скобку, проверяем тип блока
              for (const keyword of KEYWORDS) {
                if (braceLine.startsWith(keyword)) {
                  return keyword;
                }
              }
              break;
            }
          }
        }
      }
    }

    return null;
  }

  // Регистрируем провайдер автодополнения с триггерами для разных контекстов
  const completionProvider = vscode.languages.registerCompletionItemProvider(
    "desc",
    {
      provideCompletionItems(document, position, token, context) {
        // Получаем текущую строку
        const linePrefix = document
          .lineAt(position)
          .text.substr(0, position.character);

        // Используем набор предложений в зависимости от контекста
        const completionItems = [];

        // Определяем тип текущего блока (локация, предмет и т.д.)
        const blockType = determineCurrentBlockType(document, position);

        // Если линия пуста или содержит только пробелы, предлагаем ключевые слова
        if (linePrefix.trim() === "") {
          // Добавляем ключевые слова
          KEYWORDS.forEach((keyword) => {
            const item = new vscode.CompletionItem(
              keyword,
              vscode.CompletionItemKind.Keyword
            );
            item.detail = `DESC ключевое слово`;
            item.documentation = new vscode.MarkdownString(
              `Блок определения **${keyword}**`
            );
            completionItems.push(item);
          });
        }

        // Если строка заканчивается на ':', то предлагаем значения
        if (linePrefix.trim().endsWith(":")) {
          // Определяем ключ свойства
          const propertyKey = linePrefix.trim().slice(0, -1).trim();

          // Если это свойство с перечислением, предлагаем возможные значения
          if (ENUM_VALUES[propertyKey]) {
            ENUM_VALUES[propertyKey].forEach((value) => {
              const item = new vscode.CompletionItem(
                value,
                vscode.CompletionItemKind.EnumMember
              );
              item.detail = `Значение для ${propertyKey}`;
              completionItems.push(item);
            });
          } else {
            // Добавляем шаблоны для разных типов
            // Строка
            const stringItem = new vscode.CompletionItem(
              '"строка"',
              vscode.CompletionItemKind.Value
            );
            stringItem.detail = "Строковое значение";
            completionItems.push(stringItem);

            // Одинарные кавычки
            const singleQuoteItem = new vscode.CompletionItem(
              "'строка'",
              vscode.CompletionItemKind.Value
            );
            singleQuoteItem.detail = "Строковое значение (одинарные кавычки)";
            completionItems.push(singleQuoteItem);

            // Число
            const numberItem = new vscode.CompletionItem(
              "0",
              vscode.CompletionItemKind.Value
            );
            numberItem.detail = "Числовое значение";
            completionItems.push(numberItem);

            // Булево
            const trueItem = new vscode.CompletionItem(
              "true",
              vscode.CompletionItemKind.Value
            );
            trueItem.detail = "Логическое значение (истина)";
            completionItems.push(trueItem);

            const falseItem = new vscode.CompletionItem(
              "false",
              vscode.CompletionItemKind.Value
            );
            falseItem.detail = "Логическое значение (ложь)";
            completionItems.push(falseItem);

            // Null
            const nullItem = new vscode.CompletionItem(
              "null",
              vscode.CompletionItemKind.Value
            );
            nullItem.detail = "Отсутствующее значение";
            completionItems.push(nullItem);

            // Массив
            const arrayItem = new vscode.CompletionItem(
              "[]",
              vscode.CompletionItemKind.Value
            );
            arrayItem.detail = "Массив";
            completionItems.push(arrayItem);

            // Блок
            const blockItem = new vscode.CompletionItem(
              "{}",
              vscode.CompletionItemKind.Value
            );
            blockItem.detail = "Блок";
            completionItems.push(blockItem);
          }
        } else if (blockType && !linePrefix.includes(":")) {
          // Если мы внутри известного блока и не набираем значение, предлагаем свойства блока
          const properties = BLOCK_PROPERTIES[blockType] || [];
          properties.forEach((prop) => {
            const item = new vscode.CompletionItem(
              prop.name,
              vscode.CompletionItemKind.Property
            );
            item.detail = prop.detail;
            item.documentation = new vscode.MarkdownString(
              `**${prop.name}** - ${prop.detail} (тип: ${prop.type})`
            );
            item.insertText = `${prop.name}: `;
            completionItems.push(item);
          });
        }

        return completionItems;
      },
    },
    "", // Триггер на каждый символ
    ":" // Триггер на двоеточие
  );

  // Регистрируем провайдер для подсказок при наведении
  const hoverProvider = vscode.languages.registerHoverProvider("desc", {
    provideHover(document, position, token) {
      const range = document.getWordRangeAtPosition(position);
      if (!range) {
        return null;
      }

      const word = document.getText(range);

      // Проверяем, является ли слово ключевым
      if (KEYWORDS.includes(word)) {
        return new vscode.Hover(`**${word}** - блок определения в DESC`, range);
      }

      // Проверяем, является ли слово свойством в текущем блоке
      const lineText = document.lineAt(position.line).text;
      if (lineText.includes(":")) {
        const propName = lineText.split(":")[0].trim();

        // Определяем тип блока
        const blockType = determineCurrentBlockType(document, position);
        if (blockType && BLOCK_PROPERTIES[blockType]) {
          const property = BLOCK_PROPERTIES[blockType].find(
            (p) => p.name === propName
          );
          if (property) {
            const markdown = new vscode.MarkdownString();
            markdown.appendMarkdown(`**${property.name}**\n\n`);
            markdown.appendMarkdown(`${property.detail}\n\n`);
            markdown.appendMarkdown(`Тип: _${property.type}_`);
            return new vscode.Hover(markdown, range);
          }
        }
      }

      return null;
    },
  });

  // Добавляем провайдеры в подписки
  context.subscriptions.push(completionProvider);
  context.subscriptions.push(hoverProvider);

  // Регистрируем команду для показа автодополнений
  const showCompletionsCommand = vscode.commands.registerCommand(
    "desc.showCompletions",
    () => {
      vscode.commands.executeCommand("editor.action.triggerSuggest");
    }
  );

  // Применяем пользовательскую тему для DESC файлов
  const configureEditorColors = () => {
    // Проверяем, активен ли редактор DESC
    const activeEditor = vscode.window.activeTextEditor;
    if (activeEditor && activeEditor.document.languageId === "desc") {
      // Применяем подсветку для улучшения отображения
      console.log("Применение пользовательской темы для DESC файла");
    }
  };

  // Подписываемся на события изменения активного редактора
  const changeActiveEditorListener = vscode.window.onDidChangeActiveTextEditor(
    configureEditorColors
  );

  // Добавляем все регистрации в подписки контекста
  context.subscriptions.push(showCompletionsCommand);
  context.subscriptions.push(changeActiveEditorListener);

  // Применяем тему при активации расширения
  configureEditorColors();
}

/**
 * Деактивация расширения
 */
function deactivate() {
  console.log("Расширение DESC Language Support деактивировано");
}

module.exports = {
  activate,
  deactivate,
};
