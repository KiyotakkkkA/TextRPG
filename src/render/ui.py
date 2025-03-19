"""
UI компоненты для движка рендеринга.
Включает различные элементы интерфейса: панели, метки, кнопки, меню и т.д.
"""

from typing import List, Dict, Any, Optional, Union, Callable, Tuple
from src.render.core import UIElement, ConsoleHelper, Color, Keys

class Panel(UIElement):
    """
    Простая панель с опциональной границей и заголовком.
    """
    def __init__(self, x: int, y: int, width: int, height: int, title: str = "", 
                 border: bool = True, border_color: str = Color.WHITE, 
                 bg_color: str = "", title_color: str = Color.BRIGHT_WHITE):
        super().__init__(x, y, width, height)
        self.title = title
        self.border = border
        self.border_color = border_color
        self.bg_color = bg_color
        self.title_color = title_color
    
    def render(self):
        if not self.visible:
            return
        
        # Если есть фон, заполняем его
        if self.bg_color:
            for y in range(self.height):
                ConsoleHelper.move_cursor(self.x, self.y + y)
                print(f"{self.bg_color}{' ' * self.width}{Color.RESET}", end='')
        
        # Рисуем границу, если нужно
        if self.border:
            # Горизонтальные линии
            ConsoleHelper.move_cursor(self.x, self.y)
            print(ConsoleHelper.colorize('┌' + '─' * (self.width - 2) + '┐', self.border_color), end='')
            
            ConsoleHelper.move_cursor(self.x, self.y + self.height - 1)
            print(ConsoleHelper.colorize('└' + '─' * (self.width - 2) + '┘', self.border_color), end='')
            
            # Вертикальные линии
            for y in range(1, self.height - 1):
                ConsoleHelper.move_cursor(self.x, self.y + y)
                print(ConsoleHelper.colorize('│', self.border_color), end='')
                ConsoleHelper.move_cursor(self.x + self.width - 1, self.y + y)
                print(ConsoleHelper.colorize('│', self.border_color), end='')
            
            # Заголовок, если есть
            if self.title:
                title_x = self.x + (self.width - len(self.title)) // 2
                ConsoleHelper.move_cursor(title_x, self.y)
                print(ConsoleHelper.colorize(f" {self.title} ", self.title_color, self.bg_color), end='')

class Label(UIElement):
    """
    Текстовая метка.
    """
    def __init__(self, x: int, y: int, text: str, color: str = Color.WHITE, bg_color: str = ""):
        super().__init__(x, y, len(text), 1)
        self.text = text
        self.color = color
        self.bg_color = bg_color
    
    def render(self):
        if not self.visible:
            return
        
        ConsoleHelper.move_cursor(self.x, self.y)
        print(ConsoleHelper.colorize(self.text, self.color, self.bg_color), end='')
    
    def set_text(self, text: str):
        """
        Устанавливает новый текст метки.
        """
        self.text = text
        self.width = len(text)

class Button(UIElement):
    """
    Кнопка с текстом.
    """
    def __init__(self, x: int, y: int, text: str, action: Callable = None,
                 color: str = Color.WHITE, bg_color: str = "",
                 selected_color: str = Color.BLACK, selected_bg_color: str = Color.BRIGHT_WHITE):
        super().__init__(x, y, len(text) + 4, 1)
        self.text = text
        self.action = action
        self.color = color
        self.bg_color = bg_color
        self.selected_color = selected_color
        self.selected_bg_color = selected_bg_color
        self.selected = False
    
    def render(self):
        if not self.visible:
            return
        
        ConsoleHelper.move_cursor(self.x, self.y)
        
        if self.selected:
            print(ConsoleHelper.colorize(f"[ {self.text} ]", self.selected_color, self.selected_bg_color), end='')
        else:
            print(ConsoleHelper.colorize(f"[ {self.text} ]", self.color, self.bg_color), end='')
    
    def activate(self):
        """
        Активирует кнопку, вызывая связанное с ней действие.
        """
        if self.action:
            self.action()

class MenuItem:
    """
    Элемент меню с текстом и связанным действием.
    """
    def __init__(self, text: str, action: Optional[Callable] = None, enabled: bool = True,
                 icon: str = "", icon_color: str = Color.WHITE, 
                 text_parts: Optional[List[Dict[str, str]]] = None):
        """
        Инициализирует элемент меню.
        
        Args:
            text: Текст элемента меню
            action: Функция, которая будет вызвана при активации элемента
            enabled: Доступен ли элемент для выбора
            icon: Иконка элемента
            icon_color: Цвет иконки
            text_parts: Список частей текста с указанием цвета для каждой части, 
                        формат: [{"text": "текст", "color": "цвет"}, ...]
        """
        self.text = text
        self.action = action
        self.enabled = enabled
        self.icon = icon
        self.icon_color = icon_color
        self.text_parts = text_parts
        self.is_rich_text = text_parts is not None
    
    def activate(self):
        """
        Активирует элемент меню, вызывая связанное с ним действие.
        """
        if self.enabled and self.action:
            self.action()

