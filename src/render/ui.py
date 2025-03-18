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
                 icon: str = "", icon_color: str = Color.WHITE):
        self.text = text
        self.action = action
        self.enabled = enabled
        self.icon = icon
        self.icon_color = icon_color
    
    def activate(self):
        """
        Активирует элемент меню, вызывая связанное с ним действие.
        """
        if self.enabled and self.action:
            self.action()

class Menu(UIElement):
    """
    Вертикальное меню с выбором опций.
    """
    def __init__(self, x: int, y: int, width: int, items: List[MenuItem],
                 title: str = "", border: bool = True,
                 color: str = Color.WHITE, selected_color: str = Color.BRIGHT_WHITE,
                 disabled_color: str = Color.BRIGHT_BLACK,
                 border_color: str = Color.WHITE, bg_color: str = "",
                 selected_bg_color: str = "", title_color: str = Color.BRIGHT_WHITE):
        height = len(items) + (2 if border else 0)
        super().__init__(x, y, width, height)
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
        self.needs_redraw = True
        
        # Находим первый доступный элемент
        if items:
            for i, item in enumerate(items):
                if item.enabled:
                    self.selected_index = i
                    break
    
    def render(self):
        if not self.visible:
            return
        
        # Создаем панель для фона и границы
        if self.border:
            panel = Panel(self.x, self.y, self.width, self.height, 
                         self.title, True, self.border_color, self.bg_color, self.title_color)
            panel.render()
        
        # Рендерим элементы меню
        start_y = self.y + (1 if self.border else 0)
        for i, item in enumerate(self.items):
            ConsoleHelper.move_cursor(self.x + 2, start_y + i)
            
            # Определяем цвет текста и фона
            if not item.enabled:
                text_color = self.disabled_color
                bg_color = self.bg_color
            elif i == self.selected_index:
                text_color = self.selected_color
                bg_color = self.selected_bg_color or self.bg_color
            else:
                text_color = self.color
                bg_color = self.bg_color
            
            # Формируем отображаемый текст
            display_text = item.text
            if item.icon:
                icon_text = ConsoleHelper.colorize(item.icon, item.icon_color)
                display_text = f"{icon_text} {display_text}"
            
            # Добавляем стрелку для выбранного элемента
            if i == self.selected_index:
                display_text = f"▶ {display_text}"
            else:
                display_text = f"  {display_text}"
            
            # Обрезаем текст, если он не помещается
            max_length = self.width - 4
            if len(display_text) > max_length:
                display_text = display_text[:max_length - 3] + "..."
            
            # Выводим текст
            print(ConsoleHelper.colorize(display_text, text_color, bg_color), end='')
    
    def handle_input(self, key: int) -> bool:
        """
        Обрабатывает ввод с клавиатуры.
        """
        if key == Keys.UP:
            return self._select_previous()
        elif key == Keys.DOWN:
            return self._select_next()
        elif key == Keys.ENTER:
            self._activate_selected()
            return True
        
        return False
    
    def _select_previous(self):
        """
        Выбирает предыдущий доступный элемент меню.
        Возвращает True, если выбор изменился.
        """
        original_index = self.selected_index
        index = self.selected_index
        
        while True:
            index = (index - 1) % len(self.items)
            if index == original_index:
                # Прошли полный круг и не нашли доступного элемента
                return False
            
            if self.items[index].enabled:
                self.selected_index = index
                self.needs_redraw = True
                return True
    
    def _select_next(self):
        """
        Выбирает следующий доступный элемент меню.
        Возвращает True, если выбор изменился.
        """
        original_index = self.selected_index
        index = self.selected_index
        
        while True:
            index = (index + 1) % len(self.items)
            if index == original_index:
                # Прошли полный круг и не нашли доступного элемента
                return False
            
            if self.items[index].enabled:
                self.selected_index = index
                self.needs_redraw = True
                return True
    
    def _activate_selected(self):
        """
        Активирует выбранный элемент меню.
        """
        if 0 <= self.selected_index < len(self.items) and self.items[self.selected_index].enabled:
            self.items[self.selected_index].activate()

class ProgressBar(UIElement):
    """
    Индикатор прогресса.
    """
    def __init__(self, x: int, y: int, width: int, value: float, max_value: float,
                 color: str = Color.GREEN, bg_color: str = Color.BLACK,
                 border: bool = True, border_color: str = Color.WHITE,
                 show_percentage: bool = True):
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
        
        # Определяем ширину заполненной части
        progress = min(1.0, max(0.0, self.value / self.max_value))
        inner_width = self.width - (2 if self.border else 0)
        filled_width = int(inner_width * progress)
        
        # Рисуем границу и заполненную часть
        if self.border:
            print(ConsoleHelper.colorize('[', self.border_color), end='')
        
        print(ConsoleHelper.colorize('█' * filled_width, self.color) + 
              ConsoleHelper.colorize('░' * (inner_width - filled_width), self.bg_color), end='')
        
        if self.border:
            print(ConsoleHelper.colorize(']', self.border_color), end='')
        
        # Выводим процент, если нужно
        if self.show_percentage:
            percentage = f" {int(progress * 100)}%"
            ConsoleHelper.move_cursor(self.x + self.width + 1, self.y)
            print(ConsoleHelper.colorize(percentage, self.color), end='')
    
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