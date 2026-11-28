---
title: "Radar Guns: Speed from a Frequency Shift"
author: yoav
description: "A radar gun reads speed from the frequency shift of a microwave echo. At 24.150 GHz and 100 km/h the shift is 4,475 Hz, and a 20 degree angle makes the gun read 6% low."
date: 2026-02-11 12:00:00 +0200
lang: en
categories: [Physics, Technology, Law Enforcement]
tags: [radar, doppler-effect, speed-gun, physics, python]
pin: false
math: true
mermaid: false
image:
   path: /assets/images/radar-gun-speed-detection.jpg
   alt: Police radar gun measuring vehicle speed using Doppler effect
---

## 01. The question

A radar speed gun does not see the car move. It sends out a microwave beam, receives the echo from the car, and gets the speed from the frequency of the echo alone. How does a frequency become a speed?

In the United States the FCC allows speed radar in three bands [\[1\]](#ref-1):

| Band | Frequency |
|---|---:|
| X | 10.525 GHz |
| K | 24.150 GHz |
| Ka | 33.4 to 36 GHz |

The examples below use the K band, 24.150 GHz.

## 02. How big is the shift?

A car driving toward the gun meets the waves faster than they were sent, so it sees a higher frequency. The car then reflects those waves. To the gun the car is a moving source, so the frequency rises a second time. A car driving away lowers the frequency instead [\[2\]](#ref-2).

For a perfect reflector moving at speed $$v$$ the echo has frequency $$f_0 (c+v)/(c-v)$$ [\[3\]](#ref-3). Cars are slow compared with light, $$v \ll c$$, and the shift becomes

$$
\Delta f = \frac{2\,v\,f_0}{c}
$$

where $$f_0$$ is the frequency the gun sends, $$c$$ is the speed of light and $$\Delta f$$ is the shift. The 2 is the two legs: the wave is shifted once on the way to the car and once on the way back.

## 03. One case by hand

Take a car driving straight at a K band gun at 100 km/h. That car is made up for the example. Its speed is $$100 / 3.6 = 27.778$$ m/s, and $$c = 299{,}792{,}458$$ m/s [\[4\]](#ref-4).

$$
\Delta f = \frac{2 \times 27.778 \times 24.150 \times 10^{9}}{299{,}792{,}458} = 4{,}475\ \text{Hz}
$$

Each leg adds about 2,238 Hz. The carrier is 24,150,000,000 Hz, so the shift is $$1.85 \times 10^{-7}$$ of it. The exact formula from section 02 gives the same 4,475 Hz. The two forms differ by a relative $$9.3 \times 10^{-8}$$, which is about $$v/c$$.

The same car in the other bands, computed with the same formula:

| Band | $$f_0$$ (GHz) | Shift at 100 km/h (Hz) | Hz per km/h | Hz per mph |
|---|---:|---:|---:|---:|
| X | 10.525 | 1,950 | 19.5 | 31.4 |
| K | 24.150 | 4,475 | 44.8 | 72.0 |
| Ka, low end | 33.4 | 6,189 | 61.9 | 99.6 |
| Ka, high end | 36.0 | 6,671 | 66.7 | 107.4 |

A police training plan lists 31.4 Hz per mph for X band, 72 for K band and 103 for Ka band [\[1\]](#ref-1). The first two match the formula. The Ka figure of 103 lies between the two ends of the Ka band. The plan does not say which Ka frequency it used.

> All Hz values are computed with the formula and rounded to whole hertz, except the per km/h and per mph columns. They are not measurements of a real gun.
{: .prompt-info }

## 04. How does the gun turn a shift into a speed?

The gun mixes the echo with a small part of the signal it is sending. The mix beats at the difference of the two frequencies, which is $$\Delta f$$. A digital counter counts the cycles of that beat over a fixed time, and the display shows the speed [\[2\]](#ref-2).

The gun knows its own $$f_0$$, so it only has to solve the formula for $$v$$:

$$
v = \frac{c\,\Delta f}{2\,f_0}
$$

For the example, $$\Delta f = 4{,}475$$ Hz gives back 100.000 km/h. Speed is directly proportional to the shift [\[2\]](#ref-2), so 2,238 Hz would read 50 km/h.

## 05. What does an angle do?

The gun senses only the part of the car's motion that points along the line between them [\[2\]](#ref-2). A car that drives past at an angle $$\theta$$ to that line has a speed along it of $$v \cos\theta$$, and the shift becomes

$$
\Delta f = \frac{2\,v\cos\theta\,f_0}{c}
$$

The gun does not know $$\theta$$, so it reads $$v \cos\theta$$ as the speed. The reading is always at or below the true speed. For the same K band car at 100 km/h:

| Angle | $$\cos\theta$$ | Shift (Hz) | Reading (km/h) | Low by (km/h) |
|---:|---:|---:|---:|---:|
| 0° | 1.0000 | 4,475 | 100.0 | 0.0 |
| 5° | 0.9962 | 4,458 | 99.6 | 0.4 |
| 10° | 0.9848 | 4,407 | 98.5 | 1.5 |
| 20° | 0.9397 | 4,205 | 94.0 | 6.0 |
| 30° | 0.8660 | 3,876 | 86.6 | 13.4 |
| 45° | 0.7071 | 3,165 | 70.7 | 29.3 |
| 60° | 0.5000 | 2,238 | 50.0 | 50.0 |

Take a gun 5 m beside the lane aimed at a car 30 m down the road. Both distances are made up. The angle is $$\arctan(5/30) = 9.5°$$, $$\cos\theta = 0.9864$$, and the gun reads 98.6 km/h for a car doing 100.

For a stationary gun the error always favors the driver, which is why training plans tell the operator to stand close to the road and aim straight along it [\[1\]](#ref-1). The angle also changes as the car gets closer, so the reading can fall as the car approaches [\[1\]](#ref-1).

## 06. Try it

Plain Python, no packages. It recomputes the shift from section 03 and the readings from section 05.

```python
from math import cos, radians

C = 299_792_458                      # m/s, speed of light
f0 = 24.150e9                        # Hz, K band
v = 100 / 3.6                        # m/s, 100 km/h

df = 2 * v * f0 / C                  # two-way Doppler shift
print(round(df))                     # 4475

reading = df * C / (2 * f0) * 3.6    # what the gun displays, in km/h
print(round(reading, 1))             # 100.0

for angle in (10, 20, 30):
    df = 2 * v * cos(radians(angle)) * f0 / C
    print(angle, round(df * C / (2 * f0) * 3.6, 1))   # 98.5, 94.0, 86.6
```

Output:

```text
4475
100.0
10 98.5
20 94.0
30 86.6
```

## Sources

<span id="ref-1"></span>\[1\] Poole, R. (2018). _Radar / Lidar Operator, 8 hours_ [Basic Police Training Course elective, revised 4 January 2018]. ALETA. [https://media.ark.org/dps/Radar-Lidar-Operator-Lesson-Plan.pdf](https://media.ark.org/dps/Radar-Lidar-Operator-Lesson-Plan.pdf)

<span id="ref-2"></span>\[2\] Wikipedia. _Radar speed gun_. Accessed 28 November 2026. [https://en.wikipedia.org/wiki/Radar_speed_gun](https://en.wikipedia.org/wiki/Radar_speed_gun)

<span id="ref-3"></span>\[3\] Wikipedia. _Doppler radar_, section "Frequency variation". Accessed 28 November 2026. [https://en.wikipedia.org/wiki/Doppler_radar](https://en.wikipedia.org/wiki/Doppler_radar)

<span id="ref-4"></span>\[4\] NIST. _CODATA value: speed of light in vacuum_. [https://physics.nist.gov/cgi-bin/cuu/Value?c](https://physics.nist.gov/cgi-bin/cuu/Value?c)
