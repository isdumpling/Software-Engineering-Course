#!/usr/bin/env python3
"""
多课程功能演示脚本
"""
import os
import sys

# 添加课程管理模块到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'course_management'))

from course_config import CourseManager, COURSE_CONFIG

def demo_course_info():
    """演示课程信息功能"""
    print("📚 多课程系统信息")
    print("="*50)
    
    manager = CourseManager()
    
    print("🎓 支持的课程列表:")
    for course_id, config in COURSE_CONFIG.items():
        print(f"  - {config['name']} ({course_id})")
        print(f"    教材文件: {config['doc_file']}")
        print(f"    重要术语: {len(config['important_terms'])} 个")
        print(f"    查询优化: {len(config['query_optimizations'])} 个规则")
        print()

def demo_course_status():
    """演示课程状态检查"""
    print("📊 课程状态检查")
    print("="*50)
    
    manager = CourseManager()
    all_stats = manager.list_all_course_stats()
    
    for course_id, stats in all_stats.items():
        status_doc = "✅" if stats["doc_exists"] else "❌"
        status_db = "✅" if stats["vector_db_exists"] else "❌"
        
        print(f"📖 {stats['course_name']}:")
        print(f"   教材文件: {status_doc}")
        print(f"   向量数据库: {status_db}")
        
        if stats["vector_db_exists"]:
            doc_count = stats["document_count"] if stats["document_count"] >= 0 else "无法获取"
            db_size_mb = stats["vector_db_size"] / 1024 / 1024
            print(f"   文档数量: {doc_count}")
            print(f"   数据库大小: {db_size_mb:.1f} MB")
        print()

def demo_query_optimization():
    """演示查询优化功能"""
    print("🔍 查询优化规则演示")
    print("="*50)
    
    test_queries = [
        ("software-engineering", "软件开发生命周期"),
        ("software-engineering", "瀑布模型"),
        ("operating-system", "进程管理"),
        ("computer-network", "OSI模型"),
        ("data-structure", "排序算法"),
        ("database", "事务管理")
    ]
    
    for course_id, query in test_queries:
        if course_id in COURSE_CONFIG:
            config = COURSE_CONFIG[course_id]
            course_name = config["name"]
            optimizations = config.get("query_optimizations", {})
            
            print(f"📚 {course_name} - 查询: '{query}'")
            
            optimized = False
            for keyword, optimal_query in optimizations.items():
                if keyword in query.lower():
                    print(f"   ✨ 优化为: '{optimal_query}'")
                    optimized = True
                    break
            
            if not optimized:
                print(f"   📝 保持原始查询")
            print()

def demo_course_concepts():
    """演示课程重要概念"""
    print("🎯 各课程重要概念")
    print("="*50)
    
    for course_id, config in COURSE_CONFIG.items():
        course_name = config["name"]
        important_terms = config.get("important_terms", [])
        
        print(f"📚 {course_name}:")
        print(f"   核心概念({len(important_terms)}个): {', '.join(important_terms[:8])}")
        if len(important_terms) > 8:
            print(f"   还有{len(important_terms) - 8}个概念...")
        print()

def demo_file_structure():
    """演示多课程文件结构"""
    print("📁 多课程文件结构")
    print("="*50)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("后端目录结构:")
    print("backend/")
    print("├── knowledge_base/          # 原始教材文件")
    
    for course_id, config in COURSE_CONFIG.items():
        doc_file = config["doc_file"]
        doc_path = os.path.join(base_dir, "knowledge_base", doc_file)
        status = "✅" if os.path.exists(doc_path) else "❌"
        print(f"│   ├── {doc_file:<25} {status}")
    
    print("├── vector_databases/        # 向量数据库")
    for course_id, config in COURSE_CONFIG.items():
        db_path = os.path.join(base_dir, "vector_databases", course_id)
        status = "✅" if os.path.exists(db_path) else "❌"
        print(f"│   ├── {course_id}/<20} {status}")
    
    print("└── course_management/       # 课程管理脚本")
    print("    ├── course_config.py")
    print("    ├── build_course_knowledge.py")
    print("    └── build_all_courses.py")

def demo_next_steps():
    """演示后续步骤"""
    print("🚀 后续步骤指南")
    print("="*50)
    
    manager = CourseManager()
    all_stats = manager.list_all_course_stats()
    
    # 检查缺少教材的课程
    missing_docs = [cid for cid, stats in all_stats.items() if not stats["doc_exists"]]
    missing_dbs = [cid for cid, stats in all_stats.items() if not stats["vector_db_exists"]]
    
    print("📋 TODO清单:")
    
    if missing_docs:
        print("1. 准备缺少的教材文件:")
        for course_id in missing_docs:
            course_name = COURSE_CONFIG[course_id]["name"]
            doc_file = COURSE_CONFIG[course_id]["doc_file"]
            print(f"   - {course_name}: knowledge_base/{doc_file}")
    
    if missing_dbs:
        print("2. 构建缺少的向量数据库:")
        for course_id in missing_dbs:
            course_name = COURSE_CONFIG[course_id]["name"]
            print(f"   - python course_management/build_course_knowledge.py {course_id}")
    
    print("3. 执行系统迁移:")
    print("   - python migrate_to_multi_course.py")
    
    print("4. 批量构建所有课程:")
    print("   - python course_management/build_all_courses.py")
    
    print("5. 重启后端服务:")
    print("   - python main.py")
    
    print("6. 测试各课程问答:")
    print("   - 在前端界面测试不同课程的典型问题")

def main():
    """主函数"""
    demos = [
        ("课程信息", demo_course_info),
        ("课程状态", demo_course_status),
        ("查询优化", demo_query_optimization),
        ("重要概念", demo_course_concepts),
        ("文件结构", demo_file_structure),
        ("后续步骤", demo_next_steps)
    ]
    
    if len(sys.argv) > 1:
        demo_name = sys.argv[1]
        for name, func in demos:
            if demo_name.lower() in name.lower():
                func()
                return
        print(f"未找到演示: {demo_name}")
        print(f"可用的演示: {', '.join([name for name, _ in demos])}")
    else:
        print("🎮 多课程功能全面演示")
        print("="*60)
        
        for name, func in demos:
            print(f"\n💫 {name}")
            func()
            input("按回车键继续...")

if __name__ == "__main__":
    main()
