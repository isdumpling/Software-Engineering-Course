#!/usr/bin/env python3
"""
批量构建所有课程的知识库
"""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加上级目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from course_config import CourseManager, COURSE_CONFIG
from build_course_knowledge import build_course_vectordb

def check_course_prerequisites():
    """检查所有课程的前置条件"""
    print("🔍 检查课程前置条件...")
    
    manager = CourseManager()
    course_status = {}
    
    for course_id in manager.get_all_courses():
        course_name = COURSE_CONFIG[course_id]["name"]
        doc_exists = manager.course_doc_exists(course_id)
        doc_path = manager.get_course_doc_path(course_id)
        
        course_status[course_id] = {
            "name": course_name,
            "doc_exists": doc_exists,
            "doc_path": doc_path,
            "ready": doc_exists
        }
        
        status_symbol = "✅" if doc_exists else "❌"
        print(f"  {status_symbol} {course_name} ({course_id})")
        if not doc_exists:
            print(f"      缺少教材文件: {doc_path}")
    
    ready_courses = [cid for cid, status in course_status.items() if status["ready"]]
    missing_courses = [cid for cid, status in course_status.items() if not status["ready"]]
    
    print(f"\n📊 检查结果:")
    print(f"  - 可构建课程: {len(ready_courses)} 门")
    print(f"  - 缺少教材: {len(missing_courses)} 门")
    
    if missing_courses:
        print(f"\n⚠️ 需要先准备以下课程的教材文件:")
        for course_id in missing_courses:
            course_name = course_status[course_id]["name"]
            doc_path = course_status[course_id]["doc_path"]
            print(f"  - {course_name}: {doc_path}")
    
    return ready_courses, missing_courses

def build_single_course_safe(course_id):
    """安全地构建单个课程（带异常处理）"""
    course_name = COURSE_CONFIG[course_id]["name"]
    start_time = time.time()
    
    try:
        print(f"\n🚀 开始构建: {course_name} ({course_id})")
        success = build_course_vectordb(course_id)
        end_time = time.time()
        duration = end_time - start_time
        
        if success:
            print(f"✅ {course_name} 构建成功 (耗时: {duration:.1f}s)")
            return {"course_id": course_id, "success": True, "duration": duration, "error": None}
        else:
            print(f"❌ {course_name} 构建失败")
            return {"course_id": course_id, "success": False, "duration": duration, "error": "构建过程返回失败"}
            
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ {course_name} 构建出错: {e}")
        return {"course_id": course_id, "success": False, "duration": duration, "error": str(e)}

def build_all_courses_sequential(ready_courses):
    """顺序构建所有课程"""
    print(f"\n🔧 开始顺序构建 {len(ready_courses)} 门课程的知识库...")
    
    results = []
    total_start_time = time.time()
    
    for i, course_id in enumerate(ready_courses, 1):
        course_name = COURSE_CONFIG[course_id]["name"]
        print(f"\n[{i}/{len(ready_courses)}] 正在构建: {course_name}")
        
        result = build_single_course_safe(course_id)
        results.append(result)
        
        # 短暂休息，避免系统过载
        if i < len(ready_courses):
            print("⏱️ 休息2秒...")
            time.sleep(2)
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    return results, total_duration

def build_all_courses_parallel(ready_courses, max_workers=2):
    """并行构建所有课程（适用于多核心系统）"""
    print(f"\n🔧 开始并行构建 {len(ready_courses)} 门课程的知识库（最多 {max_workers} 个并发）...")
    
    results = []
    total_start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_course = {
            executor.submit(build_single_course_safe, course_id): course_id 
            for course_id in ready_courses
        }
        
        # 收集结果
        for future in as_completed(future_to_course):
            course_id = future_to_course[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                course_name = COURSE_CONFIG[course_id]["name"]
                print(f"❌ {course_name} 并行构建异常: {e}")
                results.append({
                    "course_id": course_id, 
                    "success": False, 
                    "duration": 0, 
                    "error": f"并行执行异常: {e}"
                })
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    return results, total_duration

def print_build_summary(results, total_duration):
    """打印构建总结"""
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\n" + "="*60)
    print(f"📊 构建总结")
    print(f"="*60)
    print(f"总耗时: {total_duration:.1f} 秒")
    print(f"成功构建: {len(successful)} 门课程")
    print(f"构建失败: {len(failed)} 门课程")
    
    if successful:
        print(f"\n✅ 成功构建的课程:")
        for result in successful:
            course_name = COURSE_CONFIG[result["course_id"]]["name"]
            print(f"  - {course_name} (耗时: {result['duration']:.1f}s)")
    
    if failed:
        print(f"\n❌ 构建失败的课程:")
        for result in failed:
            course_name = COURSE_CONFIG[result["course_id"]]["name"]
            print(f"  - {course_name}: {result['error']}")
    
    print(f"\n💡 后续步骤:")
    if successful:
        print(f"  1. 重启后端服务以加载新的知识库")
        print(f"  2. 测试各门课程的问答效果")
    
    if failed:
        print(f"  3. 检查失败课程的教材文件")
        print(f"  4. 重新运行失败课程的构建")

def show_current_status():
    """显示当前所有课程的状态"""
    print(f"\n📋 当前课程状态:")
    
    manager = CourseManager()
    all_stats = manager.list_all_course_stats()
    
    for course_id, stats in all_stats.items():
        course_name = stats["course_name"]
        doc_exists = "✅" if stats["doc_exists"] else "❌"
        db_exists = "✅" if stats["vector_db_exists"] else "❌"
        doc_count = stats["document_count"] if stats["document_count"] >= 0 else "?"
        
        print(f"  {course_name}:")
        print(f"    教材文件: {doc_exists}")
        print(f"    向量数据库: {db_exists}")
        if stats["vector_db_exists"]:
            print(f"    文档数量: {doc_count}")
            print(f"    数据库大小: {stats['vector_db_size'] / 1024 / 1024:.1f} MB")

def main():
    """主函数"""
    print("🚀 批量构建多课程知识库")
    print("="*50)
    
    # 解析命令行参数
    parallel_mode = "--parallel" in sys.argv
    show_status_only = "--status" in sys.argv
    
    if show_status_only:
        show_current_status()
        return
    
    # 检查前置条件
    ready_courses, missing_courses = check_course_prerequisites()
    
    if not ready_courses:
        print(f"\n❌ 没有可构建的课程，请先准备教材文件")
        return
    
    # 询问用户是否继续
    print(f"\n🤔 准备构建 {len(ready_courses)} 门课程的知识库，这可能需要较长时间。")
    choice = input("是否继续？(y/N): ").strip().lower()
    
    if choice not in ['y', 'yes', '是']:
        print("👋 已取消构建")
        return
    
    # 选择构建模式
    if parallel_mode:
        print(f"🔀 使用并行模式构建")
        results, total_duration = build_all_courses_parallel(ready_courses, max_workers=2)
    else:
        print(f"📝 使用顺序模式构建")
        results, total_duration = build_all_courses_sequential(ready_courses)
    
    # 打印总结
    print_build_summary(results, total_duration)
    
    # 显示最终状态
    show_current_status()

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
多课程知识库批量构建工具

用法:
  python build_all_courses.py              # 顺序构建所有课程
  python build_all_courses.py --parallel   # 并行构建所有课程  
  python build_all_courses.py --status     # 只显示当前状态

注意:
  - 并行模式速度更快，但需要更多内存
  - 顺序模式更稳定，适用于资源有限的环境
  - 首次运行会下载BGE模型，需要网络连接
        """)
    else:
        main()
