"""测试远程订阅：拉自己导出的 aa.json，验证解析正确"""
from app.spiders.remote_source import RemoteSourceAdapter

adapter = RemoteSourceAdapter(sources=["http://127.0.0.1:8000/aa.json"])
items = adapter.fetch_list()
print(f"从远程接口拉到 {len(items)} 条影片")
for it in items:
    d = adapter.fetch_detail(it)
    print(f"\n● {d.title}  ({d.year} {d.region} {d.type_name})")
    print(f"  评分: {d.score}  备注: {d.remarks}")
    print(f"  播放线路数: {len(set(p.play_from for p in d.plays))}")
    for p in d.plays[:3]:
        print(f"    [{p.play_from}] {p.episode_name} -> {p.play_url[:70]}...")
