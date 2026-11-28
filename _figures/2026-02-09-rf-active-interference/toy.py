"""Numbers for the post on spread spectrum and processing gain.

Run: python3 _figures/2026-02-09-rf-active-interference/toy.py
Every number in the post comes from this output.
"""
import itertools
import math

# --- 1. Toy direct-sequence link: 8 chips per bit (code and interferer are made up) ---
code = [+1, +1, -1, +1, -1, +1, +1, -1]
bits = [+1, -1, +1]
A = 3  # constant interferer amplitude added to every chip (a narrowband tone near DC)
N = len(code)
assert sum(code) == 2

print("## Toy link")
print("code sum:", sum(code))
for b in bits:
    tx = [b * c for c in code]
    rx = [t + A for t in tx]
    corr = sum(r * c for r, c in zip(rx, code)) / N
    print(f"bit {b:+d}: tx {tx}  rx {rx}  despread {corr:+.2f}  decision {'+1' if corr > 0 else '-1'}")
    assert (1 if corr > 0 else -1) == b
    assert math.isclose(corr, b + A * sum(code) / N)

# Without spreading, the same interferer on a single-sample bit
for b in bits:
    r = b + A
    print(f"no spreading, bit {b:+d}: rx {r:+d}  decision {'+1' if r > 0 else '-1'}")
assert (-1 + A) > 0  # a -1 bit is read as +1

print("interferer to signal power before despreading:", A**2, "=", f"{10*math.log10(A**2):.2f} dB")
leak = A * sum(code) / N
print("interferer power left after despreading for this code:", leak**2)

# Average over all possible 8-chip codes: leaked power is A^2 / N
total = 0.0
count = 0
for c in itertools.product([+1, -1], repeat=N):
    total += (A * sum(c) / N) ** 2
    count += 1
mean_leak = total / count
print("codes tried:", count)
print("mean leaked interferer power over all codes:", mean_leak, " A^2/N =", A**2 / N)
assert math.isclose(mean_leak, A**2 / N)
print("average gain:", N, "=", f"{10*math.log10(N):.2f} dB")

# A stronger interferer breaks the same toy link
A2 = 5
leak2 = A2 * sum(code) / N
print(f"A = {A2}: power ratio {A2**2} = {10*math.log10(A2**2):.2f} dB, leak {leak2}, "
      f"bit -1 despreads to {-1 + leak2:+.2f}")
assert -1 + leak2 > 0

# --- 2. Processing gain at full size: GPS C/A code ---
chips_per_ms = 1023            # code length, repeats every 1 ms
chip_rate = chips_per_ms * 1000
data_rate = 50                 # bit/s
G = chip_rate / data_rate
G_db = 10 * math.log10(G)
print("\n## GPS C/A")
print("chip rate (chip/s):", chip_rate)
print("bit duration (ms):", 1000 / data_rate)
print("chips per bit:", G, " code periods per bit:", G / chips_per_ms)
print(f"G = {G:,.0f} = {G_db:.2f} dB")

# Wikipedia example: 1 kHz spread to 100 kHz
print("1 kHz -> 100 kHz:", 100_000 / 1_000, "=", f"{10*math.log10(100):.0f} dB")

# --- 3. Jammer power margin (required output ratio is made up) ---
req_db = 10
margin_db = G_db - req_db
print("\n## Margin")
print(f"required output signal-to-interference: {req_db} dB = {10**(req_db/10):.0f}x")
print(f"margin = {G_db:.2f} - {req_db} = {margin_db:.2f} dB = {10**(margin_db/10):,.0f}x the signal power")
print(f"no spreading: margin = 0 - {req_db} = {-req_db} dB = {10**(-req_db/10):.1f}x")

# --- 4. Frequency hopping ---
print("\n## Hopping")
for n_ch, k in [(88, 1), (88, 11)]:
    print(f"{k} of {n_ch} channels jammed: {k/n_ch*100:.2f}% of hops hit; "
          f"power per channel if total P is split: P/{k} = {10*math.log10(1/k):.2f} dB")

# --- 5. Notch ---
print("\n## Notch")
print("10 kHz notch in a 1 MHz signal:", f"{10e3/1e6*100:.0f}% of the bandwidth")
