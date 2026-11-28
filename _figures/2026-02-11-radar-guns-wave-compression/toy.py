"""Numbers for the radar gun post. Prints every figure used in the text."""
from math import cos, radians, atan, degrees

C = 299_792_458            # m/s, exact (CODATA)
MPH = 0.44704              # m/s per mph, exact by definition
KMH = 1 / 3.6              # m/s per km/h

BANDS = [                  # GHz, from the Arkansas training plan
    ("X", 10.525),
    ("K", 24.150),
    ("Ka (low end)", 33.4),
    ("Ka (high end)", 36.0),
]


def shift(v, f0):
    """Two-way Doppler shift, small-v form: 2 v f0 / c."""
    return 2 * v * f0 / C


def shift_exact(v, f0):
    """Moving mirror, exact: f0 (c+v)/(c-v) - f0."""
    return f0 * (C + v) / (C - v) - f0


def speed(df, f0):
    return df * C / (2 * f0)


v = 100 * KMH
f0 = 24.150e9

print("## Case: K band, 100 km/h, head on")
print(f"v = {v:.3f} m/s")
print(f"wavelength = {C / f0 * 100:.3f} cm")
df = shift(v, f0)
print(f"delta f (2 v f0 / c) = {df:.1f} Hz")
print(f"delta f exact        = {shift_exact(v, f0):.1f} Hz")
print(f"relative difference  = {(shift_exact(v, f0) - df) / df:.2e}")
print(f"v / c                = {v / C:.2e}")
print(f"f0 * (1 + v/c) = f0 + {f0 * v / C:.1f} Hz (one way)")
print(f"back to speed        = {speed(df, f0) / KMH:.3f} km/h")
print(f"shift / f0           = {df / f0:.2e}")

print()
print("## Bands at 100 km/h")
print("| band | f0 (GHz) | shift at 100 km/h (Hz) | Hz per km/h | Hz per mph |")
print("|---|---:|---:|---:|---:|")
for name, g in BANDS:
    f = g * 1e9
    print(f"| {name} | {g} | {shift(v, f):,.0f} | {shift(KMH, f):.1f} | {shift(MPH, f):.1f} |")

print()
print("## Cosine effect, K band, true speed 100 km/h")
print("| angle | cos | shift (Hz) | reading (km/h) | low by (km/h) |")
print("|---:|---:|---:|---:|---:|")
for a in (0, 5, 10, 20, 30, 45, 60):
    k = cos(radians(a))
    d = shift(v * k, f0)
    r = speed(d, f0) / KMH
    print(f"| {a} | {k:.4f} | {d:,.0f} | {r:.1f} | {max(0.0, 100 - r):.1f} |")

print()
print("## Gun 5 m beside the lane, car 30 m down the road (made up)")
a = degrees(atan(5 / 30))
k = cos(radians(a))
d = shift(v * k, f0)
print(f"angle = {a:.1f} deg, cos = {k:.4f}")
print(f"shift = {d:,.0f} Hz, reading = {speed(d, f0) / KMH:.1f} km/h")

assert abs(speed(df, f0) / KMH - 100) < 1e-9
