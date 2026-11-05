import asyncio
import os
import re
import io
import time
from typing import List, Callable, Optional, Dict
import edge_tts
from edge_tts.exceptions import NoAudioReceived
from gtts import gTTS

# Danh mục giọng đọc được phân loại chi tiết
VOICE_CATALOG = {
    # --- TIẾNG VIỆT ---
    "vi-VN-HoaiMyNeural": {
        "name": "Hoài My (Nữ) - Microsoft AI",
        "lang": "Tiếng Việt 🇻🇳",
        "gender": "Nữ",
        "desc": "Truyền cảm, ngọt ngào, tự nhiên (Thích hợp: Sách kỹ năng, tiểu thuyết, tản văn)",
        "engine": "edge",
        "sample": "Chào bạn, tôi là Hoài My. Rất vui được đồng hành cùng bạn qua từng trang sách nói hôm nay."
    },
    "vi-VN-NamMinhNeural": {
        "name": "Nam Minh (Nam) - Microsoft AI",
        "lang": "Tiếng Việt 🇻🇳",
        "gender": "Nam",
        "desc": "Trầm ấm, đĩnh đạc, rõ ràng (Thích hợp: Sách kinh doanh, tài chính, triết học)",
        "engine": "edge",
        "sample": "Xin chào bạn, tôi là Nam Minh. Chúc bạn có những phút giây lắng đọng và thu thập được nhiều kiến thức giá trị."
    },
    "google-vi": {
        "name": "Chị Google (Nữ) - Google TTS",
        "lang": "Tiếng Việt 🇻🇳",
        "gender": "Nữ",
        "desc": "Giọng đọc Google Translate quen thuộc, rõ ràng từng từ",
        "engine": "gtts",
        "sample": "Xin chào, đây là giọng đọc Chị Google quen thuộc."
    },

    # --- TIẾNG ANH (MỸ) ---
    "en-US-JennyNeural": {
        "name": "Jenny (Female) - US English",
        "lang": "Tiếng Anh (Mỹ) 🇺🇸",
        "gender": "Nữ",
        "desc": "Ấm áp, tự nhiên, phong cách kể chuyện sinh động",
        "engine": "edge",
        "sample": "Hello, I am Jenny. Welcome to this audiobook experience. I hope you enjoy listening."
    },
    "en-US-GuyNeural": {
        "name": "Guy (Male) - US English",
        "lang": "Tiếng Anh (Mỹ) 🇺🇸",
        "gender": "Nam",
        "desc": "Trầm tĩnh, dễ chịu, độ rõ âm cực tốt",
        "engine": "edge",
        "sample": "Hello, I'm Guy. Let's explore the knowledge inside this book together."
    },
    "en-US-AriaNeural": {
        "name": "Aria (Female) - US English",
        "lang": "Tiếng Anh (Mỹ) 🇺🇸",
        "gender": "Nữ",
        "desc": "Truyền cảm, diễn đạt cảm xúc cao cấp",
        "engine": "edge",
        "sample": "Welcome! I am Aria, and I am delighted to be your reader today."
    },
    "en-US-ChristopherNeural": {
        "name": "Christopher (Male) - US English",
        "lang": "Tiếng Anh (Mỹ) 🇺🇸",
        "gender": "Nam",
        "desc": "Dõng dạc, phong cách phát thanh viên chuyên nghiệp",
        "engine": "edge",
        "sample": "Good day. This is Christopher, reading with professional broadcasting clarity."
    },

    # --- TIẾNG ANH (ANH - UK) ---
    "en-GB-SoniaNeural": {
        "name": "Sonia (Female) - British English",
        "lang": "Tiếng Anh (Anh) 🇬🇧",
        "gender": "Nữ",
        "desc": "Chuẩn giọng London, thanh lịch, tinh tế",
        "engine": "edge",
        "sample": "Good day to you. I'm Sonia, reading in standard British English."
    },
    "en-GB-RyanNeural": {
        "name": "Ryan (Male) - British English",
        "lang": "Tiếng Anh (Anh) 🇬🇧",
        "gender": "Nam",
        "desc": "Lịch lãm, trầm ấm chuẩn phong cách BBC",
        "engine": "edge",
        "sample": "Greetings. This is Ryan, bringing you a classic British narrative tone."
    },

    # --- TIẾNG PHÁP ---
    "fr-FR-DeniseNeural": {
        "name": "Denise (Femme) - Français",
        "lang": "Tiếng Pháp 🇫🇷",
        "gender": "Nữ",
        "desc": "Dịu dàng, phát âm chuẩn Paris",
        "engine": "edge",
        "sample": "Bonjour, je suis Denise. Bienvenue dans votre livre audio."
    },
    "fr-FR-HenriNeural": {
        "name": "Henri (Homme) - Français",
        "lang": "Tiếng Pháp 🇫🇷",
        "gender": "Nam",
        "desc": "Trầm ấm, trang nhã",
        "engine": "edge",
        "sample": "Bonjour, c'est Henri. Bonne écoute de votre ouvrage."
    },

    # --- TIẾNG NHẬT ---
    "ja-JP-NanamiNeural": {
        "name": "Nanami (女性) - 日本語",
        "lang": "Tiếng Nhật 🇯🇵",
        "gender": "Nữ",
        "desc": "Trong trẻo, diễn cảm tự nhiên",
        "engine": "edge",
        "sample": "こんにちは、七海です。素敵なオーディオブックの時間をお楽しみください。"
    },
    "ja-JP-KeitaNeural": {
        "name": "Keita (男性) - 日本語",
        "lang": "Tiếng Nhật 🇯🇵",
        "gender": "Nam",
        "desc": "Điềm đạm, ấm áp",
        "engine": "edge",
        "sample": "こんにちは、けいたです。どうぞリラックスしてお聞きください。"
    },

    # --- TIẾNG TRUNG (QUAN THOẠI) ---
    "zh-CN-XiaoxiaoNeural": {
        "name": "Xiaoxiao (女声) - 普通话",
        "lang": "Tiếng Trung 🇨🇳",
        "gender": "Nữ",
        "desc": "Ngọt ngào, tự nhiên, diễn cảm cao",
        "engine": "edge",
        "sample": "你好，我是晓晓。很高兴为你朗读这本书。"
    },
    "zh-CN-YunxiNeural": {
        "name": "Yunxi (男声) - 普通话",
        "lang": "Tiếng Trung 🇨🇳",
        "gender": "Nam",
        "desc": "Trầm ấm, giọng phát thanh chuyên nghiệp",
        "engine": "edge",
        "sample": "你好，我是云希。让我们一起开始这段听书之旅。"
    },

    # --- TIẾNG HÀN ---
    "ko-KR-SunHiNeural": {
        "name": "SunHi (여성) - 한국어",
        "lang": "Tiếng Hàn 🇰🇷",
        "gender": "Nữ",
        "desc": "Trong trẻo, thanh lịch",
        "engine": "edge",
        "sample": "안녕하세요, 선희입니다. 편안하게 오디오북을 감상해 보세요."
    },
    "ko-KR-InJoonNeural": {
        "name": "InJoon (남성) - 한국어",
        "lang": "Tiếng Hàn 🇰🇷",
        "gender": "Nam",
        "desc": "Ấm áp, nhẹ nhàng",
        "engine": "edge",
        "sample": "안녕하세요, 인준입니다. 즐거운 독서 시간이 되시길 바랍니다."
    }
}

