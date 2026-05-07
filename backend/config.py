import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    # 数据库配置
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "course_assistant")

    # 构建数据库URL
    DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

    # JWT配置
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # 邮件配置（用于密码重置）
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    # 火山引擎豆包AI配置
    ARK_API_KEY = os.getenv("ARK_API_KEY", "")
    DOUBAO_MODEL = os.getenv("DOUBAO_MODEL", "doubao-seed-1-6-thinking-250715")

    # 管理员配置
    ADMIN_USERNAMES = [
        item.strip()
        for item in os.getenv("ADMIN_USERNAMES", "admin").split(",")
        if item.strip()
    ]
    ADMIN_DEFAULT_PASSWORD = os.getenv("ADMIN_DEFAULT_PASSWORD", "")
    ADMIN_DEFAULT_EMAIL = os.getenv("ADMIN_DEFAULT_EMAIL", "admin@local.dev")

    # 知识库路径配置
    KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")
    VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "vector_databases")

settings = Settings()