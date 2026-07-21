# ==============================================================================
# TÊN FILE: tomato_disease_app.py
# CHỨC NĂNG: Nhận diện và khoanh vùng bệnh trên lá cà chua bằng AI (Roboflow)
# ==============================================================================

import streamlit as st
import requests
from PIL import Image, ImageDraw
import io
import base64

# 1. CẤU HÌNH THÔNG TIN MÔ HÌNH NHẬN DIỆN BỆNH LÁ CÀ CHUA (TOMATO LEAF DISEASE)
ROBOFLOW_API_KEY = "nPCZj42xqoUqYx7Fc2rl"  # Giữ nguyên API Key của bạn
MODEL_ID = "tomata-leaf-disease-jwi8o"
VERSION = "1"

# Đường dẫn URL API gọi mô hình nhận diện bệnh lá cà chua (Lọc lấy độ tự tin từ 25% trở lên)
URL = f"https://detect.roboflow.com/{MODEL_ID}/{VERSION}?api_key={ROBOFLOW_API_KEY}&confidence=25"

# 2. GIAO DIỆN TRANG WEB STREAMLIT
st.set_page_config(page_title="Hệ thống Bệnh cây trồng - Lá Cà chua", page_icon="🍅", layout="centered")

st.title("🍅 Hệ Thống AI Phát Hiện Bệnh Trên Lá Cà Chua")
st.write("Tải ảnh lá cà chua lên để hệ thống AI tự động phân tích, phát hiện và khoanh vùng các vị trí xuất hiện mầm bệnh.")

st.divider()

# Chức năng tải ảnh từ máy tính hoặc điện thoại lên
uploaded_file = st.file_uploader("Chọn một hình ảnh lá cà chua cần kiểm tra...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Mở ảnh gốc và chuyển hệ màu chuẩn RGB
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Ảnh lá cà chua gốc bạn đã tải lên", use_container_width=True)
    
    # Nút bấm kích hoạt mô hình AI phân tích
    if st.button("Bắt đầu kiểm tra mầm bệnh", type="primary"):
        with st.spinner("Hệ thống AI đang phân tích bề mặt lá cây..."):
            try:
                # 1. Chuyển đổi ảnh sang dạng bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_bytes = img_byte_arr.getvalue()
                
                # 2. Mã hóa dữ liệu bytes sang chuỗi Base64 để gửi qua API
                image_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                # Gọi dịch vụ phân tích API từ Roboflow
                response = requests.post(
                    URL, 
                    data=image_base64, 
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                result = response.json()
                
                st.divider()
                st.subheader("📊 Kết quả phân tích sức khỏe cây trồng:")
                
                # Bóc tách danh sách các vùng nhiễm bệnh phát hiện được
                box_list = result.get("predictions", [])
                
                # Tiến hành khoanh vùng nếu tìm thấy vết bệnh
                if len(box_list) > 0:
                    st.error(f"⚠️ CẢNH BÁO: Phát hiện {len(box_list)} vùng bị nhiễm bệnh trên lá cà chua!")
                    
                    # Tạo bản sao của ảnh để vẽ khung đè lên
                    draw_image = image.copy()
                    draw = ImageDraw.Draw(draw_image)
                    
                    # Duyệt qua từng vết bệnh tìm được để khoanh vùng
                    for box in box_list:
                        x = box.get("x")
                        y = box.get("y")
                        w = box.get("width")
                        h = box.get("height")
                        label = box.get("class", "Leaf Disease")
                        conf = box.get("confidence", 0) * 100
                        
                        # Tính toán tọa độ góc Top-Left và Bottom-Right từ tâm x, y của Roboflow
                        left = x - (w / 2)
                        top = y - (h / 2)
                        right = x + (w / 2)
                        bottom = y + (h / 2)
                        
                        # Dùng màu ĐỎ rực (#FF0000) khoanh vùng cảnh báo vết bệnh
                        color = "#FF0000"
                        label_vn = f"Bệnh: {label}"
                        
                        # Vẽ khung hình chữ nhật bao quanh vết bệnh (nét dày = 4)
                        draw.rectangle([left, top, right, bottom], outline=color, width=4)
                        
                        # Ghi chữ nhãn hiển thị tên bệnh và độ tin cậy của AI
                        text_display = f"{label_vn} ({conf:.1f}%)"
                        draw.text((left + 4, top + 4), text_display, fill=color)
                    
                    # Hiển thị bức ảnh sau khi đã được mô hình vẽ định vị mầm bệnh
                    st.image(draw_image, caption="Ảnh kết quả phân tích: Các vùng khoanh ĐỎ bị nhiễm bệnh", use_container_width=True)
                    st.warning("🚨 Khuyến cáo: Cây có dấu hiệu nhiễm bệnh (sương mai, đốm lá hoặc khảm virus). Cần tỉa bỏ lá bệnh và phun thuốc bảo vệ thực vật phù hợp!")
                else:
                    st.success("🎉 TUYỆT VỜI: Không phát hiện dấu hiệu bệnh lý! Lá cà chua phát triển khỏe mạnh.")
                    st.image(image, caption="Bề mặt lá xanh tốt, không phát hiện mầm bệnh", use_container_width=True)
                    
            except Exception as e:
                st.error(f"Đã xảy ra lỗi kết nối với máy chủ AI hoặc lỗi xử lý hình ảnh: {e}")