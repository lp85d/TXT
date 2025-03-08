# IP Webcam Stream GUI (без консоли)

Этот проект использует OpenCV и Tkinter для отображения видеопотока с IP Webcam в графическом интерфейсе без консоли.

## Установка зависимостей

Перед запуском убедитесь, что у вас установлены все необходимые пакеты:

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-tk libopencv-dev
pip3 install opencv-python pillow
```

## Код программы

```python
# -*- coding: utf-8 -*-
import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class IPWebcamApp:
    def __init__(self, root, stream_url):
        self.root = root
        self.root.title("IP Webcam Stream")
        
        # Подключение к видеопотоку
        self.cap = cv2.VideoCapture(stream_url)
        if not self.cap.isOpened():
            self.show_error("Не удалось подключиться к видеопотоку")
            return

        # Создание метки для отображения видео
        self.label = tk.Label(root)
        self.label.pack()

        # Кнопка выхода
        self.btn_exit = tk.Button(root, text="Выход", command=self.exit_app)
        self.btn_exit.pack()

        # Запуск обновления кадра
        self.update_frame()

    def show_error(self, message):
        messagebox.showerror("Ошибка", message)
        self.root.quit()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Конвертируем BGR (OpenCV) в RGB (PIL)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(image=img)
            
            # Обновляем изображение
            self.label.img_tk = img_tk
            self.label.configure(image=img_tk)

        # Запрашиваем следующий кадр
        self.root.after(30, self.update_frame)

    def exit_app(self):
        self.cap.release()
        self.root.quit()

# Запуск программы
if __name__ == "__main__":
    stream_url = 'http://10.8.0.9:8080/video'
    root = tk.Tk()
    app = IPWebcamApp(root, stream_url)
    root.mainloop()
```

## Компиляция в исполняемый файл для Debian 10

### 1. Установка `pyinstaller`

```bash
pip3 install pyinstaller
```

### 2. Компиляция без консоли

```bash
pyinstaller --noconsole --onefile --windowed OpenCV.py
```

После компиляции исполняемый файл будет находиться в папке `dist/`.

## Создание `.deb` пакета (опционально)

Если необходимо создать `.deb` пакет для Debian 10, можно использовать `dpkg-deb`:

```bash
mkdir -p myapp/DEBIAN
mkdir -p myapp/usr/local/bin
cp dist/OpenCV myapp/usr/local/bin/

cat <<EOF > myapp/DEBIAN/control
Package: ipwebcam-stream
Version: 1.0
Section: base
Priority: optional
Architecture: amd64
Depends: python3, python3-tk, libopencv-dev
Maintainer: Ваше Имя <email@example.com>
Description: GUI-приложение для просмотра видеопотока с IP Webcam.
EOF

dpkg-deb --build myapp
```

После этого появится файл `myapp.deb`, который можно установить командой:

```bash
sudo dpkg -i myapp.deb
```