class Menu(UIElement):
    """
    Меню из нескольких пунктов, которые можно выбирать и активировать.
    """
    
    def __init__(self, x: int, y: int, width: int, items: List[MenuItem],
                 title: str = "", border: bool = True,
                 color: str = Color.WHITE, selected_color: str = Color.BRIGHT_WHITE,
                 disabled_color: str = Color.BRIGHT_BLACK,
                 border_color: str = Color.WHITE, bg_color: str = "",
                 selected_bg_color: str = "", title_color: str = Color.BRIGHT_WHITE):
        """
        Инициализирует элемент Menu с указанными параметрами.
        
        Args:
            x, y: Координаты верхнего левого угла меню
            width: Ширина меню
            items: Список элементов меню
            title: Заголовок меню
            border: Отображать рамку
            color: Цвет текста
            selected_color: Цвет выбранного элемента
            disabled_color: Цвет неактивных элементов
            border_color: Цвет рамки
            bg_color: Цвет фона
            selected_bg_color: Цвет фона выбранного пункта
            title_color: Цвет заголовка
        """
        super().__init__(x, y, width, len(items) if items else 1)
        self.items = items
        self.title = title
        self.border = border
        self.color = color
        self.selected_color = selected_color
        self.disabled_color = disabled_color
        self.border_color = border_color
        self.bg_color = bg_color
        self.selected_bg_color = selected_bg_color
        self.title_color = title_color
        self.selected_index = 0
        self._effective_height = len(items) if items else 1
        self._formatted_texts = []  # Строки текста для каждого пункта меню
        self._format_item_texts()

    def _format_item_texts(self):
        """
        Форматирует тексты пунктов меню, чтобы они помещались по ширине.
        Длинные строки разбиваются на несколько строк.
        """
        self._formatted_texts = []
        self._effective_height = 0
        
        # Рассчитываем доступную ширину для текста
        available_width = self.width - 4  # Учитываем отступы
        
        for item in self.items:
            if not item.text:  # Разделитель
                self._formatted_texts.append([])
                self._effective_height += 1
                continue
                
            # Если текст с иконкой, учитываем дополнительное место
            prefix_len = len(item.icon) + 1 if item.icon else 0
            text_width = available_width - prefix_len
            
            # Для форматированного текста используем особую обработку
            if item.is_rich_text:
                # Получаем общий текст для проверки длины
                full_text = item.text
                
                if len(full_text) <= text_width:
                    # Короткий текст помещается полностью
                    self._formatted_texts.append([{
                        "text": full_text,
                        "parts": item.text_parts,
                        "is_rich": True
                    }])
                    self._effective_height += 1
                else:
                    # Для длинного форматированного текста необходимо разбить по частям
                    # Сохраняем полный текст без разбиения, но отмечаем, что он требует обрезки при рендеринге
                    self._formatted_texts.append([{
                        "text": full_text,
                        "parts": item.text_parts,
                        "is_rich": True,
                        "needs_wrap": True,
                        "width": text_width
                    }])
                    # Приблизительная оценка количества строк
                    estimated_lines = (len(full_text) + text_width - 1) // text_width
                    self._effective_height += estimated_lines
            else:
                # Обычный текст обрабатываем как раньше
                if len(item.text) <= text_width:
                    # Короткий текст помещается полностью
                    self._formatted_texts.append([item.text])
                    self._effective_height += 1
                else:
                    # Разбиваем длинный текст на строки
                    lines = []
                    remaining = item.text
                    
                    while remaining:
                        # Если строка длиннее доступной ширины
                        if len(remaining) > text_width:
                            # Ищем последний пробел в пределах доступной ширины
                            split_pos = remaining.rfind(' ', 0, text_width)
                            
                            if split_pos > 0:
                                # Нашли пробел, разбиваем по нему
                                lines.append(remaining[:split_pos])
                                remaining = remaining[split_pos+1:]
                            else:
                                # Не нашли пробел, разбиваем принудительно
                                lines.append(remaining[:text_width])
                                remaining = remaining[text_width:]
                        else:
                            # Остаток помещается целиком
                            lines.append(remaining)
                            remaining = ""
                    
                    self._formatted_texts.append(lines)
                    self._effective_height += len(lines)

    def render(self):
        """
        Отрисовывает элемент меню.
        """
        # Обновляем форматирование текста при изменении элементов
        if len(self._formatted_texts) != len(self.items):
            self._format_item_texts()
        
        if self.border:
            # Отрисовка рамки
            ConsoleHelper.move_cursor(self.x, self.y)
            corner_tl = '┌'
            corner_tr = '┐'
            corner_bl = '└'
            corner_br = '┘'
            h_line = '─'
            v_line = '│'
            
            # Верхняя линия с заголовком
            if self.title:
                title_text = f" {self.title} "
                left_width = (self.width - len(title_text)) // 2
                right_width = self.width - len(title_text) - left_width
                
                top_line = corner_tl + h_line * (left_width - 1) + title_text + h_line * (right_width - 1) + corner_tr
                top_line = ConsoleHelper.colorize(top_line, self.border_color, self.bg_color)
                
                if self.title_color:
                    # Заменяем часть с заголовком на текст с другим цветом
                    title_pos = len(corner_tl) + left_width - 1
                    title_colored = ConsoleHelper.colorize(title_text, self.title_color, self.bg_color)
                    top_line = top_line[:title_pos] + title_colored + top_line[title_pos + len(title_text):]
            else:
                top_line = corner_tl + h_line * (self.width - 2) + corner_tr
                top_line = ConsoleHelper.colorize(top_line, self.border_color, self.bg_color)
            
            print(top_line)
            
            # Отрисовка элементов меню
            curr_y = self.y + 1
            item_idx = 0
            
            for item_idx, item in enumerate(self.items):
                formatted_text = self._formatted_texts[item_idx]
                
                # Для разделителей просто рисуем горизонтальную линию
                if not item.text:
                    ConsoleHelper.move_cursor(self.x, curr_y)
                    line = v_line + h_line * (self.width - 2) + v_line
                    print(ConsoleHelper.colorize(line, self.border_color, self.bg_color))
                    curr_y += 1
                    continue
                
                # Определяем цвет для элемента
                if not item.enabled:
                    item_color = self.disabled_color
                    is_selected = False
                else:
                    is_selected = (item_idx == self.selected_index)
                    item_color = self.selected_color if is_selected else self.color
                
                # Определяем цвет фона
                item_bg = self.selected_bg_color if is_selected and item.enabled else self.bg_color
                
                # Отрисовываем каждую строку пункта меню
                for line_idx, line in enumerate(formatted_text):
                    ConsoleHelper.move_cursor(self.x, curr_y)
                    
                    # Добавляем иконку только к первой строке
                    prefix = ""
                    if line_idx == 0 and item.icon:
                        prefix = item.icon + " "
                        icon_color = item.icon_color if item.icon_color else item_color
                    
                    # Проверяем, является ли строка форматированной
                    if isinstance(line, dict) and line.get("is_rich", False):
                        # Обрабатываем форматированную строку
                        parts = line.get("parts", [])
                        
                        # Выводим вертикальную линию рамки
                        print(ConsoleHelper.colorize(v_line, self.border_color, self.bg_color), end="")
                        
                        # Выводим префикс с иконкой
                        if prefix:
                            print(ConsoleHelper.colorize(prefix, icon_color, item_bg), end="")
                        
                        # Если строка требует переноса (слишком длинная)
                        if line.get("needs_wrap", False):
                            # В этом случае вместо переноса строки с сохранением форматирования, 
                            # просто выводим первую строку с усечением
                            # Это сложный случай, который можно улучшить в будущем
                            
                            # Выводим каждую часть с своим цветом
                            current_pos = 0
                            content_width = self.width - 4 - len(prefix)
                            
                            for part in parts:
                                part_text = part["text"]
                                part_color = part["color"]
                                
                                # Если эта часть уместится в оставшееся пространство
                                if current_pos + len(part_text) <= content_width:
                                    print(ConsoleHelper.colorize(part_text, part_color, item_bg), end="")
                                    current_pos += len(part_text)
                                else:
                                    # Показываем только то, что поместится
                                    show_text = part_text[:content_width - current_pos]
                                    print(ConsoleHelper.colorize(show_text, part_color, item_bg), end="")
                                    current_pos += len(show_text)
                                    break
                            
                            # Добавляем пробелы до конца строки
                            padding = " " * (self.width - 3 - current_pos - len(prefix))
                            print(padding, end="")
                        else:
                            # Выводим каждую часть с своим цветом
                            for part in parts:
                                part_text = part["text"]
                                part_color = part["color"]
                                print(ConsoleHelper.colorize(part_text, part_color, item_bg), end="")
                            
                            # Добавляем пробелы до конца строки
                            content = line["text"]
                            padding = " " * (self.width - 3 - len(content) - len(prefix))
                            print(padding, end="")
                        
                        # Закрываем строку вертикальной линией
                        print(ConsoleHelper.colorize(v_line, self.border_color, self.bg_color))
                    else:
                        # Обрабатываем обычную строку текста
                        content = prefix + line
                        padding = " " * (self.width - 2 - len(content))
                        
                        # Отрисовываем строку
                        line_text = v_line + content + padding + v_line
                        
                        # Если есть иконка, отрисовываем её отдельно
                        if line_idx == 0 and item.icon:
                            print(ConsoleHelper.colorize(v_line, self.border_color, self.bg_color), end="")
                            print(ConsoleHelper.colorize(prefix, icon_color, item_bg), end="")
                            print(ConsoleHelper.colorize(line, item_color, item_bg), end="")
                            print(ConsoleHelper.colorize(padding, item_color, item_bg), end="")
                            print(ConsoleHelper.colorize(v_line, self.border_color, self.bg_color))
                        else:
                            # Применяем цвет к центральной части строки
                            middle_start = 1
                            middle_end = len(line_text) - 1
                            
                            print(ConsoleHelper.colorize(line_text[:middle_start], self.border_color, self.bg_color), end="")
                            print(ConsoleHelper.colorize(line_text[middle_start:middle_end], item_color, item_bg), end="")
                            print(ConsoleHelper.colorize(line_text[middle_end:], self.border_color, self.bg_color))
                    
                    curr_y += 1
            
            # Отрисовка нижней границы
            ConsoleHelper.move_cursor(self.x, curr_y)
            bottom_line = corner_bl + h_line * (self.width - 2) + corner_br
            print(ConsoleHelper.colorize(bottom_line, self.border_color, self.bg_color))
            
            # Обновляем высоту элемента
            self.height = curr_y - self.y + 1
        else:
            # Отрисовка без рамки
            curr_y = self.y
            
            # Заголовок
            if self.title:
                ConsoleHelper.move_cursor(self.x, curr_y)
                title_text = ConsoleHelper.colorize(self.title, self.title_color, self.bg_color)
                print(title_text)
                curr_y += 1
            
            # Элементы меню
            for item_idx, item in enumerate(self.items):
                formatted_text = self._formatted_texts[item_idx]
                
                # Для разделителей просто рисуем горизонтальную линию
                if not item.text:
                    ConsoleHelper.move_cursor(self.x, curr_y)
                    line = "─" * self.width
                    print(ConsoleHelper.colorize(line, self.disabled_color, self.bg_color))
                    curr_y += 1
                    continue
                
                # Определяем цвет для элемента
                if not item.enabled:
                    item_color = self.disabled_color
                    is_selected = False
                else:
                    is_selected = (item_idx == self.selected_index)
                    item_color = self.selected_color if is_selected else self.color
                
                # Определяем цвет фона
                item_bg = self.selected_bg_color if is_selected and item.enabled else self.bg_color
                
                # Отрисовываем каждую строку пункта меню
                for line_idx, line in enumerate(formatted_text):
                    ConsoleHelper.move_cursor(self.x, curr_y)
                    
                    # Добавляем иконку и выделение только к первой строке
                    prefix = ""
                    if line_idx == 0:
                        if is_selected:
                            prefix = "> "
                        if item.icon:
                            prefix += item.icon + " "
                    else:
                        # Для последующих строк добавляем отступ
                        prefix = "  " + (" " * (len(item.icon) + 1 if item.icon else 0))
                    
                    # Проверяем, является ли строка форматированной
                    if isinstance(line, dict) and line.get("is_rich", False):
                        # Выводим префикс
                        if prefix:
                            prefix_color = item.icon_color if item.icon and line_idx == 0 else item_color
                            print(ConsoleHelper.colorize(prefix, prefix_color, item_bg), end="")
                        
                        # Выводим форматированный текст
                        parts = line.get("parts", [])
                        
                        for part in parts:
                            part_text = part["text"]
                            part_color = part["color"]
                            
                            # Если выбран или отключен, корректируем цвет
                            if not item.enabled:
                                part_color = self.disabled_color
                            elif is_selected:
                                # Для выбранных элементов можно применить другой стиль
                                pass
                            
                            print(ConsoleHelper.colorize(part_text, part_color, item_bg), end="")
                        
                        print()  # Перевод строки
                    else:
                        # Формируем текст
                        content = prefix + line
                        
                        # Если есть иконка в первой строке, отрисовываем её отдельно
                        if line_idx == 0 and item.icon:
                            icon_part = prefix
                            print(ConsoleHelper.colorize(icon_part, item.icon_color if item.icon_color else item_color, item_bg), end="")
                            print(ConsoleHelper.colorize(line, item_color, item_bg))
                        else:
                            print(ConsoleHelper.colorize(content, item_color, item_bg))
                    
                    curr_y += 1
            
            # Устанавливаем правильную высоту элемента с учетом переносов строк
            self.height = curr_y - self.y

    def handle_input(self, key: int) -> bool:
        """
        Обрабатывает нажатие клавиши.
        
        Args:
            key: Код клавиши
            
        Returns:
            bool: True, если клавиша была обработана
        """
        if not self.items:
            return False
            
        if key == Keys.UP:
            self._select_previous()
            return True
        elif key == Keys.DOWN:
            self._select_next()
            return True
        elif key == Keys.ENTER:
            self._activate_selected()
            return True
            
        return False
    
    def _select_previous(self):
        """
        Выбирает предыдущий активный элемент меню.
        """
        if not self.items:
            return
            
        # Сохраняем текущий индекс, чтобы избежать бесконечного цикла
        start_index = self.selected_index
        
        # Перебираем элементы в обратном порядке
        index = (self.selected_index - 1) % len(self.items)
        
        # Если элемент неактивен или является разделителем, переходим к следующему
        while (not self.items[index].enabled or not self.items[index].text) and index != start_index:
            index = (index - 1) % len(self.items)
            
        # Если нашли активный элемент, выбираем его
        if self.items[index].enabled and self.items[index].text:
            self.selected_index = index
            self.mark_for_redraw()
    
    def _select_next(self):
        """
        Выбирает следующий активный элемент меню.
        """
        if not self.items:
            return
            
        # Сохраняем текущий индекс, чтобы избежать бесконечного цикла
        start_index = self.selected_index
        
        # Перебираем элементы
        index = (self.selected_index + 1) % len(self.items)
        
        # Если элемент неактивен или является разделителем, переходим к следующему
        while (not self.items[index].enabled or not self.items[index].text) and index != start_index:
            index = (index + 1) % len(self.items)
            
        # Если нашли активный элемент, выбираем его
        if self.items[index].enabled and self.items[index].text:
            self.selected_index = index
            self.mark_for_redraw()
    
    def _activate_selected(self):
        """
        Активирует выбранный элемент меню.
        """
        if self.items and 0 <= self.selected_index < len(self.items):
            if self.items[self.selected_index].enabled and self.items[self.selected_index].text:
                self.items[self.selected_index].activate()

