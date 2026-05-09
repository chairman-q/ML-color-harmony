import numpy as np
import xgboost as xgb
import colorsys
import os

# --- 1. TÁI SỬ DỤNG BỘ CÔNG CỤ TOÁN HỌC ---
def hex_to_hsv(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return list(colorsys.rgb_to_hsv(r, g, b))

def phan_loai_harmony(hex_list):
    hsv_list = [hex_to_hsv(c) for c in hex_list]
    hues = [hsv[0] * 360 for hsv in hsv_list]
    
    distances = []
    max_hue_diff = 0
    for i in range(len(hues)):
        for j in range(i+1, len(hues)):
            diff = min(abs(hues[i] - hues[j]), 360 - abs(hues[i] - hues[j]))
            distances.append(diff)
            if diff > max_hue_diff: max_hue_diff = diff
            
    # Phân loại thành 5 nhãn (Đã bỏ Shades theo Cách 1)
    if max_hue_diff < 15: return "monochromatic"
    if max_hue_diff < 90: return "analogous"
    if any(165 <= d <= 180 for d in distances): return "complementary"
    if any(145 <= d < 165 for d in distances): return "split_complementary"
    if any(105 <= d < 145 for d in distances): return "triad"
    
    return "others"

# --- 2. LOGIC DỰ ĐOÁN CỦA AI ---
def danh_gia_palette(hex_list):
    print(f"\n🎨 Đang phân tích bảng màu: {hex_list}")
    
    # 1. Tự động xác định loại Harmony
    label = phan_loai_harmony(hex_list)
    if label == "others":
        return "❌ Bảng màu này không theo 5 quy luật cơ bản. Máy từ chối đánh giá."
    
    print(f"🏷️ Hệ thống nhận diện: [{label.upper()}] -> Đang gọi Chuyên gia tương ứng...")
    
    # 2. Tìm và nạp não bộ của Chuyên gia đó
    model_path = f"models/expert_{label}.json"
    if not os.path.exists(model_path):
        return f"⚠️ Lỗi: Không tìm thấy file não bộ '{model_path}'. Chuyên gia này chưa được huấn luyện!"
        
    model = xgb.XGBRegressor()
    model.load_model(model_path)
    
    # 3. Chuẩn bị dữ liệu (Biến mã HEX thành 18 con số HSV)
    features = []
    for color in hex_list:
        features.extend(hex_to_hsv(color))
        
    # Padding (Điền khuyết) nếu người dùng nhập ít hơn 6 màu
    mau_con_thieu = 6 - len(hex_list)
    for _ in range(mau_con_thieu):
        features.extend([-1.0, -1.0, -1.0])
        
    X_input = np.array([features])
    
    # 4. Yêu cầu Chuyên gia dự đoán
    raw_prediction = model.predict(X_input)[0]
    
    # Giải mã Logarit (Vì lúc train ta dùng log1p, giờ phải dùng expm1 để trả về số Like thật)
    predicted_likes = np.expm1(raw_prediction)
    
    # Chuyển đổi lượt Like thành Điểm Hài Hòa (Thang 0.0 -> 10.0)
    # Giả định 1 bảng màu siêu phẩm đạt 10,000 like tương đương 10 điểm.
    harmony_score = min((predicted_likes / 10000) * 10, 10.0)
    
    return harmony_score, int(predicted_likes)

# --- 3. CHẠY THỬ NGHIỆM ---
if __name__ == "__main__":
    print("="*50)
    print("🚀 HỆ THỐNG ĐÁNH GIÁ SỰ HÀI HÒA MÀU SẮC (AI EVALUATOR)")
    print("="*50)
    
    # BẠN CÓ THỂ THAY ĐỔI CÁC MÃ MÀU Ở ĐÂY ĐỂ CHẤM ĐIỂM
    # Ví dụ 1: Một bảng màu Analogous (Tương đồng - xanh lá / vàng)
    palette_1 = ['#A8E6CF', '#DCEDC1', '#FFD3B6', '#FFAAA5']
    
    # Ví dụ 2: Một bảng màu Complementary (Bổ túc - Đỏ / Xanh dương)
    palette_2 = ['#FF4C4C', '#4C4CFF', '#FF9999', '#9999FF']

    # Chấm điểm ví dụ 1
    result1 = danh_gia_palette(palette_1)
    if isinstance(result1, tuple):
        score, likes = result1
        print(f"🌟 ĐIỂM HÀI HÒA: {score:.2f} / 10.0  (Dự kiến thu hút: ~{likes} lượt thích)")
    else:
        print(result1)

    # Chấm điểm ví dụ 2
    result2 = danh_gia_palette(palette_2)
    if isinstance(result2, tuple):
        score, likes = result2
        print(f"🌟 ĐIỂM HÀI HÒA: {score:.2f} / 10.0  (Dự kiến thu hút: ~{likes} lượt thích)")
    else:
        print(result2)