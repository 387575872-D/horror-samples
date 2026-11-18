import math, random, wave, struct

SR = 44100
DUR = 52.0
N = int(SR * DUR)
random.seed(1017)
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

def buzz(start, dur=0.5, amp=0.10):
    s = int(start * SR); n = int(dur * SR)
    for k in range(n):
        p = k / n
        gate = 1.0 if (int(p * 24) % 2) == 0 else 0.35
        add(s + k, amp * gate * math.sin(2 * math.pi * 160 * k / SR) * (1 - p * 0.2))

def pop(start, f=1150, amp=0.07):
    tone(start, 0.045, f, amp, 9)
    tone(start + 0.005, 0.03, f * 1.6, amp * 0.5, 12)

def shutter(start):
    tone(start, 0.03, 2600, 0.10, 14, 'square')
    tone(start + 0.07, 0.04, 1900, 0.08, 12, 'square')

# 房间底噪：极低 + 电流
for k in range(N):
    t = k / SR
    add(k, 0.006 * math.sin(2 * math.pi * 49 * t) + 0.0025 * random.uniform(-1, 1))

TEXTS = [1.2, 2.4, 4.4, 5.4, 6.6, 7.8, 12.4, 16.8, 17.8, 19.8, 20.8, 23.0, 24.0, 32.2, 35.0, 36.0, 36.8, 39.6, 40.6, 48.6]
SYS = [3.4, 33.0, 47.8]
PHOTOS = [11.2, 18.8, 34.0, 41.6]

for t in TEXTS:
    pop(t, 1150 + random.randint(-60, 60))
    buzz(t + 0.02, 0.28, 0.045)
for t in SYS:
    pop(t, 720, 0.05)
    buzz(t + 0.02, 0.3, 0.05)
for t in PHOTOS:
    pop(t, 980, 0.06)
    buzz(t + 0.02, 0.45, 0.07)
    noise(t + 0.02, 0.12, 0.02, 8)

shutter(13.4)
shutter(42.4)

# 语音播放：底噪渐起，然后失败
noise(28.4, 2.6, 0.02, 0.4, 0.25)
tone(28.4, 0.12, 520, 0.05, 5)
tone(31.4, 0.14, 620, 0.08, 4, 'square')
tone(31.62, 0.14, 440, 0.08, 4, 'square')

# 毛刺点
for t in [36.8, 42.4, 47.8]:
    noise(t, 0.16, 0.05, 6, 0.8)

# 结尾
tone(50.0, 1.2, 46, 0.28, 2.0)
tone(50.0, 0.7, 92, 0.10, 3.0)
tone(51.2, 0.5, 1200, 0.05, 6)

out = []
for k, v in enumerate(buf):
    t = k / SR
    fade = min(1.0, t / 0.10, (DUR - t) / 0.15)
    v = math.tanh(v * 1.7) * max(0, fade)
    out.append(int(max(-1, min(1, v)) * 24000))

with wave.open('C:/Users/39288/WorkBuddy/2026-11-17-19-03-56/wechat_horror/audio.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h', x) for x in out))
print('audio.wav written')
