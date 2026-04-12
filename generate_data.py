import pandas as pd
import numpy as np
import random

def get_harmony_type(hues):
    hues = sorted(hues)
    gaps = [hues[i] - hues[i-1] for i in range(1, len(hues))]
    gaps.append(360 - hues[-1] + hues[0])
    max_gap = max(gaps)
    
    # Monochromatic (Các màu gần như trùng Hue)
    if max_gap > 340: return "Monochromatic", 9.0
    # Analogous (Các màu nằm trong khoảng 90 độ)
    if max_gap > 270: return "Analogous", 8.5
    # Complementary (Có khoảng cách gần 180 độ)
    if any(170 <= g <= 190 for g in gaps): return "Complementary", 9.0
    # Triadic (Có khoảng cách gần 120 độ)
    if any(110 <= g <= 130 for g in gaps): return "Triadic", 8.5
    
    return "Random", 4.0

data = []
for _ in range(5000): # Tăng lên 5000 mẫu cho "no" dữ liệu
    num_colors = random.choice([3, 4, 5])
    mode = random.choice(["Analogous", "Complementary", "Triadic", "Monochromatic", "Random"])
    
    base_h = random.randint(0, 360)
    palette = []
    
    for i in range(num_colors):
        if mode == "Monochromatic":
            h = (base_h + random.randint(-5, 5)) % 360
        elif mode == "Analogous":
            h = (base_h + random.randint(-40, 40)) % 360
        elif mode == "Complementary" and i % 2 == 1:
            h = (base_h + 180 + random.randint(-10, 10)) % 360
        elif mode == "Triadic":
            h = (base_h + (i * 120) + random.randint(-10, 10)) % 360
        else:
            h = random.randint(0, 360)
        
        s = random.randint(40, 90) # Ưu tiên màu có độ bão hòa khá
        l = random.randint(30, 80) # Tránh quá tối hoặc quá sáng
        palette.append([h, s, l])
    
    # Tính điểm chuẩn
    _, base_score = get_harmony_type([p[0] for p in palette])
    
    # Thêm điểm thưởng cho sự cân bằng Sáng/Tối (Contrast)
    l_values = [p[2] for p in palette]
    contrast = np.std(l_values)
    if contrast > 15: base_score += 1.0
    
    final_score = min(10.0, base_score + random.uniform(-0.5, 0.5))
    
    row = {'num_colors': num_colors}
    for i in range(5):
        if i < num_colors:
            row[f'H{i+1}'], row[f'S{i+1}'], row[f'L{i+1}'] = palette[i]
        else:
            row[f'H{i+1}'], row[f'S{i+1}'], row[f'L{i+1}'] = -1, -1, -1
    row['harmony_score'] = round(final_score, 2)
    data.append(row)

pd.DataFrame(data).to_csv('color_dataset.csv', index=False)
print("Đã tạo xong Dataset chuẩn!")

# python generate_data.py