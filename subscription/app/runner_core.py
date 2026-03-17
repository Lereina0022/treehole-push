import json
import time
import traceback

from app.config import RECENT_DAYS, SEARCH_PAGE, SEARCH_LIMIT, SEARCH_COMMENT_LIMIT
from app.database import get_conn
from app.matcher import match_rule
from app.notifier import send_wechat
from app.parser import extract_posts
from app.treehole_client import TreeholeClient


def is_recent_post(post: dict, days: int = 7) -> bool:
    ts = post.get("timestamp")
    if not ts:
        return False
    now_ts = int(time.time())
    return (now_ts - ts) <= days * 24 * 3600


def normalize_rule(rule_json):
    if isinstance(rule_json, str):
        return json.loads(rule_json)
    if isinstance(rule_json, dict):
        return rule_json
    return {}


def fetch_active_subscriptions(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, category_name, query_text, rule_json
            FROM subscriptions
            WHERE is_active = 1
            ORDER BY id DESC
            """
        )
        return cursor.fetchall()


def save_post(cursor, post: dict):
    cursor.execute(
        """
        INSERT INTO posts (
            pid, text, post_type, timestamp, post_datetime, label, reply_count, like_num, raw_json
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            text = VALUES(text),
            post_type = VALUES(post_type),
            timestamp = VALUES(timestamp),
            post_datetime = VALUES(post_datetime),
            label = VALUES(label),
            reply_count = VALUES(reply_count),
            like_num = VALUES(like_num),
            raw_json = VALUES(raw_json)
        """,
        (
            post["pid"],
            post["text"],
            post["type"],
            post["timestamp"],
            post["datetime"],
            post["label"],
            post["reply_count"],
            post["like_num"],
            json.dumps(post.get("raw_json", {}), ensure_ascii=False),
        ),
    )


def already_pushed(cursor, pid: int, subscription_id: int) -> bool:
    cursor.execute(
        """
        SELECT id
        FROM push_logs
        WHERE pid = %s AND subscription_id = %s AND status = 'sent'
        LIMIT 1
        """,
        (pid, subscription_id),
    )
    return cursor.fetchone() is not None


def create_push_log(cursor, pid: int, subscription_id: int, status: str, error_message: str | None = None):
    cursor.execute(
        """
        INSERT INTO push_logs (pid, subscription_id, status, error_message)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            status = VALUES(status),
            error_message = VALUES(error_message)
        """,
        (pid, subscription_id, status, error_message),
    )


def build_message(sub: dict, post: dict) -> tuple[str, str]:
    title = f"树洞命中提醒：{sub['category_name']}"
    desp = (
        f"**分类**：{sub['category_name']}\n\n"
        f"**查询词**：{sub['query_text']}\n\n"
        f"**时间**：{post.get('datetime') or '未知'}\n\n"
        f"**PID**：{post.get('pid')}\n\n"
        f"**内容**：\n{post.get('text') or ''}"
    )
    return title, desp


def process_subscription(cursor, client: TreeholeClient, sub: dict) -> dict:
    print(f"\n处理订阅: {sub['category_name']} | query={sub['query_text']}")

    api_result = client.search_posts(
        keyword=sub["query_text"],
        page=SEARCH_PAGE,
        limit=SEARCH_LIMIT,
        comment_limit=SEARCH_COMMENT_LIMIT,
    )
    posts = extract_posts(api_result)
    rule = normalize_rule(sub["rule_json"])

    matched_count = 0
    sent_count = 0
    failed_count = 0
    skipped_count = 0

    for post in posts:
        if not is_recent_post(post, days=RECENT_DAYS):
            continue

        if not match_rule(post["text"], rule):
            continue

        matched_count += 1
        save_post(cursor, post)

        if already_pushed(cursor, post["pid"], sub["id"]):
            skipped_count += 1
            print(f"已推送过，跳过: PID={post['pid']}")
            continue

        title, desp = build_message(sub, post)

        try:
            send_wechat(title, desp)
            create_push_log(cursor, post["pid"], sub["id"], "sent", None)
            sent_count += 1
            print(f"推送成功: PID={post['pid']}")
        except Exception as e:
            create_push_log(cursor, post["pid"], sub["id"], "failed", repr(e))
            failed_count += 1
            print(f"推送失败: PID={post['pid']} | {repr(e)}")

    print(
        f"该订阅命中 {matched_count} 条，成功 {sent_count} 条，失败 {failed_count} 条，跳过 {skipped_count} 条"
    )

    return {
        "subscription_id": sub["id"],
        "category_name": sub["category_name"],
        "query_text": sub["query_text"],
        "matched_count": matched_count,
        "sent_count": sent_count,
        "failed_count": failed_count,
        "skipped_count": skipped_count,
    }


def run_once() -> dict:
    conn = get_conn()
    client = TreeholeClient()

    summary = {
        "success": True,
        "subscription_count": 0,
        "total_matched_count": 0,
        "total_sent_count": 0,
        "total_failed_count": 0,
        "total_skipped_count": 0,
        "results": [],
        "error": None,
    }

    try:
        subscriptions = fetch_active_subscriptions(conn)
        summary["subscription_count"] = len(subscriptions)
        print(f"当前启用订阅数: {len(subscriptions)}")

        with conn.cursor() as cursor:
            for sub in subscriptions:
                item_result = process_subscription(cursor, client, sub)
                summary["results"].append(item_result)
                summary["total_matched_count"] += item_result["matched_count"]
                summary["total_sent_count"] += item_result["sent_count"]
                summary["total_failed_count"] += item_result["failed_count"]
                summary["total_skipped_count"] += item_result["skipped_count"]

        conn.commit()
        return summary

    except Exception as e:
        conn.rollback()
        traceback.print_exc()
        summary["success"] = False
        summary["error"] = str(e)
        return summary

    finally:
        conn.close()


if __name__ == "__main__":
    print(run_once())