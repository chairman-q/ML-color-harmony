from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import colorsys
import os
import re

# =====================================================================
# PHẦN 1: THUẬT TOÁN TOÁN HỌC PHÂN LOẠI 6 LOẠI HARMONY (AUTO-LABELER)
# =====================================================================

def hex_to_hsv(hex_color):
    """Chuyển mã HEX sang hệ màu HSV (Hue, Saturation, Value)"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(r, g, b)

def phan_loai_harmony(hex_list):
    """Phân loại đủ 6 hệ màu bằng công thức khoảng cách không gian tròn"""
    if not hex_list or len(hex_list) < 2: 
        return "Others"
    
    hsv_list = [hex_to_hsv(c) for c in hex_list]
    hues = [hsv[0] * 360 for hsv in hsv_list] # Góc Hue từ 0 đến 360 độ
    sats = [hsv[1] for hsv in hsv_list]       # Độ bão hòa Saturation
    
    # 1. Tính khoảng cách góc ngắn nhất trên vòng tròn 360 độ cho tất cả các cặp màu
    distances = []
    max_hue_diff = 0
    for i in range(len(hues)):
        for j in range(i+1, len(hues)):
            diff = min(abs(hues[i] - hues[j]), 360 - abs(hues[i] - hues[j]))
            distances.append(diff)
            if diff > max_hue_diff:
                max_hue_diff = diff
                
    sat_range = max(sats) - min(sats) if sats else 0

    # 2. Phân loại Monochromatic (Đơn sắc) và Shades (Sắc thái)
    if max_hue_diff < 15:
        if sat_range < 0.3: 
            return "Shades"
        else:
            return "Monochromatic"
            
    # 3. Phân loại Analogous (Tương đồng)
    if max_hue_diff < 90:
        return "Analogous"
        
    # 4. Phân loại Complementary (Bổ túc) - Có 2 màu đối đỉnh (~180 độ)
    if any(165 <= d <= 180 for d in distances):
        return "Complementary"
        
    # 5. Phân loại Split Complementary (Bổ túc xen kẽ)
    if any(145 <= d < 165 for d in distances):
        return "Split Complementary"
        
    # 6. Phân loại Triad (Bộ ba)
    if any(105 <= d < 145 for d in distances):
        return "Triad"
        
    return "Others"

# =====================================================================
# PHẦN 2: ROBOT CÀO DỮ LIỆU & GÁN NHÃN TỰ ĐỘNG
# =====================================================================

def run_smart_scraper(pages_to_scroll=50):
    print("🤖 Đang khởi động Robot chiến thuật 'Vừa đi vừa nhặt'...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://colorhunt.co/palettes/popular")
    
    # Bộ nhớ tạm để robot không lấy trùng các bảng màu đã quét ở lần cuộn trước
    danh_sach_da_quet = set()
    tong_so_da_luu = 0

    try:
        for page in range(pages_to_scroll):
            print(f"\n⬇️ Đang quét trang {page+1}/{pages_to_scroll}...")
            
            # Chờ trang load các item
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item")))
            cac_palette = driver.find_elements(By.CSS_SELECTOR, ".item")
            print(f"👀 Đang nhìn thấy {len(cac_palette)} bảng màu trên web...")
            
            for card in cac_palette:
                # 1. Trích xuất HEX
                hex_elements = card.find_elements(By.CSS_SELECTOR, ".place")
                hex_codes = []
                for el in hex_elements:
                    text = el.get_attribute("textContent").strip()
                    if text:
                        if not text.startswith("#"): text = f"#{text}"
                        hex_codes.append(text)
                
                palette_id = "-".join(hex_codes)
                
                if palette_id in danh_sach_da_quet or len(hex_codes) != 4:
                    continue
                    
                danh_sach_da_quet.add(palette_id)

                # 2. Quét Like
                try:
                    likes = 0
                    cac_the_nho = card.find_elements(By.XPATH, ".//*") 
                    for the in reversed(cac_the_nho):
                        text = the.get_attribute("textContent").strip().lower()
                        if text and len(text) < 6 and any(c.isdigit() for c in text):
                            clean_text = text.replace(',', '')
                            match = re.search(r'\d+(\.\d+)?', clean_text)
                            if match:
                                num_val = float(match.group())
                                likes = int(num_val * 1000) if 'k' in clean_text else int(num_val)
                                break 
                    
                    if likes == 0: continue
                except:
                    continue

                # 3. Phân loại & Lưu
                label = phan_loai_harmony(hex_codes)
                if label != "Others":
                    filename = f"data_{label.lower().replace(' ', '_')}.csv"
                    file_exists = os.path.isfile(filename)
                    df = pd.DataFrame([hex_codes + [likes]], columns=['C1', 'C2', 'C3', 'C4', 'Score'])
                    df.to_csv(filename, mode='a', index=False, header=not file_exists)
                    tong_so_da_luu += 1
                    print(f"💾 [+] Lấy thành công: {label.upper()} | {likes} Likes")

            # ---------------------------------------------------------
            # BƯỚC NÂNG CẤP: CHIẾN THUẬT CUỘN YO-YO (ÉP TẢI DỮ LIỆU)
            # ---------------------------------------------------------
            print("🚶‍♂️ Đang thực hiện chiến thuật cuộn Yo-Yo để ép tải dữ liệu...")
            
            # Đập thẳng xuống đáy trang
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            
            # Nhích ngược lên một chút (khoảng 500 pixel) để cảm biến nhận diện sự chuyển động
            driver.execute_script("window.scrollBy(0, -500);")
            time.sleep(0.5)
            
            # Đập xuống đáy lần 2 để chốt hạ
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3) # Dành ra 3 giây để ColorHunt nạp bảng màu mới vào HTML

        print(f"\n🎉 HOÀN THÀNH CHIẾN DỊCH! Đã thu hoạch thành công tổng cộng {tong_so_da_luu} bảng màu chuẩn.")

    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình quét: {e}")
        
    finally:
        driver.quit()
        print("Đã đóng trình duyệt an toàn.")

if __name__ == "__main__":
    # Tham số pages_to_scroll quyết định số lượng dữ liệu thu thập.
    # Tăng lên 10 hoặc 20 nếu bạn muốn cào thêm hàng ngàn dữ liệu.
    run_smart_scraper(pages_to_scroll=200)