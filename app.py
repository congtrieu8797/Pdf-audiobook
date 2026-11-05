import os
import sys
import io
import time
import streamlit as st

# Tự động kích hoạt Streamlit server nếu người dùng chạy "python app.py" hoặc click đúp vào file app.py
if hasattr(st, "runtime") and not st.runtime.exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", os.path.abspath(__file__)]
    sys.exit(stcli.main())

from dotenv import load_dotenv

from pdf_processor import extract_text_from_pdf
from tts_engine import VOICE_CATALOG, convert_text_to_mp3, generate_voice_sample
from summarizer import summarize_for_audiobook

# Nạp biến môi trường nếu có file .env
load_dotenv()

# Thiết lập cấu hình trang Streamlit
st.set_page_config(
    page_title="AI PDF Audiobook - Chuyển Sách Thành Giọng Nói",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS để giao diện trực quan và hiện đại hơn
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .metric-badge {
        background-color: #EEF2FF;
        color: #3730A3;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎙️ AI PDF Audiobook Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Chuyển đổi sách hoặc tài liệu PDF thành sách nói truyền cảm với 2 chế độ: <b>Tóm tắt nội dung</b> hoặc <b>Đọc toàn bộ sách</b>.</div>', unsafe_allow_html=True)

# ----------------- SIDEBAR: CẤU HÌNH GIỌNG ĐỌC & AI -----------------
with st.sidebar:
    st.header("🎙️ Chọn Giọng Đọc Sách")
    
    # Bộ lọc ngôn ngữ và giới tính
    all_langs = ["Tất cả"] + sorted(list(set(v["lang"] for v in VOICE_CATALOG.values())))
    selected_lang = st.selectbox("🌐 Ngôn ngữ giọng đọc:", all_langs, index=all_langs.index("Tiếng Việt 🇻🇳") if "Tiếng Việt 🇻🇳" in all_langs else 0)
    
    selected_gender = st.radio("👤 Giới tính giọng đọc:", ["Tất cả", "Nữ", "Nam"], horizontal=True)
    
    # Lọc danh sách giọng
    filtered_voices = {}
    for vid, vinfo in VOICE_CATALOG.items():
        if selected_lang != "Tất cả" and vinfo["lang"] != selected_lang:
            continue
        if selected_gender != "Tất cả" and vinfo["gender"] != selected_gender:
            continue
        filtered_voices[vid] = vinfo

    if not filtered_voices:
        st.warning("Không tìm thấy giọng đọc phù hợp với bộ lọc, hiển thị toàn bộ giọng.")
        filtered_voices = VOICE_CATALOG

    selected_voice_key = st.selectbox(
        "🗣️ Chọn giọng đọc:",
        options=list(filtered_voices.keys()),
        format_func=lambda k: f"{filtered_voices[k]['name']} - {filtered_voices[k]['desc'].split('(')[0]}",
        index=0
    )

    current_voice_info = VOICE_CATALOG[selected_voice_key]
    st.caption(f"📌 **Mô tả:** {current_voice_info['desc']}")

    # Nút nghe thử giọng đọc
    if st.button("🔊 Nghe thử giọng này", use_container_width=True):
        with st.spinner("Đang chuẩn bị mẫu giọng..."):
            try:
                sample_audio_bytes = generate_voice_sample(selected_voice_key)
                st.audio(sample_audio_bytes, format="audio/mp3")
            except Exception as ex:
                st.error(f"Lỗi nghe thử: {ex}")

    st.markdown("---")
    st.subheader("⚡ Tùy chỉnh Giọng đọc")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        speed_rate = st.slider(
            "Tốc độ",
            min_value=-25,
            max_value=50,
            value=0,
            step=5,
            format="%d%%"
        )
        rate_str = f"{speed_rate:+d}%"
    with col_s2:
        pitch_val = st.slider(
            "Cao độ (Pitch)",
            min_value=-20,
            max_value=20,
            value=0,
            step=2,
            format="%dHz"
        )
        pitch_str = f"{pitch_val:+d}Hz"
    
    st.markdown("---")
    st.subheader("🤖 Cấu hình Tóm tắt AI (Gemini)")
    
    default_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Gemini API Key (Dùng cho chế độ Tóm tắt)",
        value=default_key,
        type="password",
        help="Lấy API Key hoàn toàn miễn phí tại https://aistudio.google.com/"
    )
    if not api_key_input:
        st.info("💡 Bạn chỉ cần API Key khi chọn chế độ **Tóm tắt**. Chế độ **Đọc toàn bộ** hoàn toàn không cần API Key!")

    summary_length = st.selectbox(
        "Độ dài bản tóm tắt:",
        [
            "Tiêu chuẩn (khoảng 6-9 phút nghe)",
            "Ngắn gọn (khoảng 3-5 phút nghe)",
            "Chi tiết (khoảng 10-15 phút nghe)"
        ],
        index=0
    )
    
    st.markdown("---")
    st.caption("✨ Hỗ trợ Microsoft Edge Neural AI & Google TTS đa ngôn ngữ.")

# ----------------- PHẦN CHÍNH: TẢI SÁCH VÀ XỬ LÝ -----------------

col_up, col_samp = st.columns([3, 1])
with col_up:
    uploaded_file = st.file_uploader(
        "📂 Tải lên file sách PDF của bạn:",
        type=["pdf"],
        help="Hỗ trợ các file sách, giáo trình, bài viết định dạng PDF."
    )
with col_samp:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🧪 Thử file sách mẫu", help="Tải sẵn file PDF mẫu về Thói quen nhỏ 1% để thử nghiệm nhanh"):
        sample_path = os.path.join(os.path.dirname(__file__), "sample_book.pdf")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f_s:
                st.session_state.sample_pdf_bytes = f_s.read()
                st.session_state.sample_pdf_name = "sample_book.pdf"
                st.success("Đã nạp file mẫu!")

# Xác định nguồn PDF (từ uploader hoặc từ file mẫu)
pdf_bytes = None
file_display_name = ""

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    file_display_name = uploaded_file.name
elif st.session_state.get("sample_pdf_bytes") is not None:
    pdf_bytes = st.session_state.sample_pdf_bytes
    file_display_name = st.session_state.sample_pdf_name

if pdf_bytes is not None:
    # Lưu file vào session state nếu đổi file
    if "current_file_name" not in st.session_state or st.session_state.current_file_name != file_display_name:
        st.session_state.current_file_name = file_display_name
        st.session_state.extracted_text = None
        st.session_state.working_text = None
        st.session_state.summary_text = None
        st.session_state.audio_path = None
        st.session_state.metadata = None
    
    # Lấy thông tin số trang nhanh từ file PDF
    from pypdf import PdfReader
    quick_reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(quick_reader.pages)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.metric("📄 Tên tài liệu", file_display_name)
    with col2:
        st.metric("📑 Tổng số trang PDF", f"{total_pages} trang")
    with col3:
        st.metric("💾 Dung lượng", f"{round(len(pdf_bytes) / 1024 / 1024, 2)} MB")

    # Chọn phạm vi trang
    st.markdown("### 1. Chọn phạm vi trang cần đọc")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        start_p = st.number_input("Trang bắt đầu", min_value=1, max_value=total_pages, value=1)
    with col_p2:
        end_p = st.number_input("Trang kết thúc", min_value=start_p, max_value=total_pages, value=total_pages)

    # 2. Xem trước và chỉnh sửa văn bản (Chống lỗi font tiếng Việt)
    st.markdown("### 2. Trích xuất & Kiểm tra Font Tiếng Việt")
    col_ext1, col_ext2, col_ext3 = st.columns([1, 1, 1])
    with col_ext1:
        if st.button("🔍 Trích xuất lại từ PDF", use_container_width=True):
            with st.spinner("Đang trích xuất và tối ưu hóa font tiếng Việt..."):
                raw_text, meta = extract_text_from_pdf(
                    io.BytesIO(pdf_bytes),
                    start_page=start_p,
                    end_page=end_p
                )
                st.session_state.working_text = raw_text
                st.session_state.metadata = meta
                st.success(f"Đã trích xuất thành công {meta['processed_pages']} trang (~{meta['word_count']} từ)!")
    
    with col_ext2:
        from vietnamese_font_fixer import fix_vietnamese_font, ai_restore_vietnamese_text
        if st.button("✨ Sửa font tự động (1-Click)", help="Giải mã font đặc biệt (hocdedang, TCVN3, VNI, Unicode tổ hợp)", use_container_width=True):
            current_txt = st.session_state.get("working_text", "")
            if current_txt:
                st.session_state.working_text = fix_vietnamese_font(current_txt)
                st.success("✅ Đã tự động khôi phục font tiếng Việt chuẩn!")
                st.rerun()

    with col_ext3:
        if st.button("🪄 Dùng AI Phục hồi font", help="Dùng Gemini AI phân tích ngữ cảnh để khôi phục hoàn hảo 100% tiếng Việt", use_container_width=True):
            current_txt = st.session_state.get("working_text", "")
            if not current_txt:
                st.warning("Chưa có nội dung để phục hồi.")
            elif not api_key_input:
                st.error("Vui lòng nhập Gemini API Key ở thanh bên trái (Sidebar) để dùng tính năng AI phục hồi.")
            else:
                with st.spinner("🤖 Gemini AI đang đọc và phục hồi từng câu chữ tiếng Việt..."):
                    try:
                        restored = ai_restore_vietnamese_text(current_txt, api_key=api_key_input)
                        st.session_state.working_text = restored
                        st.success("🎉 Gemini AI đã phục hồi tiếng Việt hoàn hảo!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Lỗi AI: {err}")

    # Nếu chưa bấm trích xuất nhưng đã có file, ta có thể tự trích xuất sẵn nếu session_state chưa có
    if "working_text" not in st.session_state or st.session_state.working_text is None:
        raw_text, meta = extract_text_from_pdf(
            io.BytesIO(pdf_bytes),
            start_page=start_p,
            end_page=end_p
        )
        st.session_state.working_text = raw_text
        st.session_state.metadata = meta

    user_edited_text = st.text_area(
        "📝 Nội dung văn bản trích xuất (Bạn có thể xem trước hoặc trực tiếp chỉnh sửa trước khi tạo sách nói):",
        value=st.session_state.get("working_text", ""),
        height=220,
        help="Toàn bộ nội dung sách tiếng Việt đã được xử lý chuẩn mã Unicode. Bạn có thể xóa bớt các dòng thừa hoặc sửa lại từ ngữ tại đây."
    )
    st.session_state.working_text = user_edited_text

    # 3. Chọn chế độ sách nói
    st.markdown("### 3. Chọn Chế độ Sách nói")
    mode = st.radio(
        "Bạn muốn tạo sách nói theo hình thức nào?",
        [
            "🌟 Tóm tắt nội dung sách (AI Audiobook Summary - Đúc kết ý chính súc tích)",
            "📖 Đọc toàn bộ sách (Full Audiobook - Đọc nguyên văn từ đầu đến cuối)"
        ],
        index=0
    )

    # Nút thực hiện
    btn_label = "🚀 Bắt đầu chuyển thành Sách nói"
    if st.button(btn_label, type="primary", use_container_width=True):
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        try:
            # Lấy text đã được trích xuất và tối ưu font
            raw_text = st.session_state.get("working_text", "").strip()
            
            if not raw_text:
                status_text.text("🔍 Đang trích xuất nội dung văn bản từ PDF...")
                raw_text, meta = extract_text_from_pdf(
                    io.BytesIO(pdf_bytes),
                    start_page=start_p,
                    end_page=end_p
                )
                st.session_state.metadata = meta
                st.session_state.working_text = raw_text
            
            if not raw_text.strip():
                st.error("⚠️ Không thể trích xuất văn bản từ phạm vi trang này. Có thể đây là file PDF dạng ảnh quét (scanned image).")
                st.stop()
            
            # Bước 2: Xử lý theo chế độ đã chọn
            text_to_speak = ""
            
            if "Tóm tắt nội dung" in mode:
                status_text.text("🤖 Bước 2/3: Đang dùng AI Gemini tóm tắt và biên soạn kịch bản sách nói...")
                progress_bar.progress(0.4)
                
                if not api_key_input:
                    st.error("❌ Vui lòng nhập Gemini API Key ở thanh bên trái (Sidebar) để sử dụng chế độ Tóm tắt bằng AI.")
                    st.stop()
                    
                summary = summarize_for_audiobook(
                    text=raw_text,
                    api_key=api_key_input,
                    length_preference=summary_length
                )
                st.session_state.summary_text = summary
                text_to_speak = summary
            else:
                status_text.text("📖 Bước 2/3: Đã nạp toàn bộ nội dung sách, chuẩn bị chuyển thành âm thanh...")
                progress_bar.progress(0.4)
                st.session_state.extracted_text = raw_text
                text_to_speak = raw_text

            # Bước 3: Chuyển văn bản thành giọng nói (TTS)
            status_text.text("🎙️ Bước 3/3: Đang khởi tạo giọng đọc AI và ghi âm...")
            
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            os.makedirs(output_dir, exist_ok=True)
            mode_prefix = "summary" if "Tóm tắt" in mode else "full"
            safe_name = os.path.splitext(file_display_name)[0][:30]
            timestamp = int(time.time())
            audio_filename = f"{mode_prefix}_{safe_name}_{timestamp}.mp3"
            output_filepath = os.path.join(output_dir, audio_filename)
            
            def tts_progress(ratio, msg):
                actual_ratio = 0.4 + (ratio * 0.55)
                progress_bar.progress(min(0.98, actual_ratio))
                status_text.text(f"🎙️ Bước 3/3: {msg}")
                
            convert_text_to_mp3(
                text=text_to_speak,
                output_path=output_filepath,
                voice=selected_voice_key,
                rate=rate_str,
                pitch=pitch_str,
                progress_callback=tts_progress
            )
            
            progress_bar.progress(1.0)
            status_text.text("✅ Hoàn tất! Sách nói của bạn đã sẵn sàng.")
            st.session_state.audio_path = output_filepath
            st.session_state.speaking_text = text_to_speak
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Có lỗi xảy ra trong quá trình xử lý: {str(e)}")
            st.exception(e)

    # ----------------- HIỂN THỊ KẾT QUẢ ĐÃ TẠO -----------------
    if st.session_state.get("audio_path") and os.path.exists(st.session_state.audio_path):
        st.markdown("---")
        st.success("🎉 **Sách nói đã được tạo thành công!**")
        
        col_res1, col_res2 = st.columns([1, 1])
        with col_res1:
            st.markdown("#### 🎧 Nghe trực tiếp:")
            with open(st.session_state.audio_path, "rb") as f_audio:
                audio_bytes = f_audio.read()
                st.audio(audio_bytes, format="audio/mp3")
                
            st.download_button(
                label="📥 Tải xuống file Sách nói MP3",
                data=audio_bytes,
                file_name=os.path.basename(st.session_state.audio_path),
                mime="audio/mp3",
                type="primary",
                use_container_width=True
            )
            
        with col_res2:
            st.markdown("#### 📊 Thống kê phiên đọc:")
            if st.session_state.get("metadata"):
                m = st.session_state.metadata
                st.write(f"- **Phạm vi trang:** {m['start_page']} đến {m['end_page']} (Tổng {m['processed_pages']} trang)")
                st.write(f"- **Số lượng từ gốc:** ~{m['word_count']:,} từ")
            if st.session_state.get("summary_text"):
                summary_words = len(st.session_state.summary_text.split())
                st.write(f"- **Số từ kịch bản tóm tắt:** ~{summary_words:,} từ")
                st.write(f"- **Thời lượng audio ước tính:** ~{round(summary_words / 150, 1)} phút")
            st.write(f"- **Giọng đọc:** {VOICE_CATALOG.get(selected_voice_key, {}).get('name', selected_voice_key)}")
            st.write(f"- **Tốc độ:** {rate_str} | **Cao độ:** {pitch_str}")

        with st.expander("📝 Xem nội dung kịch bản văn bản đã đọc", expanded=True):
            st.text_area(
                "Nội dung sách nói:",
                value=st.session_state.get("speaking_text", ""),
                height=300
            )

else:
    # Hướng dẫn khi chưa upload file
    st.markdown("""
    <div class="card">
        <h3>💡 Hướng dẫn sử dụng:</h3>
        <ol>
            <li><b>Kéo thả hoặc tải file PDF</b> của cuốn sách vào ô bên trên.</li>
            <li>Chọn <b>phạm vi trang</b> bạn muốn xử lý (ví dụ: từ trang 5 đến trang 50 để bỏ qua trang bìa và mục lục).</li>
            <li>Chọn 1 trong 2 chế độ:
                <ul>
                    <li><b>🌟 Tóm tắt nội dung sách:</b> Tận dụng AI Gemini để cô đọng cuốn sách thành một kịch bản sách nói hấp dẫn, đi thẳng vào các bài học và luận điểm cốt lõi nhất.</li>
                    <li><b>📖 Đọc toàn bộ sách:</b> Giọng đọc AI sẽ truyền cảm đọc đầy đủ nguyên văn từng trang sách của bạn mà không tóm tắt hay cắt bớt.</li>
                </ul>
            </li>
            <li>Bấm nút <b>🚀 Bắt đầu chuyển thành Sách nói</b>, sau đó nghe trực tiếp trên trình duyệt hoặc tải file <b>MP3</b> về điện thoại/máy tính!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
