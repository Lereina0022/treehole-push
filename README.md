# Treehole Push

一个轻量级的北大树洞关键词监控与微信提醒工具。

项目通过 GitHub Actions 在云端定时运行：每隔 4 小时调用树洞搜索接口，根据自定义关键词规则筛选近期帖子，并通过 Server酱发送到微信。

## 功能

- GitHub Actions 云端定时运行，无需电脑持续开机
- 根据关键词调用树洞搜索接口
- 支持简单匹配、组合匹配和排除词
- 只处理最近指定时间范围内的帖子
- 将同一订阅命中的帖子合并推送
- 使用 Server酱发送微信提醒
- 无数据库，Fork 仓库后即可独立配置

## 工作原理

```text
GitHub Actions 定时触发
        ↓
读取 subscriptions.json
        ↓
调用树洞 API 搜索 query_text
        ↓
筛选最近 5 小时的帖子
        ↓
按照 rule 进行二次匹配
        ↓
通过 Server酱推送到微信
```

默认每 4 小时运行一次，并向前检查最近 5 小时。多出的 1 小时用于容忍 GitHub Actions 延迟，但也意味着相邻两次任务之间存在重叠，少数帖子可能重复推送。

## 项目结构

```text
treehole-push/
├── .github/
│   └── workflows/
│       └── treehole_push.yml    # GitHub Actions 定时任务
├── subscription/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py            # 环境变量和运行参数
│   │   ├── matcher.py           # 关键词规则匹配
│   │   ├── notifier.py          # Server酱推送
│   │   ├── parser.py            # 解析树洞接口结果
│   │   ├── runner.py            # 主执行逻辑
│   │   └── treehole_client.py   # 树洞 API 客户端
│   ├── subscriptions.json       # 订阅规则
│   └── requirements.txt         # Python 依赖
├── env.example.txt              # 本地环境变量示例
├── .gitignore
└── README.md
```

## 快速部署

### 1. Fork 仓库

点击仓库页面右上角的 **Fork**，将项目复制到自己的 GitHub 账号下。

### 2. 配置 GitHub Secrets

进入自己 Fork 后的仓库：

```text
Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

依次添加以下 Secrets：

| Secret | 用途 |
| --- | --- |
| `TREEHOLE_AUTHORIZATION` | 树洞请求中的 Authorization |
| `TREEHOLE_COOKIE` | 树洞登录 Cookie |
| `TREEHOLE_X_XSRF_TOKEN` | 树洞请求中的 X-XSRF-Token |
| `TREEHOLE_UUID` | 树洞请求中的 UUID |
| `SERVERCHAN_SENDKEY` | Server酱 SendKey |

树洞认证信息可以从已登录树洞的浏览器网络请求中查看。认证信息可能过期；如果 Actions 出现 `401` 或 `403`，通常需要重新获取并更新相应 Secret。

> 请勿将 Cookie、Authorization、XSRF Token 或 Server酱 SendKey 写入代码、提交到仓库或分享给他人。

### 3. 配置 Server酱

1. 打开 [Server酱](https://sct.ftqq.com/)
2. 登录并绑定微信
3. 获取 SendKey
4. 将 SendKey 保存为仓库 Secret `SERVERCHAN_SENDKEY`

### 4. 修改订阅规则

编辑：

```text
subscription/subscriptions.json
```

保存并提交后，后续任务会自动读取新规则。

### 5. 启用并测试 GitHub Actions

进入仓库的 **Actions** 页面，选择 **Treehole Push**，点击：

```text
Run workflow
→ Run workflow
```

第一次使用时建议先手动运行。日志中出现以下内容，说明程序已经开始处理订阅：

```text
开始运行，共 3 个订阅，回看最近 5.0 小时
处理订阅: 实习招聘 | query=实习
```

任务显示绿色勾表示本轮执行成功。即使没有符合规则的帖子，也不会发送微信通知。

## 订阅规则

`subscriptions.json` 最外层是一个数组，每个对象代表一个订阅。

### 简单模式

简单模式下，任意一个关键词出现即可命中：

```json
{
  "category_name": "课程信息",
  "query_text": "课程",
  "rule": {
    "mode": "simple",
    "keywords": ["补选", "退课", "课程群", "调课"],
    "exclude": ["求课程资料"]
  }
}
```

逻辑为：

```text
包含“补选 / 退课 / 课程群 / 调课”中的任意一个词，
并且不包含“求课程资料”。
```

### 高级模式

高级模式中，组内是“或”，组间是“且”：

```json
{
  "category_name": "金融实习",
  "query_text": "实习",
  "rule": {
    "mode": "advanced",
    "groups": [
      ["实习", "招聘", "内推"],
      ["证券", "基金", "投行", "金融"]
    ],
    "exclude": ["求实习", "已截止"]
  }
}
```

逻辑为：

```text
（实习 或 招聘 或 内推）
且
（证券 或 基金 或 投行 或 金融）
且不包含
（求实习 或 已截止）
```

字段说明：

| 字段 | 含义 |
| --- | --- |
| `category_name` | 推送中显示的订阅名称 |
| `query_text` | 提交给树洞 API 的初步搜索词 |
| `mode` | `simple` 或 `advanced` |
| `keywords` | 简单模式使用的关键词列表 |
| `groups` | 高级模式使用的关键词组 |
| `exclude` | 排除词；出现任意一个即不推送 |

`query_text` 用于从树洞取得候选帖子，`rule` 用于在本地进行更精确的二次筛选。建议让 `query_text` 使用覆盖范围较大的核心词，再通过 `rule` 缩小结果。

## 定时设置

工作流默认配置为：

```yaml
schedule:
  - cron: "17 */4 * * *"
