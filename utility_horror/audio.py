import math, random, wave, struct

SR = 44100
DUR = 45.0
N = int(SR * DUR)
random.seed(7)
buf = [0.0] * N

def add(i, v):
    if 0 <= i < N:
        buf[i] += v

def tone(start, dur, freq, amp, decay=1.0, kind='sine'):
    s = int(start * SR); n = int(dur * SR)
    for k in range(n):
        env = math.exp(-decay * k / max(n, 1) * 4)
        ph = 2 * math.pi * freq * k / SR
        if kind == 'square':
            v = 1.0 if math.sin(ph) >= 0 else -1.0
        else:
            v = math.sin(ph)
        add(s + k, amp * env * v)

def noise(start, dur, amp, decay=1.0, rate=0.5):
    s = int(start * SR); n = int(dur * SR)
    prev = 0.0
    for k in range(n):
        env = math.exp(-decay * k / max(n, 1) * 4)
        x = random.uniform(-1, 1)
        prev = prev * (1 - rate * 0.1) + x * (rate * 0.1)
        add(s + k, amp * env * prev)

def drip(start, amp=0.10, pitch=1900):
    # 主滴 + 两次回声
    for j, dl in enumerate([0.0, 0.19, 0.37]):
        f = pitch * (1 - 0.18 * j)
        a = amp * (0.55 ** j)
        s = int((start + dl) * SR); n = int(0.06 * SR)
        for k in range(n):
            env = math.exp(-9 * k / n)
            ph = 2 * math.pi * f * k / SR
            vib = 1 + 0.35 * math.sin(2 * math.pi * 220 * k / SR)
            add(s + k, a * env * math.sin(ph * vib))

def pop(start, f=1150, amp=0.06):
    tone(start, 0.045, f, amp, 9)
    tone(start + 0.005, 0.03, f * 1.6, amp * 0.5, 12)

def chime(start):
    tone(start, 0.16, 880, 0.09, 3.2)
    tone(start + 0.14, 0.20, 660, 0.08, 2.8)

def shutter(start):
    tone(start, 0.03, 2600, 0.09, 14, 'square')
    tone(start + 0.07, 0.04, 1900, 0.07, 12, 'square')

def slide(start):
    noise(start, 0.30, 0.045, 1.4, 0.8)

# 底噪：老屋水管低鸣 + 房间噪声
for k in range(N):
    t = k / SR
    wob = 0.6 + 0.4 * math.sin(2 * math.pi * 0.23 * t)
    v = 0.012 * math.sin(2 * math.pi * 88 * t) * wob
    v += 0.012 * math.sin(2 * math.pi * 132 * t) * wob
    v += 0.003 * random.uniform(-1, 1)
    add(k, v)

# 滴水：前半段稀疏，后半段越来越密
drip_times = []
t = 1.4
gap = 2.2
while t < 42.0:
    drip_times.append(t)
    drip(t, amp=0.09 + 0.004 * t, pitch=1900 + random.randint(-140, 140))
    gap = max(0.55, gap * 0.94)
    t += gap + random.uniform(0, 0.4)
# 结尾：滴水突然停止，最后一滴在黑屏里
drip(43.6, amp=0.12, pitch=1700)

# 锁屏 / 通知
chime(0.95)
chime(2.35)
slide(3.25)
pop(3.3, 900, 0.05)

# 工单照片
shutter(10.85); pop(10.8, 980, 0.05)
shutter(13.45); pop(13.4, 980, 0.05)
pop(16.05, 760, 0.05)

# 客服消息
for t in [19.4, 20.6, 21.8, 23.0, 24.4, 25.6, 26.8]:
    pop(t, 1150 + random.randint(-50, 50))
    buzz_t = t
    # 手机震动
    s = int(buzz_t * SR)
    for k in range(int(0.24 * SR)):
        gate = 1.0 if (int(k / SR * 24) % 2) == 0 else 0.3
        add(s + k, 0.035 * gate * math.sin(2 * math.pi * 160 * k / SR))

# 毛刺 / 关键句
for t in [23.0, 31.5, 34.8, 42.5]:
    noise(t, 0.15, 0.05, 6, 0.85)

# 复核照片推送
chime(27.3); slide(27.25)
shutter(28.0)
chime(33.05)

# 最后一卷
chime(34.65); slide(34.6)
noise(35.25, 0.4, 0.02, 1.2, 0.5)   # 楼道环境

# 呼叫
for i in range(4):
    tone(37.75 + i * 0.42, 0.28, 425, 0.055, 2.5)
    tone(37.75 + i * 0.42, 0.28, 445, 0.045, 2.5)
tone(39.0, 0.2, 320, 0.07, 4, 'square')

# 好友申请
chime(39.65)

# 锁屏 2
chime(40.95); chime(41.75); chime(42.55)

# 结尾低频
tone(43.0, 1.3, 46, 0.28, 2.0)
tone(43.0, 0.7, 92, 0.10, 3.0)

out = []
for k, v in enumerate(buf):
    t = k / SR
    fade = min(1.0, t / 0.10, (DUR - t) / 0.15)
    v = math.tanh(v * 1.7) * max(0, fade)
    out.append(int(max(-1, min(1, v)) * 24000))

with wave.open('C:/Users/39288/WorkBuddy/2026-11-17-19-03-56/utility_horror/audio.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h', x) for x in out))
print('audio.wav written')
