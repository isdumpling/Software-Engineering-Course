# AiAgent2/backend/check_ocr.py
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

PDF_SOURCE_PATH = "knowledge_base/se.pdf"
PAGES_TO_CHECK = 23 # 我们只检查前5页就足够了

def check_text_quality():
    print(f"🕵️  正在对PDF '{PDF_SOURCE_PATH}' 进行 OCR 质量检查...")

    try:
        images = convert_from_path(PDF_SOURCE_PATH, first_page=1, last_page=PAGES_TO_CHECK)

        for i, image in enumerate(images):
            page_num = i + 1
            print(f"\n===== 📄 第 {page_num} 页 OCR 识别结果 =====\n")

            # 使用中文简体语言包进行识别
            text = pytesseract.image_to_string(image, lang='chi_sim')

            print(text)

        print(f"\n========================================")
        print("✅ 检查完成。请查看上面打印的文本，判断识别出的文字是否清晰、准确、有意义。")

    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")

if __name__ == "__main__":
    check_text_quality()