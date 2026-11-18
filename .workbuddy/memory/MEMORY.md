# 项目长期笔记

## GitHub 同步
- 远程：`origin https://github.com/387575872-D/horror-samples.git`，主分支 `LS_main`（本机要求分支名以 `LS_` 开头）。
- 一键同步：`bash sync_github.sh "提交说明"`。默认每次任务收尾执行一次。
- `.gitignore` 已排除 `*/frames/`、`*/edge-profile*/`、`*.wav`、`*/photos/*.png`；成片 mp4 和压缩后的 jpg 会入库。


## 视频样片制作（dispatch_horror）
- 目录：`dispatch_horror/`。成片 `dispatch_horror_20s.mp4`；可编辑源 `render.html`（改文案/配色/时间轴）、`audio.py`（改音效）、`capture.mjs` + `make_video.py`（重渲染导出）。
- 渲染链路已验证可用：Edge headless + CDP 截图 → PNG 序列 → imageio-ffmpeg 内置 ffmpeg 编码。本机无系统 ffmpeg，用 `python -m pip install imageio-ffmpeg` 解决。
- **必须**给每次 headless 渲染分配唯一 user-data-dir、唯一调试端口和 URL 版本号，否则会连到残留标签页、加载到旧 HTML，出现「改了代码但画面不变」的假象。
- Node 侧批量删除超过 50 个文件会触发 safe-delete 守卫；逐帧输出直接覆盖同名文件即可。
