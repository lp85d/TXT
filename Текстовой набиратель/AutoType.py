import time
import keyboard
import sys
import shutil
import win32api
import win32gui
import win32process

# ==================== НАСТРОЙКИ ПРОГРАММЫ ====================

# Текст для печати
TEXT_TO_TYPE = """# Найдите Developer Command Prompt в меню Пуск или запустите:
"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat"

# Затем:
cd C:\Windows\system32\winget-cli\src
msbuild AppInstallerCLI.sln /p:Configuration=Release /p:Platform=x64"""

# Время обратного отсчета перед началом печати (секунды)
COUNTDOWN_SECONDS = 5

# Задержка между символами при печати (секунды)
TYPING_DELAY = 0.02

# Задержка после переключения раскладки (секунды)
LAYOUT_SWITCH_DELAY = 0.3

# Отправлять ли Enter после последней строки
SEND_ENTER_AT_END = True

# ==================== КОД ПРОГРАММЫ ====================

ENGLISH_LOCALE_ID = 0x0409
RUSSIAN_LOCALE_ID = 0x0419

def countdown(seconds):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rЗапуск через: {remaining} секунд ")
        sys.stdout.flush()
        time.sleep(1)
    print("\rНачинаю ввод текста...           ")

def get_current_keyboard_layout():
    hwnd = win32gui.GetForegroundWindow()
    thread_id = win32process.GetWindowThreadProcessId(hwnd)[0]
    layout_id = win32api.GetKeyboardLayout(thread_id) & (2**16 - 1)
    return layout_id

def switch_to_layout(target_layout):
    current = get_current_keyboard_layout()
    if current == target_layout:
        return True
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
    print(f"Команда для ввода (многострочный текст):\n{text.center(cols)}\n")
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
        is_last_block = block_num == len(blocks)

        if needed_layout == 'newline':
            if is_last_block and not SEND_ENTER_AT_END:
                print(f"Блок {block_num}: Последний перевод строки пропущен")
                continue
            print(f"Блок {block_num}: Переход на новую строку")
            keyboard.write("\n", delay=TYPING_DELAY)
            continue

        if needed_layout is not None and current_layout != needed_layout:
            layout_name = 'русскую' if needed_layout == RUSSIAN_LOCALE_ID else 'английскую'
            print(f"Блок {block_num}: Переключение раскладки на {layout_name}")
            if switch_to_layout(needed_layout):
                current_layout = needed_layout
                time.sleep(LAYOUT_SWITCH_DELAY)

        print(f"Блок {block_num}: Печатаю '{content}'")
        keyboard.write(content, delay=TYPING_DELAY)

    print("\nТекст напечатан.")

if __name__ == "__main__":
    print("Программа запущена.")
    print(f"Настройки: задержка {TYPING_DELAY}с между символами, отсчет {COUNTDOWN_SECONDS}с, последняя строка с Enter={SEND_ENTER_AT_END}")
    print()
    countdown(COUNTDOWN_SECONDS)
    type_text_with_layout_switch(TEXT_TO_TYPE)
