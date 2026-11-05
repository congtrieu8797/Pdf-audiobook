import os
from typing import Optional
from google import genai

AUDIOBOOK_SUMMARY_PROMPT = """
Bạn là một chuyên gia biên tập sách nói chuyên nghiệp và người dẫn truyện lôi cuốn.
Nhiệm vụ của bạn là đọc toàn bộ nội dung sách/tài liệu dưới đây và soạn thảo một BẢN TÓM TẮT DÀNH RIÊNG CHO SÁCH NÓI (Audiobook Script).

Yêu cầu khi viết kịch bản sách nói:
1. Văn phong: Tự nhiên, truyền cảm, gần gũi, sử dụng các từ ngữ giàu hình ảnh và nhịp điệu phù hợp cho việc NGHE thay vì ĐỌC. Tránh dùng các ký hiệu khó đọc như dấu gạch đầu dòng (*, -, #), không dùng bảng biểu phức tạp.
2. Cấu trúc kịch bản:
   - Lời mở đầu chào đón người nghe và giới thiệu chủ đề, thông điệp cốt lõi của tác phẩm.
   - Các luận điểm hoặc bài học quan trọng nhất (kèm ví dụ hoặc câu chuyện minh họa súc tích).
   - Đúc kết cuối cùng và lời nhắn nhủ dành cho người nghe.
3. Ngôn ngữ: Tiếng Việt chuẩn mực, mạch lạc, hấp dẫn.

Nội dung tài liệu:
\"\"\"
{text}
\"\"\"
"""

def summarize_for_audiobook(
    text: str, 
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.8-flash",
    length_preference: str = "Tiêu chuẩn (khoảng 5-10 phút nghe)"
) -> str:
    """
    Tóm tắt nội dung văn bản thành kịch bản sách nói truyền cảm bằng Gemini API.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "Chưa có Gemini API Key. Vui lòng nhập API Key trên giao diện hoặc đặt biến môi trường GEMINI_API_KEY."
        )

    client = genai.Client(api_key=key)
    
    length_instruction = ""
    if "Ngắn gọn" in length_preference:
        length_instruction = "Hãy tóm tắt cô đọng trong khoảng 500 - 800 từ (khoảng 3-5 phút nghe)."
    elif "Chi tiết" in length_preference:
        length_instruction = "Hãy tóm tắt chi tiết, sâu sắc trong khoảng 1500 - 2500 từ (khoảng 10-15 phút nghe)."
    else:
        length_instruction = "Hãy tóm tắt đầy đủ trong khoảng 900 - 1400 từ (khoảng 6-9 phút nghe)."

    prompt = AUDIOBOOK_SUMMARY_PROMPT.format(text=text) + f"\nLưu ý độ dài: {length_instruction}"
    
    candidate_models = [
        model_name,
        "gemini-3.8-flash",
        "gemini-3-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    seen = set()
    ordered_models = [m for m in candidate_models if not (m in seen or seen.add(m))]
    
    import time
    last_error = None
    for m in ordered_models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_error = e
                err_msg = str(e)
                if any(code in err_msg for code in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "404", "NOT_FOUND"]):
                    time.sleep(1.0)
                    continue
                raise e
            
    raise last_error
