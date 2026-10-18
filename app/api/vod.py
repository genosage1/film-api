"""
兼容苹果CMS MacCMS V10 采集接口。

你的影视APP只要填这个地址就能直接拉数据，例如：
  http://你的服务器:8000/api.php/provide/vod/

支持参数：
  ac=list                  返回分类列表
  ac=videolist             影片分页列表
  ac=detail&ids=1,2        按ID返回详情（含播放地址）
  ac=detail&wd=流浪地球     按关键词搜索
  t=1   分类ID筛选（这里按 type_name 模糊匹配，可不传）
  pg=1  页码
  limit=20 每页条数
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Vod, VodPlay

router = APIRouter()


def _play_url(vod: Vod) -> str:
    """把 vod_play 列表拼成苹果CMS播放串：
    线路名$$$集名$地址#集名$地址$$$线路名$$$...
    """
    groups: dict[str, list[str]] = {}
    for p in vod.play_sources:
        groups.setdefault(p.play_from or "线路1", []).append(f"{p.episode_name}${p.play_url}")
    return "$$$".join(
        f"{name}$$$" + "#".join(eps) for name, eps in groups.items()
    )


def _to_list_item(vod: Vod, with_play: bool = False) -> dict:
    item = {
        "vod_id": vod.id,
        "vod_name": vod.title,
        "vod_pic": vod.poster,
        "vod_remarks": vod.remarks,
        "vod_year": vod.year,
        "vod_area": vod.region,
        "vod_lang": vod.language,
        "vod_type": vod.type_name,
        "vod_actor": vod.actor,
        "vod_director": vod.director,
        "vod_content": vod.description,
        "vod_score": f"{vod.score:.1f}" if vod.score else "",
        "vod_time": vod.updated_at.strftime("%Y-%m-%d") if vod.updated_at else "",
    }
    if with_play:
        item["vod_play_url"] = _play_url(vod)
    return item


@router.get("/api.php/provide/vod/")
def provide_vod(
    ac: str = Query("videolist"),
    t: int = Query(0, description="分类ID，预留"),
    pg: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    ids: str = Query("", description="逗号分隔的影片ID"),
    wd: str = Query("", description="搜索关键词"),
    db: Session = Depends(get_db),
):
    # 1) 分类列表
    if ac == "list":
        rows = db.query(Vod.type_name).distinct().all()
        classes = [
            {"type_id": i + 1, "type_name": r[0]}
            for i, r in enumerate(rows) if r[0]
        ]
        return {"code": 1, "msg": "数据列表", "class": classes, "list": []}

    # 2) 按ID查详情
    if ac == "detail" and ids:
        id_list = [int(x) for x in ids.split(",") if x.strip().isdigit()]
        vods = db.query(Vod).filter(Vod.id.in_(id_list)).all()
        return {
            "code": 1, "msg": "数据列表", "page": 1, "pagecount": 1,
            "limit": str(limit), "total": len(vods),
            "list": [_to_list_item(v, with_play=True) for v in vods],
        }

    # 3) 搜索
    if ac == "detail" and wd:
        q = db.query(Vod).filter(Vod.title.contains(wd)).order_by(Vod.updated_at.desc())
        total = q.count()
        vods = q.offset((pg - 1) * limit).limit(limit).all()
        return {
            "code": 1, "msg": "数据列表", "page": pg,
            "pagecount": (total + limit - 1) // limit,
            "limit": str(limit), "total": total,
            "list": [_to_list_item(v, with_play=True) for v in vods],
        }

    # 4) 影片列表（默认）
    q = db.query(Vod).order_by(Vod.updated_at.desc())
    total = q.count()
    vods = q.offset((pg - 1) * limit).limit(limit).all()
    return {
        "code": 1, "msg": "数据列表", "page": pg,
        "pagecount": (total + limit - 1) // limit,
        "limit": str(limit), "total": total,
        "list": [_to_list_item(v) for v in vods],
    }
