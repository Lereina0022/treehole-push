# Treehole Push

一个本地运行的树洞关键词监控与微信推送工具。

这个项目会定时搜索指定关键词的树洞内容，根据自定义规则进行匹配；如果命中，就通过微信推送服务把提醒发到你的个人微信。

当前版本定位为：

- **本地部署**
- **单用户使用**
- **Windows 环境优先**
- **通过 Server酱推送到微信**
- **使用 MySQL 存储订阅、帖子和推送记录**

---

## 1. 项目功能

本项目目前支持以下功能：

- 本地定时运行树洞监控脚本
- 根据关键词搜索树洞内容
- 按自定义规则匹配帖子正文
- 命中后将消息推送到个人微信
- 自动记录已推送内容，避免重复发送
- 使用数据库保存订阅规则、帖子数据和推送日志

---

## 2. 适用场景

这个项目适合以下场景：

- 监控树洞中与课程签到、实习招聘、考试通知等相关的信息
- 用关键词订阅自己关心的话题
- 不想手动频繁刷树洞，希望有新内容时自动提醒
- 想做一个本地自动化消息推送的小项目

例如，你可以配置类似这样的订阅：

- `考古学通论 + 签到`
- `实习 + 产品`
- `保研 + 夏令营`
- `租房 + 五道口`

---

## 3. 项目结构

```text
treehole_push/
├─ app/
│  ├─ __init__.py
│  ├─ config.py          # 读取环境变量配置
│  ├─ database.py        # MySQL 连接
│  ├─ parser.py          # 树洞接口结果解析
│  ├─ matcher.py         # 订阅规则匹配
│  ├─ treehole_client.py # 树洞请求客户端
│  ├─ notifier.py        # 微信推送（Server酱）
│  └─ runner_core.py     # 主执行逻辑
│
├─ scripts/
│  ├─ run_once.bat       # 手动执行一次
│  └─ start_runner.bat   # 循环执行（测试用）
│
├─ sql/
│  └─ init.sql           # 数据库初始化脚本
│
├─ .env.example          # 配置文件模板
├─ .gitignore            # Git 忽略文件
├─ requirements.txt      # Python 依赖
└─ README.md

---

## 4. 运行环境

- Python 3.10+
- MySQL 8.0+
- Windows（推荐）
- 能访问树洞接口和 Server酱

```bash
pip install -r requirements.txt

---

## 5. 配置环境

修改env.example至.env，并根据指示进行个性化配置
树洞配置
- TREEHOLE_AUTHORIZATION=Bearer xxx
- TREEHOLE_COOKIE=xxx
- TREEHOLE_X_XSRF_TOKEN=xxx
- TREEHOLE_UUID=xxx
会过期，需要定时更新

MySQL配置
- TREEHOLE_AUTHORIZATION=Bearer xxx
- TREEHOLE_COOKIE=xxx
- TREEHOLE_X_XSRF_TOKEN=xxx
- TREEHOLE_UUID=xxx

微信推送
- SERVERCHAN_SENDKEY=SCTxxxxxxxxxxxxxxxx
获取方式：
1、打开 https://sct.ftqq.com
2、登录
3、创建 SendKey
4、绑定微信

---

## 6. 增加订阅
在sql文件中增加个性化关键词订阅
{
  "mode": "advanced",
  "groups": [
    ["关键词A"],
    ["关键词B", "关键词C"]
  ],
  "exclude": ["排除词"]
}

---

## 7. 长期运行
- scripts/run_once.bat
Win系统可在任务计划程序设置定时运行以上文件

---
