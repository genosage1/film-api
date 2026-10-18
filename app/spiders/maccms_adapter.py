"""
通用苹果CMS(MacCMS V10)采集适配器。

适配绝大多数苹果CMS模板站，典型页面结构：
  列表页:  /type/{分类ID}-{页码}.html
          <ul class="stui-vodlist"> <li> ... <a href="/voddetail/xx.html" title="..."> <img data-original="封面">
  详情页:  /voddetail/{id}.html
          <h1 class="title">标题</h1>
          <meta> / 文本里含 地区/语言/年份/导演/主演/简介
          JS里 var player_aaaa = {"url":"...m3u8","name":"第01集",...}
          或多集播放列表: <a class="play_item" href="/voddplay/{id}-1-1.html">第01集</a>

使用方法：
  1. 把 base_url 改成你自己的源（例如 "https://你的影视站"）
  2. 在 app/scheduler.py 的 _SPIDERS 里注册：
       from .spiders.maccms_adapter import MacCMSAdapter
       _SPIDERS.append((MacCMSAdapter(), 3))
  3. 启动即可。

注意：采集需授权的源；本文件仅作技术演示。
"""
from __future__ import annotations

import json
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import BaseAdapter, DetailInfo, ListItem, PlayItem


class MacCMSAdapter(BaseAdapter):
    # ====== 改成你自己的源 ======
    name = "maccms"
    base_url = "https://example.com"

    # 要抓的分类ID（苹果CMS后台分类ID），1=动作/2=喜剧...按你源站实际填
    type_ids = [1, 2, 3, 4]

    def _list_url(self, type_id: int, page: int) -> str:
        return f"{self.base_url}/type/{type_id}-{page}.html"

    # ---------- 列表页 ----------
    def fetch_list(self, page: int = 1) -> list[ListItem]:
        items: list[ListItem] = []
        for tid in self.type_ids:
            try:
                resp = self.get(self._list_url(tid, page))
            except Exception as e:
                print(f"[{self.name}] list {tid}-{page} error: {e}")
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            # 标准模板：ul.stui-vodlist li a（部分模板是 .vodlist 或 .list-body）
            for a in soup.select("ul.stui-vodlist li a, ul.vodlist li a, .list-body li a"):
                href = a.get("href", "")
                if not href or not href.endswith(".html") and "/voddetail/" not in href and "/detail/" not in href:
                    continue
                title = a.get("title") or a.get("alt") or ""
                if not title:
                    img = a.find("img")
                    if img:
                        title = img.get("alt", "") or img.get("title", "")
                poster = ""
                img = a.find("img")
                if img:
                    poster = img.get("data-original") or img.get("src", "")
                items.append(ListItem(
                    title=title.strip(),
                    detail_url=urljoin(self.base_url, href),
                    poster=urljoin(self.base_url, poster) if poster else "",
                ))
        return items

    # ---------- 详情页 ----------
    def fetch_detail(self, item: ListItem) -> DetailInfo:
        html = self.get(item.detail_url).text
        soup = BeautifulSoup(html, "html.parser")

        # 标题
        h = soup.select_one("h1.title, .stui-content__detail h1, h1")
        title = h.get_text(strip=True) if h else item.title

        # 文本信息块：苹果CMS通常在 .detail 里以 "地区：大陆" 这种形式罗列
        text_block = soup.select_one(".stui-content__detail, .detail, .content-detail")
        text = text_block.get_text(" ", strip=True) if text_block else ""

        def pick(label: str) -> str:
            m = re.search(rf"{label}[：:]\s*([^\s]+)", text)
            return m.group(1).strip() if m else ""

        region = pick("地区") or pick("地区:")
        language = pick("语言")
        year = pick("年份") or pick("上映")
        director = pick("导演")
        actor = pick("主演")

        # 简介
        desc = ""
        d = soup.select_one(".desc, .detail-content, .stui-content__detail .info")
        if d:
            desc = d.get_text(" ", strip=True)

        # 海报
        poster = item.poster
        if not poster:
            img = soup.select_one(".vod-pic img, .stui-content__thumb img")
            if img:
                poster = urljoin(self.base_url, img.get("data-original") or img.get("src", ""))

        # 评分（从文本里抽一个浮点数）
        score = 0.0
        m = re.search(r"(\d+\.\d+)", text)
        if m:
            try:
                score = float(m.group(1))
            except ValueError:
                score = 0.0

        # 备注：最新更新集数
        remarks = ""
        rm = soup.select_one(".pic-text, .remarks, .st-vod-list .remarks")
        if rm:
            remarks = rm.get_text(strip=True)

        plays = self._parse_plays(html, soup)

        return DetailInfo(
            title=title,
            detail_url=item.detail_url,
            type_name=pick("类型"),
            region=region,
            language=language,
            year=year,
            score=score,
            director=director,
            actor=actor,
            remarks=remarks,
            poster=poster,
            description=desc,
            plays=plays,
        )

    # ---------- m3u8 提取（核心） ----------
    def _parse_plays(self, html: str, soup: BeautifulSoup) -> list[PlayItem]:
        """
        兼容三种常见形态：
        A) 详情页直接内嵌 var player_aaaa = {"url":"...m3u8","name":"第01集"}
        B) 详情页内嵌 var player_data = {"url":"$$$第01集$url#第02集$url"}
        C) 详情页只有播放列表 <a href="/voddplay/x-1-1.html">第01集</a>，需要逐集请求播放页再抠 url
        """
        plays: list[PlayItem] = []

        # --- A: player_aaaa ---
        m = re.search(r"var\s+player_aaa\w*\s*=\s*(\{.*?\})\s*[;<]", html, re.S)
        if m:
            try:
                data = json.loads(m.group(1))
                url = data.get("url", "")
                if url:
                    plays.append(PlayItem(
                        play_from=data.get("from", "线路1") or "线路1",
                        episode_name=data.get("name", "正片") or "正片",
                        play_url=url,
                    ))
                    return plays
            except json.JSONDecodeError:
                pass

        # --- B: player_data / vod_play_url 形如 "线路1$$$第01集$url#第02集$url"
        m = re.search(r"(?:player_data|vod_play_url|play_url)\s*=\s*[\"']([^\"']+\.m3u8[^\"']*)[\"']", html)
        if m:
            plays = self._split_play_string(m.group(1))
            if plays:
                return plays

        # --- C: 逐集抓播放页 ---
        episode_links = soup.select("a[href*='voddplay'], a[href*='/play/']")
        seen = set()
        for a in episode_links:
            href = a.get("href", "")
            ep_name = a.get_text(strip=True) or "正片"
            full = urljoin(self.base_url, href)
            if full in seen:
                continue
            seen.add(full)
            try:
                play_html = self.get(full).text
                pm = re.search(r"var\s+player_aaa\w*\s*=\s*(\{.*?\})\s*[;<]", play_html, re.S)
                if pm:
                    data = json.loads(pm.group(1))
                    plays.append(PlayItem(
                        play_from="线路1",
                        episode_name=ep_name,
                        play_url=data.get("url", ""),
                    ))
            except Exception as e:
                print(f"[{self.name}] play page {full} error: {e}")
        return plays

    @staticmethod
    def _split_play_string(s: str) -> list[PlayItem]:
        """
        把苹果CMS播放串拆成 PlayItem 列表。
        串格式: 线路1$$$第01集$url#第02集$url$$$线路2$$$第01集$url
        按 $$$ 切分后，"线路名块"和"集数块"是相邻的两个独立块。
        """
        out: list[PlayItem] = []
        current_line = "线路1"
        for block in s.split("$$$"):
            block = block.strip()
            if not block:
                continue
            if "$" not in block:
                # 纯线路名块
                current_line = block
                continue
            # 集数块：第01集$url#第02集$url
            for ep in block.split("#"):
                if "$" not in ep:
                    continue
                name, url = ep.split("$", 1)
                if url.strip():
                    out.append(PlayItem(play_from=current_line, episode_name=name, play_url=url))
        return out
