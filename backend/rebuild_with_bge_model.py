#!/usr/bin/env python3
"""
使用新的BGE模型重建向量数据库
"""
import os
import shutil
from targeted_fix_retrieval import extract_lifecycle_focused_content, create_priority_documents

# 尝试使用新版本
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    print("✅ 使用新版 langchain_huggingface.HuggingFaceEmbeddings")
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    print("⚠️ 回退到 langchain_community.embeddings.HuggingFaceEmbeddings")

from langchain_community.vectorstores import Chroma

# 配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCX_SOURCE_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, 'knowledge_base', 'se.docx'))
CHROMA_DB_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, 'chroma_db'))
NEW_EMBEDDING_MODEL_NAME = "BAAI/bge-large-zh-v1.5"

def rebuild_vectordb_with_bge():
    """使用BGE模型重建向量数据库"""
    print("🚀 开始使用BGE大模型重建向量数据库...")
    
    try:
        # 1. 删除旧的向量数据库
        if os.path.exists(CHROMA_DB_PATH):
            print(f"🗑️ 删除旧的向量数据库: {CHROMA_DB_PATH}")
            shutil.rmtree(CHROMA_DB_PATH)
        
        # 2. 重新提取和处理内容（使用我们之前的优化方法）
        print(f"📄 重新处理知识库内容: {DOCX_SOURCE_PATH}")
        categorized_content, uncategorized_content = extract_lifecycle_focused_content(DOCX_SOURCE_PATH)
        documents = create_priority_documents(categorized_content, uncategorized_content)
        
        if not documents:
            print("❌ 未能创建有效文档")
            return False
        
        print(f"✅ 成功创建了 {len(documents)} 个优化文档")
        
        # 3. 加载新的BGE嵌入模型
        print(f"🧠 正在加载新的BGE嵌入模型: {NEW_EMBEDDING_MODEL_NAME}")
        embeddings = HuggingFaceEmbeddings(model_name=NEW_EMBEDDING_MODEL_NAME)
        print("✅ BGE嵌入模型加载成功")
        
        # 4. 创建新的向量数据库
        print(f"💾 正在创建新的向量数据库（1024维）...")
        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=CHROMA_DB_PATH
        )
        
        # 5. 验证新数据库
        doc_count = len(vectordb._collection.get()['documents'])
        print(f"📊 新向量数据库创建成功，包含 {doc_count} 个文档")
        
        # 6. 测试新模型的检索效果
        print(f"\n🧪 测试新BGE模型的检索效果...")
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        
        test_queries = [
            "软件开发生命周期",
            "软件开发的几个阶段", 
            "这门课程的主要内容",
            "瀑布模型"
        ]
        
        for query in test_queries:
            print(f"\n🔍 测试查询: '{query}'")
            try:
                results = retriever.invoke(query)
                for i, result in enumerate(results):
                    # 提取标签
                    content = result.page_content
                    tag = "无标签"
                    if content.startswith('['):
                        tag_end = content.find(']')
                        if tag_end > 0:
                            tag = content[1:tag_end]
                    
                    print(f"   结果 {i+1}: [{tag}] {content[:80]}...")
            except Exception as e:
                print(f"   ❌ 查询失败: {e}")
        
        print(f"\n🎉 BGE模型向量数据库重建完成！")
        print(f"💡 现在请重启后端服务以使用新的模型和数据库")
        return True
        
    except Exception as e:
        print(f"❌ 重建过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = rebuild_vectordb_with_bge()
    if success:
        print(f"\n✅ 重建成功！重启后端服务即可体验更强大的BGE模型")
    else:
        print(f"\n❌ 重建失败，请检查错误信息")