AVAILABLE_VOICES = {k: f"{v['lang']} - {v['name']}" for k, v in VOICE_CATALOG.items()}

def sanitize_text_for_tts(text: str) -> str:
    """
    Làm sạch văn bản, loại bỏ các ký tự đặc biệt nguy hiểm gây lỗi NoAudioReceived
    hoặc lỗi cú pháp SSML trong Microsoft Edge TTS.
    """
    if not text:
        return ""
    
    # 1. Thay thế các ký tự SSML/XML đặc biệt
    text = text.replace('&', ' và ')
    text = text.replace('<', ' ')
    text = text.replace('>', ' ')
    
    # 2. Thay thế ký hiệu đặc biệt thành chữ để TTS phát âm tự nhiên
    text = text.replace('%', ' phần trăm ')
    text = text.replace('$', ' đô la ')
    text = text.replace('@', ' a còng ')
    text = text.replace('/', ' trên ')
    text = text.replace('+', ' cộng ')
    text = text.replace('=', ' bằng ')
    
    # 3. Loại bỏ chuỗi ký tự gạch nối, bằng, hoa thị lặp lại (như ---, ===, ***)
    text = re.sub(r'[-=_*~#]{2,}', ' ', text)
    
    # 4. Loại bỏ các ký tự điều khiển ASCII và bullet points lạ
    text = re.sub(r'[\x00-\x1f\x7f-\x9f\u2022\u2023\u25E6\u2043\u2219]', ' ', text)
    
    # 5. Chuẩn hóa khoảng trắng
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    return text.strip()

