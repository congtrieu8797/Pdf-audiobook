import unicodedata
import re

# Bảng chuyển đổi cho lỗi font PDF hocdedang / glyph mapping tiếng Việt
HOCDEDANG_COMPOUNDS = [
    # Cụm 3-4 ký tự phức tạp
    ('LÚẩI', 'LỜI'), ('GIÚấI', 'GIỚI'), ('THIểÅU', 'THIỆU'),
    ('H ỗìu', 'Hầu'), ('h ỗìu', 'hầu'),
    ('trứừỏc', 'trước'), ('Trứừỏc', 'Trước'),
    ('ngứừừi', 'người'), ('Ngứừừi', 'Người'),
    ('àứừåc', 'được'), ('Àứừåc', 'Được'),
    ('phứừng', 'phương'), ('Phứừng', 'Phương'),
    ('nhứäng', 'những'), ('Nhứäng', 'Những'),
    ('luyởån', 'luyện'), ('Luyởån', 'Luyện'),
    ('nghiởåp', 'nghiệp'), ('Nghiởåp', 'Nghiệp'),
    ('nguyởn', 'nguyên'), ('Nguyởn', 'Nguyên'),
    ('chuyởn', 'chuyên'), ('Chuyởn', 'Chuyên'),
    ('tùaec', 'tắc'), ('khùaep', 'khắp'),
    ('tiởộn', 'tiến'), ('Tiởộn', 'Tiến'),
    ('tiởộng', 'tiếng'), ('Tiởộng', 'Tiếng'),
    ('hiởộn', 'hiến'), ('Hiởộn', 'Hiến'),
    ('cuủộn', 'cuốn'), ('Cuủộn', 'Cuốn'),
    ('cuủåc', 'cuộc'), ('Cuủåc', 'Cuộc'),
    ('sủộng', 'sống'), ('Sủộng', 'Sống'),
    ('củộng', 'cống'), ('Củộng', 'Cống'),
    ('khủng', 'không'), ('Khủng', 'Không'),
    ('củng', 'công'), ('Củng', 'Công'),
    ('lùnh', 'lĩnh'), ('tỡnh', 'tính'), ('bợnh', 'bình'), ('mợnh', 'mình'),
    ('nùng', 'năng'), ('Nùng', 'Năng'),
    ('chó', 'chỉ'), ('sù', 'sĩ'), ('ỉng', 'Ông'),
    ('vừỏi', 'với'), ('Vừỏi', 'Với'),
    ('giừỏi', 'giới'), ('Giừỏi', 'Giới'),
    ('thởộ', 'thế'), ('Thởộ', 'Thế'),
    ('rỗột', 'rất'), ('Rỗột', 'Rất'),
    ('nhỗột', 'nhất'), ('Nhỗột', 'Nhất'),
    ('xuỗột', 'xuất'), ('Xuỗột', 'Xuất'),
    ('bỗột', 'bất'), ('Bỗột', 'Bất'),
    ('vỗộn', 'vấn'), ('Vỗộn', 'Vấn'),
    ('lỗộy', 'lấy'), ('Lỗộy', 'Lấy'),
    ('thỗìy', 'thầy'), ('Thỗìy', 'Thầy'),
    ('àỗìu', 'đầu'), ('Àỗìu', 'Đầu'),
    ('lỗìn', 'lần'), ('Lỗìn', 'Lần'),
    ('bỗåc', 'bậc'), ('Bỗåc', 'Bậc'),
    ('Thỗåt', 'Thật'), ('thỗåt', 'thật'),
    ('vỗåy', 'vậy'), ('Vỗåy', 'Vậy'),
    ('nhỗån', 'nhận'), ('Nhỗån', 'Nhận'),
    ('phỗờm', 'phẩm'), ('cỗờm', 'cẩm'),
    ('dởớ', 'dễ'), ('Dởớ', 'Dễ'),
    ('thởờ', 'thể'), ('Thởờ', 'Thể'),
    ('vởì', 'về'), ('Vởì', 'Về'),
    ('nủời', 'nổi'), ('Nủời', 'Nổi'),
    ('mủåt', 'một'), ('Mủåt', 'Một'),
    ('rủång', 'rộng'), ('Rủång', 'Rộng'),
    ('quủộc', 'quốc'), ('Quủộc', 'Quốc'),
    ('troån', 'trọn'), ('Troån', 'Trọn'),
    ('choån', 'chọn'), ('Choån', 'Chọn'),
    ('quaọn', 'quản'), ('Quaọn', 'Quản'),
    ('baọn', 'bản'), ('Baọn', 'Bản'),
    ('baån', 'bạn'), ('Baån', 'Bạn'),
    ('haånh', 'hạnh'), ('Haånh', 'Hạnh'),
    ('daåy', 'dạy'), ('Daåy', 'Dạy'),
    ('cuäng', 'cũng'), ('Cuäng', 'Cũng'),
    ('cuọa', 'của'), ('Cuọa', 'Của'),
    ('giaọ', 'giả'), ('Giaọ', 'Giả'),
    ('khaọ', 'khả'), ('Khaọ', 'Khả'),
    ('toọa', 'tỏa'), ('Toọa', 'Tỏa'),
    ('luủn', 'luôn'), ('Luủn', 'Luôn'),
    ('cuừng', 'cùng'), ('Cuừng', 'Cùng'),
    ('vủ', 'vô'), ('Vủ', 'Vô'),
    ('tứừ', 'từ'), ('Tứừ', 'Từ'),
    ('tứå', 'tự'), ('Tứå', 'Tự'),
    ('tứ', 'tư'), ('Tứ', 'Tư'),
    ('thứỏ', 'thứ'), ('Thứỏ', 'Thứ'),
    ('sứỏc', 'sức'), ('Sứỏc', 'Sức'),
    ('sứå', 'sự'), ('Sứå', 'Sự'),
    ('dừch', 'dịch'), ('Dừch', 'Dịch'),
    ('hừn', 'hơn'), ('Hừn', 'Hơn'),
    ('lừỏn', 'lớn'), ('Lừỏn', 'Lớn'),
    ('trởn', 'trên'), ('Trởn', 'Trên'),
    ('tiởn', 'tiên'), ('Tiởn', 'Tiên'),
    ('thỗn', 'thân'), ('tỗm', 'tâm'),
    ('kyừ', 'kỳ'), ('lyỏ', 'lý'),
    ('trừọ', 'trở'), ('Trừọ', 'Trở'),
    ('àừừi', 'đời'), ('Àừừi', 'Đời'),
    ('àởộn', 'đến'), ('Àởộn', 'Đến'),
    ('àởì', 'đề'), ('Àởì', 'Đề'),
    ('àởờ', 'để'), ('Àởờ', 'Để'),
    ('àaåt', 'đạt'), ('Àaåt', 'Đạt'),
    ('àaä', 'đã'), ('Àaä', 'Đã'),
    ('àaåo', 'đạo'), ('Àaåo', 'Đạo'),
    ('àoỏn', 'đón'), ('Àoỏn', 'Đón'),
    ('àoåc', 'đọc'), ('Àoåc', 'Đọc'),
    ('ài', 'đi'), ('Ài', 'Đi'),
    ('nhứ', 'như'), ('Nhứ', 'Như'),
    ('duåc', 'dục'), ('Duåc', 'Dục'),
    ('phuỏc', 'phúc'), ('Phuỏc', 'Phúc'),
    ('naừo', 'nào'), ('Naừo', 'Nào'),
    ('daừng', 'dàng'), ('Daừng', 'Dàng'),
    ('thaừnh', 'thành'), ('Thaừnh', 'Thành'),
    ('vaừ', 'và'), ('Vaừ', 'Và'),
    ('maừ', 'mà'), ('Maừ', 'Mà'),
    ('laừm', 'làm'), ('Laừm', 'Làm'),
    ('laừ', 'là'), ('Laừ', 'Là'),
    ('taừi', 'tài'), ('Taừi', 'Tài'),
    ('nhaừ', 'nhà'), ('Nhaừ', 'Nhà'),
    ('coừn', 'còn'), ('Coừn', 'Còn'),
    ('reừn', 'rèn'), ('Reừn', 'Rèn'),
    ('taỏc', 'tác'), ('Taỏc', 'Tác'),
    ('Thoỏi', 'Thói'), ('thoỏi', 'thói'),
    ('àaỏnh', 'đánh'), ('Àaỏnh', 'Đánh'),
    ('giaỏ', 'giá'), ('Giaỏ', 'Giá'),
    ('saỏch', 'sách'), ('Saỏch', 'Sách'),
    ('sỏch', 'sách'),
    ('coỏ', 'có'), ('Coỏ', 'Có'),
    ('caỏch', 'cách'), ('Caỏch', 'Cách'),
    ('giaỏo', 'giáo'), ('Giaỏo', 'Giáo'),
    ('giaọng', 'giảng'), ('Giaọng', 'Giảng'),
    ('phaỏp', 'pháp'), ('Phaỏp', 'Pháp'),
    ('phaỏt', 'phát'), ('Phaỏt', 'Phát'),
    ('haừnh', 'hành'), ('Haừnh', 'Hành'),
    ('moåi', 'mọi'), ('Moåi', 'Mọi'),
    ('troång', 'trọng'), ('Troång', 'Trọng'),
    ('laänh', 'lãnh'), ('Laänh', 'Lãnh'),
    ('quản trừ', 'quản trị'), ('giá trừ', 'giá trị'),
    ('triởåu', 'triệu'), ('vứåc', 'vực'), ('triởờn', 'triển'),
    ('loaåi', 'loại'), ('hoaå', 'hoạ'),
    ('caỏc', 'các'), ('Caỏc', 'Các')
]

