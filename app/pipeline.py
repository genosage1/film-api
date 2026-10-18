"""采集结果写库 pipeline：去重 + upsert"""
from __future__ import annotations

from sqlalchemy.orm import Session

from .models import Vod, VodPlay
from .spiders.base import DetailInfo, fingerprint


def save_detail(db: Session, info: DetailInfo, source_name: str) -> Vod:
    """把一条详情写入数据库；已存在则更新元信息并重建播放源"""
    fp = fingerprint(info.title, info.year, info.region)

    vod = db.query(Vod).filter(Vod.fingerprint == fp).first()
    if vod is None:
        vod = Vod(fingerprint=fp)
        db.add(vod)

    vod.title = info.title
    vod.sub_title = info.sub_title
    vod.type_name = info.type_name
    vod.region = info.region
    vod.language = info.language
    vod.year = info.year
    vod.score = float(info.score or 0)
    vod.director = info.director
    vod.actor = info.actor
    vod.remarks = info.remarks
    vod.poster = info.poster
    vod.description = info.description
    vod.source_name = source_name
    vod.source_url = info.detail_url

    # 播放源：先清后插（简单稳妥；量大可做 diff）
    vod.play_sources.clear()
    for p in info.plays:
        vod.play_sources.append(VodPlay(
            play_from=p.play_from,
            episode_name=p.episode_name,
            play_url=p.play_url,
        ))

    db.commit()
    db.refresh(vod)
    return vod


def run_crawler(db: Session, adapter, max_page: int = 1) -> int:
    """跑一个采集器并写库，返回入库条数"""
    details = adapter.crawl(max_page=max_page)
    n = 0
    for d in details:
        try:
            save_detail(db, d, adapter.name)
            n += 1
        except Exception as e:
            print(f"[pipeline] save failed {d.title}: {e}")
    return n
