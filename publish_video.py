#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把一个样片目录发布到协作仓库 Bao114514/phone-chat-horror。

用法：
    python publish_video.py router_horror "在线设备"
    python publish_video.py router_horror "在线设备" --merge

默认：推到 other-films/<slug> 的 LS_ 分支并开 PR（不自动合并）。
--merge：PR 创建后直接合并进 main。
--force：仓库里已有同名但内容不同的文件时也覆盖（默认保留仓库版本）。
重复运行是安全的——没有文件变化时直接退出，不会产生空 PR。

入库内容遵守仓库约定：成片 mp4、contact_sheet、源码入；audio.wav / audio_sfx.wav
（过程音轨）和 check_* / final_* / zoom_*（QA 截图）不入。
"""
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import time
import urllib.request
from datetime import date

OWNER = "Bao114514"
REPO = "phone-chat-horror"
ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, "_repo_phonechat")
URL = f"https://github.com/{OWNER}/{REPO}.git"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
# 本机 git 走 OpenSSL 取不到根证书，网络相关命令统一强制 schannel 并关吊销检查
GIT_SAFE = ["-c", "http.sslBackend=schannel", "-c", "http.schannelCheckRevoke=false"]

# audio.wav / audio_sfx.wav 是过程音轨，仓库 .gitignore 明确排除，不要入库
FILES = ["render.html", "audio.py", "photos.js", "prep_photos.py",
         "make_video.py", "contact_sheet.png"]
# 调画面时留下的 QA 截图，不属于素材
SKIP_PREFIX = ("check_", "final_", "zoom_")


def git(*args, cwd=None, capture=False):
    return subprocess.run(["git"] + GIT_SAFE + list(args), cwd=cwd, check=True,
                          text=True, capture_output=capture)


def token():
    p = subprocess.run(["git", "credential", "fill"], text=True,
                       input="protocol=https\nhost=github.com\n\n",
                       capture_output=True)
    for line in p.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    raise RuntimeError("没有取到 GitHub 凭据")


def api(method, path, body=None):
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": "Bearer " + token(),
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json"})
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, context=ctx) as r:
        return json.loads(r.read().decode())


def same_file(a, b):
    return os.path.getsize(a) == os.path.getsize(b) and \
        open(a, "rb").read() == open(b, "rb").read()


def put(src, dst, force):
    """仓库里已有同名且内容不同的文件时保留仓库版本。

    协作仓库里 render.html / audio.py / make_video.py 可能已被对方改过
    （加 --sfx、改掉写死路径等），本地版本盲目覆盖会直接抹掉对方的改动。
    """
    if os.path.isfile(dst) and not force and not same_file(src, dst):
        print(f"[keep] {os.path.basename(dst)} 仓库版本与本地不同，保留仓库版本"
              f"（确认要覆盖就加 --force）")
        return False
    shutil.copy2(src, dst)
    return True


def copy_sample(src, dest, force=False):
    os.makedirs(dest, exist_ok=True)
    for name in FILES:
        p = os.path.join(src, name)
        if os.path.isfile(p):
            put(p, os.path.join(dest, name), force)
    for name in os.listdir(src):
        if name.startswith(SKIP_PREFIX) or name in ("audio.wav", "audio_sfx.wav"):
            continue
        if name.endswith(".mp4"):
            put(os.path.join(src, name), os.path.join(dest, name), force)
    photos = os.path.join(src, "photos")
    if os.path.isdir(photos):
        os.makedirs(os.path.join(dest, "photos"), exist_ok=True)
        for name in os.listdir(photos):
            if name.endswith(".jpg"):
                shutil.copy2(os.path.join(photos, name),
                             os.path.join(dest, "photos"))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    folder = sys.argv[1].rstrip("/\\")
    title = sys.argv[2]
    do_merge = "--merge" in sys.argv
    src = os.path.join(ROOT, folder)
    if not os.path.isfile(os.path.join(src, "render.html")):
        raise SystemExit(f"找不到 {src}/render.html")

    slug = re.sub(r"[_\s]+", "-", folder).lower()
    branch = f"LS_{date.today():%Y%m%d}_{slug}"

    if not os.path.isdir(os.path.join(WORK, ".git")):
        git("clone", "--depth", "1", URL, WORK)
    git("fetch", "origin", "main", cwd=WORK)
    git("checkout", "-f", "main", cwd=WORK)
    git("reset", "--hard", "origin/main", cwd=WORK)
    if branch in git("branch", "--list", branch, cwd=WORK, capture=True).stdout:
        git("branch", "-D", branch, cwd=WORK, capture=True)
    git("checkout", "-b", branch, cwd=WORK)

    dest = os.path.join(WORK, "other-films", slug)
    copy_sample(src, dest, force="--force" in sys.argv)

    git("add", "-A", f"other-films/{slug}", cwd=WORK)
    status = git("status", "--short", cwd=WORK, capture=True).stdout
    if not status.strip():
        print(f"[skip] other-films/{slug} 与 main 一致，没有变更。")
        return
    print(status)
    git("commit", "-m", f"feat: 新增 {slug} 样片《{title}》", cwd=WORK)
    git("push", "-u", "origin", branch, cwd=WORK)

    pr = api("POST", "/pulls", {
        "title": f"feat: 新增 {slug} 样片《{title}》",
        "head": branch, "base": "main",
        "body": f"新增模拟恐怖样片《{title}》。\n\n- 目录：`other-films/{slug}`\n"
                f"- 含 render.html / audio.py / photos.js / 成片 mp4 / 总览图\n"})
    print("PR:", pr["html_url"])
    if do_merge:
        num = pr["number"]
        for _ in range(8):
            if api("GET", f"/pulls/{num}").get("mergeable"):
                break
            time.sleep(2)
        api("PUT", f"/pulls/{num}/merge",
            {"merge_method": "merge",
             "commit_title": f"merge: 合并 {slug} 样片《{title}》"})
        print("已合并到 main")


if __name__ == "__main__":
    main()
