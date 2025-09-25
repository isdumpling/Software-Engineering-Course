# /home/dumpling/projects/Software-Engineering-Course/backend/process_pdf.py (具备OCR功能的最终版本)
import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# --- 配置 ---
PDF_SOURCE_PATH = "knowledge_base/se.pdf"
CHROMA_DB_PATH = "chroma_db"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def ocr_pdf_to_documents(pdf_path):
    """
    使用 OCR 从纯图片 PDF 中提取文本并转换为 Document 对象。
    """
    print("⚠️ 检测到可能是图片PDF，正在启动 OCR 模式...")
    images = convert_from_path(pdf_path)
    documents = []
    
    for i, image in enumerate(images):
        page_num = i + 1
        print(f"📄 正在 OCR 处理第 {page_num}/{len(images)} 页...")
        try:
            # 使用 Tesseract 从图片中提取文本
            text = pytesseract.image_to_string(image, lang='chi_sim') # 假设是英文书籍
            if text.strip(): # 只有在提取到文本时才创建文档
                metadata = {"source": pdf_path, "page": page_num}
                documents.append(Document(page_content=text, metadata=metadata))
        except Exception as e:
            print(f" OCR 处理第 {page_num} 页时出错: {e}")
            
    print(f"✅ OCR 处理完成，成功提取 {len(documents)} 页的内容。")
    return documents

def main():
    """
    处理PDF文件，生成向量嵌入并存入ChromaDB。
    """
    print("🚀 开始处理PDF文件...")

    if not os.path.exists(PDF_SOURCE_PATH):
        print(f"❌ 错误：找不到PDF文件，请确保 '{PDF_SOURCE_PATH}' 文件存在。")
        return

    # 1. 尝试使用 OCR 加载 PDF
    documents = ocr_pdf_to_documents(PDF_SOURCE_PATH)

    if not documents:
        print("❌ 错误：OCR未能从PDF中提取任何内容。请检查文件是否损坏。")
        return

    # 2. 切分文本
    print("🔪 正在进行文本分块...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    texts = text_splitter.split_documents(documents)
    
    if not texts:
        print("❌ 错误：文本分块后内容为空。")
        return
        
    print(f"✅ 文本分块完成，共生成 {len(texts)} 个文本块。")

    # 3. 加载嵌入模型
    print(f"🧠 正在加载嵌入模型: {EMBEDDING_MODEL_NAME}")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    print("✅ 嵌入模型加载成功。")

    # 4. 创建并持久化向量数据库
    print(f"💾 正在创建向量数据库并存入 '{CHROMA_DB_PATH}'...")
    vectordb = Chroma.from_documents(
        documents=texts, 
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    vectordb.persist()
    print("🎉 所有步骤完成！您的图片版PDF知识库已成功创建。")


if __name__ == "__main__":
    main()