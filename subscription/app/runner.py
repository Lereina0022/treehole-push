import json
import time
from pathlib import Path

from app.config import (
    LOOKBACK_HOURS,
    SEARCH_LIMIT,
    SEARCH_COMMENT_LIMIT,
)
from app.matcher import match_rule
from app.notifier import send_wechat
from app.parser import extract_posts
from app.treehole_client import TreeholeClient


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUBSCRIPTIONS_FILE = PROJECT_ROOT / "subscriptions.json"


def is_within_hours(post: dict, hours: float) -> bool:
    """判断帖子是否发布于指定小时范围内。"""
    timestamp = post.get("timestamp")

    if not timestamp:
        return False

    age_seconds = int(time.time()) - int(timestamp)

    # 同时排除时间戳异常、位于未来的帖子
    return 0 <= age_seconds <= hours * 3600


def load_subscriptions() -> list[dict]:
    """从 JSON 文件读取订阅规则。"""
    if not SUBSCRIPTIONS_FILE.exists():
        raise FileNotFoundError(
            f"找不到订阅文件: {SUBSCRIPTIONS_FILE}"
        )

    with SUBSCRIPTIONS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        subscriptions = json.load(file)

    if not isinstance(subscriptions, list):
        raise ValueError(
            "subscriptions.json 最外层必须是数组"
        )

    return subscriptions


def build_message(
    subscription: dict,
    posts: list[dict]
) -> tuple[str, str]:
    """把同一订阅本轮命中的帖子合并成一条消息。"""
    title = (
        f"树洞提醒："
        f"{subscription['category_name']}"
        f"（{len(posts)}条）"
    )

    sections = []

    for post in posts:
        section = (
            f"### PID {post.get('pid')}\n\n"
            f"**时间**："
            f"{post.get('datetime') or '未知'}\n\n"
            f"**内容**：\n\n"
            f"{post.get('text') or ''}"
        )
        sections.append(section)

    description = "\n\n---\n\n".join(sections)

    return title, description


def process_subscription(
    client: TreeholeClient,
    subscription: dict
) -> dict:
    """搜索并处理一个订阅。"""
    category_name = subscription["category_name"]
    query_text = subscription["query_text"]
    rule = subscription.get("rule", {})

    print(
        f"处理订阅: {category_name} | "
        f"query={query_text}"
    )

    api_response = client.search_posts(
        keyword=query_text,
        page=1,
        limit=SEARCH_LIMIT,
        comment_limit=SEARCH_COMMENT_LIMIT,
    )

    posts = extract_posts(api_response)

    matched_posts = []
    seen_pids = set()

    for post in posts:
        pid = post.get("pid")

        # 防止同一次API结果中出现重复PID
        if not pid or pid in seen_pids:
            continue

        if not is_within_hours(
            post,
            LOOKBACK_HOURS
        ):
            continue

        if not match_rule(
            post.get("text", ""),
            rule
        ):
            continue

        seen_pids.add(pid)
        matched_posts.append(post)

    # 按发布时间从早到晚排列
    matched_posts.sort(
        key=lambda item: item.get("timestamp") or 0
    )

    if not matched_posts:
        print(f"{category_name}: 本轮没有命中")
        return {
            "category_name": category_name,
            "matched_count": 0,
            "sent": False,
        }

    title, description = build_message(
        subscription,
        matched_posts
    )

    send_wechat(title, description)

    print(
        f"{category_name}: "
        f"成功推送 {len(matched_posts)} 条"
    )

    return {
        "category_name": category_name,
        "matched_count": len(matched_posts),
        "sent": True,
    }


def run_once() -> dict:
    """完整执行一轮树洞搜索和推送。"""
    subscriptions = load_subscriptions()
    client = TreeholeClient()

    results = []
    failed_count = 0

    print(
        f"开始运行，共 {len(subscriptions)} 个订阅，"
        f"回看最近 {LOOKBACK_HOURS} 小时"
    )

    for subscription in subscriptions:
        try:
            result = process_subscription(
                client,
                subscription
            )
            results.append(result)

        except Exception as error:
            failed_count += 1

            category_name = subscription.get(
                "category_name",
                "未知订阅"
            )

            print(
                f"{category_name}: 处理失败 | "
                f"{error!r}"
            )

            results.append({
                "category_name": category_name,
                "matched_count": 0,
                "sent": False,
                "error": str(error),
            })

    summary = {
        "subscription_count": len(subscriptions),
        "failed_count": failed_count,
        "total_matched_count": sum(
            item["matched_count"]
            for item in results
        ),
        "results": results,
    }

    print(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2
        )
    )

    return summary


if __name__ == "__main__":
    result = run_once()

    # 如果存在失败，让GitHub Actions显示失败状态
    if result["failed_count"] > 0:
        raise SystemExit(1)