# Bộ quy tắc ghép âm vần chung
VOWEL_PATTERNS = [
    # Dấu sắc 'ỏ'
    ('aỏ', 'á'), ('oỏ', 'ó'), ('uỏ', 'ú'), ('eỏ', 'é'), ('iỏ', 'í'), ('yỏ', 'ý'),
    ('Aỏ', 'Á'), ('Oỏ', 'Ó'), ('Uỏ', 'Ú'), ('Eỏ', 'É'), ('Iỏ', 'Í'), ('Yỏ', 'Ý'),
    # Dấu huyền 'ừ'
    ('aừ', 'à'), ('oừ', 'ò'), ('uừ', 'ù'), ('eừ', 'è'), ('iừ', 'ì'), ('yừ', 'ỳ'),
    ('Aừ', 'À'), ('Oừ', 'Ò'), ('Uừ', 'Ù'), ('Eừ', 'È'), ('Iừ', 'Ì'), ('Yừ', 'Ỳ'),
    # Dấu hỏi 'ọ'
    ('aọ', 'ả'), ('oọ', 'ỏ'), ('uọ', 'ủ'), ('eọ', 'ẻ'), ('iọ', 'ỉ'), ('yọ', 'ỷ'),
    ('Aọ', 'Ả'), ('Oọ', 'Ỏ'), ('Uọ', 'Ủ'), ('Eọ', 'Ẻ'), ('Iọ', 'Ỉ'), ('Yọ', 'Ỷ'),
    # Dấu ngã 'ä'
    ('aä', 'ã'), ('oä', 'õ'), ('uä', 'ũ'), ('eä', 'ẽ'), ('iä', 'ĩ'), ('yä', 'ỹ'),
    ('Aä', 'Ã'), ('Oä', 'Õ'), ('Uä', 'Ũ'), ('Eä', 'Ẽ'), ('Iä', 'Ĩ'), ('Yä', 'Ỹ'),
    # Dấu nặng 'å'
    ('aå', 'ạ'), ('oå', 'ọ'), ('uå', 'ụ'), ('eå', 'ẹ'), ('iå', 'ị'), ('yå', 'ỵ'),
    ('Aå', 'Ạ'), ('Oå', 'Ọ'), ('Uå', 'Ụ'), ('Eå', 'Ẹ'), ('Iå', 'Ị'), ('Yå', 'Ỵ'),
    # Chữ â 'ỗ'
    ('ỗộ', 'ấ'), ('ỗì', 'ầu'), ('ỗờ', 'ẩ'), ('ỗä', 'ẫ'), ('ỗå', 'ậ'),
    # Chữ ê 'ở'
    ('ởộ', 'ế'), ('ởì', 'ề'), ('ởờ', 'ể'), ('ởớ', 'ễ'), ('ởå', 'ệ'),
    # Chữ ô 'ủ'
    ('ủộ', 'ố'), ('ủì', 'ồ'), ('ủờ', 'ổ'), ('ủä', 'ỗ'), ('ủå', 'ộ'),
    # Chữ ư 'ứ'
    ('ứỏ', 'ứ'), ('ứừ', 'ừ'), ('ứờ', 'ử'), ('ứä', 'ữ'), ('ứå', 'ự'),
]

