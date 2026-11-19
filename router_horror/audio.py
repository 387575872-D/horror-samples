import math, random, wave, struct

from pathlib import Path
OUT = Path(__file__).resolve().parent / 'audio.wav'

SR = 44100
DUR = 45.0
N = int(SR * DUR)
random.seed(417)
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

def pop(start, f=1150, amp=0.06):
    tone(start, 0.045, f, amp, 9)
    tone(start + 0.005, 0.03, f * 1.6, amp * 0.5, 12)

def chime(start):
    tone(start, 0.16, 880, 0.09, 3.2)
    tone(start + 0.14, 0.20, 660, 0.08, 2.8)

def slide(start):
    noise(start, 0.30, 0.045, 1.4, 0.8)

def sonar(start, f=900, amp=0.10):
    tone(start, 0.22, f, amp, 2.6)
    tone(start, 0.22, f * 0.5, amp * 0.4, 2.6)

def buzz(start, dur=0.4, amp=0.09):
    s = int(start * SR); n = int(dur * SR)
    for k in range(n):
        gate = 1.0 if (int(k / SR * 24) % 2) == 0 else 0.3
        add(s + k, amp * gate * math.sin(2 * math.pi * 160 * k / SR))

def click(start):
    tone(start, 0.03, 2400, 0.09, 14, 'square')

# 底噪：路由器电流 + 房间
for k in range(N):
    t = k / SR
    wob = 0.6 + 0.4 * math.sin(2 * math.pi * 0.31 * t)
    v = 0.011 * math.sin(2 * math.pi * 96 * t) * wob
    v += 0.006 * math.sin(2 * math.pi * 154 * t)
    v += 0.0025 * random.uniform(-1, 1)
    add(k, v)

chime(0.95); chime(2.35); slide(3.25)

# 设备列表逐条上线
for t in [4.0, 4.5, 5.0, 5.5, 6.0]:
    pop(t, 1000 + random.randint(-40, 40), 0.04)
for t in [7.0, 7.8]:
    pop(t, 760, 0.05)
    buzz(t + 0.02, 0.3, 0.05)

slide(10.25)
# 声呐：距离 0.5m，慢
for t in [11.0, 12.0, 13.0]:
    sonar(t, 900, 0.09)
click(14.0)          # 点断开
pop(14.1, 700, 0.05)
# 重连 + 距离缩短，声呐变快变尖
buzz(15.4, 0.5, 0.08)
noise(15.4, 0.15, 0.05, 6, 0.85)
for t in [15.6, 16.0, 16.45, 16.9]:
    sonar(t, 1200, 0.11)

slide(18.05)
# 第二台：同 MAC，声呐极快
for i in range(14):
    t = 19.0 + i * 0.42
    if t > 25.4: break
    sonar(t, 1400 + i * 30, 0.10)
buzz(20.2, 0.35, 0.06)   # MAC 一致警告

slide(26.05)
chime(26.15)
noise(26.5, 6.5, 0.016, 0.15, 0.3)   # 电视雪花底噪
tone(29.0, 0.5, 320, 0.05, 2.0, 'saw')

slide(34.05)
# 拓扑：红点逼近，声呐连成一片
for i in range(10):
    t = 34.8 + i * 0.30
    if t > 37.4: break
    sonar(t, 1500 + i * 40, 0.09)
pop(37.7, 980, 0.05)     # 弹窗
click(39.2)              # 点拒绝
buzz(39.6, 0.5, 0.08)
noise(39.6, 0.15, 0.05, 6, 0.85)

slide(41.05)
chime(41.25); chime(42.05)

# 结尾
tone(43.0, 1.3, 46, 0.28, 2.0)
tone(43.0, 0.7, 92, 0.10, 3.0)
noise(43.0, 0.2, 0.06, 6, 0.8)
sonar(43.8, 1600, 0.12)  # 黑屏里最后一声

out = []
for k, v in enumerate(buf):
    t = k / SR
    fade = min(1.0, t / 0.10, (DUR - t) / 0.15)
    v = math.tanh(v * 1.7) * max(0, fade)
    out.append(int(max(-1, min(1, v)) * 24000))

with wave.open(str(OUT), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h', x) for x in out))
print('audio.wav written')
