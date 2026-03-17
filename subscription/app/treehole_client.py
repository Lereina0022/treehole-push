from typing import Any, Dict

import requests

from app.config import (
    TREEHOLE_BASE_URL,
    TREEHOLE_SEARCH_API,
    TREEHOLE_AUTHORIZATION,
    TREEHOLE_COOKIE,
    TREEHOLE_X_XSRF_TOKEN,
    TREEHOLE_UUID,
    TREEHOLE_TIMEOUT,
    require_treehole_config,
)


class TreeholeClient:
    def __init__(self) -> None:
        require_treehole_config()

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json, text/plain, */*",
                "Authorization": TREEHOLE_AUTHORIZATION,
                "Cookie": TREEHOLE_COOKIE,
                "X-Xsrf-Token": TREEHOLE_X_XSRF_TOKEN,
                "Uuid": TREEHOLE_UUID,
                "User-Agent": "Mozilla/5.0",
                "Referer": TREEHOLE_BASE_URL + "/",
            }
        )

    def search_posts(
        self,
        keyword: str,
        page: int = 1,
        limit: int = 20,
        comment_limit: int = 10,
    ) -> Dict[str, Any]:
        url = f"{TREEHOLE_BASE_URL}{TREEHOLE_SEARCH_API}"
        params = {
            "keyword": keyword,
            "page": page,
            "limit": limit,
            "comment_limit": comment_limit,
        }

        resp = self.session.get(url, params=params, timeout=TREEHOLE_TIMEOUT)
        resp.raise_for_status()

        data = resp.json()
        if not isinstance(data, dict):
            raise RuntimeError("树洞接口返回不是 JSON object")

        return data