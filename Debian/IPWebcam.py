# -*- coding: utf-8 -*-
import cv2
import tkinter as tk
from tkinter import messagebox

# Функция для отображения ошибок через графический интерфейс
def show_error(message):
    root = tk.Tk()
    root.withdraw()  # Скрыть основное окно
    messagebox.showerror("Ошибка", message)
    root.quit()

# URL видеопотока с IP Webcam
stream_url = 'http://10.8.0.9:8080/video'

# Создание объекта VideoCapture
cap = cv2.VideoCapture(stream_url)

# Проверка успешности подключения
if not cap.isOpened():
    show_error("Не удалось подключиться к видеопотоку")
    exit()

# Чтение и отображение кадров
while True:
    ret, frame = cap.read()
    if not ret:
        show_error("Не удалось получить кадр")
        break

    cv2.imshow('IP Webcam Stream', frame)

    # Выход при нажатии клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождение ресурсов
cap.release()
cv2.destroyAllWindows()
