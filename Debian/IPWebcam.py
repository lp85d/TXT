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

        # Очищаем буфер кадров для минимизации задержек
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

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
        # Пропускаем старые кадры, чтобы получить наиболее свежий
        for _ in range(5):
            self.cap.grab()

        ret, frame = self.cap.read()
        if ret:
            # Конвертируем BGR (OpenCV) в RGB (PIL)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(image=img)
            
            # Обновляем изображение
            self.label.img_tk = img_tk
            self.label.configure(image=img_tk)

        # Запрашиваем следующий кадр с минимальной задержкой
        self.root.after(10, self.update_frame)

    def exit_app(self):
        self.cap.release()
        self.root.quit()

# Запуск программы
if __name__ == "__main__":
    stream_url = 'http://10.8.0.9:8080/video'
    root = tk.Tk()
    app = IPWebcamApp(root, stream_url)
    root.mainloop()
