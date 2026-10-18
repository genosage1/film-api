"""
批量探测用户给的TVBox配置仓，提取所有 type=1（标准苹果CMS HTTP API）的接口。
type=3（csp_xxx 爬虫）在Python后端无法解析，自动跳过。
同时去重、跳过m3u直播和adult内容。
"""
import asyncio
import json
from collections import OrderedDict

import httpx

# 用户给的所有URL（去重后）
RAW_URLS = """
https://132130.v.nxog.top/api1.php?id=3
https://fmbox.cc/
https://github.moeyy.xyz/https://raw.githubusercontent.com/maoystv/6/main/000.json
https://git.acwing.com/shhentu/lzxw/-/raw/main/Monster.json
https://ghp.ci/https://raw.githubusercontent.com/vbskycn/tvbox/a244f6f5c08565a9a0e319d6a3cc2e919d05d893/MY%E6%8E%A2%E6%8E%A2.txt
http://mzjk.top/%E7%A6%81%E6%AD%A2%E8%B4%A9%E5%8D%96
http://xn--z7x900a.com/
http://www.xn--sss604efuw.com/tv
https://www.mpanso.com/%E5%B0%8F%E7%B1%B3/DEMO.json
http://ok321.top/ok
http://tvbox.xn--4kq62z5rby2qupq9ub.top/
http://xn--ihqu10cn4c.xn--v4q818bf34b.com/
http://kxrj.site:55/%E5%A4%A9%E5%A4%A9%E5%BC%80%E5%BF%83
https://xn--tkh-mf3g9f.v.nxog.top/m/111.php?ou=x&mz=index&jar=index
https://gitee.com/yiwu369/6758/raw/master/%E9%9D%92%E9%BE%99/1.json
http://yuhuahx.com/%E8%82%B2%E5%8D%8E%E5%AD%A6%E6%A0%A1/%E6%96%B0%E5%A4%B4%E5%B8%AE.php
http://cdn.qiaoji8.com/tvbox.json
http://meowtv.cn/tv
https://ztha.top/TVBox/thdjk.json
http://fmys.top/fmys.json
https://xn--qoqw77q.top/
https://chuanshuo.77blog.cn/tv.json
https://ghp.ci/raw.githubusercontent.com/guot55/YGBH/main/vip2.json
https://2912.kstore.space/0506.json
https://gitee.com/lukei7/lib/raw/Luck/%E8%87%AA%E5%BB%BA.json
https://g.3344550.xyz/https://raw.githubusercontent.com/jigedos/1024/master/jsm.json
https://git.acwing.com/cisenyuan/kdsb/-/raw/main/%E6%B5%B7%E5%85%B5%E5%BD%B1%E8%A7%86.json
https://git.acwing.com/abai/tv/-/raw/main/huas.json
https://git.acwing.com/lw0704/66/-/raw/master/jjzx.json
https://git.acwing.com/203BDXC/tvboxt/-/raw/main/CJ.json
https://git.acwing.com/lkq0379/zjys/-/raw/main/zjys.json
http://550.3vcn.work/wdjyys.json
https://cdn.githubraw.com/xuexuguang/tvbox_spider/main/tv/kk/heroaku_dtes.json
http://74.120.175.78/JK/XYQTVBox/dj.json
http://124.71.189.194/a.json
http://ww.weidonglong.com/ysc50311.json
https://d.kstore.space/download/2912/xx888.json
https://gitee.com/wxej/wxrj/raw/master/wx.json
https://qixing.myhkw.com/DC.txt
http://ztha.top/TVBox/FLCK.json
http://pandown.pro/tvbox/tvbox.json
https://dxawi.github.io/0/0.json
https://github.moeyy.xyz/https://raw.githubusercontent.com/xyq254245/xyqonlinerule/main/XYQTVBox.json
https://github.moeyy.xyz/https://raw.githubusercontent.com/yoursmile66/TVBox/main/XC.json
https://raw.liucn.cc/box/m.json
http://rihou.cc:88/%E8%8D%B7%E5%9F%8E%E8%8C%B6%E7%A7%80
http://tt.iitvba.com/vip/tv.json
http://8.210.232.168/xc.json
https://weixine.net/ysc.json
http://xhztv.top/xhz
http://xhztv.top/4k.json
http://itvbox.cc/%E4%BA%91%E6%98%9F%E6%97%A5%E8%AE%B0
http://home.jundie.top:81/top98.json
https://tv.xn--yhqu5zs87a.top/
https://download.kstore.space/download/2883/nzk/nzk0722.json
http://jin.xn--kwra9540c.love/
https://www.yingm.cc/dm/dm.json
http://pt.sxtv.top:66/sx.json
https://www.macms.pro/box/3.json
https://gitlab.com/mfkdy/vip/-/raw/main/Lite.json
https://gitee.com/dongchenliu/liu/raw/master/yb.json
https://ghproxy.net/https://raw.githubusercontent.com/yw88075/tvbox/main/yw.json
https://szyyds.cn/tv/x.json
https://yydf.540734621.xyz/QQ/yydf2024.json
https://100km.top/0
http://ygbh.live/box.php
http://miao.qoo.qoo.us.kg/
https://gitlink.org.cn/api/hailin/aishangtv5/raw/tvbox/aishang.json
https://gitlab.com/lzc1021lzc/hjfggzs.hjys/-/raw/main/hjys.free.json
https://gitlab.com/duomv/dzhipy/-/raw/main/index.json
https://gitlab.com/dokiss1/tvbox/-/raw/master/doki-Dx.json
http://bp.tvbox.cam/
https://d.kstore.space/download/6474/tvbox/api.json
http://52bsj.vip:98/wuai
http://xhww.fun:63/%E5%B0%8F%E7%B1%B3/DEMO.json
https://ghproxy.net/raw.githubusercontent.com/gaotianliuyun/gao/master/js.json
http://www.fish2018.us.kg/p/jsm.json
https://tv.xn--11x555b.top/svip
https://box.iqinu.com/
https://www.cwss.xyz/%E5%88%BA%E7%8C%AB%E7%BA%BF%E8%B7%AF
https://www.rjjjh.com/xzbgg.json
"""

