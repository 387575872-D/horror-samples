import subprocess, os, base64, json
import imageio_ffmpeg

ROOT = 'C:/Users/39288/WorkBuddy/2026-11-17-19-03-56/router_horror'
PH = os.path.join(ROOT, 'photos')
ff = imageio_ffmpeg.get_ffmpeg_exe()

CAST = os.path.join(PH, '真实手机夜间照片_从客厅电视屏幕的位置向前拍_昏暗的客厅_一_2026-11-18T14-30-15.png')
DOOR = os.path.join(PH, '智能门铃猫眼鱼眼镜头拍摄_夜晚居民楼楼道_一个模糊的人影紧贴_2026-11-18T14-30-35.png')

JOBS = [
    (CAST, 'cast.jpg', 'crop=1080:900:0:0,scale=760:634'),
    (DOOR, 'door.jpg',  'crop=1024:934:0:0,scale=640:584'),
]
for src, out, vf in JOBS:
    dst = os.path.join(PH, out)
    subprocess.run([ff, '-y', '-i', src, '-vf', vf, '-q:v', '4', dst], check=True, capture_output=True)
    print('ok', out)

photos = {}
for _, out, _ in JOBS:
    with open(os.path.join(PH, out), 'rb') as f:
        photos[out.split('.')[0]] = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()

with open(os.path.join(ROOT, 'photos.js'), 'w', encoding='utf-8') as f:
    f.write('window.PHOTOS=' + json.dumps(photos) + ';')
print('photos.js written')
