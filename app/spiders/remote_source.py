"""
远程片源订阅适配器。

作用：拉取别人已经整理好的苹果CMS接口（/aa.json 或 /api.php/provide/vod/），
把影片和播放地址直接导入你自己的数据库。因为格式统一，一次请求拿全量。

配置：
  REMOTE_SOURCES = [
      "https://别人的站/aa.json",
      "https://另一个站/api.php/provide/vod/",
  ]

注意：你拉来的片源是否有版权，由你自己承担。
"""
from __future__ import annotations

import httpx
from bs4 import BeautifulSoup  # noqa: F401  保留备用

from ..config import settings
from .base import BaseAdapter, DetailInfo, ListItem, PlayItem


# ===== 在这里填别人的接口地址 =====
# 经探测可用的苹果CMS标准源（带 ac=videolist 直接拿影片+播放地址）
REMOTE_SOURCES: list[str] = [
    "https://bfzyapi.com/api.php/provide/vod/?ac=videolist&pg=1",
    "https://hhzyapi.com/api.php/provide/vod/?ac=videolist&pg=1",
    "https://jszyapi.com/api.php/provide/vod/?ac=videolist&pg=1",
    "https://suoniapi.com/api.php/provide/vod/from/snm3u8?ac=videolist&pg=1",
    "https://api.1080zyku.com/inc/apijson.php?ac=videolist&pg=1",
]


def _split_play_url(play_url_str: str) -> list[PlayItem]:
    """
    解析苹果CMS播放串:
      线路1$$$第01集$url#第02集$url$$$线路2$$$第01集$url
    """
    out: list[PlayItem] = []
    current_line = "线路1"
    for block in (play_url_str or "").split("$$$"):
        block = block.strip()
        if not block:
            continue
        if "$" not in block:
            current_line = block
            continue
        for ep in block.split("#"):
            if "$" not in ep:
                continue
            name, url = ep.split("$", 1)
            if url.strip():
                out.append(PlayItem(play_from=current_line, episode_name=name, play_url=url))
    return out


def _doc_to_detail(doc: dict, source_url: str) -> DetailInfo:
    """把 aa.json 里的一条 list 转成 DetailInfo"""
    return DetailInfo(
        title=doc.get("vod_name", ""),
        detail_url=source_url,
        type_name=doc.get("vod_type", ""),
        region=doc.get("vod_area", ""),
        language=doc.get("vod_lang", ""),
        year=str(doc.get("vod_year", "")),
        score=float(doc.get("vod_score") or 0),
        director=doc.get("vod_director", ""),
        actor=doc.get("vod_actor", ""),
        remarks=doc.get("vod_remarks", ""),
        poster=doc.get("vod_pic", ""),
        description=doc.get("vod_content", ""),
        plays=_split_play_url(doc.get("vod_play_url", "")),
    )


class RemoteSourceAdapter(BaseAdapter):
    """一个适配器对应一组远程接口；自动翻页拉取，fetch_detail 直接命中缓存。"""

    name = "remote"
    base_url = "https://example.com"

    # 每个源最多翻多少页
    MAX_PAGES = 5

    def __init__(self, sources: list[str] | None = None, max_pages: int = MAX_PAGES) -> None:
        super().__init__()
        self.sources = sources or REMOTE_SOURCES
        self.max_pages = max_pages
        # 缓存从远程拉到的完整详情，避免 fetch_detail 再发一次请求
        self._cache: dict[str, DetailInfo] = {}

    def _page_url(self, url: str, page: int) -> str:
        """把 URL 里的 pg=N 替换成目标页码"""
        if "pg=" in url:
            return url.split("pg=")[0] + f"pg={page}" + (url.split("pg=", 1)[1].split("&", 1)[1] if "&" in url.split("pg=", 1)[1] else "")
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}pg={page}"

    def fetch_list(self, page: int = 1) -> list[ListItem]:
        if page != 1:
            return []
        items: list[ListItem] = []
        for url in self.sources:
            source_count = 0
            for p in range(1, self.max_pages + 1):
                page_url = self._page_url(url, p)
                try:
                    resp = self.client.get(page_url, timeout=settings.spider_timeout)
                    data = resp.json()
                except Exception as e:
                    print(f"[remote] {page_url} 请求失败: {e}")
                    break  # 这个源翻页中断
                docs = data.get("list") or data.get("data") or []
                if not docs:
                    break  # 没数据了，翻页结束
                for doc in docs:
                    title = doc.get("vod_name", "")
                    if not title:
                        continue
                    detail = _doc_to_detail(doc, url)
                    key = f"{title}|{detail.year}|{detail.region}"
                    if key in self._cache:
                        continue  # 跨页去重
                    self._cache[key] = detail
                    items.append(ListItem(
                        title=title,
                        detail_url=key,
                        poster=detail.poster,
                        remarks=detail.remarks,
                    ))
                    source_count += 1
                self.sleep()  # 翻页间隔，防反爬
            print(f"[remote] {url} 本源入库 {source_count} 部")
        return items

    def fetch_detail(self, item: ListItem) -> DetailInfo:
        # 直接命中缓存，不再请求
        return self._cache[item.detail_url]
