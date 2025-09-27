#!/usr/bin/env python3
"""
快速测试当前向量数据库的状态
"""
import os
from langchain_community.vectorstores import Chroma

# 尝试使用新版本
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

def test_current_vectordb():
    """测试当前向量数据库的状态"""
    CHROMA_DB_PATH = "chroma_db"
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    
    print("🔍 正在检查当前向量数据库状态...")
    
    try:
        # 加载当前的向量数据库
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        vectordb = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)
        
        # 获取数据库信息
        collection = vectordb._collection
        all_data = collection.get()
        
        print(f"📊 数据库统计:")
        print(f"   - 文档总数: {len(all_data['documents'])}")
        
        # 分析文档标签分布
        tag_counts = {}
        lifecycle_docs = []
        
        for i, doc in enumerate(all_data['documents']):
            # 提取标签
            if doc.startswith('['):
                tag_end = doc.find(']')
                if tag_end > 0:
                    tag = doc[1:tag_end]
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                    
                    # 收集生命周期相关文档
                    if 'lifecycle' in tag.lower() or '重要' in tag:
                        lifecycle_docs.append((i, tag, doc[:150]))
        
        print(f"\n📋 文档标签分布:")
        for tag, count in sorted(tag_counts.items()):
            print(f"   {tag}: {count} 个文档")
        
        print(f"\n🎯 生命周期相关文档:")
        if lifecycle_docs:
            for i, (idx, tag, content) in enumerate(lifecycle_docs):
                print(f"   {i+1}. [{tag}] {content}...")
        else:
            print("   ⚠️  没有找到生命周期相关文档!")
        
        # 测试检索
        print(f"\n🧪 测试检索功能:")
        retriever = vectordb.as_retriever(search_kwargs={"k": 5})
        
        test_queries = ["软件开发生命周期", "软件生存周期", "开发阶段"]
        
        for query in test_queries:
            print(f"\n查询: '{query}'")
            results = retriever.invoke(query)
            
            for i, result in enumerate(results):
                # 提取标签
                content = result.page_content
                tag = "无标签"
                if content.startswith('['):
                    tag_end = content.find(']')
                    if tag_end > 0:
                        tag = content[1:tag_end]
                
                print(f"   结果 {i+1}: [{tag}] {content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def force_restart_hint():
    """提供强制重启的建议"""
    print(f"\n💡 解决建议:")
    print(f"1. 完全停止后端服务 (Ctrl+C)")
    print(f"2. 重新启动: python start.py")
    print(f"3. 如果问题持续，可能需要重建ai_service实例")

if __name__ == "__main__":
    if test_current_vectordb():
        force_restart_hint()