class ProgressBar(UIElement):
    """
    Прогресс-бар для отображения прогресса.
    """
    def __init__(self, x: int, y: int, width: int, value: float, max_value: float,
                 color: str = Color.GREEN, bg_color: str = Color.BLACK,
                 border: bool = True, border_color: str = Color.WHITE,
                 show_percentage: bool = True):
        """
        Инициализирует прогресс-бар.
        
        Args:
            x (int): X-координата
            y (int): Y-координата
            width (int): Ширина прогресс-бара
            value (float): Текущее значение
            max_value (float): Максимальное значение
            color (str): Цвет заполненной части
            bg_color (str): Цвет пустой части
            border (bool): Отображать ли границу
            border_color (str): Цвет границы
            show_percentage (bool): Отображать ли процент справа от прогресс-бара
        """
        super().__init__(x, y, width, 1)
        self.value = value
        self.max_value = max_value
        self.color = color
        self.bg_color = bg_color
        self.border = border
        self.border_color = border_color
        self.show_percentage = show_percentage
    
    def render(self):
        if not self.visible:
            return
        
        ConsoleHelper.move_cursor(self.x, self.y)
        
        # Вместо отрисовки прогресс-бара показываем текущее и максимальное значение
        current_value = int(self.value)
        max_value = int(self.max_value)
        status_text = f"{current_value} / {max_value}"
        
        # Рисуем значения с цветом
        print(ConsoleHelper.colorize(status_text, self.color), end='')
    
    def set_value(self, value: float):
        """
        Устанавливает текущее значение прогресса.
        """
        self.value = value