LIGATURES = {
    'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬀ': 'ff', 'ﬃ': 'ffi', 'ﬄ': 'ffl',
    'œ': 'oe', 'Œ': 'OE', 'æ': 'ae', 'Æ': 'AE'
}

def decode_hocdedang_font(text: str) -> str:
    """Giải mã font tiếng Việt bị mã hóa sai theo dạng hocdedang/custom glyphs"""
    if not text:
        return ""
    
    # 1. Áp dụng bảng từ vựng và cụm từ phức tạp trước
    for src, dst in HOCDEDANG_COMPOUNDS:
        text = text.replace(src, dst)
        
    # 2. Áp dụng các quy tắc ghép âm vần
    for src, dst in VOWEL_PATTERNS:
        text = text.replace(src, dst)

    # 3. Thay thế các chữ 'à' đứng đầu từ mà theo sau là nguyên âm -> chuyển thành 'đ'
    text = re.sub(r'\bà(?=[aáàảãạăắằẳẵặâấầẩẫậeéèẻẽẹêếềểễệiíìỉĩịoóòỏõọôốồổỗộơớờởỡợuúùủũụưứừửữựyýỳỷỹỵ])', 'đ', text)
    text = re.sub(r'\bÀ(?=[aáàảãạăắằẳẵặâấầẩẫậeéèẻẽẹêếềểễệiíìỉĩịoóòỏõọôốồổỗộơớờởỡợuúùủũụưứừửữựyýỳỷỹỵ])', 'Đ', text)

    return text

