import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pickle

# 1. Đọc dữ liệu
df = pd.read_csv('color_dataset.csv')

# 2. Hàm chuyển đổi tính toán Sin/Cos cho Hue
def transform_features(data):
    new_data = pd.DataFrame()
    new_data['num_colors'] = data['num_colors']
    
    for i in range(1, 6):
        h = data[f'H{i}']
        # Chuyển H sang Sin/Cos để máy hiểu vòng tròn màu 0-360
        new_data[f'H{i}_sin'] = np.where(h == -1, 0, np.sin(np.radians(h)))
        new_data[f'H{i}_cos'] = np.where(h == -1, 0, np.cos(np.radians(h)))
        new_data[f'S{i}'] = data[f'S{i}'] / 100.0
        new_data[f'L{i}'] = data[f'L{i}'] / 100.0
    return new_data

# Chuẩn bị dữ liệu
X = transform_features(df.drop('harmony_score', axis=1))
y = df['harmony_score']

# Lưu danh sách tên cột để app.py dùng theo đúng thứ tự
feature_names = X.columns.tolist()

# 3. Huấn luyện
model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42)
model.fit(X, y)

# 4. Lưu mô hình VÀ danh sách tên cột
with open('color_model.pkl', 'wb') as f:
    pickle.dump({'model': model, 'feature_names': feature_names}, f)

print("Đã luyện xong AI mới và lưu kèm danh sách tính năng!")

# python train_model.py