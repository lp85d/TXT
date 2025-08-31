import time
import keyboard
import sys
import shutil

# Текст команды для печати.
text = 'Get-Content README.md'

def countdown(seconds):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rЗапуск через: {remaining} секунд ")
        sys.stdout.flush()
        time.sleep(1)
    print("\rНачинаю ввод текста...           ")

def switch_layout_to_english():
    print("Переключаю раскладку на английский (Alt+Shift)...")
    keyboard.press_and_release('alt+shift')
    time.sleep(0.5)
    print("Раскладка переключена.")

def type_text(text):
    cols = shutil.get_terminal_size().columns
    centered_text = text.center(cols)
    print(f"Команда для ввода:\n{centered_text}\n")
    print("Начинаю печатать текст...")
    keyboard.write(text, delay=0.05)
    print("\nТекст напечатан.")
    print("Нажимаю Enter...")
    keyboard.press_and_release('enter')
    print("Enter нажат.")

if __name__ == "__main__":
    print("Программа запущена.")
    countdown(5)
    switch_layout_to_english()
    time.sleep(1)
    type_text(text)
