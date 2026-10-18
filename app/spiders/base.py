"""
采集适配器基类。

新增一个影视源时，继承 BaseAdapter，实现三个方法即可：
  1. fetch_list(page)        拿列表页，返回摘要 + 详情页 URL
  2. fetch_detail(url)       拿详情页，返回影片元信息
  3. parse_play_url(html)    从播放页 HTML / 接口返回里抠出 m3u8

所有方法输出统一 dataclass，由统一的 pipeline 写库，采集层不直接碰数据库。
"""
from __future__ import annotations

import abc
import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

from ..config import settings


@dataclass
class ListItem:
    """列表页一条摘要"""
    title: str
    detail_url: str
    poster: str = ""
    remarks: str = ""


@dataclass
class PlayItem:
    """一个播放地址（一集/一条线路的一个播放地址）"""
    play_from: str          # 线路名：线路1 / 高清
    episode_name: str       # 第01集 / 正片
    play_url: str           # m3u8 / mp4


@dataclass
class DetailInfo:
    """详情页完整信息"""
    title: str
    detail_url: str
    sub_title: str = ""
    type_name: str = ""
    region: str = ""
    language: str = ""
    year: str = ""
    score: float = 0.0
    director: str = ""
    actor: str = ""
    remarks: str = ""
    poster: str = ""
    description: str = ""
    plays: list[PlayItem] = field(default_factory=list)


def fingerprint(title: str, year: str, region: str) -> str:
    """统一去重指纹"""
    raw = f"{title.strip()}|{year.strip()}|{region.strip()}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


class BaseAdapter(abc.ABC):
    """所有采集源的基类"""

    name: str = "base"            # 来源站唯一标识，写库时存 source_name
    base_url: str = ""            # 站点根地址

    def __init__(self) -> None:
        self.client = httpx.Client(
            timeout=settings.spider_timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                ),
                "Referer": self.base_url,
            },
            follow_redirects=True,
        )

    def sleep(self) -> None:
        time.sleep(random.uniform(settings.spider_delay_min, settings.spider_delay_max))

    def get(self, url: str, **kwargs) -> httpx.Response:
        self.sleep()
        resp = self.client.get(url, **kwargs)
        resp.raise_for_status()
        return resp

    # ---------- 子类必须实现 ----------
    @abc.abstractmethod
    def fetch_list(self, page: int = 1) -> list[ListItem]:
        """抓列表页，返回 ListItem 列表"""

    @abc.abstractmethod
    def fetch_detail(self, item: ListItem) -> DetailInfo:
        """抓详情页，返回 DetailInfo（含播放地址）"""

    # ---------- 统一入口 ----------
    def crawl(self, max_page: int = 1) -> list[DetailInfo]:
        """跑 max_page 页，返回完整详情列表，由 pipeline 写库"""
        results: list[DetailInfo] = []
        for p in range(1, max_page + 1):
            try:
                items = self.fetch_list(p)
            except Exception as e:  # 一个页面挂了不影响其他
                print(f"[{self.name}] list page {p} error: {e}")
                continue
            for it in items:
                try:
                    results.append(self.fetch_detail(it))
                except Exception as e:
                    print(f"[{self.name}] detail {it.detail_url} error: {e}")
        return results
