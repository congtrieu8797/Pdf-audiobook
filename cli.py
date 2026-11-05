import argparse
import os
import sys

# Đảm bảo mã hóa UTF-8 trên Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv

from pdf_processor import extract_text_from_pdf
from tts_engine import convert_text_to_mp3, VOICE_CATALOG
from summarizer import summarize_for_audiobook

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Chuyển sách PDF thành Sách nói Audio (MP3)")
    parser.add_argument("pdf_path", help="Đường dẫn đến file PDF")
    parser.add_argument("--mode", choices=["summary", "full"], default="summary", 
                        help="Chế độ: 'summary' (tóm tắt) hoặc 'full' (đọc toàn bộ)")
    parser.add_argument("--voice", default="vi-VN-HoaiMyNeural", 
                        choices=list(VOICE_CATALOG.keys()), help="Mã giọng đọc (ví dụ: vi-VN-HoaiMyNeural, vi-VN-NamMinhNeural, google-vi)")
    parser.add_argument("--rate", default="+0%", help="Tốc độ đọc (ví dụ: '+10%%', '-5%%')")
    parser.add_argument("--pitch", default="+0Hz", help="Cao độ đọc (ví dụ: '+5Hz', '-5Hz')")
    parser.add_argument("--start", type=int, default=1, help="Trang bắt đầu (mặc định: 1)")
    parser.add_argument("--end", type=int, default=None, help="Trang kết thúc (mặc định: hết)")
    parser.add_argument("--output", default=None, help="Tên file mp3 đầu ra")

    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Lỗi: Không tìm thấy file '{args.pdf_path}'")
        sys.exit(1)

    print(f"[*] Đang trích xuất nội dung từ '{args.pdf_path}'...")
    raw_text, meta = extract_text_from_pdf(args.pdf_path, start_page=args.start, end_page=args.end)
    print(f"[+] Trích xuất thành công: {meta['processed_pages']} trang, ~{meta['word_count']} từ.")

    text_to_speak = ""
    if args.mode == "summary":
        print("[*] Đang tóm tắt nội dung bằng Gemini AI...")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("[!] Cảnh báo: Biến môi trường GEMINI_API_KEY chưa được đặt. Hãy gán GEMINI_API_KEY để sử dụng chế độ summary.")
            sys.exit(1)
        text_to_speak = summarize_for_audiobook(raw_text, api_key=api_key)
        print("[+] Hoàn tất kịch bản tóm tắt.")
    else:
        print("[*] Chế độ đọc toàn bộ sách...")
        text_to_speak = raw_text

    output_path = args.output
    if not output_path:
        base_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
        output_path = f"{args.mode}_{base_name}.mp3"

    print(f"[*] Đang chuyển văn bản thành giọng nói (Voice: {args.voice}, Rate: {args.rate}, Pitch: {args.pitch})...")
    def on_progress(ratio, msg):
        percent = int(ratio * 100)
        sys.stdout.write(f"\r[{percent}%] {msg}")
        sys.stdout.flush()

    convert_text_to_mp3(text_to_speak, output_path, voice=args.voice, rate=args.rate, pitch=args.pitch, progress_callback=on_progress)
    print(f"\n[+] Đã tạo thành công file sách nói: {output_path}")

if __name__ == "__main__":
    main()