class TextBox(UIElement):
    """
    Многострочный текстовый блок с прокруткой.
    """
    def __init__(self, x: int, y: int, width: int, height: int, text: str = "",
                 color: str = Color.WHITE, bg_color: str = "", border: bool = True,
                 border_color: str = Color.WHITE, title: str = "", 
                 title_color: str = Color.BRIGHT_WHITE):
        super().__init__(x, y, width, height)
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.border = border
        self.border_color = border_color
        self.title = title
        self.title_color = title_color
        self.scroll_offset = 0
        self._lines = []
        self._update_lines()
    
    def _update_lines(self):
        """
        Обновляет внутренний список строк в соответствии с текстом и шириной.
        """
        self._lines = []
        inner_width = self.width - (4 if self.border else 0)
        
        # Разбиваем текст на строки
        for line in self.text.split('\n'):
            # Разбиваем длинные строки
            while len(line) > inner_width:
                self._lines.append(line[:inner_width])
                line = line[inner_width:]
            self._lines.append(line)
    
    def render(self):
        if not self.visible:
            return
        
        # Создаем панель для фона и границы
        if self.border:
            panel = Panel(self.x, self.y, self.width, self.height, 
                         self.title, True, self.border_color, self.bg_color, self.title_color)
            panel.render()
        
        # Определяем видимую область текста
        inner_height = self.height - (2 if self.border else 0)
        visible_lines = self._lines[self.scroll_offset:self.scroll_offset + inner_height]
        
        # Рендерим видимые строки
        start_y = self.y + (1 if self.border else 0)
        start_x = self.x + (2 if self.border else 0)
        
        for i, line in enumerate(visible_lines):
            ConsoleHelper.move_cursor(start_x, start_y + i)
            print(ConsoleHelper.colorize(line, self.color, self.bg_color), end='')
    
    def set_text(self, text: str):
        """
        Устанавливает новый текст и обновляет разбивку на строки.
        """
        self.text = text
        self._update_lines()
        
        # Корректируем смещение прокрутки, если оно вышло за пределы
        max_offset = max(0, len(self._lines) - (self.height - (2 if self.border else 0)))
        self.scroll_offset = min(self.scroll_offset, max_offset)
    
    def scroll_up(self, lines: int = 1):
        """
        Прокручивает текст вверх на указанное количество строк.
        """
        self.scroll_offset = max(0, self.scroll_offset - lines)
    
    def scroll_down(self, lines: int = 1):
        """
        Прокручивает текст вниз на указанное количество строк.
        """
        max_offset = max(0, len(self._lines) - (self.height - (2 if self.border else 0)))
        self.scroll_offset = min(max_offset, self.scroll_offset + lines)

