import tkinter as tk
from tkinter import messagebox
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import hashlib

class BarcodeGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор штрихкодов")
        self.root.geometry("800x600")
        self.root.configure(bg="#2b2d31")

        self.existing_urls = set()
        self.rows = []
        self.cache_dir = os.path.join(os.getcwd(), "cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.barcode_width = 100
        self.barcode_height = 30

        # Основной фрейм
        main_frame = tk.Frame(root, bg="#2b2d31")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Заголовок
        tk.Label(main_frame, text="Генератор штрихкодов", font=("Helvetica", 16, "bold"),
                 bg="#2b2d31", fg="#e5e7eb").pack(pady=(0, 15))

        # Фрейм для списка
        self.scrollable_frame = tk.Frame(main_frame, bg="#313338")
        self.scrollable_frame.pack(fill="both", expand=True)

        # Заголовки
        header_frame = tk.Frame(self.scrollable_frame, bg="#1f2023")
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Ссылки", font=("Helvetica", 10, "bold"),
                 bg="#1f2023", fg="#e5e7eb", anchor="w", padx=10).pack(side="left", fill="x", expand=True)
        tk.Label(header_frame, text="Штрихкод", font=("Helvetica", 10, "bold"),
                 bg="#1f2023", fg="#e5e7eb", width=15).pack(side="right")

        # Кнопки
        button_frame = tk.Frame(main_frame, bg="#2b2d31")
        button_frame.pack(fill="x", pady=10)

        tk.Button(button_frame, text="Вставить", command=self.paste_from_clipboard,
                  font=("Helvetica", 10, "bold"), bg="#f59e0b", fg="white").pack(side="left", padx=5, expand=True)
        tk.Button(button_frame, text="Генерировать", command=self.generate_barcodes,
                  font=("Helvetica", 10, "bold"), bg="#10b981", fg="white").pack(side="left", padx=5, expand=True)
        tk.Button(button_frame, text="Печать", command=self.print_barcodes,
                  font=("Helvetica", 10, "bold"), bg="#3b82f6", fg="white").pack(side="left", padx=5, expand=True)

    def add_row(self, url):
        row_frame = tk.Frame(self.scrollable_frame, bg="#313338")
        row_frame.pack(fill="x", padx=5, pady=2)

        url_label = tk.Label(row_frame, text=url, font=("Helvetica", 9), bg="#313338", fg="#d1d5db", anchor="w", padx=5)
        url_label.pack(side="left", fill="both", expand=True)

        barcode_label = tk.Label(row_frame, bg="#313338")
        barcode_label.pack(side="right", padx=5)

        self.rows.append((url_label, barcode_label))

    def paste_from_clipboard(self):
        try:
            clipboard_text = self.root.clipboard_get()
            urls = [line.strip() for line in clipboard_text.splitlines() if line.strip()]
            for url in urls:
                if url not in self.existing_urls:
                    self.existing_urls.add(url)
                    self.add_row(url)
        except tk.TclError:
            pass

    def generate_barcodes(self):
        EAN = barcode.get_barcode_class('ean13')

        for url_label, barcode_label in self.rows:
            url = url_label.cget("text")

            # Извлекаем нужные части ссылки
            clean_url = url.replace("https://", "").replace("http://", "")  
            short_url = clean_url[:7] + clean_url[-6:]  

            # Генерируем числовой код (только цифры, дополняем до 12 символов)
            numeric_url = ''.join(filter(str.isdigit, url))[:12].zfill(12)

            try:
                # Генерация штрихкода
                ean = EAN(numeric_url, writer=ImageWriter())
                unique_id = hashlib.md5(url.encode()).hexdigest()
                fullname = os.path.join(self.cache_dir, unique_id)
                ean.save(fullname)

                # Открываем изображение
                img = Image.open(f"{fullname}.png")
                img = img.resize((self.barcode_width, self.barcode_height), Image.LANCZOS)

                # Создаем изображение с текстом
                new_height = self.barcode_height + 20  
                new_img = Image.new("RGB", (self.barcode_width, new_height), "white")
                draw = ImageDraw.Draw(new_img)

                # Загружаем шрифт
                try:
                    font = ImageFont.truetype("arial.ttf", 10)
                except IOError:
                    font = ImageFont.load_default()

                # Центрируем текст
                text_top = short_url
                text_bottom = numeric_url

                top_bbox = draw.textbbox((0, 0), text_top, font=font)
                bottom_bbox = draw.textbbox((0, 0), text_bottom, font=font)

                top_x = (self.barcode_width - (top_bbox[2] - top_bbox[0])) // 2
                bottom_x = (self.barcode_width - (bottom_bbox[2] - bottom_bbox[0])) // 2

                draw.text((top_x, 5), text_top, fill="black", font=font)
                new_img.paste(img, (0, 18))

                # Отображение изображения в Tkinter
                photo = ImageTk.PhotoImage(new_img)
                barcode_label.config(image=photo)
                barcode_label.image = photo

            except Exception as e:
                print(f"Ошибка генерации для {url}: {str(e)}")

    def print_barcodes(self):
        messagebox.showinfo("Печать", "Функция печати еще не реализована")

if __name__ == "__main__":
    root = tk.Tk()
    app = BarcodeGenerator(root)
    root.mainloop()
