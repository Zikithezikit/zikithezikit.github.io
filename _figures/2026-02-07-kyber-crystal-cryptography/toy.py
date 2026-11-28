"""Toy LWE encryption of one bit, in the same shape as K-PKE in FIPS 203.

No polynomial ring, no compression, no Fujisaki-Okamoto transform.
n = 3, q = 97. Secrets and errors are in {-1, 0, 1}.
Run: python3 toy.py
"""
import itertools

n, q = 3, 97
half = q // 2                      # 48: the bit 1 is encoded as 48, the bit 0 as 0

A = [[31, 58, 12],
     [76, 5, 90],
     [44, 63, 27]]                 # public matrix, made up for the example
s = [1, -1, 1]                     # secret
e = [1, 0, -1]                     # key error

def matvec(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]

def transpose(M):
    return [list(r) for r in zip(*M)]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def md(x):
    return x % q

def centered(x):
    x = x % q
    return x - q if x > q // 2 else x

# key generation
As = matvec(A, s)
b_raw = [As[i] + e[i] for i in range(n)]
b = [md(x) for x in b_raw]
print("## key generation")
print("A s        =", As)
print("A s + e    =", b_raw, "-> mod", q, "->", b)

# encryption of the bit 1
bit = 1
r = [1, 1, 0]                      # one-time randomness
e1 = [0, 1, -1]
e2 = 1
At_r = matvec(transpose(A), r)
u_raw = [At_r[i] + e1[i] for i in range(n)]
u = [md(x) for x in u_raw]
bt_r = dot(b, r)
v_raw = bt_r + e2 + bit * half
v = md(v_raw)
print("\n## encryption of bit", bit)
print("A^T r      =", At_r)
print("A^T r + e1 =", u_raw, "-> mod", q, "->", u)
print("b . r      =", bt_r)
print("b.r+e2+enc =", bt_r, "+", e2, "+", bit * half, "=", v_raw, "-> mod", q, "->", v)

# decryption
u_s = dot(u, s)
w_raw = v - u_s
w = md(w_raw)
print("\n## decryption")
print("u . s      =", u_s)
print("w = v - u.s=", v, "-", u_s, "=", w_raw, "-> mod", q, "->", w)
noise = centered(w - bit * half)
print("w - 48     =", w - bit * half, "(noise term)")
# noise term from the algebra: e.r + e2 - s.e1
algebra = dot(e, r) + e2 - dot(s, e1)
print("e.r + e2 - s.e1 =", dot(e, r), "+", e2, "-", dot(s, e1), "=", algebra)
assert noise == algebra
dist0 = min(w, q - w)
dist1 = abs(w - half)
print("distance of w to 0 =", dist0, ", to 48 =", dist1)
decoded = 1 if dist1 < dist0 else 0
print("decoded bit =", decoded)
assert decoded == bit

# the noise bound: every entry is in {-1,0,1}, so |e.r| <= n, |e2| <= 1, |s.e1| <= n
bound = n + 1 + n
print("\n## noise bound")
print("largest possible |noise| =", n, "+ 1 +", n, "=", bound)
print("decoding is safe while |noise| <", q / 4, "(q/4)")
assert bound < q / 4

# exhaustive check for this key: all r, e1, e2 in {-1,0,1}, both bits
ok = 0
total = 0
for rr in itertools.product([-1, 0, 1], repeat=n):
    for ee1 in itertools.product([-1, 0, 1], repeat=n):
        for ee2 in [-1, 0, 1]:
            for bb in (0, 1):
                uu = [md(x + y) for x, y in zip(matvec(transpose(A), list(rr)), ee1)]
                vv = md(dot(b, list(rr)) + ee2 + bb * half)
                ww = md(vv - dot(uu, s))
                d = 1 if abs(ww - half) < min(ww, q - ww) else 0
                total += 1
                ok += (d == bb)
print("\n## exhaustive check for this key")
print(ok, "of", total, "encryptions decode correctly")
assert ok == total

# what the attacker sees: A and b. At n = 3 the secret falls to brute force.
cands = []
for cs in itertools.product([-1, 0, 1], repeat=n):
    resid = [centered(b[i] - dot(A[i], list(cs))) for i in range(n)]
    if all(abs(x) <= 1 for x in resid):
        cands.append((cs, resid))
print("\n## brute force over the 3^3 = 27 ternary secrets")
print("secrets whose residual b - A s has every entry in {-1,0,1}:", cands)
assert [list(c[0]) for c in cands] == [s]

# sizes from FIPS 203, Algorithms 13 to 15 and Table 3 (k = 3, d_u = 10, d_v = 4)
k, du, dv = 3, 10, 4
print("\n## ML-KEM-768 sizes, from the formulas in FIPS 203")
print("encapsulation key 384k + 32 =", 384 * k + 32)
print("ciphertext 32(du k + dv)    =", 32 * (du * k + dv))