def split_text_into_chunks(text: str, max_chars: int = 1200) -> List[str]:
    """Chia nhỏ văn bản thành các đoạn theo ranh giới câu, loại bỏ các đoạn rỗng"""
    sanitized = sanitize_text_for_tts(text)
    if len(sanitized) <= max_chars:
        return [sanitized] if sanitized else []

    sentence_endings = re.compile(r'(?<=[.!?\n])\s+')
    sentences = sentence_endings.split(sanitized)
    
    chunks = []
    current_chunk = []
    current_len = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(sentence) > max_chars:
            sub_parts = re.split(r'(?<=[,;:])\s+', sentence)
            for sub in sub_parts:
                sub = sub.strip()
                if not sub:
                    continue
                if current_len + len(sub) > max_chars and current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [sub]
                    current_len = len(sub)
                else:
                    current_chunk.append(sub)
                    current_len += len(sub)
            continue

        if current_len + len(sentence) > max_chars and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_len = len(sentence)
        else:
            current_chunk.append(sentence)
            current_len += len(sentence)
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    # Chỉ giữ lại các chunk có chứa ký tự chữ cái hoặc số
    valid_chunks = [ch for ch in chunks if re.search(r'[a-zA-Z0-9À-ỹ]', ch)]
    return valid_chunks

