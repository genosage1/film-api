"""FastAPI 入口

启动：
    uvicorn app.main:app --reload
接口文档：
    http://127.0.0.1:8000/docs
静态采集文件：
    http://127.0.0.1:8000/aa.json
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.vod import router as vod_router
from .config import settings
from .database import SessionLocal, init_db
from .exporter import export_aa_json
from .scheduler import crawl_all, start_scheduler

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：建表 → 灌数据 → 导出 aa.json → 开定时任务
    init_db()
    crawl_all()
    db = SessionLocal()
    try:
        export_aa_json(db)
        print("[startup] aa.json 已导出")
    finally:
        db.close()
    start_scheduler()
    yield


app = FastAPI(title="Film API", version="0.1.0", lifespan=lifespan)
app.include_router(vod_router)

# 把 static 目录挂到根路径，这样 /aa.json 直接可下载
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/admin/crawl")
def admin_crawl():
    """手动触发一次全量采集，并重导出 aa.json"""
    crawl_all()
    db = SessionLocal()
    try:
        path = export_aa_json(db)
    finally:
        db.close()
    return {"ok": True, "msg": "采集并导出完成", "file": str(path)}


@app.post("/admin/export")
def admin_export():
    """只重新导出 aa.json（不重新采集）"""
    db = SessionLocal()
    try:
        path = export_aa_json(db)
    finally:
        db.close()
    return {"ok": True, "file": str(path)}