class DialogBox(UIElement):
    """
    Диалоговое окно с текстом и кнопками.
    """
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 buttons: List[Button], title: str = "",
                 color: str = Color.WHITE, bg_color: str = Color.BG_BLACK,
                 border_color: str = Color.WHITE, title_color: str = Color.BRIGHT_WHITE):
        super().__init__(x, y, width, height)
        self.text = text
        self.buttons = buttons
        self.title = title
        self.color = color
        self.bg_color = bg_color
        self.border_color = border_color
        self.title_color = title_color
        self.selected_button_index = 0
        
        # Добавляем кнопки как дочерние элементы
        for button in buttons:
            self.add_child(button)
        
        # Создаем текстовый блок для текста
        text_height = height - 4  # Оставляем место для кнопок внизу
        self.text_box = TextBox(x + 2, y + 1, width - 4, text_height, text,
                               color, bg_color, False)
        self.add_child(self.text_box)
        
        # Располагаем кнопки внизу диалогового окна
        self._arrange_buttons()
    
    def _arrange_buttons(self):
        """
        Располагает кнопки равномерно внизу диалогового окна.
        """
        total_buttons_width = sum(button.width for button in self.buttons)
        spacing = (self.width - total_buttons_width) // (len(self.buttons) + 1)
        
        current_x = self.x + spacing
        button_y = self.y + self.height - 2
        
        for i, button in enumerate(self.buttons):
            button.x = current_x
            button.y = button_y
            current_x += button.width + spacing
            
            # Устанавливаем выделение для первой кнопки
            button.selected = (i == self.selected_button_index)
    
    def render(self):
        if not self.visible:
            return
        
        # Создаем панель для фона и границы
        panel = Panel(self.x, self.y, self.width, self.height, 
                     self.title, True, self.border_color, self.bg_color, self.title_color)
        panel.render()
    
    def handle_input(self, key: int) -> bool:
        """
        Обрабатывает ввод с клавиатуры.
        """
        if key == Keys.LEFT:
            self._select_previous_button()
            return True
        elif key == Keys.RIGHT:
            self._select_next_button()
            return True
        elif key == Keys.ENTER:
            self._activate_selected_button()
            return True
        
        return False
    
    def _select_previous_button(self):
        """
        Выбирает предыдущую кнопку.
        """
        if len(self.buttons) <= 1:
            return
        
        # Снимаем выделение с текущей кнопки
        self.buttons[self.selected_button_index].selected = False
        
        # Выбираем предыдущую кнопку
        self.selected_button_index = (self.selected_button_index - 1) % len(self.buttons)
        
        # Выделяем новую кнопку
        self.buttons[self.selected_button_index].selected = True
    
    def _select_next_button(self):
        """
        Выбирает следующую кнопку.
        """
        if len(self.buttons) <= 1:
            return
        
        # Снимаем выделение с текущей кнопки
        self.buttons[self.selected_button_index].selected = False
        
        # Выбираем следующую кнопку
        self.selected_button_index = (self.selected_button_index + 1) % len(self.buttons)
        
        # Выделяем новую кнопку
        self.buttons[self.selected_button_index].selected = True
    
    def _activate_selected_button(self):
        """
        Активирует выбранную кнопку.
        """
        if 0 <= self.selected_button_index < len(self.buttons):
            self.buttons[self.selected_button_index].activate()

