"""Bande-son de la pub Artisan Relance (15 s) : musique 120 BPM + effets sonores.
Tout est synthétisé ici, donc libre de droits. Sortie : bande-son.wav (48 kHz, stéréo).
Usage : python3 bande_son.py
"""
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR, DUR = 48000, 15.0
N = int(SR * DUR)
t_all = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)


def add(sig, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt((1 - pan) / 2) * 1.414
    R[i:i + len(sig)] += sig * np.sqrt((1 + pan) / 2) * 1.414


def filt(x, kind, f):
    sos = butter(2, f, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x)


def env(n, a, d):
    e = np.ones(n)
    na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / SR / d)
    return e


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


def saw(f, n, detune=0.0):
    ph = (np.arange(n) / SR * f * (1 + detune)) % 1
    return 2 * ph - 1


# ---------------- MUSIQUE (120 BPM : 1 temps = 0,5 s, 1 mesure = 2 s) ----------------
BEAT = 0.5
# accords (notes MIDI) par mesure de 2 s : Am F C G Am F G C
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60], [55, 59, 62], [48, 52, 55, 60]]
ROOT = [45, 41, 48, 43, 45, 41, 43, 36]


def kick():
    n = int(.35 * SR); tt = np.arange(n) / SR
    f = 50 + 110 * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)


def hat(d=.05):
    n = int(d * 3 * SR)
    return filt(rng.standard_normal(n), "high", 7000) * env(n, .001, d)


def clap():
    n = int(.25 * SR)
    return filt(rng.standard_normal(n), "band", [900, 2600]) * env(n, .002, .07)


for b in range(30):
    tb = b * BEAT
    calm = 3.6 <= tb < 6.0           # scène 2 : l'attente, on retire la grosse caisse
    if not calm and tb < 14.0:
        add(kick(), tb, .9)
    if tb >= 1.0 and tb < 14.0:
        add(hat(), tb + BEAT / 2, .22, .3)
    if tb >= 6.0 and tb < 14.0 and b % 2 == 1:
        add(clap(), tb, .35, -.1)

# basse en croches
for bar in range(8):
    for k in range(4 if bar == 7 else 8):
        st = bar * 2 + k * .25
        if st >= 14.0: break
        n = int(.24 * SR)
        s = saw(note(ROOT[bar]), n) * env(n, .005, .12)
        add(filt(s, "low", 420), st, .32)

# nappe (pad)
for bar in range(8):
    st = bar * 2.0
    d = 2.0 if bar < 7 else 1.0
    n = int((d + .4) * SR)
    s = sum(saw(note(m), n, dt) for m in CH[bar] for dt in (-.004, .004))
    e = np.minimum(1, np.arange(n) / (.25 * SR)) * np.minimum(1, (n - np.arange(n)) / (.3 * SR))
    add(filt(s, "low", 1600) * e, st, .05, 0)

# arpège à partir de la scène 3
for i in range(int((14.0 - 6.0) / .125)):
    st = 6.0 + i * .125
    bar = int(st // 2)
    notes = CH[bar] + [CH[bar][0] + 12]
    m = notes[i % len(notes)] + 12
    n = int(.2 * SR); tt = np.arange(n) / SR
    s = (np.sin(2 * np.pi * note(m) * tt) + .3 * np.sin(4 * np.pi * note(m) * tt)) * env(n, .002, .07)
    add(s, st, .09, .4 if i % 2 else -.4)

# accord final qui résonne (14 s)
n = int(1.0 * SR); tt = np.arange(n) / SR
fin = sum(np.sin(2 * np.pi * note(m) * tt) + .4 * np.sin(2 * np.pi * note(m + 12) * tt) for m in [48, 52, 55, 60, 64])
fin *= np.minimum(1, tt / .01) * np.exp(-tt * 1.6)
add(fin, 14.0, .09)
add(kick(), 14.0, 1.0)
add(filt(rng.standard_normal(int(1 * SR)), "high", 5000) * env(int(1 * SR), .005, .25), 14.0, .12)

# coupure de la musique avant la transition 2 -> 3 (5,6 s, 4 images)
a, b = int(5.6 * SR), int(5.733 * SR)
fade = int(.01 * SR)
for ch in (L, R):
    ch[a:b] *= 0
    ch[a - fade:a] *= np.linspace(1, 0, fade)
    ch[b:b + fade] *= np.linspace(0, 1, fade)

music_L, music_R = L.copy(), R.copy()
L[:] = 0; R[:] = 0

# ---------------- EFFETS SONORES ----------------


def whoosh(d=.35, f0=400, f1=3000):
    n = int(d * SR); x = rng.standard_normal(n); out = np.zeros(n)
    seg = 512
    for i in range(0, n, seg):
        k = i / n
        f = f0 * (f1 / f0) ** k
        out[i:i + seg] = filt(x[i:i + seg], "band", [f * .7, min(f * 1.4, 20000)])
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return out * e


def impact(heavy=1.0):
    n = int(.6 * SR); tt = np.arange(n) / SR
    f = 45 + 90 * np.exp(-tt * 20)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * (6 / heavy))
    crack = filt(rng.standard_normal(n), "low", 3000) * np.exp(-tt * 30)
    return body + .35 * crack


