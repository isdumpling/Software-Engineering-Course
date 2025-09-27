#!/usr/bin/env python3
"""
深入分析向量检索质量的脚本
"""
import os
import sys
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 配置
CHROMA_DB_PATH = "chroma_db"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def analyze_vector_database():
    """分析向量数据库的内容和质量"""
    print("🔍 正在分析向量数据库...")
    
    # 加载嵌入模型和向量数据库
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectordb = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)
    
    # 获取数据库统计信息
    collection = vectordb._collection
    all_data = collection.get()
    
    print(f"📊 数据库统计:")
    print(f"   - 总文档数: {len(all_data['documents'])}")
    print(f"   - 平均文档长度: {sum(len(doc) for doc in all_data['documents']) / len(all_data['documents']):.1f} 字符")
    
    # 分析文档长度分布
    doc_lengths = [len(doc) for doc in all_data['documents']]
    print(f"   - 最短文档: {min(doc_lengths)} 字符")
    print(f"   - 最长文档: {max(doc_lengths)} 字符")
    
    # 显示所有文档的简要信息
    print(f"\n📄 所有文档预览:")
    for i, doc in enumerate(all_data['documents']):
        print(f"\n文档 {i+1} (长度: {len(doc)}):")
        print(f"内容: {doc[:150]}...")
        
        # 检查是否包含关键词
        keywords = ['软件开发', '生命周期', '测试', '需求分析', '设计', '编码', '维护']
        found_keywords = [kw for kw in keywords if kw in doc]
        if found_keywords:
            print(f"包含关键词: {found_keywords}")
    
    return vectordb

def test_specific_queries(vectordb):
    """测试特定查询的检索效果"""
    print(f"\n🎯 详细测试检索效果:")
    
    test_cases = [
        ("软件开发生命周期", "应该找到关于软件开发过程、阶段的内容"),
        ("需求分析", "应该找到关于需求获取、分析的内容"),
        ("软件测试", "应该找到关于测试方法、策略的内容"),
        ("系统设计", "应该找到关于系统架构、设计的内容"),
        ("编码实现", "应该找到关于编程、实现的内容"),
    ]
    
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
    
    for query, expected in test_cases:
        print(f"\n" + "="*60)
        print(f"🔍 查询: '{query}'")
        print(f"📝 期望: {expected}")
        
        try:
            results = retriever.invoke(query)
            print(f"✅ 检索到 {len(results)} 个结果")
            
            for i, result in enumerate(results):
                print(f"\n📄 结果 {i+1}:")
                print(f"   内容: {result.page_content[:200]}...")
                print(f"   元数据: {result.metadata}")
                
                # 分析相关性
                relevance_score = calculate_simple_relevance(query, result.page_content)
                print(f"   相关性评分: {relevance_score:.2f}")
                
        except Exception as e:
            print(f"❌ 检索失败: {e}")

def calculate_simple_relevance(query, content):
    """简单的相关性计算"""
    query_words = set(query.lower().split())
    content_words = set(content.lower().split())
    
    # 计算词汇重叠度
    overlap = len(query_words.intersection(content_words))
    total_query_words = len(query_words)
    
    if total_query_words == 0:
        return 0.0
        
    return overlap / total_query_words

def analyze_embedding_similarity():
    """分析嵌入向量的相似度"""
    print(f"\n🧠 分析嵌入向量相似度:")
    
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    # 测试一些关键词的嵌入
    test_words = ["软件开发", "生命周期", "测试", "可靠性", "面向对象", "储蓄系统"]
    
    print(f"测试词汇的嵌入向量长度:")
    for word in test_words:
        vector = embeddings.embed_query(word)
        print(f"   '{word}': {len(vector)} 维")
    
    # 计算词汇间的相似度
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    
    vectors = [embeddings.embed_query(word) for word in test_words]
    similarity_matrix = cosine_similarity(vectors)
    
    print(f"\n相似度矩阵 (余弦相似度):")
    print("        ", "  ".join(f"{word[:6]:>6}" for word in test_words))
    for i, word in enumerate(test_words):
        similarities = "  ".join(f"{sim:.3f}" for sim in similarity_matrix[i])
        print(f"{word[:8]:>8} {similarities}")

def main():
    """主函数"""
    try:
        print("🚀 开始向量检索质量分析...")
        
        # 1. 分析数据库内容
        vectordb = analyze_vector_database()
        
        # 2. 测试特定查询
        test_specific_queries(vectordb)
        
        # 3. 分析嵌入相似度
        analyze_embedding_similarity()
        
        print(f"\n🎉 分析完成！")
        
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