def _get_gtts_audio_bytes(text: str, lang: str = "vi") -> bytes:
    """Tạo audio bytes dự phòng từ Google TTS (gTTS)"""
    tts = gTTS(text=text, lang=lang, slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

async def _convert_edge_tts(
    text: str,
    output_path: str,
    voice: str = "vi-VN-HoaiMyNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz",
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> str:
    """Tạo audio qua Microsoft Edge TTS với cơ chế Auto-Retry và Fallback gTTS chống lỗi NoAudioReceived"""
    chunks = split_text_into_chunks(text)
    total_chunks = len(chunks)
    
    if total_chunks == 0:
        raise ValueError("Văn bản không có nội dung chữ hợp lệ để chuyển thành giọng nói.")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fallback_lang = "vi" if "vi" in voice else "en"
    
    with open(output_path, "wb") as f_out:
        for idx, chunk in enumerate(chunks):
            if progress_callback:
                progress = idx / total_chunks
                progress_callback(progress, f"Đang đọc phần {idx + 1}/{total_chunks}...")
            
            # Thử với Edge TTS tối đa 2 lần, nếu lỗi thì fallback sang gTTS cho riêng chunk đó
            chunk_written = False
            for attempt in range(2):
                try:
                    communicate = edge_tts.Communicate(text=chunk, voice=voice, rate=rate, pitch=pitch)
                    received_any = False
                    async for chunk_data in communicate.stream():
                        if chunk_data["type"] == "audio":
                            f_out.write(chunk_data["data"])
                            received_any = True
                    if received_any:
                        chunk_written = True
                        break
                except (NoAudioReceived, Exception) as ex:
                    if attempt == 0:
                        await asyncio.sleep(0.5)
                        continue
                    # Ở lần thử thứ 2 nếu vẫn lỗi, dùng gTTS dự phòng
                    break
            
            # Nếu Edge TTS không trả về audio cho chunk này, dùng gTTS dự phòng
            if not chunk_written:
                try:
                    fallback_bytes = _get_gtts_audio_bytes(chunk, lang=fallback_lang)
                    f_out.write(fallback_bytes)
                except Exception:
                    pass  # Bỏ qua chunk này nếu cả 2 đều không đọc được để không làm gián đoạn cả cuốn sách
                    
    if progress_callback:
        progress_callback(1.0, "Hoàn tất tạo file âm thanh!")
        
    return output_path

def _convert_gtts(
    text: str,
    output_path: str,
    lang: str = "vi",
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> str:
    """Tạo audio qua Google TTS (gTTS)"""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    if progress_callback:
        progress_callback(0.3, "Đang kết nối Google TTS...")
        
    clean_text = sanitize_text_for_tts(text)
    tts = gTTS(text=clean_text, lang=lang, slow=False)
    tts.save(output_path)
    
    if progress_callback:
        progress_callback(1.0, "Hoàn tất tạo file âm thanh từ Google TTS!")
        
    return output_path

def convert_text_to_mp3(
    text: str,
    output_path: str,
    voice: str = "vi-VN-HoaiMyNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz",
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> str:
    """
    Chuyển văn bản thành file âm thanh MP3 dựa theo giọng đã chọn (Edge AI hoặc gTTS).
    Có cơ chế tự động Fallback kiên cố, không bao giờ để lỗi NoAudioReceived làm sập ứng dụng.
    """
    voice_info = VOICE_CATALOG.get(voice, {})
    engine = voice_info.get("engine", "edge")
    
    if engine == "gtts":
        lang = "vi" if "vi" in voice else "en"
        return _convert_gtts(text, output_path, lang=lang, progress_callback=progress_callback)
    else:
        try:
            return asyncio.run(
                _convert_edge_tts(text, output_path, voice=voice, rate=rate, pitch=pitch, progress_callback=progress_callback)
            )
        except Exception as e:
            # Fallback toàn cục sang Google TTS nếu toàn bộ kết nối Edge TTS gặp sự cố
            if progress_callback:
                progress_callback(0.5, "Đang kích hoạt chế độ dự phòng Google TTS...")
            lang = "vi" if "vi" in voice else "en"
            return _convert_gtts(text, output_path, lang=lang, progress_callback=progress_callback)

def generate_voice_sample(voice: str) -> bytes:
    """
    Tạo nhanh file mẫu âm thanh (vài giây) để nghe thử trước khi chọn giọng.
    """
    voice_info = VOICE_CATALOG.get(voice, VOICE_CATALOG["vi-VN-HoaiMyNeural"])
    sample_text = sanitize_text_for_tts(voice_info.get("sample", "Xin chào, đây là giọng đọc thử nghiệm."))
    engine = voice_info.get("engine", "edge")

    temp_path = os.path.join(os.path.dirname(__file__), "output", f"sample_{voice}.mp3")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)

    if engine == "gtts":
        lang = "vi" if "vi" in voice else "en"
        tts = gTTS(text=sample_text, lang=lang, slow=False)
        tts.save(temp_path)
    else:
        async def _make_sample():
            com = edge_tts.Communicate(text=sample_text, voice=voice)
            await com.save(temp_path)
        try:
            asyncio.run(_make_sample())
        except Exception:
            lang = "vi" if "vi" in voice else "en"
            tts = gTTS(text=sample_text, lang=lang, slow=False)
            tts.save(temp_path)

    with open(temp_path, "rb") as f:
        audio_data = f.read()
    return audio_data
