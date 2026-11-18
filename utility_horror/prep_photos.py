import subprocess, os, base64, json
import imageio_ffmpeg

ROOT = 'C:/Users/39288/WorkBuddy/2026-11-17-19-03-56/utility_horror'
PH = os.path.join(ROOT, 'photos')
ff = imageio_ffmpeg.get_ffmpeg_exe()

HOUSE  = os.path.join(PH, '真实手机照片_南方农村夜晚的老式自建房外观_白色瓷砖墙面有些_2026-11-18T02-38-28.png')
METER  = os.path.join(PH, '真实手机特写照片_墙角水泥台上的老式机械水表_玻璃表盘内侧起_2026-11-18T02-38-44.png')
SELFIE = os.path.join(PH, '真实手机前置摄像头自拍_一个二十多岁的中国男人穿灰色工作反光_2026-11-18T02-39-01.png')
BOWLS  = os.path.join(PH, '真实手机照片_昏暗的中国老屋堂屋_正中一张老式八仙木桌_桌上_2026-11-18T02-39-18.png')
DOOR   = os.path.join(PH, '真实手机照片_现代城市公寓楼道里拍摄的深色防盗门特写_门上贴_2026-11-18T02-39-37.png')

JOBS = [
    (HOUSE,  'house.jpg',  'crop=1536:934:0:0,scale=900:546'),
    (METER,  'meter.jpg',  'crop=1024:934:0:0,scale=640:584'),
    (SELFIE, 'selfie.jpg', 'crop=1024:934:0:0,scale=640:584'),
    (BOWLS,  'bowls.jpg',  'crop=1024:934:0:0,scale=640:584'),
    (DOOR,   'door.jpg',   'crop=1024:1446:0:0,scale=640:904'),
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
