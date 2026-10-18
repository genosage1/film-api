import httpx

# 测 ac=videolist 拿带播放地址的数据
test_urls = [
    "https://hhzyapi.com/api.php/provide/vod/?ac=videolist&pg=1",
    "https://bfzyapi.com/api.php/provide/vod/?ac=videolist&pg=1",
    "https://jszyapi.com/api.php/provide/vod/?ac=videolist&pg=1",
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
                print(f"  片名: {s.get('vod_name')}")
                print(f"  有vod_play_url: {'vod_play_url' in s}")
                if s.get("vod_play_url"):
                    print(f"  播放串前100字: {s['vod_play_url'][:100]}")
        print()
    except Exception as e:
        print(f"[ERR] {u}: {e}\n")