```

它表示每隔 4 小时触发一次。GitHub Actions 使用 UTC 时间，且定时任务不保证精确到分钟，实际启动可能有所延迟。

如需修改回看范围，可以编辑工作流中的：

```yaml
LOOKBACK_HOURS: "5"
```

回看时间越长，漏掉帖子的风险越低，但相邻任务发生重复推送的可能性越高。

## 本地测试

如果希望在提交前本地测试：

```bash
cd subscription
pip install -r requirements.txt
```

复制环境变量示例并填写自己的配置，然后运行：

```bash
python -m app.runner
```

本地测试可能发送真实的 Server酱通知，请先确认订阅规则和 SendKey。

## 常见问题

### Actions 报 `401` 或 `403`

树洞 Cookie、Authorization 或 XSRF Token 可能已经失效。重新登录树洞，获取最新认证信息并更新 GitHub Secrets。

### 提示找不到 `subscriptions.json`

确认文件路径和名称严格为：

```text
subscription/subscriptions.json
```

### Actions 成功但没有收到通知

可能原因包括：

- 最近 5 小时没有符合规则的帖子
- 排除词过滤了候选帖子
- Server酱尚未正确绑定微信
- `SERVERCHAN_SENDKEY` 配置错误

可以先查看 Actions 日志，确认每个订阅显示“本轮没有命中”还是推送失败。

### 为什么会收到重复帖子

项目目前不使用数据库，也不跨任务保存已推送 PID。由于任务每 4 小时执行一次、默认回看 5 小时，相邻任务有约 1 小时重叠，因此重叠区间内的帖子可能再次推送。

这是无数据库轻量方案的已知取舍：提高容错能力，同时接受少量重复提醒。

## 已知限制

- 不保存帖子和推送历史
- 不提供跨轮次严格去重
- GitHub Actions 可能延迟或偶尔执行失败
- 只检查 API 返回范围内的候选帖子，搜索结果过多时可能遗漏
- 树洞认证信息需要在过期后手动更新
- 关键词匹配基于字符串，不进行语义理解

## 免责声明

本项目仅供个人学习和信息提醒使用。使用时请遵守相关网站规则，妥善保管个人认证信息，合理设置运行频率，避免对接口造成不必要的请求压力。
