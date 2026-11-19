# 项目长期笔记

## GitHub 同步（两个仓库，用途不同）

### 1) 协作仓库 = 成片默认去处（2026-11-19 用户要求「以后视频传到这」）
- `https://github.com/Bao114514/phone-chat-horror`（branch `main`，本地克隆在 `_repo_phonechat/`）。
- 发布命令：`python publish_video.py <项目目录> "<片名>" --merge`
  → 复制到 `other-films/<slug>/`、建 `LS_<日期>_<slug>` 分支、推送、开 PR、合并。
  脚本幂等：内容没变会打印 `[skip]` 直接退出，不会造空 PR。
- 入库文件集：`render.html` `audio.py` `audio.wav` `photos.js` `prep_photos.py` `make_video.py`
  `contact_sheet.png` `*.mp4` `photos/*.jpg`。照片的原始 `.png`（带 AI 水印）不入库。
- 仓库自身 `.gitignore` 忽略了 `*.wav`，所以脚本用 `git add -f` 强制加入。
- 该仓库 `other-films/` 下已有 5 个样片：dispatch / elevator / utility / wechat / router，均含 mp4+总览图。
- 注意：仓库里部分样片还多一个 `*_sfx.mp4`（Bao 端做的音效版），我这边只产出主成片。

### 2) 个人镜像仓库 = 本地备份
- `origin https://github.com/387575872-D/horror-samples.git`，主分支 `LS_main`（本机 hook 要求分支名 `LS_` 开头）。
- 一键同步：`bash sync_github.sh "提交说明"`。
- `.gitignore` 已排除 `*/frames/`、`*/edge-profile*/`、`*.wav`、`*/photos/*.png`；成片 mp4 和压缩后的 jpg 会入库。


## 视频样片制作（dispatch_horror）
- 目录：`dispatch_horror/`。成片 `dispatch_horror_20s.mp4`；可编辑源 `render.html`（改文案/配色/时间轴）、`audio.py`（改音效）、`capture.mjs` + `make_video.py`（重渲染导出）。
- 渲染链路已验证可用：Edge headless + CDP 截图 → PNG 序列 → imageio-ffmpeg 内置 ffmpeg 编码。本机无系统 ffmpeg，用 `python -m pip install imageio-ffmpeg` 解决。
- **必须**给每次 headless 渲染分配唯一 user-data-dir、唯一调试端口和 URL 版本号，否则会连到残留标签页、加载到旧 HTML，出现「改了代码但画面不变」的假象。
- Node 侧批量删除超过 50 个文件会触发 safe-delete 守卫；逐帧输出直接覆盖同名文件即可。