class FlexPanel(UIElement):
    """
    Гибкая панель, которая адаптивно отображает содержимое без жёсткой структуры.
    Поддерживает различные стили оформления и автоматическое расположение элементов.
    """
    def __init__(self, x: int, y: int, width: int, height: int, 
                 style: str = "minimal", bg_color: str = "", padding: int = 0):
        """
        Инициализирует гибкую панель.
        
        Args:
            x, y: Координаты левого верхнего угла
            width, height: Размеры панели
            style: Стиль оформления ("none", "minimal", "single", "double", "ascii")
            bg_color: Цвет фона
            padding: Внутренний отступ от краёв
        """
        super().__init__(x, y, width, height)
        self.style = style
        self.bg_color = bg_color
        self.padding = padding
        self.content = []  # Список строк с содержимым
        self.content_colors = []  # Цвета для каждой строки
        self.auto_size = False  # Авторазмер по содержимому
        
        # Определяем символы границ в зависимости от стиля
        self._define_border_chars()
    
    def _define_border_chars(self):
        """Определяет символы для отрисовки границы в зависимости от стиля"""
        if self.style == "minimal":
            self.borders = {
                "top_left": "┌", "top_right": "┐", "bottom_left": "└", "bottom_right": "┘",
                "horizontal": "─", "vertical": "│", "left_junction": "├", "right_junction": "┤",
                "top_junction": "┬", "bottom_junction": "┴", "cross": "┼"
            }
        elif self.style == "double":
            self.borders = {
                "top_left": "╔", "top_right": "╗", "bottom_left": "╚", "bottom_right": "╝",
                "horizontal": "═", "vertical": "║", "left_junction": "╠", "right_junction": "╣",
                "top_junction": "╦", "bottom_junction": "╩", "cross": "╬"
            }
        elif self.style == "ascii":
            self.borders = {
                "top_left": "+", "top_right": "+", "bottom_left": "+", "bottom_right": "+",
                "horizontal": "-", "vertical": "|", "left_junction": "+", "right_junction": "+",
                "top_junction": "+", "bottom_junction": "+", "cross": "+"
            }
        elif self.style == "none":
            self.borders = {
                "top_left": " ", "top_right": " ", "bottom_left": " ", "bottom_right": " ",
                "horizontal": " ", "vertical": " ", "left_junction": " ", "right_junction": " ",
                "top_junction": " ", "bottom_junction": " ", "cross": " "
            }
        else:  # По умолчанию - одинарная линия
            self.borders = {
                "top_left": "┌", "top_right": "┐", "bottom_left": "└", "bottom_right": "┘",
                "horizontal": "─", "vertical": "│", "left_junction": "├", "right_junction": "┤",
                "top_junction": "┬", "bottom_junction": "┴", "cross": "┼"
            }
    
    def set_content(self, content: List[str], colors: Optional[List[str]] = None):
        """
        Устанавливает содержимое панели.
        
        Args:
            content: Список строк для отображения
            colors: Список цветов для каждой строки (или None для использования цвета по умолчанию)
        """
        self.content = content
        if colors and len(colors) == len(content):
            self.content_colors = colors
        else:
            self.content_colors = [Color.WHITE] * len(content)
        
        if self.auto_size:
            # Вычисляем высоту на основе содержимого
            content_height = len(content) + (self.padding * 2)
            if self.style != "none":
                content_height += 2  # Добавляем место для верхней и нижней границы
            self.height = content_height
            
            # Вычисляем ширину на основе самой длинной строки
            max_width = max((len(line) for line in content), default=0) + (self.padding * 2)
            if self.style != "none":
                max_width += 2  # Добавляем место для левой и правой границы
            self.width = max_width
        
        self.needs_redraw = True
    
    def render(self):
        """Отрисовывает гибкую панель с содержимым"""
        if not self.visible:
            return
        
        # Заполняем фон, если указан
        if self.bg_color:
            for y in range(self.height):
                ConsoleHelper.move_cursor(self.x, self.y + y)
                print(f"{self.bg_color}{' ' * self.width}{Color.RESET}", end='')
        
        # Рисуем границы, если стиль не "none"
        if self.style != "none":
            # Верхняя граница
            ConsoleHelper.move_cursor(self.x, self.y)
            border_color = Color.BRIGHT_BLACK if self.style == "minimal" else Color.WHITE
            print(ConsoleHelper.colorize(
                self.borders["top_left"] + self.borders["horizontal"] * (self.width - 2) + self.borders["top_right"], 
                border_color), end='')
            
            # Нижняя граница
            ConsoleHelper.move_cursor(self.x, self.y + self.height - 1)
            print(ConsoleHelper.colorize(
                self.borders["bottom_left"] + self.borders["horizontal"] * (self.width - 2) + self.borders["bottom_right"], 
                border_color), end='')
            
            # Боковые границы
            for y in range(1, self.height - 1):
                ConsoleHelper.move_cursor(self.x, self.y + y)
                print(ConsoleHelper.colorize(self.borders["vertical"], border_color), end='')
                ConsoleHelper.move_cursor(self.x + self.width - 1, self.y + y)
                print(ConsoleHelper.colorize(self.borders["vertical"], border_color), end='')
        
        # Выводим содержимое с учётом отступов
        content_x = self.x + (1 if self.style != "none" else 0) + self.padding
        content_y = self.y + (1 if self.style != "none" else 0) + self.padding
        
        for i, line in enumerate(self.content):
            if content_y + i >= self.y + self.height - (1 if self.style != "none" else 0) - self.padding:
                break  # Выходим за пределы панели
                
            ConsoleHelper.move_cursor(content_x, content_y + i)
            print(ConsoleHelper.colorize(
                line[:self.width - 2 * ((1 if self.style != "none" else 0) + self.padding)], 
                self.content_colors[i]), end='')

