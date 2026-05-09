import streamlit as st
import numpy as np
import xgboost as xgb
import colorsys
import os

# --- 1. TỪ ĐIỂN MÔ TẢ (Phải đặt ở đầu để tránh KeyError) ---
harmony_descriptions = {
    "Analogous": "Gồm các màu nằm liền kề nhau trên vòng tròn màu, tạo cảm giác hài hòa, tự nhiên và êm dịu. (Uses adjacent colors on the color wheel, creating a harmonious, natural, and soft feeling.)",
    "Monochromatic": "Sử dụng một màu gốc duy nhất nhưng biến thiên về độ sáng/tối, mang lại sự thanh lịch và tối giản. (Uses one base hue with lightness/value variations, resulting in an elegant and minimal style.)",
    "Complementary": "Gồm các màu nằm đối diện trực tiếp nhau trên vòng tròn màu, tạo độ tương phản mạnh mẽ và rực rỡ. (Uses opposite colors on the wheel, producing strong and vibrant contrast.)",
    "Split Complementary": "Dùng 1 màu chính kết hợp với 2 màu nằm sát bên cạnh màu đối diện, dịu hơn Complementary. (Uses one base color plus two neighbors of its opposite, softer than a direct complementary scheme.)",
    "Triad": "Gồm 3 màu tạo thành một tam giác đều trên vòng tròn màu, mang lại sự sống động và cân bằng. (Uses three evenly spaced colors on the wheel, giving a lively and balanced palette.)"
}

# --- 2. LOGIC TOÁN HỌC & AI ---
def hex_to_hsv(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return list(colorsys.rgb_to_hsv(r, g, b))

def danh_gia_palette_chuyen_gia(harmony_label, hex_list):
    # Chuyển nhãn sang viết thường để khớp với file .json (vd: expert_analogous.json)
    model_name = harmony_label.lower().replace(' ', '_')
    model_path = f"models/expert_{model_name}.json"
    
    if not os.path.exists(model_path):
        return False, f"⚠️ Không tìm thấy mô hình cho: {harmony_label}. Hãy chạy model_trainer.py trước. (Model not found for: {harmony_label}. Please run model_trainer.py first.)"
        
    model = xgb.XGBRegressor()
    model.load_model(model_path)
    
    # Chuẩn bị input 18 số (6 màu x 3 giá trị HSV)
    features = []
    for color in hex_list:
        features.extend(hex_to_hsv(color))
    while len(features) < 18:
        features.extend([-1.0, -1.0, -1.0])
        
    # AI dự đoán
    raw_prediction = model.predict(np.array([features]))[0]
    
    # Quy đổi điểm số (Dựa trên ngưỡng log của lượt like từ 4.0 đến 9.0)
    score = ((raw_prediction - 4.0) / (9.0 - 4.0)) * 10.0
    score = max(1.0, min(score, 10.0)) # Giới hạn trong khoảng 1-10
    
    return True, float(score)

# --- 3. GIAO DIỆN WEB STREAMLIT ---
st.set_page_config(page_title="ML Color Harmony", page_icon="🎨")

st.title("ML Color Harmony Scoring System")
st.markdown("Hệ thống phân tích và chấm điểm độ hài hòa (color harmony) của bảng màu dựa trên mô hình học máy.")
st.markdown("A Machine Learning (ML) system that analyzes and scores the harmony of a color palette.")
st.divider()

# Phần chọn Harmony
st.subheader("Thiết lập quy luật (Rule setup)")
harmony_type = st.selectbox("Chọn quy luật phối màu (Select harmony rule):", list(harmony_descriptions.keys()))
st.info(f"📖 {harmony_descriptions[harmony_type]}")

# Thiết lập số lượng màu dựa trên quy luật
if harmony_type in ["Analogous", "Monochromatic"]:
    num_colors = st.radio("Số lượng màu (Number of colors):", [3, 4, 5], horizontal=True, index=1)
elif harmony_type == "Complementary":
    num_colors = st.radio("Số lượng màu (Number of colors):", [2, 4], horizontal=True, index=1)
else:
    num_colors = 3
    st.caption(f"💡 Quy luật {harmony_type} sử dụng 3 màu. ({harmony_type} uses 3 colors.)")

# Chọn màu trực quan
st.subheader("Chọn bảng màu (Choose palette)")
cols = st.columns(num_colors)
hex_list = []
default_colors = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3"]

for i in range(num_colors):
    with cols[i]:
        color = st.color_picker(f"Màu {i+1} (Color {i+1})", default_colors[i])
        hex_list.append(color)

# Hiển thị dải màu xem trước
html_colors = "".join([f"<div style='background-color: {c}; width: {100/num_colors}%; height: 40px; float: left;'></div>" for c in hex_list])
st.markdown(f"<div style='width: 100%; height: 40px; border-radius: 5px; overflow: hidden; margin-bottom: 20px;'>{html_colors}</div>", unsafe_allow_html=True)

# NÚT BẤM VÀ HIỂN THỊ KẾT QUẢ (Tất cả phải nằm trong khối if st.button)
if st.button("Phân tích (Analyze)", use_container_width=True):
    success, result = danh_gia_palette_chuyen_gia(harmony_type, hex_list)
    
    if success:
        score = result
        st.success("Phân tích hoàn tất! (Analysis completed!)")
        
        # Hiển thị Metric
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Điểm hài hòa (Harmony Score)", f"{score:.2f} / 10.0")
        with c2:
            if score >= 8.0: st.write("✨ **Bảng màu xuất sắc!** (**Excellent palette!**)")
            elif score >= 5.0: st.write("👍 **Khá ổn định.** (**Fairly balanced.**)")
            else: st.write("⚠️ **Cần cải thiện thêm.** (**Needs further improvement.**)")
            
            # Thanh tiến trình
            st.progress(score / 10.0)
    else:
        st.error(result)