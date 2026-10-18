import httpx

# 测几个源的实际返回
test_urls = [
    "https://api.wujinapi.me/api.php/provide/vod/?ac=list",
    "https://hhzyapi.com/api.php/provide/vod/?ac=list",
    "https://api.tiankongapi.com/api.php/provide/vod",
]
headers = {"User-Agent": "Mozilla/5.0"}
for u in test_urls:
    try:
        r = httpx.get(u, timeout=12, follow_redirects=True, headers=headers)
        print(f"[{r.status_code}] {u}")
        if r.status_code == 200:
            j = r.json()
            print(f"  code={j.get('code')}  total={j.get('total')}  list数={len(j.get('list', []))}")
            if j.get("list"):
                s = j["list"][0]
                print(f"  示例: {s.get('vod_name')}  播放字段: {'vod_play_url' in s}")
        print()
    except Exception as e:
        print(f"[ERR] {u}: {e}\n")
