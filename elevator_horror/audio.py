import math, random, wave, struct

SR = 44100
DUR = 60.0
N = int(SR * DUR)
random.seed(20261017)
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
        elif kind == 'saw':
            v = 2 * ((freq * k / SR) % 1.0) - 1.0
        else:
            v = math.sin(ph)
        add(s + k, amp * env * v)

def noise(start, dur, amp, decay=1.0, rate=1.0):
    s = int(start * SR); n = int(dur * SR)
    prev = 0.0
    for k in range(n):
        env = math.exp(-decay * k / max(n, 1) * 4)
        x = random.uniform(-1, 1)
        prev = prev * (1 - rate * 0.08) + x * (rate * 0.08)
        add(s + k, amp * env * prev)

def rumble(start, dur, amp):
    s = int(start * SR); n = int(dur * SR)
    for k in range(n):
        p = k / n
        env = math.sin(math.pi * p) ** 0.6
        f = 46 + 22 * p
        add(s + k, amp * env * math.sin(2 * math.pi * f * k / SR))

# 底噪：极低频压迫 + 空调风
for k in range(N):
    t = k / SR
    am = 0.55 + 0.45 * math.sin(2 * math.pi * 0.07 * t)
    v = 0.024 * math.sin(2 * math.pi * 41 * t) + 0.014 * math.sin(2 * math.pi * 61.5 * t) * am
    v += 0.003 * random.uniform(-1, 1)
    add(k, v)

# 自检提示音
for i, t in enumerate([0.45, 1.25, 2.05, 2.95, 4.15]):
    tone(t, 0.08, 900 + i * 40, 0.08, 7)
    tone(t + 0.05, 0.05, 1800, 0.025, 10)

# 电梯到站：叮咚 + 门机
for i in range(8):
    t = 5.0 + i * 1.0
    tone(t, 0.55, 880, 0.11, 3.0)
    tone(t + 0.22, 0.65, 659, 0.10, 2.6)
    rumble(t + 0.02, 0.42, 0.06)
    noise(t + 0.02, 0.18, 0.02, 6)

# 走廊监控底噪
noise(13.0, 8.0, 0.012, 0.02, 0.35)

# 呼梯记录点击
for i in range(6):
    tone(21.4 + i * 0.8, 0.03, 1500 + i * 60, 0.045, 14, 'square')

# 重量上升：音高逐步抬高
for i in range(17):
    t = 30.0 + i * 0.4
    if t > 36.4: break
    tone(t, 0.06, 280 + i * 34, 0.055, 10, 'square')

# 校准提示
tone(36.8, 0.10, 720, 0.08, 6)
tone(37.0, 0.16, 480, 0.08, 4)

# 轿厢：低频、滴水、呼吸
for k in range(int(37 * SR), int(45 * SR)):
    t = k / SR
    add(k, 0.012 * math.sin(2 * math.pi * 52 * t) * (0.6 + 0.4 * math.sin(2 * math.pi * 0.9 * t)))
for t in [38.2, 39.6, 41.1, 42.7, 44.0]:
    tone(t, 0.09, 1350, 0.05, 12)
    tone(t + 0.02, 0.05, 900, 0.03, 14)
noise(43.3, 1.2, 0.018, 1.2, 0.5)

# 下坠 / 楼层信号异常
rumble(45.0, 6.0, 0.07)
for t in [46.2, 48.1, 50.0, 51.2, 52.1]:
    noise(t, 0.18, 0.06, 5, 0.9)
    tone(t, 0.10, 170, 0.07, 8, 'square')
rumble(51.0, 0.9, 0.09)

# 超载警报
for i in range(9):
    t = 53.0 + i * 0.48
    if t > 57.0: break
    tone(t, 0.20, 780 if i % 2 == 0 else 560, 0.10, 3, 'square')
    tone(t, 0.20, 390 if i % 2 == 0 else 280, 0.05, 3)

# 载重归零：下滑音
tone(56.4, 0.9, 420, 0.08, 2.0, 'saw')
tone(56.4, 0.9, 210, 0.06, 2.0)

# 结尾撞击 + 余响
tone(58.0, 1.3, 48, 0.30, 2.0)
tone(58.0, 0.8, 96, 0.12, 3.0)
noise(58.0, 0.25, 0.08, 6, 0.7)
for k in range(int(58.2 * SR), int(59.8 * SR)):
    t = k / SR
    add(k, 0.008 * math.sin(2 * math.pi * 43 * t) * max(0, 1 - (t - 58.2) / 1.6))

out = []
for k, v in enumerate(buf):
    t = k / SR
    fade = min(1.0, t / 0.10, (DUR - t) / 0.15)
    v = math.tanh(v * 1.7) * max(0, fade)
    out.append(int(max(-1, min(1, v)) * 24000))

with wave.open('C:/Users/39288/WorkBuddy/2026-11-17-19-03-56/elevator_horror/audio.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h', x) for x in out))
print('audio.wav written')
