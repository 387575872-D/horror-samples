import subprocess, os
import imageio_ffmpeg

ROOT = 'C:/Users/39288/WorkBuddy/2026-11-17-19-03-56/router_horror'
ff = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [
    ff, '-y',
    '-framerate', '20', '-i', os.path.join(ROOT, 'frames', '%04d.png'),
    '-i', os.path.join(ROOT, 'audio.wav'),
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '128k', '-shortest',
    '-movflags', '+faststart',
    os.path.join(ROOT, 'router_45s.mp4')
]
subprocess.run(cmd, check=True)
print('video written:', os.path.join(ROOT, 'router_45s.mp4'))