class RichText(UIElement):
    """
    Компонент для отображения форматированного текста с поддержкой
    разных цветов, стилей и эмодзи.
    """
    def __init__(self, x: int, y: int, width: int, height: int, 
                 default_color: str = Color.WHITE, bg_color: str = ""):
        """
        Инициализирует компонент форматированного текста.
        
        Args:
            x, y: Координаты левого верхнего угла
            width, height: Размеры области текста
            default_color: Цвет текста по умолчанию
            bg_color: Цвет фона
        """
        super().__init__(x, y, width, height)
        self.default_color = default_color
        self.bg_color = bg_color
        self.paragraphs = []  # Список абзацев
        self.current_offset = 0  # Текущее смещение при прокрутке
        self.formatted_lines = []  # Отформатированные строки для отображения
        
    def add_text(self, text: str, color: Optional[str] = None, prepend: bool = False, new_line: bool = True):
        """
        Добавляет текст в компонент.
        
        Args:
            text: Текст для добавления
            color: Цвет текста (None для использования цвета по умолчанию)
            prepend: Если True, добавляет текст в начало, иначе в конец
            new_line: Если True, текст добавляется как новый абзац, иначе добавляется к последнему абзацу
        """
        if not new_line and self.paragraphs:
            # Добавляем текст к последнему абзацу без переноса строки
            if prepend:
                # Добавляем в начало первого абзаца
                self.paragraphs[0]["text"] = text + self.paragraphs[0]["text"]
                self.paragraphs[0]["multicolor"] = True
            else:
                # Добавляем в конец последнего абзаца
                last_paragraph = self.paragraphs[-1]
                last_paragraph["text"] += text
                last_paragraph["multicolor"] = True
                # Сохраняем информацию о частях текста с разными цветами
                if "parts" not in last_paragraph:
                    last_paragraph["parts"] = [
                        {"text": last_paragraph["text"][:-len(text)], "color": last_paragraph["color"]},
                    ]
                last_paragraph["parts"].append({"text": text, "color": color or self.default_color})
        else:
            # Создаем новый абзац
            paragraph = {
                "text": text,
                "color": color or self.default_color,
                "multicolor": False
            }
            
            if prepend:
                self.paragraphs.insert(0, paragraph)
            else:
                self.paragraphs.append(paragraph)
        
        self._format_text()
        self.needs_redraw = True
    
    def clear(self):
        """Очищает весь текст"""
        self.paragraphs = []
        self.formatted_lines = []
        self.current_offset = 0
        self.needs_redraw = True
    
    def _format_text(self):
        """Форматирует текст по ширине компонента"""
        self.formatted_lines = []
        
        for paragraph in self.paragraphs:
            text = paragraph["text"]
            color = paragraph["color"]
            is_multicolor = paragraph.get("multicolor", False)
            
            # Если параграф многоцветный, обрабатываем его по-особому
            if is_multicolor and "parts" in paragraph:
                # Добавляем многоцветную строку как есть, без разбивки
                self.formatted_lines.append({
                    "text": text,
                    "color": color,
                    "multicolor": True,
                    "parts": paragraph["parts"]
                })
                continue
            
            # Разбиваем длинные строки по словам
            words = text.split()
            if not words:
                self.formatted_lines.append({"text": "", "color": color, "multicolor": False})
                continue
                
            current_line = words[0]
            for word in words[1:]:
                # Если слово поместится в текущую строку, добавляем его
                if len(current_line) + len(word) + 1 <= self.width:
                    current_line += " " + word
                else:
                    # Иначе добавляем текущую строку в список и начинаем новую
                    self.formatted_lines.append({"text": current_line, "color": color, "multicolor": False})
                    current_line = word
                    
            # Добавляем последнюю строку
            if current_line:
                self.formatted_lines.append({"text": current_line, "color": color, "multicolor": False})
                
    def scroll_up(self, lines: int = 1):
        """Прокручивает текст вверх"""
        self.current_offset = max(0, self.current_offset - lines)
        self.needs_redraw = True
    
    def scroll_down(self, lines: int = 1):
        """Прокручивает текст вниз"""
        max_offset = max(0, len(self.formatted_lines) - self.height)
        self.current_offset = min(max_offset, self.current_offset + lines)
        self.needs_redraw = True
    
    def render(self):
        """Отрисовывает форматированный текст"""
        if not self.visible:
            return
            
        # Заполняем фон, если указан
        if self.bg_color:
            for y in range(self.height):
                ConsoleHelper.move_cursor(self.x, self.y + y)
                print(f"{self.bg_color}{' ' * self.width}{Color.RESET}", end='')
        
        # Отображаем видимые строки с учётом смещения
        visible_lines = self.formatted_lines[self.current_offset:self.current_offset + self.height]
        
        for i, line in enumerate(visible_lines):
            if i >= self.height:
                break
                
            ConsoleHelper.move_cursor(self.x, self.y + i)
            
            if line.get("multicolor", False) and "parts" in line:
                # Рисуем многоцветную строку
                text_parts = line["parts"]
                for part in text_parts:
                    part_text = part["text"]
                    part_color = part["color"]
                    print(ConsoleHelper.colorize(part_text, part_color, self.bg_color), end='')
                # Дополняем строку пробелами до нужной ширины
                remaining_width = self.width - len(line["text"])
                if remaining_width > 0:
                    print(' ' * remaining_width, end='')
            else:
                # Рисуем обычную строку
                print(ConsoleHelper.colorize(
                    line["text"].ljust(self.width)[:self.width], 
                    line["color"], 
                    self.bg_color), end='')

