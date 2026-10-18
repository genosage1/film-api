# 免费部署指南（GitHub Pages + Actions）

不用买服务器，完全免费，自动定时更新。

## 第一步：注册 GitHub 账号

1. 打开 https://github.com/signup
2. 用邮箱注册，验证邮箱
3. 登录进去

## 第二步：创建新仓库

1. 点右上角 **+** → **New repository**
2. 仓库名填：`film-api`（随便起，英文）
3. 选 **Public**（公开，免费层必须公开）
4. 不要勾选 "Add a README file"
5. 点 **Create repository**

创建后页面会显示一堆 git 命令，先放着不管。

## 第三步：把代码传到 GitHub

在你电脑上打开 PowerShell，进入项目目录：

```powershell
cd "C:\Users\lenovo\Doubao\chats\2026-10-18\new-chat-1\film_api"
```

依次执行（把下面 `你的用户名` 换成你的 GitHub 用户名）：

```powershell
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/你的用户名/film-api.git
git push -u origin main
```

第一次 push 会弹浏览器让你登录 GitHub，授权就行。

## 第四步：开启 GitHub Pages

1. 进入你的仓库页面
2. 点 **Settings**（顶部标签栏）
3. 左边菜单找 **Pages**
4. 在 "Build and deployment" 下：
   - Source 选 **Deploy from a branch**
   - Branch 选 **main**，文件夹选 **/ (root)**
   - 点 **Save**
5. 等 1 分钟，刷新页面，顶部会出现你的网站地址：
   `https://你的用户名.github.io/film-api/`

## 第五步：触发第一次采集

1. 回到仓库主页，点 **Actions** 标签
2. 左边选 "定时采集并更新 aa.json"
3. 右边点 **Run workflow** 按钮 → 再点 **Run workflow**
4. 等 1-2 分钟，绿色勾就是成功了

## 第六步：拿到你的接口地址

采集完成后，你的 `aa.json` 地址就是：

```
https://你的用户名.github.io/film-api/static/aa.json
```

把这个地址填到你的影视 APP 里，就能拉到你的片单了。

---

## 后续更新

- 每 6 小时 GitHub Actions 会自动跑一次采集，更新片单
- 你也可以随时去 Actions 页面手动点 "Run workflow" 立刻更新
- 想加新的影视源，改 `app/spiders/remote_source.py` 里的 `REMOTE_SOURCES`，push 上去就行

## 注意

- 免费版仓库必须是 Public（公开的）
- GitHub Actions 每月有免费额度（2000 分钟），你这个每天跑 4 次，一次 1 分钟，完全用不完
- 国内访问 GitHub Pages 可能偶尔慢，但基本能用
