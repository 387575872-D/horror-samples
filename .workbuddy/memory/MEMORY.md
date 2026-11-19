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

## 协作仓库的约定（Bao 端定的，2026-11-19 已全部对齐）
- **交接文档放仓库根目录，不放 `docs/`**（`交接-Bao端到LS端-*.md`）。我这边写 `交接-LS端到Bao端-*.md`，同样放根目录。
- **成片一律 A/B 双份**：原片 hash 不许改，混音重制版加 `_sfx` 后缀，两份都入库。五个样片现已俱全。
- **过程产物不入库**：`other-films/*/audio.wav`、`audio_sfx.wav`、`frames/`、`edge-profile*/`、
  `check_* / final_* / zoom_*.png` 全走 `.gitignore`。只留成片、`contact_sheet.png`、源码。
- 素材统一进 `assets/` 子目录（`bg` `portraits` `cards` `icons` `overlays` `sfx` `avatars` `frames`）
  并在 `assets/manifest.json` 登记；**`source`/`license` 字段一个字都不能改**（Mixkit 许可已核实）。
- 混音 profile 名：`python_ep01` `html_ep1..ep4` `elevator` `utility` `wechat` `dispatch` `router`。
  响度基准：mean ≈ −32dB、max ≈ −9~−11dB。
- **⚠️ 血的教训**：发布脚本曾用本地版本静默覆盖 Bao 在 `b83b2cd` 改好的 `audio.py`/`make_video.py`
  （`--sfx` 支持丢失、绝对路径复活）。已恢复，且脚本现在「仓库版本与本地不同就保留仓库版本并打印 `[keep]`」，
  要覆盖必须显式 `--force`。
- `tools/mix_sfx.py` 的 `--ffmpeg` 已加回退：PATH 没有 ffmpeg 时自动用 imageio-ffmpeg。

## 素材生成（`assets/`）
- 图像素材链路：**ImageGen 出原图（右下角带「AI生成 WORKBUD>」水印）→ `tools/make_assets.py` 裁 80px 水印
  → 按清单规格 cover 裁切/缩放 → 落 `assets/` → 在 `assets/manifest.json` 的 `images` 数组登记**。
  AI 原图带水印不入库（放工作区 `gen_assets/`，已 gitignore），只入库成品。
- 程序化素材（飘雪 / 颗粒 / 图标）用固定随机种子，重跑同一张，比 AI 生成更干净可控。
- **本机装 Pillow 要走腾讯云镜像**（`https://mirrors.cloud.tencent.com/pypi/simple`）：
  阿里云镜像每次都断在 IncompleteRead 同一字节，清华源直接取不到包。
- 做不出来的：真实感音效。程序化合成和 `render_story.py` 里 numpy 那套同档次，必须靠真实 CC0 素材。


## 视频样片制作（dispatch_horror）
- 目录：`dispatch_horror/`。成片 `dispatch_horror_20s.mp4`；可编辑源 `render.html`（改文案/配色/时间轴）、`audio.py`（改音效）、`capture.mjs` + `make_video.py`（重渲染导出）。
- 渲染链路已验证可用：Edge headless + CDP 截图 → PNG 序列 → imageio-ffmpeg 内置 ffmpeg 编码。本机无系统 ffmpeg，用 `python -m pip install imageio-ffmpeg` 解决。
- **必须**给每次 headless 渲染分配唯一 user-data-dir、唯一调试端口和 URL 版本号，否则会连到残留标签页、加载到旧 HTML，出现「改了代码但画面不变」的假象。
- Node 侧批量删除超过 50 个文件会触发 safe-delete 守卫；逐帧输出直接覆盖同名文件即可。
