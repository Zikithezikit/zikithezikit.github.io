"""Toy Schnorr proof of knowledge, done at p = 23, q = 11, g = 2.

Prints every number used in the post. Run:
    python3 _figures/2026-02-21-zero-knowledge-proofs-schnorr/toy.py > toy.out.md
"""
import hashlib

p, q, g = 23, 11, 2


def H(*parts):
    """Fiat-Shamir challenge: SHA-256 of the comma-joined parts, reduced mod q."""
    data = ",".join(map(str, parts)).encode()
    return int.from_bytes(hashlib.sha256(data).digest(), "big") % q


def verify_equation(y, t, c, s):
    return pow(g, s, p) == t * pow(y, c, p) % p


print("## group")
assert (p - 1) % q == 0 and pow(g, q, p) == 1 and g != 1
print(f"p={p} q={q} p-1={p-1} = {q} * {(p-1)//q}  g={g}  g^q mod p = {pow(g, q, p)}")
print("| e | " + " | ".join(str(e) for e in range(q + 1)) + " |")
print("|---|" + "---|" * (q + 1))
print("| g^e mod p | " + " | ".join(str(pow(g, e, p)) for e in range(q + 1)) + " |")
subgroup = sorted(pow(g, e, p) for e in range(q))
print("subgroup elements (sorted):", subgroup)
assert len(set(subgroup)) == q

x = 7
y = pow(g, x, p)
print("\n## keys")
print(f"x={x} y=g^x mod p={y}  y^q mod p={pow(y, q, p)}")
dlog = {pow(g, e, p): e for e in range(q)}
assert dlog[y] == x
print(f"table lookup of y={y} gives x={dlog[y]}")

print("\n## interactive run")
k, c = 4, 5
t = pow(g, k, p)
s = (k + c * x) % q
print(f"k={k} t=g^k mod p={t}")
print(f"c={c}")
print(f"c*x={c*x}  k+c*x={k+c*x}  s=(k+c*x) mod q={s}")
lhs = pow(g, s, p)
yc = pow(y, c, p)
rhs = t * yc % p
print(f"g^s mod p={lhs}  y^c mod p={yc}  t*y^c={t*yc}  t*y^c mod p={rhs}")
assert lhs == rhs and verify_equation(y, t, c, s)
print("integer sum without mod q:", k + c * x, " divided by c:", (k + c * x) / c)

print("\n## why s hides x: fixed x and c, every k")
ks = list(range(q))
ss = [(kk + c * x) % q for kk in ks]
print("k:", ks)
print("s:", ss)
assert sorted(ss) == ks

print("\n## simulated transcript, no x")
cs, ss_ = 3, 9
ts = pow(g, ss_, p) * pow(y, -cs, p) % p
print(f"c={cs} s={ss_} t=g^s*y^-c mod p={ts}")
print(f"check: g^s mod p={pow(g, ss_, p)}  t*y^c mod p={ts*pow(y,cs,p)%p}")
assert verify_equation(y, ts, cs, ss_)

print("\n## nonce reuse")
k = 4
c1, c2 = 5, 9
s1, s2 = (k + c1 * x) % q, (k + c2 * x) % q
t = pow(g, k, p)
print(f"k={k} t={t} c1={c1} s1={s1} c2={c2} s2={s2}")
assert verify_equation(y, t, c1, s1) and verify_equation(y, t, c2, s2)
ds, dc = (s1 - s2) % q, (c1 - c2) % q
inv = pow(dc, -1, q)
rec = ds * inv % q
print(f"s1-s2 mod q={ds}  c1-c2 mod q={dc}  inverse of c1-c2 mod q={inv}  check {dc}*{inv}={dc*inv}={dc*inv % q} mod q")
print(f"x=(s1-s2)*inv mod q={rec}")
assert rec == x
krec = (s1 - c1 * rec) % q
print(f"k=s1-c1*x mod q={krec}")
assert krec == k

print("\n## Fiat-Shamir")
k = 9
t = pow(g, k, p)
digest = hashlib.sha256(",".join(map(str, (g, y, t))).encode()).hexdigest()
c = H(g, y, t)
s = (k + c * x) % q
print(f"k={k} t={t} input='{g},{y},{t}' sha256={digest}")
print(f"first 8 hex digits {digest[:8]}  full hash mod q = {int(digest, 16) % q}  c={c}")
print(f"s=(k+c*x) mod q = ({k}+{c}*{x}) mod {q} = {s}")
lhs = pow(g, s, p)
yc = pow(y, c, p)
print(f"g^s mod p={lhs}  y^c mod p={yc}  t*y^c mod p={t*yc%p}")
assert lhs == t * yc % p
print(f"proof=(t={t}, s={s})")
# wrong response
print("wrong s+1 passes?", pow(g, (s + 1) % q, p) == t * yc % p)

print("\n## forging without x (grind over c, s)")
found = []
attempts = 0
first = None
for s_ in range(q):
    for c_ in range(q):
        attempts += 1
        t_ = pow(g, s_, p) * pow(y, -c_, p) % p
        if H(g, y, t_) == c_:
            found.append((t_, s_, c_))
            if first is None:
                first = (attempts, t_, s_, c_)
print(f"pairs tried={attempts}  passing pairs={len(found)}  first success at attempt {first[0]}: t={first[1]} s={first[2]} c={first[3]}")
for t_, s_, c_ in found:
    assert verify_equation(y, t_, c_, s_)
print("passing:", found)

print("\n## cave odds")
print("2^-20 =", 2 ** -20, " 1/2^20 =", 2 ** 20)
