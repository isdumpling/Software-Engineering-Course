#!/usr/bin/env python3
"""
诊断知识库内容的脚本
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 检查ChromaDB内容
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    
    print("🔍 正在检查向量数据库内容...")
    
    # 配置
    CHROMA_DB_PATH = "chroma_db"
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    
    # 加载嵌入模型和向量数据库
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectordb = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)
    
    # 获取数据库中的所有文档
    collection = vectordb._collection
    all_docs = collection.get()
    
    print(f"📊 向量数据库统计:")
    print(f"   - 总文档数: {len(all_docs['documents'])}")
    print(f"   - 总ID数: {len(all_docs['ids'])}")
    
    print(f"\n📄 前5个文档内容预览:")
    for i, doc in enumerate(all_docs['documents'][:5]):
        print(f"\n--- 文档 {i+1} ---")
        print(f"长度: {len(doc)} 字符")
        print(f"内容预览: {doc[:200]}...")
        if len(doc) < 50:
            print(f"⚠️  警告: 这个文档内容太短了!")
    
    # 测试检索功能
    print(f"\n🔍 测试检索功能:")
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    test_query = "软件工程"
    results = retriever.get_relevant_documents(test_query)
    
    print(f"查询: '{test_query}'")
    print(f"检索结果数: {len(results)}")
    
    for i, result in enumerate(results):
        print(f"\n检索结果 {i+1}:")
        print(f"内容: {result.page_content[:200]}...")
        print(f"元数据: {result.metadata}")

except Exception as e:
    print(f"❌ 检查过程中出错: {e}")
    import traceback
    traceback.print_exc()

# 检查原始DOCX文件
try:
    print(f"\n📋 检查原始DOCX文件...")
    
    # 尝试使用python-docx
    try:
        import docx
        
        docx_path = "knowledge_base/se.docx"
        if os.path.exists(docx_path):
            doc = docx.Document(docx_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            print(f"DOCX文件统计:")
            print(f"   - 总段落数: {len(paragraphs)}")
            print(f"   - 文件大小: {os.path.getsize(docx_path)} 字节")
            
            print(f"\n前5个段落内容:")
            for i, para in enumerate(paragraphs[:5]):
                print(f"\n段落 {i+1} (长度: {len(para)}):")
                print(f"{para[:150]}...")
                
        else:
            print(f"❌ DOCX文件不存在: {docx_path}")
            
    except ImportError:
        print("⚠️  python-docx 未安装，无法检查DOCX内容")
        
except Exception as e:
    print(f"❌ 检查DOCX时出错: {e}")
