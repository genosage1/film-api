"""
GitHub Actions 采集脚本：跑一次采集，导出 aa.json
不启动 Web 服务，只做数据拉取和导出。
"""
from app.database import init_db, SessionLocal
from app.exporter import export_aa_json
from app.scheduler import crawl_all


def main():
    init_db()
    db = SessionLocal()
    try:
        crawl_all()  # 跑所有采集器
        path = export_aa_json(db)  # 导出 aa.json
        print(f"✅ 采集完成，导出文件: {path}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
