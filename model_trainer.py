import pandas as pd
import numpy as np
import xgboost as xgb
import colorsys
import os

HARMONY_TYPES = ['analogous', 'monochromatic', 'complementary', 'split_complementary', 'triad']

def hex_to_hsv(hex_color):
    """Chuyển HEX sang HSV"""
    hex_color = str(hex_color).lstrip('#')
    if len(hex_color) != 6: return [0.0, 0.0, 0.0]
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return list(colorsys.rgb_to_hsv(r, g, b))

def create_padded_features(color_list):
    """Biến danh sách màu có độ dài bất kỳ (2-5) thành 18 con số chuẩn hóa"""
    features = []
    for color in color_list:
        features.extend(hex_to_hsv(color))
        
    # Padding: Điền -1.0 cho các màu còn thiếu (Tối đa 6 màu = 18 số)
    while len(features) < 18:
        features.extend([-1.0, -1.0, -1.0])
        
    return features

def prepare_data_with_augmentation(file_path):
    """Đọc dữ liệu và Tự động sinh thêm các kịch bản 2, 3, 5 màu"""
    if not os.path.exists(file_path):
        return None, None
        
    df = pd.read_csv(file_path)
    if df.empty:
        return None, None

    X_features = []
    y_labels = []

    for index, row in df.iterrows():
        try:
            # Dữ liệu gốc 4 màu từ ColorHunt
            c1, c2, c3, c4 = str(row.iloc[0]), str(row.iloc[1]), str(row.iloc[2]), str(row.iloc[3])
            score = float(row.iloc[4])
            log_score = np.log1p(score)
            
            base_colors = [c1, c2, c3, c4]

            # 1. Nạp bản gốc (4 màu)
            X_features.append(create_padded_features(base_colors))
            y_labels.append(log_score)

            # 2. Sinh ra bản 3 màu (Dùng cho Triad, Split Complementary)
            X_features.append(create_padded_features(base_colors[:3]))
            y_labels.append(log_score)

            # 3. Sinh ra bản 2 màu (Dùng cho Complementary)
            X_features.append(create_padded_features(base_colors[:2]))
            y_labels.append(log_score)

            # 4. Sinh ra bản 5 màu (Dùng cho Analogous, Monochromatic)
            # Kỹ thuật: Lấy 4 màu gốc và thêm màu thứ 2 vào làm màu nhấn thứ 5
            X_features.append(create_padded_features(base_colors + [c2]))
            y_labels.append(log_score)

        except Exception:
            continue

    return np.array(X_features), np.array(y_labels)

def train_and_save_experts():
    print("🧠 BẮT ĐẦU HUẤN LUYỆN 5 CHUYÊN GIA (HỖ TRỢ ĐA DỮ LIỆU INPUT)...\n")
    os.makedirs("models", exist_ok=True)
    
    for harmony in HARMONY_TYPES:
        file_path = f"data_{harmony}.csv"
        print(f"--- Đang nạp sách giáo khoa cho [Chuyên gia {harmony.upper()}] ---")
        
        # Gọi hàm xử lý dữ liệu nâng cao
        X, y = prepare_data_with_augmentation(file_path)
        
        if X is None or len(X) < 3:
            print(f"⚠️ Bỏ qua chuyên gia [{harmony}]. Không có dữ liệu.")
            continue
            
        print(f"✅ Đã tạo ra {len(X)} kịch bản màu sắc (Bao gồm 2,3,4,5 màu). Đang huấn luyện...")
        
        model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5, # Tăng độ sâu vì dữ liệu giờ đã phức tạp hơn
            random_state=42,
            objective='reg:squarederror'
        )
        
        model.fit(X, y)
        
        model_path = f"models/expert_{harmony}.json"
        model.save_model(model_path)
        print(f"💾 Đã lưu não bộ mới vào: {model_path}\n")

    print("Model training finished!")

if __name__ == "__main__":
    train_and_save_experts()