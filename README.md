# 🎙️ AI PDF Audiobook Generator (Công Cụ Sách Nói Tự Động)

Công cụ chuyển đổi tài liệu hoặc sách PDF thành **sách nói (Audiobook)** tự động với 2 chế độ linh hoạt:
1. **🌟 Tóm tắt nội dung sách (AI Summary):** Ứng dụng AI Gemini để tóm tắt các luận điểm, bài học cốt lõi nhất và biên tập thành kịch bản sách nói hấp dẫn, truyền cảm.
2. **📖 Đọc toàn bộ sách (Full Audiobook):** Chuyển nguyên văn toàn bộ nội dung (hoặc phạm vi trang bạn chọn) thành file âm thanh hoàn chỉnh.

---

## 🗣️ Hệ thống Giọng đọc Đa dạng & Nghe thử Trực quan
Ứng dụng được trang bị bộ sưu tập giọng đọc AI phong phú:
- **🇻🇳 Tiếng Việt:**
  - 👩 **Hoài My (Nữ - Microsoft AI)**: Truyền cảm, tự nhiên, ngọt ngào (phù hợp sách kỹ năng, tiểu thuyết, tản văn).
  - 👨 **Nam Minh (Nam - Microsoft AI)**: Trầm ấm, dõng dạc, rõ ràng (phù hợp kinh doanh, tài chính, triết học).
  - 🤖 **Chị Google (Nữ - Google TTS)**: Giọng đọc Chị Google thân thuộc, dí dỏm.
- **🌐 Đa ngôn ngữ quốc tế:**
  - 🇺🇸 Tiếng Anh (Mỹ): Jenny, Guy, Aria, Christopher
  - 🇬🇧 Tiếng Anh (Anh): Sonia, Ryan
  - 🇫🇷 Tiếng Pháp: Denise, Henri
  - 🇯🇵 Tiếng Nhật: Nanami, Keita
  - 🇨🇳 Tiếng Trung: Xiaoxiao, Yunxi
  - 🇰🇷 Tiếng Hàn: SunHi, InJoon
- **Bộ lọc thông minh:** Lọc theo **Ngôn ngữ** và **Giới tính (Nam/Nữ)**.
- **Nút "🔊 Nghe thử giọng này":** Nghe thử âm sắc trước khi chuyển đổi toàn bộ sách.
- **Tùy biến âm thanh nâng cao:** Điều chỉnh tốc độ đọc (`-25%` đến `+50%`) và cao độ giọng (`-20Hz` đến `+20Hz`).

---

## 🚀 Cách chạy ứng dụng

### Cách 1: Chạy nhanh bằng 1-Click (Khuyên dùng trên Windows)
Nhấp đúp chuột vào file:
```
run.bat
```

### Cách 2: Chạy qua dòng lệnh (Terminal)
```powershell
uv run streamlit run app.py
```

### Cách 3: Chạy CLI (Dòng lệnh)
```powershell
# Nghe giọng Nam Minh:
uv run python cli.py sample_book.pdf --mode full --voice vi-VN-NamMinhNeural --rate +5%

# Nghe giọng Chị Google:
uv run python cli.py sample_book.pdf --mode full --voice google-vi
```
