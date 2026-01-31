import keyboard
import time
import win32api
import win32con

is_executing = False

# Виртуальные коды клавиш
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # ALT

VK_CODES = {
    'U': 0x55, 'X': 0x58, 'Q': 0x51, 'W': 0x57,
    'V': 0x56, 'A': 0x41, 'Y': 0x59, 'H': 0x48, 'P': 0x50,
    '9': 0x39, '2': 0x32, '7': 0x37
}

def force_release_all_modifiers():
    """ПРИНУДИТЕЛЬНО отпускает ВСЕ модификаторы через keybd_event"""
    print("  [FORCE RELEASE] Отпускаю Shift, Ctrl, Alt через keybd_event...")
    
    # Отпускаем левый и правый Shift
    win32api.keybd_event(0xA0, 0, win32con.KEYEVENTF_KEYUP, 0)  # Left Shift
    win32api.keybd_event(0xA1, 0, win32con.KEYEVENTF_KEYUP, 0)  # Right Shift
    win32api.keybd_event(VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Generic Shift
    
    # Отпускаем левый и правый Ctrl
    win32api.keybd_event(0xA2, 0, win32con.KEYEVENTF_KEYUP, 0)  # Left Ctrl
    win32api.keybd_event(0xA3, 0, win32con.KEYEVENTF_KEYUP, 0)  # Right Ctrl
    win32api.keybd_event(VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Generic Ctrl
    
    # Отпускаем левый и правый Alt
    win32api.keybd_event(0xA4, 0, win32con.KEYEVENTF_KEYUP, 0)  # Left Alt
    win32api.keybd_event(0xA5, 0, win32con.KEYEVENTF_KEYUP, 0)  # Right Alt
    win32api.keybd_event(VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)  # Generic Alt
    
    # Отпускаем F12
    win32api.keybd_event(0x7B, 0, win32con.KEYEVENTF_KEYUP, 0)  # F12

def press_key(vk_code):
    """Нажать клавишу через keybd_event"""
    win32api.keybd_event(vk_code, 0, 0, 0)

def release_key(vk_code):
    """Отпустить клавишу через keybd_event"""
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)

def tap_key(vk_code, delay=0.15):
    """Нажать и отпустить клавишу"""
    press_key(vk_code)
    time.sleep(0.05)
    release_key(vk_code)
    time.sleep(delay)

def type_uppercase_letter(letter, delay=0.15):
    """Ввести заглавную букву (с Shift)"""
    press_key(VK_SHIFT)
    time.sleep(0.03)
    tap_key(VK_CODES[letter], 0.05)
    release_key(VK_SHIFT)
    time.sleep(delay)

def type_digit(digit, delay=0.15):
    """Ввести цифру"""
    tap_key(VK_CODES[digit], delay)

def type_sequence():
    """Вводит последовательность через keybd_event"""
    global is_executing
    
    if is_executing:
        return
    
    is_executing = True
    
    print("\n" + "="*70)
    print(">>> НАЧАЛО ВЫПОЛНЕНИЯ")
    print("="*70)
    
    print("\n>>> ПРИНУДИТЕЛЬНО отжимаю ВСЕ клавиши...")
    
    # Сначала через keyboard
    keyboard.release('shift')
    keyboard.release('ctrl')
    keyboard.release('alt')
    keyboard.release('f12')
    time.sleep(0.1)
    
    # ЗАТЕМ через keybd_event (ГЛАВНОЕ!)
    force_release_all_modifiers()
    time.sleep(0.6)  # ДЛИННАЯ ПАУЗА чтобы система обработала
    
    print("\n>>> UXQW")
    type_uppercase_letter('U')
    type_uppercase_letter('X')
    type_uppercase_letter('Q')
    type_uppercase_letter('W')
    
    print(">>> TAB #1")
    tap_key(win32con.VK_TAB, 0.5)
    
    print(">>> 9VA2")
    type_digit('9')
    type_uppercase_letter('V')
    type_uppercase_letter('A')
    type_digit('2')
    
    print(">>> TAB #2")
    tap_key(win32con.VK_TAB, 0.5)
    
    print(">>> YVHP")
    type_uppercase_letter('Y')
    type_uppercase_letter('V')
    type_uppercase_letter('H')
    type_uppercase_letter('P')
    
    print(">>> TAB #3")
    tap_key(win32con.VK_TAB, 0.5)
    
    print(">>> AH7X")
    type_uppercase_letter('A')
    type_uppercase_letter('H')
    type_digit('7')
    type_uppercase_letter('X')
    
    print("\n" + "="*70)
    print(">>> ВВОД ЗАВЕРШЕН!")
    print("="*70 + "\n")
    
    is_executing = False

def check_hotkey(e):
    if e.name == 'f12' and e.event_type == 'down':
        if keyboard.is_pressed('shift') and keyboard.is_pressed('ctrl'):
            print("\n!!! HOTKEY DETECTED !!!")
            import threading
            threading.Thread(target=type_sequence, daemon=True).start()

print("=" * 70)
print("ПРОГРАММА ДЛЯ ИГР (С ПРИНУДИТЕЛЬНЫМ ОТЖАТИЕМ)")
print("=" * 70)
print("Последовательность: UXQW → TAB → 9VA2 → TAB → YVHP → TAB → AH7X")
print()
print("Нажмите Shift+Ctrl+F12 (руками или через SetPoint)")
print("Для выхода нажмите Ctrl+C")
print("=" * 70)
print()

keyboard.on_press_key('f12', check_hotkey)

try:
    keyboard.wait()
except KeyboardInterrupt:
    print("\n" + "=" * 70)
    print("Программа остановлена")
    print("=" * 70)