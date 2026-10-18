# Film API —— 自研影视采集接口骨架

FastAPI + SQLAlchemy + 爬虫 Adapter 架构，输出**兼容苹果CMS（MacCMS V10）**的接口，
你的影视 APP 直接把接口地址填进去就能用。

## 目录结构

```
film_api/
├── app/
│   ├── main.py            # FastAPI 入口，启动自动建表+灌数据+定时任务
│   ├── config.py         # 配置（读 .env）
│   ├── database.py        # 数据库连接（默认 SQLite，开箱即用）
│   ├── models.py         # Vod / VodPlay / Category 模型
│   ├── pipeline.py        # 采集结果去重写库
│   ├── scheduler.py      # APScheduler 定时采集
│   ├── api/vod.py         # 兼容苹果CMS的接口路由
│   └── spiders/
│       ├── base.py         # BaseAdapter 抽象类 + 统一输出结构
│       └── demo_adapter.py # 示例采集器（内置mock数据，注释里有真实站写法）
├── sql/init.sql          # MySQL 建表脚本（SQLite 自动建表可不用）
├── requirements.txt
└── .env.example
```

## 快速启动

```bash
cd film_api
pip install -r requirements.txt
copy .env.example .env        # Windows
uvicorn app.main:app --reload
```

启动后自动：建表 → 跑一次 demo 采集器灌 3 条示例数据 → 开启每 30 分钟定时采集。

## 接口地址

- 接口文档（Swagger）：http://127.0.0.1:8000/docs
- 苹果CMS 接口：http://127.0.0.1:8000/api.php/provide/vod/
  - 分类：`?ac=list`
  - 列表：`?ac=videolist&pg=1&limit=10`
  - 详情：`?ac=detail&ids=1`
  - 搜索：`?ac=detail&wd=流浪地球`
- 手动采集：`POST /admin/crawl`

## 新增一个真实影视源

1. 在 `app/spiders/` 复制 `demo_adapter.py` 为 `xxx_adapter.py`
2. 继承 `BaseAdapter`，实现 `name`、`base_url`、`fetch_list()`、`fetch_detail()`
   - `fetch_detail` 里重点解析播放页，把 m3u8 填进 `PlayItem.play_url`
3. 在 `app/scheduler.py` 的 `_SPIDERS` 里注册：
   ```python
   from .spiders.xxx_adapter import XxxAdapter
   _SPIDERS.append((XxxAdapter(), 3))
   ```
4. 重启即可，APP 端不用改任何东西。

## 切 MySQL

编辑 `.env`：
```
DATABASE_URL=mysql+pymysql://user:pass@127.0.0.1:3306/film_api?charset=utf8mb4
```
先执行 `sql/init.sql` 建库建表，再启动。

## 注意

- 采集未授权影视源有版权风险，仅限学习/内网使用，对外上线请确认授权。
- m3u8 若有 Referer 防盗链，可在后端加一层代理转发接口，APP 直接请求你自己的代理地址。
