#!/usr/bin/env python3
"""
从单课程架构迁移到多课程架构的工具
"""
import os
import shutil
import sys

def migrate_to_multi_course():
    """执行迁移流程"""
    print("🚀 开始从单课程架构迁移到多课程架构")
    print("="*60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. 备份当前的ai_service.py
    ai_service_path = os.path.join(base_dir, "ai_service.py")
    backup_path = os.path.join(base_dir, "ai_service_backup.py")
    
    if os.path.exists(ai_service_path):
        print("📦 备份原始ai_service.py...")
        shutil.copy2(ai_service_path, backup_path)
        print(f"   ✅ 备份到: {backup_path}")
    
    # 2. 替换ai_service.py
    multi_course_path = os.path.join(base_dir, "ai_service_multi_course.py")
    if os.path.exists(multi_course_path):
        print("🔄 替换ai_service.py为多课程版本...")
        shutil.copy2(multi_course_path, ai_service_path)
        print("   ✅ ai_service.py已更新为多课程版本")
    else:
        print("   ❌ 找不到ai_service_multi_course.py文件")
        return False
    
    # 3. 创建目录结构
    print("📁 创建多课程目录结构...")
    
    # 创建knowledge_base目录
    knowledge_base_dir = os.path.join(base_dir, "knowledge_base")
    os.makedirs(knowledge_base_dir, exist_ok=True)
    
    # 创建vector_databases目录
    vector_db_dir = os.path.join(base_dir, "vector_databases")
    os.makedirs(vector_db_dir, exist_ok=True)
    
    # 4. 迁移现有的软件工程数据
    old_chroma_path = os.path.join(base_dir, "chroma_db")
    new_se_path = os.path.join(vector_db_dir, "software-engineering")
    
    if os.path.exists(old_chroma_path):
        print("📚 迁移现有的软件工程向量数据库...")
        if os.path.exists(new_se_path):
            print("   ⚠️ 目标路径已存在，先删除...")
            shutil.rmtree(new_se_path)
        shutil.move(old_chroma_path, new_se_path)
        print(f"   ✅ 迁移完成: {old_chroma_path} -> {new_se_path}")
    
    # 5. 移动现有的软件工程教材文件
    old_se_docx = os.path.join(base_dir, "knowledge_base", "se.docx")
    new_se_docx = os.path.join(knowledge_base_dir, "software-engineering.docx")
    
    if os.path.exists(old_se_docx):
        print("📖 重命名软件工程教材文件...")
        shutil.move(old_se_docx, new_se_docx)
        print(f"   ✅ 重命名完成: se.docx -> software-engineering.docx")
    
    # 6. 创建course_management目录的__init__.py文件
    course_mgmt_dir = os.path.join(base_dir, "course_management")
    init_file = os.path.join(course_mgmt_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write('"""多课程管理模块"""\n')
        print("   ✅ 创建course_management/__init__.py")
    
    print("\n✅ 迁移完成！")
    print("📋 迁移总结:")
    print("   - ai_service.py 已更新为多课程版本")
    print("   - 原版本备份为 ai_service_backup.py")
    print("   - 软件工程数据已迁移到新的目录结构")
    print("   - 创建了多课程目录结构")
    
    print("\n🎯 下一步操作:")
    print("   1. 准备其他课程的教材文件(.docx)")
    print("   2. 运行: python course_management/build_all_courses.py --status")
    print("   3. 运行: python course_management/build_course_knowledge.py <course_id>")
    print("   4. 重启后端服务")
    
    return True

def rollback_migration():
    """回滚迁移"""
    print("🔄 开始回滚到单课程架构...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backup_path = os.path.join(base_dir, "ai_service_backup.py")
    ai_service_path = os.path.join(base_dir, "ai_service.py")
    
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, ai_service_path)
        print("✅ 已恢复原始的ai_service.py")
        
        # 还原软件工程数据库
        vector_db_dir = os.path.join(base_dir, "vector_databases", "software-engineering")
        old_chroma_path = os.path.join(base_dir, "chroma_db")
        
        if os.path.exists(vector_db_dir) and not os.path.exists(old_chroma_path):
            shutil.move(vector_db_dir, old_chroma_path)
            print("✅ 已恢复chroma_db目录")
        
        print("🎉 回滚完成！请重启后端服务。")
        return True
    else:
        print("❌ 找不到备份文件，无法回滚")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        rollback_migration()
    elif len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
多课程架构迁移工具

用法:
    python migrate_to_multi_course.py          # 执行迁移
    python migrate_to_multi_course.py --rollback   # 回滚迁移
    python migrate_to_multi_course.py --help       # 显示帮助

迁移内容:
    - 将ai_service.py更新为多课程版本
    - 创建新的目录结构
    - 迁移现有的软件工程数据
    - 备份原始文件以便回滚
        """)
    else:
        success = migrate_to_multi_course()
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
