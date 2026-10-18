"""
示例采集器。

为了让你一启动就能看到接口返回数据，这里内置了几条 mock 影片；
真实接站时，把 _mock_detail 换成真实的 httpx 请求 + BeautifulSoup 解析即可。

接真实站的典型套路（注释里给的是苹果CMS类站的通用写法）：

    def fetch_list(self, page=1):
        html = self.get(f"{self.base_url}/type/1-{page}.html").text
        soup = BeautifulSoup(html, "lxml")
        items = []
        for a in soup.select("ul.stui-vodlist li a"):
            items.append(ListItem(
                title=a.get("title", ""),
                detail_url=urljoin(self.base_url, a["href"]),
                poster=a.find("img")["data-original"] if a.find("img") else "",
            ))
        return items

    def fetch_detail(self, item):
        html = self.get(item.detail_url).text
        soup = BeautifulSoup(html, "lxml")
        # m3u8 通常藏在 var player_aaaa = {...} 里
        m = re.search(r"var player_aaa\w*\s*=\s*(\{.*?\});", html)
        play_url = json.loads(m.group(1)).get("url") if m else ""
        ...
"""
from __future__ import annotations

from .base import BaseAdapter, DetailInfo, ListItem, PlayItem


class DemoAdapter(BaseAdapter):
    name = "demo"
    base_url = "https://example.com"

    # 内置演示数据（真实使用时删掉，改为抓取）
    _MOCK = [
        DetailInfo(
            title="流浪地球2",
            detail_url="https://example.com/vod/1.html",
            type_name="科幻", region="大陆", language="国语",
            year="2023", score="8.3",
            director="郭帆", actor="吴京 / 刘德华 / 李雪健",
            remarks="HD", poster="https://picsum.photos/seed/film1/300/420",
            description="太阳即将毁灭，人类在地球表面建造出巨大的推进器，寻找新家园。",
            plays=[
                PlayItem(play_from="线路1", episode_name="正片",
                         play_url="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"),
            ],
        ),
        DetailInfo(
            title="狂飙", detail_url="https://example.com/vod/2.html",
            type_name="犯罪", region="大陆", language="国语",
            year="2023", score="8.5",
            director="徐纪周", actor="张译 / 张颂文 / 李一桐",
            remarks="全39集", poster="https://picsum.photos/seed/film2/300/420",
            description="一线刑警安欣与黑恶势力团伙展开长达二十年的正邪较量。",
            plays=[
                PlayItem(play_from="线路1", episode_name="第01集",
                         play_url="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"),
                PlayItem(play_from="线路1", episode_name="第02集",
                         play_url="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"),
                PlayItem(play_from="线路2", episode_name="第01集",
                         play_url="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"),
            ],
        ),
        DetailInfo(
            title="奥本海默", detail_url="https://example.com/vod/3.html",
            type_name="传记", region="欧美", language="英语",
            year="2023", score="8.9",
            director="克里斯托弗·诺兰", actor="基里安·墨菲 / 艾米莉·布朗特",
            remarks="HD", poster="https://picsum.photos/seed/film3/300/420",
            description="讲述理论物理学家罗伯特·奥本海默领导曼哈顿计划、研制原子弹的故事。",
            plays=[
                PlayItem(play_from="线路1", episode_name="正片",
                         play_url="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"),
            ],
        ),
    ]

    def fetch_list(self, page: int = 1) -> list[ListItem]:
        # 演示数据只有一页
        if page != 1:
            return []
        return [ListItem(title=d.title, detail_url=d.detail_url,
                        poster=d.poster, remarks=d.remarks) for d in self._MOCK]

    def fetch_detail(self, item: ListItem) -> DetailInfo:
        for d in self._MOCK:
            if d.detail_url == item.detail_url:
                return d
        raise ValueError(f"no mock detail for {item.detail_url}")
