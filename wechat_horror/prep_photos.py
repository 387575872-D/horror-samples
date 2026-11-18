import subprocess, os, base64, json
import imageio_ffmpeg

ROOT = 'C:/Users/39288/WorkBuddy/2026-11-17-19-03-56/wechat_horror'
PH = os.path.join(ROOT, 'photos')
ff = imageio_ffmpeg.get_ffmpeg_exe()

FAMILY = os.path.join(PH, '旧家庭合影_2000年代中国三口之家在公园合影_母亲短发微笑_2026-11-17T14-04-34.png')
KITCHEN = os.path.join(PH, '真实手机随手拍_夜晚的中国家庭厨房和小餐桌_桌上两碗热汤面__2026-11-17T14-03-36.png')
LIVING = os.path.join(PH, '真实手机闪光灯照片_夜晚昏暗的客厅_老式电视机闪着雪花屏_一_2026-11-17T14-03-51.png')
DOORWAY = os.path.join(PH, '真实手机照片_从卧室内部看向黑暗的走廊_房门半开_走廊尽头有_2026-11-17T14-04-06.png')
BEHIND = os.path.join(PH, '参考照片里这位母亲的外貌_短发_中年_穿着朴素__生成一张真_2026-11-17T14-06-00.png')

JOBS = [
    # (src, out, vf)
    (FAMILY,  'family.jpg',    'crop=1024:944:0:0,scale=720:664'),
    (FAMILY,  'avatar_mom.jpg','crop=290:290:195:250,scale=256:256'),
    (FAMILY,  'avatar_me.jpg', 'crop=300:300:395:330,scale=256:256'),
    (KITCHEN, 'kitchen.jpg',   'crop=1024:944:0:0,scale=720:664'),
    (LIVING,  'living.jpg',    'crop=1024:944:0:0,scale=720:664'),
    (DOORWAY, 'doorway.jpg',   'crop=1024:1456:0:0,scale=720:1024'),
    (BEHIND,  'behind.jpg',    'crop=1024:1456:0:0,scale=720:1024'),
]
for src, out, vf in JOBS:
    dst = os.path.join(PH, out)
    cmd = [ff, '-y', '-i', src, '-vf', vf, '-q:v', '4', dst]
    subprocess.run(cmd, check=True, capture_output=True)
    print('ok', out)

photos = {}
for _, out, _ in JOBS:
    with open(os.path.join(PH, out), 'rb') as f:
        photos[out.split('.')[0]] = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()

with open(os.path.join(ROOT, 'photos.js'), 'w', encoding='utf-8') as f:
    f.write('window.PHOTOS=' + json.dumps(photos) + ';')
print('photos.js written')
