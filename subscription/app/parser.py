from datetime import datetime


def extract_posts(api_response: dict) -> list[dict]:
    items = api_response.get("data", {}).get("list", [])
    posts = []

    for item in items:
        ts = item.get("timestamp")
        posts.append(
            {
                "pid": item.get("pid"),
                "text": item.get("text", "") or "",
                "type": item.get("type"),
                "timestamp": ts,
                "datetime": datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else None,
                "label": item.get("label", 0),
                "reply_count": item.get("reply", 0),
                "like_num": item.get("likenum", 0),
                "tags_list": item.get("tags_list", []),
                "raw_json": item,
            }
        )

    return posts