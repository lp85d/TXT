import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("1000x700")
        
        # Переменные для параметров обработки
        self.scale_percent_width = tk.IntVar(value=600)
        self.scale_percent_height = tk.IntVar(value=600)
        self.blur_kernel_size = tk.IntVar(value=3)
        self.threshold_value = tk.IntVar(value=229)
        self.dilate_kernel_size = tk.IntVar(value=2)
        self.dilate_iterations = tk.IntVar(value=10)
        self.min_object_area = tk.IntVar(value=5)
        self.max_gap = tk.IntVar(value=9)
        self.min_digit_separation = tk.IntVar(value=10)
        self.max_line_thickness = tk.IntVar(value=100)
        self.min_line_thickness = tk.IntVar(value=1)
        
        self.input_path = ""
        self.output_path = ""
        self.original_image = None
        self.processed_image = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Основные фреймы
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Левая панель - параметры
        left_frame = ttk.LabelFrame(main_frame, text="Параметры обработки", padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W), padx=(0, 10))
        
        # Правая панель - изображения
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Конфигурация весов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Параметры обработки
        params = [
            ("Масштаб по ширине (%):", self.scale_percent_width, 100, 1000),
            ("Масштаб по высоте (%):", self.scale_percent_height, 100, 1000),
            ("Размер ядра размытия:", self.blur_kernel_size, 1, 15),
            ("Порог бинаризации:", self.threshold_value, 0, 255),
            ("Размер ядра дилатации:", self.dilate_kernel_size, 1, 10),
            ("Итерации дилатации:", self.dilate_iterations, 1, 20),
            ("Мин. площадь объекта:", self.min_object_area, 1, 100),
            ("Макс. расстояние:", self.max_gap, 1, 50),
            ("Мин. разделение цифр:", self.min_digit_separation, 1, 50),
            ("Макс. толщина линии:", self.max_line_thickness, 1, 200),
            ("Мин. толщина линии:", self.min_line_thickness, 1, 50)
        ]
        
        for i, (label, var, min_val, max_val) in enumerate(params):
            ttk.Label(left_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Scale(left_frame, from_=min_val, to=max_val, variable=var, 
                     orient=tk.HORIZONTAL, length=200).grid(row=i, column=1, pady=2, padx=(5, 0))
            ttk.Label(left_frame, textvariable=var).grid(row=i, column=2, padx=(5, 0))
        
        # Кнопки управления
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=len(params), column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Выбрать изображение", command=self.select_image).pack(pady=5, fill=tk.X)
        ttk.Button(button_frame, text="Обработать", command=self.process_image).pack(pady=5, fill=tk.X)
        ttk.Button(button_frame, text="Сохранить результат", command=self.save_image).pack(pady=5, fill=tk.X)
        ttk.Button(button_frame, text="Сбросить настройки", command=self.reset_settings).pack(pady=5, fill=tk.X)
        
        # Область для изображений
        images_frame = ttk.LabelFrame(right_frame, text="Изображения")
        images_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Исходное изображение
        orig_frame = ttk.Frame(images_frame)
        orig_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        ttk.Label(orig_frame, text="Исходное изображение").pack()
        self.original_canvas = tk.Canvas(orig_frame, width=400, height=300, bg='white')
        self.original_canvas.pack(pady=5)
        
        # Обработанное изображение
        proc_frame = ttk.Frame(images_frame)
        proc_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        ttk.Label(proc_frame, text="Обработанное изображение").pack()
        self.processed_canvas = tk.Canvas(proc_frame, width=400, height=300, bg='white')
        self.processed_canvas.pack(pady=5)
        
        # Конфигурация весов для изображений
        images_frame.columnconfigure(0, weight=1)
        images_frame.columnconfigure(1, weight=1)
        images_frame.rowconfigure(0, weight=1)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if file_path:
            self.input_path = file_path
            self.load_original_image()
            self.status_var.set(f"Загружено изображение: {os.path.basename(file_path)}")
    
    def load_original_image(self):
        try:
            self.original_image = cv2.imread(self.input_path)
            if self.original_image is None:
                messagebox.showerror("Ошибка", "Не удалось загрузить изображение")
                return
            
            # Масштабируем для отображения
            display_img = self.resize_image_for_display(self.original_image)
            self.display_image_on_canvas(display_img, self.original_canvas)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке изображения: {str(e)}")
    
    def resize_image_for_display(self, image, max_size=(400, 300)):
        height, width = image.shape[:2]
        
        # Вычисляем коэффициенты масштабирования
        scale_x = max_size[0] / width
        scale_y = max_size[1] / height
        scale = min(scale_x, scale_y)
        
        if scale < 1:
            new_width = int(width * scale)
            new_height = int(height * scale)
            return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return image
    
    def display_image_on_canvas(self, image, canvas):
        # Конвертируем BGR в RGB
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Конвертируем в формат для tkinter
        pil_image = Image.fromarray(image_rgb)
        tk_image = ImageTk.PhotoImage(pil_image)
        
        # Очищаем canvas и отображаем изображение
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
        canvas.image = tk_image  # Сохраняем ссылку
    
    def process_image(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала выберите изображение")
            return
        
        try:
            self.status_var.set("Обработка изображения...")
            self.root.update()
            
            # Получаем параметры из интерфейса
            params = {
                'scale_percent_width': self.scale_percent_width.get(),
                'scale_percent_height': self.scale_percent_height.get(),
                'blur_kernel_size': (self.blur_kernel_size.get(), self.blur_kernel_size.get()),
                'threshold_value': self.threshold_value.get(),
                'dilate_kernel_size': self.dilate_kernel_size.get(),
                'dilate_iterations': self.dilate_iterations.get(),
                'min_object_area': self.min_object_area.get(),
                'max_gap': self.max_gap.get(),
                'min_digit_separation': self.min_digit_separation.get(),
                'max_line_thickness': self.max_line_thickness.get(),
                'min_line_thickness': self.min_line_thickness.get()
            }
            
            # Обрабатываем изображение
            processed = self.process_image_with_params(self.original_image, params)
            self.processed_image = processed
            
            # Отображаем результат
            display_img = self.resize_image_for_display(processed)
            self.display_image_on_canvas(display_img, self.processed_canvas)
            
            self.status_var.set("Обработка завершена")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обработке изображения: {str(e)}")
            self.status_var.set("Ошибка обработки")
    
    def process_image_with_params(self, img, params):
        # Масштабирование изображения
        width = int(img.shape[1] * params['scale_percent_width'] / 100)
        height = int(img.shape[0] * params['scale_percent_height'] / 100)
        dim = (width, height)
        resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_LANCZOS4)

        gray = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, params['blur_kernel_size'], 0)
        _, binary = cv2.threshold(blur, params['threshold_value'], 255, cv2.THRESH_BINARY_INV)

        kernel = np.ones((params['dilate_kernel_size'], params['dilate_kernel_size']), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=params['dilate_iterations'])

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Функции для обработки контуров
        def get_contour_bbox(contour):
            return cv2.boundingRect(contour)

        def group_contours_by_digits(contours):
            if not contours:
                return []
            
            min_digit_separation = params['min_digit_separation']
            
            sorted_data = sorted(
                [(i, get_contour_bbox(c)) for i, c in enumerate(contours)], 
                key=lambda x: x[1][0]
            )
            
            groups = []
            if not sorted_data:
                return groups

            current_group_indices = [sorted_data[0][0]]
            
            for i in range(1, len(sorted_data)):
                current_idx, current_bbox = sorted_data[i]
                prev_idx, prev_bbox = sorted_data[i-1]
                
                prev_right = prev_bbox[0] + prev_bbox[2]
                current_left = current_bbox[0]
                horizontal_gap = current_left - prev_right
                
                if horizontal_gap > min_digit_separation:
                    groups.append(current_group_indices)
                    current_group_indices = [current_idx]
                else:
                    current_group_indices.append(current_idx)
            
            groups.append(current_group_indices)
            return groups

        def find_closest_points(contour1, contour2):
            cnt1_points = contour1.reshape(-1, 2)
            cnt2_points = contour2.reshape(-1, 2)
            
            min_distance = float('inf')
            best_p1, best_p2 = None, None
            
            step1 = max(1, len(cnt1_points) // 20)
            step2 = max(1, len(cnt2_points) // 20)
            
            for p1 in cnt1_points[::step1]:
                for p2 in cnt2_points[::step2]:
                    dist = np.linalg.norm(p1 - p2)
                    if dist < min_distance:
                        min_distance = dist
                        best_p1, best_p2 = p1, p2
            
            return min_distance, best_p1, best_p2

        contour_map = {i: contours[i] for i in range(len(contours))}
        contour_groups_indices = group_contours_by_digits(contours)

        connected = dilated.copy()

        for i, group_indices in enumerate(contour_groups_indices):
            sorted_group_indices = sorted(group_indices, key=lambda idx: get_contour_bbox(contour_map[idx])[0])
            
            for j in range(len(sorted_group_indices) - 1):
                idx1 = sorted_group_indices[j]
                idx2 = sorted_group_indices[j+1]

                contour1 = contour_map[idx1]
                contour2 = contour_map[idx2]

                min_dist, p1, p2 = find_closest_points(contour1, contour2)

                if min_dist <= params['max_gap']:
                    normalized_dist = min_dist / params['max_gap']
                    float_thickness = params['max_line_thickness'] - (normalized_dist * (params['max_line_thickness'] - params['min_line_thickness']))
                    thickness = max(params['min_line_thickness'], int(round(float_thickness)))
                    
                    cv2.line(connected, tuple(p1.astype(int)), tuple(p2.astype(int)), 255, thickness)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(connected, connectivity=8)
        cleaned = np.zeros_like(connected)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] > params['min_object_area']:
                cleaned[labels == i] = 255

        result = cv2.bitwise_not(cleaned)
        return result
    
    def save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Предупреждение", "Сначала обработайте изображение")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                cv2.imwrite(file_path, self.processed_image)
                self.status_var.set(f"Изображение сохранено: {os.path.basename(file_path)}")
                messagebox.showinfo("Успех", "Изображение успешно сохранено")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def reset_settings(self):
        # Сброс к значениям по умолчанию
        self.scale_percent_width.set(600)
        self.scale_percent_height.set(600)
        self.blur_kernel_size.set(3)
        self.threshold_value.set(229)
        self.dilate_kernel_size.set(2)
        self.dilate_iterations.set(10)
        self.min_object_area.set(5)
        self.max_gap.set(9)
        self.min_digit_separation.set(10)
        self.max_line_thickness.set(100)
        self.min_line_thickness.set(1)
        
        self.status_var.set("Настройки сброшены к значениям по умолчанию")

def main():
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()