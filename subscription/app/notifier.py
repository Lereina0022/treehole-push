import requests
from app.config import SERVERCHAN_SENDKEY, require_serverchan_config


def send_wechat(title: str, desp: str) -> bool:
    require_serverchan_config()

    url = f"https://sctapi.ftqq.com/{SERVERCHAN_SENDKEY}.send"
    data = {
        "title": title[:80],
        "desp": desp[:10000],
    }

    resp = requests.post(url, data=data, timeout=10)
    resp.raise_for_status()

    result = resp.json()
    if result.get("code") == 0:
        return True

    raise RuntimeError(f"Server酱发送失败: {result}")