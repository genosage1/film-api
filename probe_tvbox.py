import httpx
from collections import Counter

urls = [
    "https://github.moeyy.xyz/https://raw.githubusercontent.com/maoystv/6/main/000.json",
    "https://ztha.top/TVBox/thdjk.json",
    "https://chuanshuo.77blog.cn/tv.json",
    "http://cdn.qiaoji8.com/tvbox.json",
]
headers = {"User-Agent": "Mozilla/5.0"}
for u in urls:
    try:
        r = httpx.get(u, timeout=15, follow_redirects=True, headers=headers)
        print(f"[{r.status_code}] {u}  len={len(r.text)}")
        if r.status_code != 200:
            continue
        j = r.json()
        sites = j.get("sites", [])
        print(f"  sites数: {len(sites)}")
        for s in sites[:5]:
            print(f"  - name={s.get('name')}  type={s.get('type')}  api={str(s.get('api'))[:90]}")
        c = Counter(s.get("type") for s in sites)
        print(f"  type分布: {dict(c)}")
        # type=1 是苹果CMS标准API，挑几个看api
        type1 = [s for s in sites if s.get("type") == 1 and str(s.get("api", "")).startswith("http")]
        print(f"  type=1(http api) 数: {len(type1)}")
        for s in type1[:5]:
            print(f"    * {s.get('name')}: {s.get('api')}")
        break
    except Exception as e:
        print(f"[ERR] {u}: {e}")
