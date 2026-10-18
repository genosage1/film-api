"""定时采集任务"""
from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from .database import SessionLocal
from .exporter import export_aa_json
from .pipeline import run_crawler
from .spiders.demo_adapter import DemoAdapter
from .spiders.open_movie_adapter import OpenMovieAdapter
from .spiders.remote_source import RemoteSourceAdapter
# 填好 base_url 后取消下面注释即可启用真实采集
# from .spiders.maccms_adapter import MacCMSAdapter

_scheduler: BackgroundScheduler | None = None

# 在这里注册你所有的采集器：(adapter实例, 抓几页)
_SPIDERS = [
    (DemoAdapter(), 1),
    (OpenMovieAdapter(), 1),   # CC-BY 开源电影，合法片源
    (RemoteSourceAdapter(), 1),  # 远程订阅别人的接口（在 remote_source.py 填 URL）
    # (MacCMSAdapter(), 3),   # <- 填好 MacCMSAdapter.base_url 后打开这行
]


def crawl_all() -> None:
    db = SessionLocal()
    try:
        for adapter, pages in _SPIDERS:
            n = run_crawler(db, adapter, max_page=pages)
            print(f"[scheduler] {adapter.name} 入库 {n} 条")
        # 采集完自动重导出 aa.json
        export_aa_json(db)
        print("[scheduler] aa.json 已更新")
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    _scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    # 每 30 分钟跑一次采集；按需调整
    _scheduler.add_job(crawl_all, "interval", minutes=30, id="crawl_all")
    _scheduler.start()
    return _scheduler
