import time
import keyboard
import sys
import shutil
import win32api
import win32gui
import win32process

# ==================== НАСТРОЙКИ ПРОГРАММЫ ====================

# Текст для печати
TEXT_TO_TYPE = """Get-Content README.md
| Select-String -Pattern "Visual Studio|Build|Requirements" -A 5 -B 5

Пример четвёртого абзаца текста
С новой строки.
Текст с английскими и русскими буквами."""

# Время обратного отсчета перед началом печати (секунды)
COUNTDOWN_SECONDS = 5

# Задержка между символами при печати (секунды)
TYPING_DELAY = 0.02

# Задержка после переключения раскладки (секунды)
LAYOUT_SWITCH_DELAY = 0.3

# ==================== КОД ПРОГРАММЫ ====================

# Идентификаторы раскладок
ENGLISH_LOCALE_ID = 0x0409  # Английская
RUSSIAN_LOCALE_ID = 0x0419  # Русская

def countdown(seconds):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rЗапуск через: {remaining} секунд ")
        sys.stdout.flush()
        time.sleep(1)
    print("\rНачинаю ввод текста...           ")

def get_current_keyboard_layout():
    """Получить текущий идентификатор раскладки клавиатуры активного окна."""
    hwnd = win32gui.GetForegroundWindow()
    thread_id = win32process.GetWindowThreadProcessId(hwnd)[0]
    layout_id = win32api.GetKeyboardLayout(thread_id) & (2**16 - 1)
    return layout_id

def switch_to_layout(target_layout):
    """Переключить на конкретную раскладку."""
    current = get_current_keyboard_layout()
    if current == target_layout:
        return True
    
    # Переключаем до тех пор, пока не получим нужную раскладку
    for _ in range(3):
        keyboard.press_and_release('alt+shift')
        time.sleep(0.2)
        current = get_current_keyboard_layout()
        if current == target_layout:
            return True
    
    return False

def is_cyrillic(char):
    return '\u0400' <= char <= '\u04FF' or '\u0500' <= char <= '\u052F'

def is_latin(char):
    return char.isalpha() and not is_cyrillic(char)

def analyze_text(text):
    """Разбить текст на блоки (рус/англ + переносы строк)."""
    blocks = []
    current_block = ""
    current_layout = None
    i = 0

    while i < len(text):
        char = text[i]

        if char == '\n':
            if current_block:
                blocks.append((current_layout, current_block))
                current_block = ""

            # считаем сколько подряд переводов строк
            newline_count = 1
            while i + 1 < len(text) and text[i + 1] == '\n':
                newline_count += 1
                i += 1

            for _ in range(newline_count):
                blocks.append(('newline', '\n'))

            current_layout = None

        elif is_cyrillic(char):
            needed_layout = RUSSIAN_LOCALE_ID
            if current_layout != needed_layout:
                if current_block:
                    blocks.append((current_layout, current_block))
                    current_block = ""
                current_layout = needed_layout
            current_block += char

        elif is_latin(char):
            needed_layout = ENGLISH_LOCALE_ID
            if current_layout != needed_layout:
                if current_block:
                    blocks.append((current_layout, current_block))
                    current_block = ""
                current_layout = needed_layout
            current_block += char

        else:
            current_block += char

        i += 1

    if current_block:
        blocks.append((current_layout, current_block))

    return blocks

def type_text_with_layout_switch(text):
    cols = shutil.get_terminal_size().columns
    centered_text = text.center(cols)
    print(f"Команда для ввода (многострочный текст):\n{centered_text}\n")
    
    print("Анализирую текст...")
    blocks = analyze_text(text)
    
    print("План печати:")
    for i, (layout, content) in enumerate(blocks, 1):
        if layout == 'newline':
            print(f"  {i}. [ENTER]")
        elif layout == RUSSIAN_LOCALE_ID:
            print(f"  {i}. [РУССКАЯ] '{content}'")
        elif layout == ENGLISH_LOCALE_ID:
            print(f"  {i}. [АНГЛИЙСКАЯ] '{content}'")
        else:
            print(f"  {i}. [ТЕКУЩАЯ] '{content}'")
    print()
    
    print("Начинаю печатать текст блоками...")
    current_layout = None
    
    for block_num, (needed_layout, content) in enumerate(blocks, 1):
        if needed_layout == 'newline':
            print(f"Блок {block_num}: Переход на новую строку")
            # именно так, чтобы enter гарантированно отработал
            keyboard.write("\n", delay=TYPING_DELAY)
            continue
        
        if needed_layout is not None and current_layout != needed_layout:
            layout_name = 'русскую' if needed_layout == RUSSIAN_LOCALE_ID else 'английскую'
            print(f"Блок {block_num}: Переключение раскладки на {layout_name}")
            
            if switch_to_layout(needed_layout):
                current_layout = needed_layout
                time.sleep(LAYOUT_SWITCH_DELAY)
            else:
                print(f"Не удалось переключить раскладку!")
        
        print(f"Блок {block_num}: Печатаю '{content}'")
        keyboard.write(content, delay=TYPING_DELAY)
    
    print("\nТекст напечатан.")

if __name__ == "__main__":
    print("Программа запущена.")
    print(f"Настройки: задержка {TYPING_DELAY}с между символами, отсчет {COUNTDOWN_SECONDS}с")
    print()
    
    countdown(COUNTDOWN_SECONDS)
    type_text_with_layout_switch(TEXT_TO_TYPE)
