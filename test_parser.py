"""
离线验证 maccms_adapter 的解析逻辑：
用一段模拟的苹果CMS HTML，验证列表选择器、player_aaaa 提取、播放串拆分是否正确。
运行：python test_parser.py
"""
from app.spiders.maccms_adapter import MacCMSAdapter

# 1) 模拟 player_aaaa 形态（单集/单线路）
html_A = '''
<html><body>
<script>var player_aaaa = {"url":"https://cdn.example.com/movie/1.m3u8","name":"正片","from":"线路1"};</script>
</body></html>
'''

# 2) 模拟已拼接好的播放串（多线路多集）
play_str = "线路1$$$第01集$https://a.com/1.m3u8#第02集$https://a.com/2.m3u8$$$线路2$$$第01集$https://b.com/1.m3u8"

# 3) 模拟列表页片段
list_html = '''
<html><body>
<ul class="stui-vodlist">
  <li><a href="/voddetail/101.html" title="测试影片A"><img data-original="/pic/a.jpg"></a></li>
  <li><a href="/voddetail/102.html" title="测试影片B"><img data-original="/pic/b.jpg"></a></li>
</ul>
</body></html>
'''

from bs4 import BeautifulSoup

print("=== 测试A: player_aaaa 提取 ===")
adapter = MacCMSAdapter.__new__(MacCMSAdapter)  # 不触发 __init__（不建httpx client）
plays = adapter._parse_plays(html_A, BeautifulSoup(html_A, "html.parser"))
for p in plays:
    print(f"  [{p.play_from}] {p.episode_name} -> {p.play_url}")
assert plays and "1.m3u8" in plays[0].play_url, "A失败"

print("\n=== 测试B: 播放串拆分 ===")
plays2 = MacCMSAdapter._split_play_string(play_str)
for p in plays2:
    print(f"  [{p.play_from}] {p.episode_name} -> {p.play_url}")
assert len(plays2) == 3, f"B失败，期望3条，实际{len(plays2)}"

print("\n=== 测试C: 列表页选择器 ===")
soup = BeautifulSoup(list_html, "html.parser")
links = soup.select("ul.stui-vodlist li a")
for a in links:
    print(f"  title={a.get('title')}  href={a.get('href')}")
assert len(links) == 2, "C失败"

print("\n全部通过 ✓")