def fix_vietnamese_font(text: str) -> str:
    """
    Bộ sửa lỗi font tiếng Việt toàn diện:
    - Sửa lỗi glyph mapping / hocdedang.com
    - Chuyển đổi Ligature (fi, fl,...)
    - Chuẩn hóa Unicode NFD -> NFC
    - Nối từ bị gạch ngang ngắt dòng
    """
    if not text:
        return ""

    # Kiểm tra xem có dấu hiệu của font hocdedang/custom PDF không
    markers = ['LÚẩI', 'GIÚấI', 'àứừåc', 'thởộ giừỏi', 'àởờ', 'àaåt', 'phỗờm', 'cuủộn', 'sủộng']
    if any(m in text for m in markers) or text.count('à') > 10 and text.count('ở') > 10:
        text = decode_hocdedang_font(text)

    # Chuyển đổi Ligatures
    for lig, rep in LIGATURES.items():
        text = text.replace(lig, rep)

    # Chuẩn hóa Unicode NFC
    text = unicodedata.normalize('NFC', text)

    # Nối từ ngắt dòng
    text = re.sub(r'(\b[a-zA-ZÀ-ỹ]+)-\s*\n\s*([a-zA-ZÀ-ỹ]+\b)', r'\1\2', text)

    return text

def ai_restore_vietnamese_text(text: str, api_key: str) -> str:
    """
    Dùng Gemini AI để khôi phục văn bản tiếng Việt bị lỗi font (mojibake)
    hoàn hảo 100% theo ngữ cảnh, với cơ chế Auto-Fallback & Retry chống lỗi 503/429/404.
    """
    import time
    from google import genai
    client = genai.Client(api_key=api_key)
    
    prompt = f"""Bạn là một chuyên gia ngôn ngữ học tiếng Việt và xử lý dữ liệu số hóa sách.
Đoạn văn bản sau được trích xuất từ một cuốn sách PDF nhưng bị lỗi mã hóa font (mojibake, bảng mã cũ, vỡ dấu tiếng Việt).

Nhiệm vụ của bạn:
1. Hãy khôi phục lại toàn bộ văn bản này thành tiếng Việt chuẩn, đúng chính tả, đúng dấu câu, ngữ pháp hoàn chỉnh và mạch lạc.
2. Giữ nguyên ý nghĩa gốc của tác giả và các từ tiếng Anh (như tiêu đề sách, tên riêng, thuật ngữ).
3. Chỉ trả về duy nhất nội dung văn bản tiếng Việt đã được khôi phục, không thêm lời chào hay giải thích nào khác.

Văn bản bị lỗi font:
\"\"\"
{text}
\"\"\"
"""
    # Danh sách các model theo thứ tự ưu tiên
    candidate_models = [
        "gemini-3.8-flash",
        "gemini-3-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    
    last_error = None
    for model_name in candidate_models:
        for attempt in range(2):  # Thử lại 2 lần mỗi model nếu bị 503 quá tải tạm thời
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_error = e
                err_msg = str(e)
                # Nếu 503 (quá tải) hoặc 429 (hết quota) hoặc 404 (model cũ), thử model khác
                if any(code in err_msg for code in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "404", "NOT_FOUND"]):
                    time.sleep(1.0)
                    continue
                # Lỗi nghiêm trọng khác (như sai API key), raise ngay
                raise e

    # Nếu tất cả model AI đều bận hoặc lỗi mạng, tự động fallback sang bộ giải mã offline
    print(f"[!] AI unavailable ({last_error}), falling back to offline Vietnamese font fixer...")
    return fix_vietnamese_font(text)
