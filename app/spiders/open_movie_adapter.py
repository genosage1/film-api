"""
开源电影适配器（合法、无版权风险）。

收录 Blender 基金会 Open Movie Project 的作品，全部采用 Creative Commons
Attribution 3.0/4.0 许可——你可以免费使用、播放、再分发，只需在 APP 里
注明原作者与许可协议。

这些是真实存在、有完整制作班底的短片电影，不是测试占位片。
播放地址使用公开可访问的 HLS/mp4 测试流；如在国内部署，建议把视频文件
转存到你自己的 OSS/COS 并替换 play_url。
"""
from __future__ import annotations

from .base import BaseAdapter, DetailInfo, ListItem, PlayItem

# 公开测试流（CC-BY，来源 mux / Google gtv sample bucket）
_HLS = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
_MP4_BBB = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
_MP4_SINTEL = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"
_MP4_TOS = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
_MP4_ED = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"


class OpenMovieAdapter(BaseAdapter):
    name = "openmovie"
    base_url = "https://peach.blender.org"

    _MOVIES: list[DetailInfo] = [
        DetailInfo(
            title="大雄兔 Big Buck Bunny",
            detail_url="https://peach.blender.org/",
            type_name="动画/短片", region="荷兰", language="无对白",
            year="2008", score=8.0,
            director="Sacha Goedegebuer", actor="Blender Institute",
            remarks="CC-BY 开源电影",
            poster="https://picsum.photos/seed/bbb/300/420",
            description=(
                "一只体型巨大、性情温顺的兔子，在森林里被三只啮齿小动物恶作剧后，"
                "精心策划了一场幽默的复仇。Blender 基金会第二部开源电影，全片使用开源软件制作。"
            ),
            plays=[
                PlayItem("HLS流", "正片", _HLS),
                PlayItem("MP4", "正片", _MP4_BBB),
            ],
        ),
        DetailInfo(
            title="辛特尔 Sintel",
            detail_url="https://durian.blender.org/",
            type_name="奇幻/短片", region="荷兰", language="英语",
            year="2010", score=8.2,
            director="Colin Levy", actor="Halcyon (配音)",
            remarks="CC-BY 开源电影",
            poster="https://picsum.photos/seed/sintel/300/420",
            description=(
                "少女辛特尔流浪天涯，只为寻找她救下又走失的小龙。一段关于执着、"
                "孤独与救赎的黑暗奇幻旅程，Blender 基金会第三部开源电影。"
            ),
            plays=[
                PlayItem("HLS流", "正片", _HLS),
                PlayItem("MP4", "正片", _MP4_SINTEL),
            ],
        ),
        DetailInfo(
            title="钢铁之泪 Tears of Steel",
            detail_url="https://mango.blender.org/",
            type_name="科幻/真人CG", region="荷兰", language="英语",
            year="2012", score=7.8,
            director="Ian Hubert", actor="Derek de Lint / Vanja Rukavina",
            remarks="CC-BY 开源电影",
            poster="https://picsum.photos/seed/tos/300/420",
            description=(
                "未来的阿姆斯特丹，一群科学家试图阻止一台被唤醒的巨型机器人毁灭世界。"
                "实拍与绿幕结合 Blender CG，真人电影与开源特效的实验之作。"
            ),
            plays=[
                PlayItem("HLS流", "正片", _HLS),
                PlayItem("MP4", "正片", _MP4_TOS),
            ],
        ),
        DetailInfo(
            title="大象之梦 Elephants Dream",
            detail_url="https://orange.blender.org/",
            type_name="科幻/实验", region="荷兰", language="英语",
            year="2006", score=7.3,
            director="Bassam Kurdali", actor="Emo / Proog",
            remarks="CC-BY 开源电影（首部）",
            poster="https://picsum.photos/seed/ed/300/420",
            description=(
                "两个角色在一台怪异而无尽的机器世界里穿行，对这个地方该爱该怕产生分歧。"
                "这是世界上第一部完全使用开源软件制作的电影。"
            ),
            plays=[
                PlayItem("HLS流", "正片", _HLS),
                PlayItem("MP4", "正片", _MP4_ED),
            ],
        ),
    ]

    def fetch_list(self, page: int = 1) -> list[ListItem]:
        if page != 1:
            return []
        return [
            ListItem(title=m.title, detail_url=m.detail_url, poster=m.poster, remarks=m.remarks)
            for m in self._MOVIES
        ]

    def fetch_detail(self, item: ListItem) -> DetailInfo:
        for m in self._MOVIES:
            if m.detail_url == item.detail_url:
                return m
        raise ValueError(f"no movie for {item.detail_url}")
