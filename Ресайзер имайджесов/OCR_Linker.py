import cv2
import numpy as np

input_path = r"C:\Users\user\Desktop\project\7\debug_ocr_images\card_01\pin2_01_original.png"
output_path = r"C:\Users\user\Desktop\project\7\debug_ocr_images\card_01\1.png"

scale_percent_width = 600
scale_percent_height = 600

blur_kernel_size = (3, 3)
threshold_value = 229
dilate_kernel_size = 2
dilate_iterations = 10
min_object_area = 5
max_gap = 9
min_digit_separation = 10
max_line_thickness = 100
min_line_thickness = 1

def get_contour_bbox(contour):
    return cv2.boundingRect(contour)

def group_contours_by_digits(contours):
    if not contours:
        return []
    
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

img = cv2.imread(input_path)

# Масштабирование изображения
width = int(img.shape[1] * scale_percent_width / 100)
height = int(img.shape[0] * scale_percent_height / 100)
dim = (width, height)
resized_img = cv2.resize(img, dim, interpolation = cv2.INTER_LANCZOS4) # Использование INTER_LANCZOS4 для лучшего качества

gray = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY) # Используем resized_img
blur = cv2.GaussianBlur(gray, blur_kernel_size, 0)
_, binary = cv2.threshold(blur, threshold_value, 255, cv2.THRESH_BINARY_INV)

kernel = np.ones((dilate_kernel_size, dilate_kernel_size), np.uint8)
dilated = cv2.dilate(binary, kernel, iterations=dilate_iterations)

contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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

        if min_dist <= max_gap:
            normalized_dist = min_dist / max_gap
            float_thickness = max_line_thickness - (normalized_dist * (max_line_thickness - min_line_thickness))
            thickness = max(min_line_thickness, int(round(float_thickness)))
            
            cv2.line(connected, tuple(p1.astype(int)), tuple(p2.astype(int)), 255, thickness)

num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(connected, connectivity=8)
cleaned = np.zeros_like(connected)
for i in range(1, num_labels):
    if stats[i, cv2.CC_STAT_AREA] > min_object_area:
        cleaned[labels == i] = 255

result = cv2.bitwise_not(cleaned)
cv2.imwrite(output_path, result)
