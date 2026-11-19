#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《在线设备》45s：默认保持原流程；--sfx 基于原成片生成 A/B 混音版。"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
MIXER = ROOT / "tools" / "mix_sfx.py"
ORIGINAL = "router_45s.mp4"
DURATION = 45.0
PROFILE = "router"
CRF = "19"


def ffmpeg_exe():
    p = shutil.which("ffmpeg")
    if p:
        return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sfx", action="store_true", help="生成 A/B 混音版，不覆盖原成片")
    ap.add_argument("--sfx-profile", default=PROFILE)
    args = ap.parse_args()

    audio = HERE / "audio.wav"
    if not audio.exists():
        raise SystemExit(f"找不到 {audio}，请先运行 audio.py")

    play_audio = audio
    if args.sfx:
        mixed = HERE / "audio_sfx.wav"
        subprocess.run([
            sys.executable, str(MIXER),
            "--base", str(audio), "--out", str(mixed),
            "--profile", args.sfx_profile, "--duration", str(DURATION),
        ], check=True)
        play_audio = mixed

    ff = ffmpeg_exe()
    frames = HERE / "frames"
    has_frames = frames.exists() and any(frames.glob("*.png"))
    if has_frames:
        cmd = [ff, "-y", "-loglevel", "error", "-framerate", "20",
               "-i", str(frames / "%04d.png")]
    else:
        if not args.sfx:
            raise SystemExit("逐帧 PNG 未入库；请用 --sfx 基于原成片生成 A/B 版")
        src = HERE / ORIGINAL
        if not src.exists():
            raise SystemExit(f"找不到原成片：{src}")
        cmd = [ff, "-y", "-loglevel", "error", "-i", str(src)]

    cmd += ["-i", str(play_audio), "-map", "0:v:0", "-map", "1:a:0"]
    if has_frames:
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", CRF,
                "-pix_fmt", "yuv420p"]
    else:
        cmd += ["-c:v", "copy"]

    out_name = ORIGINAL[:-4] + "_sfx.mp4" if args.sfx else ORIGINAL
    out = HERE / out_name
    cmd += ["-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print(f"video written: {out}")


if __name__ == "__main__":
    main()
