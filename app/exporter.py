"""
把数据库全量导出成苹果CMS静态采集文件 aa.json。

导出后文件在 static/aa.json，用 nginx/caddy 直接托管：
    location / {
        root /path/to/film_api/static;
    }
别人填 http://你的域名/aa.json 就能被苹果CMS类APP采集。
"""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from .models import Vod

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
EXPORT_FILE = STATIC_DIR / "aa.json"


def _play_from_and_url(vod: Vod) -> tuple[str, str]:
    """返回 (线路名字符串, 完整播放串)，符合苹果CMS格式"""
    groups: dict[str, list[str]] = {}
    for p in vod.play_sources:
        groups.setdefault(p.play_from or "线路1", []).append(
            f"{p.episode_name}${p.play_url}"
        )
    lines = list(groups.keys())
    play_from = "$$$".join(lines)
    play_url = "$$$".join(
        f"{line}$$$" + "#".join(groups[line]) for line in lines
    )
    return play_from, play_url


def export_aa_json(db: Session) -> Path:
    """全量导出，返回文件路径"""
    STATIC_DIR.mkdir(exist_ok=True)
    vods = db.query(Vod).order_by(Vod.updated_at.desc()).all()

    items = []
    for v in vods:
        play_from, play_url = _play_from_and_url(v)
        items.append({
            "vod_id": v.id,
            "vod_name": v.title,
            "vod_pic": v.poster,
            "vod_remarks": v.remarks,
            "vod_year": v.year,
            "vod_area": v.region,
            "vod_lang": v.language,
            "vod_type": v.type_name,
            "vod_actor": v.actor,
            "vod_director": v.director,
            "vod_content": v.description,
            "vod_score": f"{v.score:.1f}" if v.score else "",
            "vod_time": v.updated_at.strftime("%Y-%m-%d") if v.updated_at else "",
            "vod_play_from": play_from,
            "vod_play_url": play_url,
        })

    payload = {
        "code": "1",
        "msg": "数据列表",
        "page": "1",
        "pagecount": "1",
        "limit": str(len(items)),
        "total": str(len(items)),
        "list": items,
    }

    EXPORT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return EXPORT_FILE