def riser(d=.45):
    n = int(d * SR); tt = np.arange(n) / SR
    f = 200 * (8 ** (tt / d))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * .4 + filt(rng.standard_normal(n), "high", 2000) * .5
    return s * (tt / d) ** 2


def ding(f=1320):
    n = int(.6 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tt) + .5 * np.sin(2 * np.pi * f * 1.5 * tt)) * env(n, .002, .18)


def click():
    n = int(.03 * SR)
    return filt(rng.standard_normal(n), "band", [2000, 6000]) * env(n, .0005, .006)


def glitch():
    n = int(.15 * SR)
    x = np.sign(np.sin(2 * np.pi * 180 * np.arange(n) / SR)) * (rng.random(n) > .3)
    return filt(x * env(n, .001, .08), "band", [300, 4000])


def shimmer():
    out = np.zeros(int(1.0 * SR))
    for i, m in enumerate([84, 88, 91, 96, 100]):
        n = int(.6 * SR); tt = np.arange(n) / SR
        s = np.sin(2 * np.pi * note(m) * tt) * env(n, .003, .2)
        j = int(i * .08 * SR); out[j:j + n] += s
    return out


def tick():
    n = int(.02 * SR)
    return filt(rng.standard_normal(n), "high", 3000) * env(n, .0005, .004)


# Scène 1
for i, (st, pan) in enumerate([(0.0, -.6), (0.12, .6), (0.32, -.5), (0.52, .5)]):
    add(whoosh(.32, 300, 2500), st, .35, pan)
add(impact(1.2), 0.3, .75)
add(riser(.45), 2.55, .35)
# Scène 2
add(whoosh(.4, 600, 4000), 3.42, .3, 0)
for k in range(12):
    add(click(), 3.3 + k * .033, .25)
add(impact(.6), 4.4, .45)
for k in range(6):                       # tic-tac discret
    add(tick(), 4.0 + k * .25, .25, .2 if k % 2 else -.2)
add(glitch(), 5.733, .4)
add(whoosh(.3, 800, 5000), 5.72, .28, .5)
# Scène 3
add(impact(.6), 6.0, .4)
for st, pan in [(6.3, -.3), (6.85, 0), (7.4, .3)]:
    add(ding(1320 if st < 7 else 1568), st, .22, pan)
add(impact(.5), 7.6, .4)
add(whoosh(.5, 300, 3000), 8.45, .3)
# Scène 4
add(impact(.5), 9.4, .35)
for k in range(3):
    add(click(), 9.85 + k * .4, .45)
add(riser(.4), 11.6, .3)
# Scène 5
add(impact(1.6), 12.0, .9)
add(click(), 13.4, .7)
add(ding(2093), 13.4, .1)
add(shimmer(), 14.2, .2)

fx_L, fx_R = L.copy(), R.copy()

# ---------------- MIXAGE ----------------
mixL = music_L * 1.0 + fx_L * 1.0
mixR = music_R * 1.0 + fx_R * 1.0
# fondu de sortie très court sur les 80 dernières ms
f = int(.08 * SR)
mixL[-f:] *= np.linspace(1, 0, f); mixR[-f:] *= np.linspace(1, 0, f)
peak = max(np.abs(mixL).max(), np.abs(mixR).max())
mix = np.stack([mixL, mixR], 1) / peak * .89
wavfile.write("bande-son.wav", SR, (mix * 32767).astype(np.int16))
print("bande-son.wav écrit,", DUR, "s")