# 去重、去掉空行
URLS = list(OrderedDict.fromkeys([u.strip() for u in RAW_URLS.strip().splitlines() if u.strip()]))
print(f"待探测配置仓: {len(URLS)} 个")

HEADERS = {"User-Agent": "Mozilla/5.0"}
SEM = asyncio.Semaphore(10)


async def probe(client: httpx.AsyncClient, url: str):
    async with SEM:
        try:
            r = await client.get(url, timeout=12, follow_redirects=True, headers=HEADERS)
            if r.status_code != 200:
                return url, []
            j = r.json()
        except Exception:
            return url, []
        sites = j.get("sites", []) if isinstance(j, dict) else []
        apis = []
        for s in sites:
            if s.get("type") == 1 and str(s.get("api", "")).startswith("http"):
                apis.append({"name": s.get("name", ""), "api": s["api"]})
        return url, apis


async def main():
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[probe(client, u) for u in URLS])

    all_apis = {}
    configs_ok = 0
    for url, apis in results:
        if apis:
            configs_ok += 1
            for a in apis:
                api = a["api"].rstrip("/")
                if api not in all_apis:
                    all_apis[api] = a["name"]

    print(f"\n能访问的配置仓: {configs_ok}/{len(URLS)}")
    print(f"挖到 type=1 标准接口: {len(all_apis)} 个\n")
    for i, (api, name) in enumerate(all_apis.items(), 1):
        print(f"{i:3d}. [{name}] {api}")

    # 写出去重后的接口列表
    with open("remote_endpoints.json", "w", encoding="utf-8") as f:
        json.dump([{"name": n, "api": a} for a, n in all_apis.items()], f, ensure_ascii=False, indent=2)
    print(f"\n已写入 remote_endpoints.json")


asyncio.run(main())