class SidebarLayout(UIElement):
    """
    Компонент для создания макета с боковой панелью и основной областью.
    Автоматически адаптируется к размеру экрана.
    """
    def __init__(self, x: int, y: int, width: int, height: int, 
                sidebar_width: int, sidebar_position: str = "left",
                separator: bool = True, separator_color: str = Color.BRIGHT_BLACK):
        """
        Инициализирует макет с боковой панелью.
        
        Args:
            x, y: Координаты левого верхнего угла
            width, height: Размеры всего макета
            sidebar_width: Ширина боковой панели
            sidebar_position: Положение боковой панели ("left" или "right")
            separator: Отображать ли разделитель между панелями
            separator_color: Цвет разделителя
        """
        super().__init__(x, y, width, height)
        self.sidebar_width = min(sidebar_width, width - 1)  # Не даём боковой панели занять весь экран
        self.sidebar_position = sidebar_position
        self.separator = separator
        self.separator_color = separator_color
        
        # Создаём контейнеры для элементов
        self.sidebar_elements = []
        self.main_elements = []
    
    def add_to_sidebar(self, element: UIElement):
        """Добавляет элемент в боковую панель"""
        self.sidebar_elements.append(element)
        element.parent = self
        
        # Корректируем координаты элемента относительно боковой панели
        if self.sidebar_position == "left":
            element.x = self.x + element.x
        else:
            element.x = self.x + self.width - self.sidebar_width + element.x
            
        element.y = self.y + element.y
        self.children.append(element)
        return element
    
    def add_to_main(self, element: UIElement):
        """Добавляет элемент в основную область"""
        self.main_elements.append(element)
        element.parent = self
        
        # Корректируем координаты элемента относительно основной области
        if self.sidebar_position == "left":
            element.x = self.x + self.sidebar_width + (1 if self.separator else 0) + element.x
        else:
            element.x = self.x + element.x
            
        element.y = self.y + element.y
        self.children.append(element)
        return element
    
    def render(self):
        """Отрисовывает макет с боковой панелью"""
        if not self.visible:
            return
            
        # Рисуем разделитель, если нужно
        if self.separator:
            separator_x = self.x + self.sidebar_width if self.sidebar_position == "left" else self.x + self.width - self.sidebar_width - 1
            
            for y in range(self.height):
                ConsoleHelper.move_cursor(separator_x, self.y + y)
                print(ConsoleHelper.colorize("│", self.separator_color), end='') 