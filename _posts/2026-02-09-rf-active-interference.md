---
title: "Spread Spectrum: The Maths of Beating Interference"
author: yoav
description: "Direct-sequence spread spectrum gains the ratio of chip rate to data rate against interference: 43.11 dB for a 50 bit/s signal sent at 1,023,000 chips a second. The maths by hand, and what it means for a jammer's power."
date: 2026-02-09 12:00:00 +0200
lang: en
categories: [RF, Security, Embedded Systems]
tags: [rf, jamming, spread-spectrum, direct-sequence, frequency-hopping, processing-gain]
pin: false
math: true
mermaid: false
image:
  path: /assets/images/rf-jet-interference.jpg
  alt: Modern military aircraft with advanced RF systems
---

## 01. What does interference do to a receiver?

A receiver finds a signal by comparing its power with everything else in the band. Interference is any other power in the band. It can be accidental or deliberate. Deliberate interference is called jamming. What matters is the ratio of signal power to interference power. When it falls below what the receiver needs, bits are lost.

Radar texts name three kinds of noise jamming [\[1\]](#ref-1):

- Spot jamming puts all of the jammer's power on one frequency.
- Sweep jamming moves its full power from one frequency to another. It covers several frequencies, but not all at once.
- Barrage jamming switches so fast that it looks like a constant source across the whole band.

A fourth kind, repeater jamming, retransmits a manipulated copy of the received signal [\[1\]](#ref-1). This post is about the first three. The defences below make the same total power count for less.

## 02. How does spreading help?

Direct-sequence spread spectrum (DSSS) multiplies each data bit by a fast code. Each symbol of the code is a chip. Chips are shorter than bits, so the signal takes more bandwidth. The spreading factor is the ratio of the chip rate to the data rate [\[2\]](#ref-2).

The receiver multiplies by the same code again. That restores the data. Interference never had the code, so it is not restored and stays spread out [\[2\]](#ref-2). For white noise, the signal-to-noise ratio after despreading is higher by the spreading factor [\[2\]](#ref-2).

Spread spectrum has two original goals: to resist jamming, and to hide the signal from a listener [\[3\]](#ref-3). The same source says direct sequence resists continuous narrowband jamming well, and frequency hopping resists pulse jamming better [\[3\]](#ref-3).

## 03. A link small enough to do by hand

Take 8 chips per bit. The code is made up for the example:

| chip | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| code $$c_i$$ | +1 | +1 | −1 | +1 | −1 | +1 | +1 | −1 |

Its chips add up to 2. Data bits are $$b = +1$$ or $$b = -1$$. The transmitter sends $$b\,c_i$$ on chip $$i$$.

The interferer is also made up. It adds a constant $$A = 3$$ to every chip. A constant is the simplest narrowband interferer, because all its power sits at one frequency, zero. The signal has amplitude 1, so the interferer has 9 times the signal's power, which is 9.54 dB.

The receiver multiplies each received chip by $$c_i$$, adds them and divides by $$N = 8$$. Since $$c_i^2 = 1$$:

$$
y = \frac{1}{N}\sum_{i=1}^{N}\left(b\,c_i + A\right)c_i = b + \frac{A}{N}\sum_{i=1}^{N} c_i
$$

The first term is the data. The second is what the interferer leaves behind. Here it is $$3 \cdot 2 / 8 = 0.75$$.

| bit sent | chips received | $$y$$ | decision |
|:-:|---|:-:|:-:|
| +1 | 4, 4, 2, 4, 2, 4, 4, 2 | +1.75 | +1, right |
| −1 | 2, 2, 4, 2, 4, 2, 2, 4 | −0.25 | −1, right |

_Computed with `toy.py`. The code and the interferer are made up for the example._

Without spreading, one sample per bit carries the same interferer. A bit of −1 arrives as $$-1 + 3 = 2$$ and is read as +1. That is wrong.

With spreading, the interferer power left after despreading is $$0.75^2 = 0.5625$$ for this code. Other codes leave other amounts. Averaged over all 256 possible 8-chip codes, the leftover is $$A^2/N = 1.125$$. Against a signal power of 1, that is a gain of exactly 8, which is 9.03 dB. This code is better than average.

The link has a limit. At $$A = 5$$ (13.98 dB) the leftover is $$5 \cdot 2 / 8 = 1.25$$. A bit of −1 arrives as $$-1 + 1.25 = +0.25$$ and is read as +1. Eight chips are not enough for that interferer.

## 04. How big is the gain at full size?

The gain is the spreading factor. With chip rate $$R_c$$ and data rate $$R_b$$:

$$
G = \frac{R_c}{R_b}, \qquad G_{\text{dB}} = 10\log_{10} G
$$

Processing gain is usually quoted in decibels. A signal of 1 kHz spread to 100 kHz has a ratio of 100000 / 1000 = 100, which is 20 dB [\[4\]](#ref-4). The toy link above has $$G = 8$$, which is 9.03 dB.

GPS gives a real case. Its civilian C/A code is a sequence of 1,023 chips that repeats every millisecond, at 1.023 Mchip/s [\[5\]](#ref-5) [\[6\]](#ref-6). The navigation message is sent at 50 bit/s and is combined with the code by XOR [\[5\]](#ref-5) [\[6\]](#ref-6). One bit lasts 1 / 50 s = 20 ms, which is 20 repetitions of the code.

| quantity | value | where it comes from |
|---|---:|---|
| chips per code period | 1,023 | source [\[5\]](#ref-5) |
| code period | 1 ms | source [\[5\]](#ref-5) |
| chip rate $$R_c$$ | 1,023,000 chip/s | 1,023 chips per ms |
| data rate $$R_b$$ | 50 bit/s | source [\[5\]](#ref-5) |
| chips per bit $$G$$ | 20,460 | $$R_c / R_b$$ |
| gain $$G_{\text{dB}}$$ | 43.11 dB | $$10\log_{10} 20460$$ |

> Decibels turn ratios into sums. 10 dB is a factor of 10, 20 dB is 100, 30 dB is 1,000. Add the decibels, multiply the ratios.
{: .prompt-info }

The gain costs bandwidth. A spread signal takes about $$G$$ times the bandwidth of the data it carries [\[4\]](#ref-4).

## 05. What does the gain mean for a jammer?

Say the receiver needs an output signal-to-interference ratio of at least $$q$$. The gain multiplies the input ratio, so the largest interference-to-signal ratio the link tolerates at its input is

$$
\left(\frac{J}{S}\right)_{\max} = \frac{G}{q}, \qquad 10\log_{10}\left(\frac{J}{S}\right)_{\max} = G_{\text{dB}} - q_{\text{dB}}
$$

This is my derivation from the statement in section 02 that despreading raises the ratio by the spreading factor. It assumes the jammer does not know the code and its power acts like noise, and it ignores receiver losses.

Take $$q = 10$$ dB, which is 10 times. That value is made up for the example.

- Without spreading, $$G = 1$$. The margin is $$0 - 10 = -10$$ dB. The interference must stay at 0.1 times the signal power.
- With the GPS-like gain, the margin is $$43.11 - 10 = 33.11$$ dB. The interference can reach 2,046 times the signal power before the link fails.

The ratio between the two is 20,460, the gain itself. The jammer needs 20,460 times the power for the same effect. That holds only while the code is secret.

## 06. What if the jammer follows the signal in frequency?

Frequency-hopping spread spectrum (FHSS) changes the carrier frequency by a pattern. A code known to both transmitter and receiver sets the pattern [\[7\]](#ref-7). Jamming is hard when the pattern is unknown, and a hopping system resists deliberate jamming unless the adversary knows the pattern [\[7\]](#ref-7).

The idea is old. Hedy Kiesler Markey (Hedy Lamarr) and George Antheil filed "Secret communication system" on 10 June 1941. It was granted on 11 August 1942 as US patent 2,292,387 [\[8\]](#ref-8). It says its player-piano-style record would permit 88 different carrier frequencies [\[8\]](#ref-8).

Use 88 channels as an example, taken from that patent and not from a modern system. A jammer that does not know the pattern and covers $$k$$ channels at once hits a fraction $$k/N$$ of the hops:

- $$k = 1$$: $$1/88 = 1.14\%$$ of hops.
- $$k = 11$$: $$11/88 = 12.5\%$$ of hops.

If the jammer's total power is $$P$$ and it covers $$k$$ channels evenly, each gets $$P/k$$. At $$k = 11$$ that is $$-10.41$$ dB per channel. Covering more channels puts less power on each one. This is my arithmetic, not a measurement.

Hopping can also move away from busy channels. Bluetooth's adaptive frequency hopping avoids crowded frequencies in the hop sequence. Wikipedia dates it to version 1.2 of the standard, in 2003 [\[7\]](#ref-7).

## 07. What removes one strong narrowband signal?

A notch filter is a band-stop filter with a narrow stopband. It is used to remove a specific interfering frequency [\[9\]](#ref-9). A fixed notch only helps while the interferer stays on that frequency.

A spread signal is wide, so a thin notch costs little of it. Take a 1 MHz signal and a 10 kHz notch. Both are made up for the example. The notch removes $$10/1000 = 1\%$$ of the bandwidth. If the power is spread evenly, that is about 1% of the signal power. An unspread narrowband signal on the interferer's frequency would lose all of it.

## 08. Try it

The plain-Python version of sections 04 and 05:

```python
import math

chip_rate, data_rate = 1_023_000, 50   # chip/s and bit/s of the GPS C/A signal
G = chip_rate / data_rate              # processing gain as a ratio
q_db = 10                              # required output ratio, made up
print(G, round(10 * math.log10(G), 2), round(10 * math.log10(G) - q_db, 2))
```

It prints the gain as a ratio, the gain in dB and the margin in dB:

```
20460.0 43.11 33.11
```

## Sources

<span id="ref-1"></span>\[1\] Wikipedia contributors. _Radar jamming and deception_. Wikipedia. [https://en.wikipedia.org/wiki/Radar_jamming_and_deception](https://en.wikipedia.org/wiki/Radar_jamming_and_deception). Accessed 2026-11-28.

<span id="ref-2"></span>\[2\] Wikipedia contributors. _Direct-sequence spread spectrum_. Wikipedia. [https://en.wikipedia.org/wiki/Direct-sequence_spread_spectrum](https://en.wikipedia.org/wiki/Direct-sequence_spread_spectrum). Accessed 2026-11-28.

<span id="ref-3"></span>\[3\] Wikipedia contributors. _Spread spectrum_. Wikipedia. Cites Torrieri, D. (2018), _Principles of Spread-Spectrum Communication Systems_, 4th ed., for the two goals. [https://en.wikipedia.org/wiki/Spread_spectrum](https://en.wikipedia.org/wiki/Spread_spectrum). Accessed 2026-11-28.

<span id="ref-4"></span>\[4\] Wikipedia contributors. _Processing gain_. Wikipedia. [https://en.wikipedia.org/wiki/Processing_gain](https://en.wikipedia.org/wiki/Processing_gain). Accessed 2026-11-28.

<span id="ref-5"></span>\[5\] Wikipedia contributors. _GPS signals_. Wikipedia. [https://en.wikipedia.org/wiki/GPS_signals](https://en.wikipedia.org/wiki/GPS_signals). Accessed 2026-11-28.

<span id="ref-6"></span>\[6\] MathWorks. _GPS signals_. Satellite Communications Toolbox documentation. [https://www.mathworks.com/help/satcom/gs/gps-signals.html](https://www.mathworks.com/help/satcom/gs/gps-signals.html). Accessed 2026-11-28.

<span id="ref-7"></span>\[7\] Wikipedia contributors. _Frequency-hopping spread spectrum_. Wikipedia. [https://en.wikipedia.org/wiki/Frequency-hopping_spread_spectrum](https://en.wikipedia.org/wiki/Frequency-hopping_spread_spectrum). Accessed 2026-11-28.

<span id="ref-8"></span>\[8\] Markey, H. K., & Antheil, G. (1942). _Secret communication system_. US Patent 2,292,387, filed 10 June 1941, granted 11 August 1942. [https://patents.google.com/patent/US2292387A/en](https://patents.google.com/patent/US2292387A/en)

<span id="ref-9"></span>\[9\] Wikipedia contributors. _Band-stop filter_. Wikipedia. [https://en.wikipedia.org/wiki/Band-stop_filter](https://en.wikipedia.org/wiki/Band-stop_filter). Accessed 2026-11-28.
