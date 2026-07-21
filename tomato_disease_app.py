# ==============================================================================
# TÊN FILE: tomato_disease_app.py
# CHỨC NĂNG: Nhận diện và phân loại bệnh/lá khỏe trên lá cà chua
# ==============================================================================

import streamlit as st
import requests
from PIL import Image, ImageDraw
import io
import base64

# 1. CẤU HÌNH THÔNG TIN MÔ HÌNH NHẬN DIỆN BỆNH LÁ CÀ CHUA (TOMATO LEAF DISEASE)
ROBOFLOW_API_KEY = "nPCZj42xqoUqYx7Fc2rl"
MODEL_ID = "tomata-leaf-disease-jwi8o"
VERSION = "1"

# Đường dẫn URL API gọi mô hình
URL = f"https://detect.roboflow.com/{MODEL_ID}/{VERSION}?api_key={ROBOFLOW_API_KEY}&confidence=25"

# 2. GIAO DIỆN TRANG WEB STREAMLIT
st.set_page_config(page_title="Hệ thống Bệnh cây trồng - Lá Cà chua", page_icon="🍅", layout="centered")

st.title("🍅 Hệ Thống AI Phát Hiện Bệnh Trên Lá Cà Chua")
st.write("Tải ảnh lá cà chua lên để hệ thống AI tự động phân tích, kiểm tra sức khỏe và khoanh vùng mầm bệnh.")

st.divider()

uploaded_file = st.file_uploader("Chọn một hình ảnh lá cà chua cần kiểm tra...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Ảnh lá cà chua gốc bạn đã tải lên", use_container_width=True)
    
    if st.button("Bắt đầu kiểm tra mầm bệnh", type="primary"):
        with st.spinner("Hệ thống AI đang phân tích bề mặt lá cây..."):
            try:
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_bytes = img_byte_arr.getvalue()
                
                image_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                response = requests.post(
                    URL, 
                    data=image_base64, 
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                result = response.json()
                
                st.divider()
                st.subheader("📊 Kết quả phân tích sức khỏe cây trồng:")
                
                box_list = result.get("predictions", [])
                
                if len(box_list) > 0:
                    draw_image = image.copy()
                    draw = ImageDraw.Draw(draw_image)
                    
                    has_disease = False
                    
                    for box in box_list:
                        x = box.get("x")
                        y = box.get("y")
                        w = box.get("width")
                        h = box.get("height")
                        label = box.get("class", "").strip()
                        conf = box.get("confidence", 0) * 100
                        
                        left = x - (w / 2)
                        top = y - (h / 2)
                        right = x + (w / 2)
                        bottom = y + (h / 2)
                        
                        # LOGIC KIỂM TRA: Nếu nhãn chứa chữ "healthy" -> Lá khỏe (Màu XANH LÁ)
                        if "healthy" in label.lower():
                            color = "#00FF00"  # Màu Xanh lá
                            label_vn = f"Lá khỏe ({label})"
                        else:
                            color = "#FF0000"  # Màu Đỏ cho lá bệnh
                            label_vn = f"Bệnh: {label}"
                            has_disease = True
                        
                        # Vẽ khung hình chữ nhật
                        draw.rectangle([left, top, right, bottom], outline=color, width=4)
                        
                        # Ghi chữ nhãn
                        text_display = f"{label_vn} ({conf:.1f}%)"
                        draw.text((left + 4, top + 4), text_display, fill=color)
                    
                    # Cảnh báo dựa trên thực tế có bệnh hay không
                    if has_disease:
                        st.error(f"⚠️ CẢNH BÁO: Phát hiện lá bị nhiễm bệnh!")
                        st.image(draw_image, caption="Kết quả: Vùng ĐỎ là vết bệnh, vùng XANH LÁ là lá khỏe mạnh", use_container_width=True)
                        st.warning("🚨 Khuyến cáo: Tỉa bỏ các lá có khoanh vùng ĐỎ và phun thuốc phòng ngừa thích hợp.")
                    else:
                        st.success(f"🎉 TUYỆT VỜI: Tất cả các vùng được nhận diện đều là lá KHOẺ MẠNH ({len(box_list)} vùng)!")
                        st.image(draw_image, caption="Kết quả: Các vùng khoanh XANH LÁ thể hiện lá phát triển tốt", use_container_width=True)
                    
                else:
                    st.info("ℹ️ Không tìm thấy vùng lá rõ ràng hoặc lá hoàn toàn bình thường.")
                    st.image(image, caption="Bề mặt lá xanh tốt, không phát hiện mầm bệnh", use_container_width=True)
                    
            except Exception as e:
                st.error(f"Đã xảy ra lỗi kết nối với máy chủ AI hoặc lỗi xử lý hình ảnh: {e}")
