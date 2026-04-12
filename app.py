import streamlit as st
import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt

def hex_to_hsl(hex_str):
    hex_str = hex_str.lstrip('#')
    r, g, b = tuple(int(hex_str[i:i+2], 16) for i in range(0, 6, 2))
    r, g, b = r/255.0, g/255.0, b/255.0
    mx, mn = max(r, g, b), min(r, g, b)
    df, l = mx - mn, (mx + mn) / 2
    if df == 0: h, s = 0, 0
    else:
        s = df / (1 - abs(2*l - 1))
        if mx == r: h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g: h = (60 * ((b - r) / df) + 120) % 360
        else: h = (60 * ((r - g) / df) + 240) % 360
    return h, s*100, l*100

# Load model và tên cột
with open('color_model.pkl', 'rb') as f:
    data_saved = pickle.load(f)
    model = data_saved['model']
    feature_names = data_saved['feature_names']

st.title("Color Harmony Analysis")
st.write("Phân tích sự hài hòa của các tổ hợp màu sắc (3-5 màu) dựa trên lý thuyết màu sắc (Tương đồng, Bổ sung, Tam giác, v.v.).")
st.write("Analyze the harmony of color combinations (3-5 colors) based on color theory (Analogous, Complementary, Triadic, etc.).")
st.divider()

num_colors = st.select_slider("Số lượng màu (Number of colors):", options=[3, 4, 5])
cols = st.columns(num_colors)
active_colors = []
for i in range(num_colors):
    with cols[i]:
        c = st.color_picker(f"Color {i+1}", value=["#FF5733", "#FFC300", "#DAF7A6", "#581845", "#900C3F"][i])
        active_colors.append(c)

if st.button("Phân tích (Analyze)", type="primary"):
    # Tạo dictionary chứa dữ liệu
    input_data = {'num_colors': num_colors}
    for i in range(1, 6):
        if i <= num_colors:
            h, s, l = hex_to_hsl(active_colors[i-1])
            input_data[f'H{i}_sin'] = np.sin(np.radians(h))
            input_data[f'H{i}_cos'] = np.cos(np.radians(h))
            input_data[f'S{i}'] = s / 100.0
            input_data[f'L{i}'] = l / 100.0
        else:
            input_data[f'H{i}_sin'] = 0.0
            input_data[f'H{i}_cos'] = 0.0
            input_data[f'S{i}'] = 0.0
            input_data[f'L{i}'] = 0.0
            
    # Ép dữ liệu vào DataFrame với đúng thứ tự cột mà Model yêu cầu
    input_df = pd.DataFrame([input_data])[feature_names]
    
    score = model.predict(input_df)[0]
    
    st.divider()
    st.metric("Harmony Score", f"{score:.2f} / 10")
    
    if score >= 8.5:
        st.success("Tuyệt đỉnh! Đây là một tổ hợp màu chuẩn mực. (Awesome! This is a perfect color combination.)")
        st.balloons()
    elif score >= 7.0:
        st.info("Rất tốt! Các màu sắc phối hợp khá ăn ý. (Very good! The colors complement each other quite well.)")
    else:
        st.warning("Hơi thiếu hài hòa. Bạn thử thay đổi độ sáng hoặc dùng các màu đối diện trên vòng tròn màu xem sao. (A little bit out of balance. Try changing the brightness or using the opposite colors on the color wheel.)")

st.divider()
st.write("Source code: [ML-color-harmony](https://github.com/chairman-q/ML-color-harmony)")

# venv\Scripts\activate
# streamlit run app.py