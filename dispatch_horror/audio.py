import math, random, wave, struct

SR = 44100
DUR = 20.0
N = int(SR * DUR)
random.seed(917)

buf = [0.0] * N

def add(i, v):
    if 0 <= i < N:
        buf[i] += v

def tone(start, dur, freq, amp, decay=1.0, kind='sine'):
    s = int(start * SR)
    n = int(dur * SR)
    for k in range(n):
        env = math.exp(-decay * k / max(n, 1) * 4)
        ph = 2 * math.pi * freq * k / SR
        if kind == 'square':
            v = 1.0 if math.sin(ph) >= 0 else -1.0
        elif kind == 'noise':
            v = random.uniform(-1, 1)
        else:
            v = math.sin(ph)
        add(s + k, amp * env * v)

# 基础低频压迫感
for k in range(N):
    t = k / SR
    am = 0.5 + 0.5 * math.sin(2 * math.pi * 0.13 * t)
    v = 0.030 * math.sin(2 * math.pi * 48 * t) + 0.018 * math.sin(2 * math.pi * 72.5 * t) * am
    add(k, v)

# 启动自检：短促电子音
for i, t in enumerate([0.35, 0.85, 1.35, 1.85, 2.55]):
    tone(t, 0.09, 880 + i * 60, 0.10, 6)
    tone(t, 0.05, 1760 + i * 120, 0.035, 9)

# 新订单提示
for t in [3.02, 15.82]:
    tone(t, 0.18, 660, 0.14, 4)
    tone(t + 0.16, 0.22, 990, 0.13, 3)

# 确认接单
tone(4.55, 0.10, 523, 0.10, 6)

# 心跳 / 状态异常
for t in [6.95, 7.18, 7.42, 7.66]:
    tone(t, 0.16, 62, 0.20, 8)
    tone(t + 0.10, 0.10, 48, 0.12, 9)

# 通讯噪声
for i in range(18):
    t = 6.3 + i * 0.12 + random.random() * 0.05
    tone(t, 0.04, random.randint(1200, 3200), 0.025, 12, 'noise')

# 日志打字声
for t in [12.25 + i * 0.42 + j * 0.045 for i in range(6) for j in range(4)]:
    tone(t, 0.025, random.randint(900, 1600), 0.035, 14, 'square')

# CCTV 噪声段
for k in range(int(9 * SR), int(12 * SR)):
    t = k / SR
    add(k, random.uniform(-0.035, 0.035) * (0.6 + 0.4 * math.sin(2 * math.pi * 3.7 * t)))
tone(10.35, 0.30, 1200, 0.11, 5, 'square')
tone(10.70, 0.30, 760, 0.10, 5, 'square')

# 警告蜂鸣
for t in [12.9, 13.35, 13.8, 14.25, 14.7]:
    tone(t, 0.14, 440, 0.13, 4, 'square')

# 异常关闭 / 重派单
tone(15.0, 0.65, 180, 0.26, 2.5, 'sawtooth') if False else tone(15.0, 0.65, 180, 0.26, 2.5)
tone(15.05, 0.55, 90, 0.20, 3)
for i in range(10):
    tone(15.3 + i * 0.13, 0.05, 300 + i * 90, 0.05, 10, 'square')

# 结尾低频撞击与电流断裂
tone(18.0, 1.1, 55, 0.30, 1.8)
for k in range(int(18.0 * SR), int(19.85 * SR)):
    t = k / SR
    add(k, random.uniform(-0.09, 0.09) * max(0, 1 - (t - 18.0) / 1.85))
tone(19.6, 0.35, 1400, 0.13, 7, 'noise')
tone(19.72, 0.28, 48, 0.34, 4)

# 限幅 + 尾部淡出
out = []
for k, v in enumerate(buf):
    t = k / SR
    fade = min(1.0, t / 0.08, (DUR - t) / 0.12)
    v = math.tanh(v * 1.6) * max(0, fade)
    out.append(int(max(-1, min(1, v)) * 24000))

with wave.open('C:/Users/39288/WorkBuddy/2026-11-17-19-03-56/dispatch_horror/audio.wav', 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h', x) for x in out))
print('audio.wav written')
