"""크랑이뉴스 릴스용 배경음악 자동 작곡 (저작권 없는 오리지널).

날짜를 씨앗(seed)으로 써서 매일 다른, 잔잔하고 상쾌한 아침 곡을 만든다.
같은 날짜로 다시 돌리면 같은 곡이 나온다.

    python3 gen_music.py <출력.wav> [--seed 2026-10-09] [--sec 24]
"""
import argparse
import datetime
import hashlib

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100

PROGRESSIONS = [  # 장조 기준 음계 도수(0=I) — 밝고 편안한 진행
    [0, 5, 3, 4], [0, 4, 5, 3], [5, 3, 0, 4], [0, 3, 4, 4],
    [3, 4, 2, 5], [0, 2, 3, 4], [5, 4, 3, 4], [0, 5, 1, 4],
]
MAJOR = [0, 2, 4, 5, 7, 9, 11]
PENTA = [0, 2, 4, 7, 9]


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a=0.01, r=0.3):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    rel = np.clip((t[-1] - t) / max(r, 1e-4), 0, 1) if n else e
    return e * np.minimum(1, rel * 3) * np.exp(-t * 1.2)


def epiano(freq, dur, vel=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    w = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 4)
         + 0.12 * np.sin(2 * np.pi * freq * 3 * t) * np.exp(-t * 7))
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)
    return vel * w * trem * env(n, 0.005, 0.4)


def bell(freq, dur, vel=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    w = (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t * 6)
         + 0.2 * np.sin(2 * np.pi * freq * 5.4 * t) * np.exp(-t * 10))
    return vel * w * np.exp(-t * 3.5)


def shaker(rng, vel=0.05):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    b, a = butter(2, 5000 / (SR / 2), btype="high")
    e = np.minimum(1, t / 0.02) * np.exp(-t * 35)
    return vel * lfilter(b, a, rng.standard_normal(n)) * e


def bass(freq, dur, vel=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    w = np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(2 * np.pi * freq * 2 * t)
    return vel * w * env(n, 0.01, 0.2)


def kick(vel=0.8):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 110 * np.exp(-t * 18) + 45
    return vel * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def snare(rng, vel=0.25):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    b, a = butter(2, [1500 / (SR / 2), 7000 / (SR / 2)], btype="band")
    return vel * (lfilter(b, a, noise) * np.exp(-t * 18) + 0.3 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25))


def hat(rng, vel=0.07):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    b, a = butter(2, 7000 / (SR / 2), btype="high")
    return vel * lfilter(b, a, rng.standard_normal(n)) * np.exp(-t * 60)


def add(buf, sig, start):
    i = int(start * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += sig[: j - i]


def compose(seed_text, sec=24.0):
    seed = int(hashlib.md5(seed_text.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    key = int(rng.integers(60, 67))          # 근음 (C4 ~ F#4) — 밝은 음역
    bpm = float(rng.integers(86, 101))
    prog = PROGRESSIONS[int(rng.integers(len(PROGRESSIONS)))]
    swing = float(rng.uniform(0.0, 0.06))
    beat = 60 / bpm
    bar = beat * 4
    n = int((sec + 2) * SR)
    L = np.zeros(n)
    R = np.zeros(n)

    def chord(deg):
        root = key + MAJOR[deg % 7]
        notes = [root, root + (MAJOR[(deg + 2) % 7] - MAJOR[deg % 7]) % 12,
                 root + (MAJOR[(deg + 4) % 7] - MAJOR[deg % 7]) % 12,
                 root + (MAJOR[(deg + 6) % 7] - MAJOR[deg % 7]) % 12]
        return root, notes

    t = 0.0
    bi = 0
    melody_density = float(rng.uniform(0.3, 0.45))
    while t < sec:
        deg = prog[bi % len(prog)]
        root, notes = chord(deg)
        # 코드 (살짝 흩뿌려 치기)
        for k, m in enumerate(notes):
            s = epiano(midi_hz(m), bar * 0.95, 0.12)
            add(L, s * (0.9 - 0.1 * k), t + k * 0.012)
            add(R, s * (0.6 + 0.1 * k), t + k * 0.012)
        # 베이스
        for b_ in (0, 2.5):
            s = bass(midi_hz(root - 24), beat * 1.4)
            add(L, s, t + b_ * beat)
            add(R, s, t + b_ * beat)
        # 드럼 — 가볍고 상쾌하게 (첫 마디는 조용히 시작)
        if bi > 0:
            for b_ in range(4):
                bt = t + b_ * beat
                if b_ == 0 or (b_ == 2 and rng.random() < 0.7):
                    k_ = kick(0.38)
                    add(L, k_, bt)
                    add(R, k_, bt)
                if b_ in (1, 3):
                    s_ = snare(rng, 0.11)
                    add(L, s_ * 0.8, bt)
                    add(R, s_, bt)
                for h in (0, 0.5):
                    off = h * beat + (swing * beat if h else 0)
                    sh = shaker(rng)
                    add(L, sh, bt + off)
                    add(R, sh * 0.7, bt + off)
        # 멜로디 (펜타토닉, 드문드문)
        if bi > 0:
            for step in range(8):
                if rng.random() < melody_density:
                    m = key + 12 + PENTA[int(rng.integers(len(PENTA)))] + (12 if rng.random() < 0.2 else 0)
                    st = t + step * beat / 2
                    if rng.random() < 0.5:
                        s = bell(midi_hz(m + 12), beat * 1.5, 0.07)
                    else:
                        s = epiano(midi_hz(m), beat * 0.9, 0.08)
                    add(L, s * 0.7, st)
                    add(R, s, st + 0.01)
        t += bar
        bi += 1

    mix = np.stack([L, R], axis=1)[: int(sec * SR)]
    # 맑은 아침 느낌: 고음은 거의 살리고 잡음은 아주 약하게
    b, a = butter(2, 11000 / (SR / 2), btype="low")
    mix = lfilter(b, a, mix, axis=0)
    mix += rng.standard_normal(mix.shape) * 0.0012
    # 페이드 인/아웃
    fi, fo = int(0.8 * SR), int(2.0 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix /= max(1e-6, np.abs(mix).max()) / 0.7
    info = {"bpm": bpm, "key_midi": key, "progression": prog}
    return (mix * 32767).astype(np.int16), info


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--seed", default=datetime.date.today().isoformat())
    ap.add_argument("--sec", type=float, default=24.0)
    a = ap.parse_args()
    audio, info = compose(a.seed, a.sec)
    wavfile.write(a.out, SR, audio)
    print(a.out, info)
