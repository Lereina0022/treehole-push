import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# Treehole
# =========================
TREEHOLE_BASE_URL = os.getenv("TREEHOLE_BASE_URL", "https://treehole.pku.edu.cn").rstrip("/")
TREEHOLE_SEARCH_API = os.getenv("TREEHOLE_SEARCH_API", "/chapi/api/v3/hole/list_comments")

TREEHOLE_AUTHORIZATION = os.getenv("TREEHOLE_AUTHORIZATION", "").strip()
TREEHOLE_COOKIE = os.getenv("TREEHOLE_COOKIE", "").strip()
TREEHOLE_X_XSRF_TOKEN = os.getenv("TREEHOLE_X_XSRF_TOKEN", "").strip()
TREEHOLE_UUID = os.getenv("TREEHOLE_UUID", "").strip()
TREEHOLE_TIMEOUT = int(os.getenv("TREEHOLE_TIMEOUT", "15"))

# =========================
# MySQL
# =========================
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1").strip()
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root").strip()
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "").strip()
MYSQL_DB = os.getenv("MYSQL_DB", "treehole_push").strip()

# =========================
# Server酱
# =========================
SERVERCHAN_SENDKEY = os.getenv("SERVERCHAN_SENDKEY", "").strip()

# =========================
# Runner
# =========================
RUNNER_INTERVAL_SECONDS = int(os.getenv("RUNNER_INTERVAL_SECONDS", "600"))
RECENT_DAYS = int(os.getenv("RECENT_DAYS", "7"))
SEARCH_PAGE = int(os.getenv("SEARCH_PAGE", "1"))
SEARCH_LIMIT = int(os.getenv("SEARCH_LIMIT", "20"))
SEARCH_COMMENT_LIMIT = int(os.getenv("SEARCH_COMMENT_LIMIT", "10"))

# =========================
# Helpers
# =========================
def require_treehole_config() -> None:
    missing = []
    if not TREEHOLE_AUTHORIZATION:
        missing.append("TREEHOLE_AUTHORIZATION")
    if not TREEHOLE_COOKIE:
        missing.append("TREEHOLE_COOKIE")
    if not TREEHOLE_X_XSRF_TOKEN:
        missing.append("TREEHOLE_X_XSRF_TOKEN")
    if not TREEHOLE_UUID:
        missing.append("TREEHOLE_UUID")

    if missing:
        raise RuntimeError(f"缺少树洞配置: {', '.join(missing)}")


def require_serverchan_config() -> None:
    if not SERVERCHAN_SENDKEY:
        raise RuntimeError("缺少 SERVERCHAN_SENDKEY")