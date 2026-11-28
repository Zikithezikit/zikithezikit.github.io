---
title: "Schnorr's Protocol: A Zero-Knowledge Proof by Hand"
author: yoav
description: "A Schnorr proof shows you know x behind y = g^x with three numbers: a commitment, a challenge and a response. Worked by hand in a group of 11 elements, including how one reused nonce gives x away."
date: 2026-02-21 10:00:00 +0200
lang: en
categories: [Cryptography, Mathematics, Security]
tags: [zero-knowledge, schnorr, fiat-shamir, discrete-logarithm, cryptography, python]
pin: false
math: true
mermaid: false
image:
   path: /assets/images/zkp-schnorr.jpg
   alt: Zero Knowledge Proofs concept illustration
---

## 01. The question

A password check sends the password to the server, so the server learns it. A proof of knowledge aims at the opposite: show that you know a secret, and send nothing the secret can be computed from.

There are two parties. The **prover** holds a secret $$x$$. The **verifier** holds a public value computed from it, here $$y = g^x$$. The prover wants to convince the verifier that it knows $$x$$ without sending $$x$$.

The notion comes from Goldwasser, Micali and Rackoff [\[1\]](#ref-1). A proof of this kind has three properties:

- Completeness: a prover who knows $$x$$ always convinces the verifier.
- Soundness: a prover who does not know $$x$$ is rejected, except with a small probability.
- Zero knowledge: the verifier learns nothing it could not have computed without the prover, beyond the fact that the prover knows $$x$$.

Schnorr's protocol does this in three messages. Section 05 runs it by hand in a group with 11 elements.

> Every number from section 05 on is made up for the example and was computed by a script, `_figures/2026-02-21-zero-knowledge-proofs-schnorr/toy.py` in the site repository. The group is far too small to be secure.
{: .prompt-info }

## 02. A cave first

The standard story is a cave [\[2\]](#ref-2). The cave is a ring with one entrance. A locked door joins the two sides at the back, one side called left and the other right.

Alice walks in and picks a side. Bob waits outside and cannot see which one. Then he shouts a side, and Alice has to come out of it.

- If Alice has the key to the door, she can always do it. She walks through the door when she has to switch sides.
- If she does not, she succeeds only when Bob happens to shout the side she entered. That is one chance in 2.

After $$n$$ rounds a cheater survives with probability $$2^{-n}$$. For $$n = 20$$ that is 1 in 1,048,576 (formula).

Suppose Bob films every round. The film proves nothing to a third person, because Alice and Bob could have agreed on the sides in advance and staged it. A record that anyone could fake carries no information about the key. Section 07 makes the same point with numbers.

Schnorr's protocol replaces the coin flip by a challenge $$c$$ drawn from a set of $$q$$ values, so one round leaves a cheater a chance of 1 in $$q$$.

## 03. The group and the hard problem

The protocol needs a group where raising to a power is easy and undoing it is hard. The usual choice is the numbers modulo a prime $$p$$ and a subgroup of prime order $$q$$, where $$q$$ divides $$p - 1$$ and $$g$$ is an element of order $$q$$. The protocol is Schnorr's [\[3\]](#ref-3). RFC 8235 uses this setup for it [\[4\]](#ref-4).

The prover picks a secret $$x$$ in $$0, 1, \dots, q-1$$ and publishes

$$
y = g^x \bmod p
$$

Going from $$x$$ to $$y$$ is one modular exponentiation. Going from $$y$$ back to $$x$$ is the discrete logarithm problem. RFC 8235 assumes it is intractable, and recommends $$p$$ of about 2048 to 3072 bits and $$q$$ of 224 to 256 bits for a security level of at least 128 bits [\[4\]](#ref-4).

Exponents live modulo $$q$$. Since $$g^q \equiv 1 \pmod{p}$$, two exponents that differ by a multiple of $$q$$ give the same power. The verifier also checks that $$y$$ is in the subgroup, that is $$y^q \equiv 1 \pmod{p}$$ [\[4\]](#ref-4).

## 04. Three moves

| move | who | sends | how it is computed |
|---|---|---|---|
| 1. commit | prover | $$t$$ | pick a random $$k$$ in $$0, \dots, q-1$$, then $$t = g^k \bmod p$$ |
| 2. challenge | verifier | $$c$$ | pick a random $$c$$ in $$0, \dots, q-1$$ |
| 3. respond | prover | $$s$$ | $$s = (k + c\,x) \bmod q$$ |

The verifier accepts if

$$
g^s \equiv t \cdot y^c \pmod{p}
$$

It holds for an honest prover because the exponents add:

$$
g^s = g^{k + c x} = g^k \cdot \left(g^x\right)^c = t \cdot y^c
$$

The nonce $$k$$ is a one-time mask. Without it the response would be $$s = c\,x \bmod q$$, and dividing by $$c$$ would give $$x$$.

RFC 8235 writes the response as $$r = v - a c \bmod q$$ and checks $$V = g^r A^c$$ [\[4\]](#ref-4). That is the same protocol with the sign flipped. It also draws $$c$$ from $$2^{t}$$ values, for example $$t = 160$$, and not from $$q$$ values. I use the range $$0, \dots, q-1$$ so that the toy stays small.

## 05. A group small enough to do by hand

Real parameters are a 2048-bit $$p$$ and a 256-bit $$q$$. The toy uses $$p = 23$$, $$q = 11$$ and $$g = 2$$. The moves are identical.

Check the group. $$p - 1 = 22 = 11 \times 2$$, so 11 divides it. The powers of 2 modulo 23:

| $$e$$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $$2^e \bmod 23$$ | 1 | 2 | 4 | 8 | 16 | 9 | 18 | 13 | 3 | 6 | 12 | 1 |

$$2^{11} \bmod 23 = 1$$ and 11 is prime, so 2 has order 11. The subgroup is 1, 2, 3, 4, 6, 8, 9, 12, 13, 16, 18. The row repeats after $$e = 11$$, which is why exponents are taken modulo 11.

The prover picks the secret $$x = 7$$. The public key is $$y = 2^7 \bmod 23 = 13$$. As a check, $$13^{11} \bmod 23 = 1$$, so 13 is in the subgroup.

| value | symbol | number | who knows it |
|---|---|---:|---|
| prime | $$p$$ | 23 | everyone |
| subgroup order | $$q$$ | 11 | everyone |
| generator | $$g$$ | 2 | everyone |
| public key | $$y$$ | 13 | everyone |
| secret | $$x$$ | 7 | prover |

Elliptic-curve versions run the same moves in a group of curve points. Computing $$g^k$$ becomes a scalar multiplication $$k \cdot G$$ [\[4\]](#ref-4).

## 06. The three moves, with numbers

**Move 1.** The prover picks $$k = 4$$ and sends $$t = 2^4 \bmod 23 = 16$$.

**Move 2.** The verifier picks $$c = 5$$ and sends it.

**Move 3.** The prover computes and sends $$s$$:

$$
s = (k + c\,x) \bmod q = (4 + 5 \cdot 7) \bmod 11 = 39 \bmod 11 = 6
$$

**The check.** Both sides of $$g^s \equiv t \cdot y^c$$ are computed modulo 23:

$$
\begin{array}{lll}
\text{left} & g^s = 2^6 = 64 \equiv 18 & \\
\text{right} & t \cdot y^c = 16 \cdot 13^5 = 16 \cdot 4 = 64 \equiv 18 & (13^5 \bmod 23 = 4)
\end{array}
$$

Both sides are 18, so the verifier accepts. The verifier saw $$t = 16$$, $$c = 5$$ and $$s = 6$$. It never saw $$k$$ or $$x$$.

## 07. Why the verifier cannot find x

The verifier knows $$y = 13$$ and the transcript $$(t, c, s) = (16, 5, 6)$$. There are three ways to try for $$x$$.

**Solve the response.** The equation $$s = k + c\,x \bmod q$$ has two unknowns, $$k$$ and $$x$$. Fix $$x = 7$$ and $$c = 5$$ and let $$k$$ run over all 11 values. The responses are 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1. Each value of $$s$$ appears exactly once. So when $$k$$ is uniform, $$s$$ is uniform, and $$s$$ alone says nothing about $$x$$.

This is also why the reduction modulo $$q$$ matters. Without it the response is the plain integer 39, and $$39 / 5 = 7.8$$ lands next to $$x = 7$$.

**Take the logarithm of y.** Look 13 up in the table of powers: $$2^7 = 13$$. Here that is a table of 11 entries. At 256-bit $$q$$ no such table exists, and finding $$x$$ is the discrete logarithm problem from section 03.

**Look for a pattern in the transcript.** Anyone can write a passing transcript without $$x$$. Pick $$c = 3$$ and $$s = 9$$ at random, then solve the check for $$t$$:

$$
t = g^s \cdot y^{-c} \bmod p = 2^9 \cdot 13^{-3} \bmod 23 = 12
$$

The check gives $$g^s = 2^9 \bmod 23 = 6$$ and $$t \cdot y^c = 12 \cdot 13^3 \bmod 23 = 6$$. The transcript $$(12, 3, 9)$$ passes, and I made it without $$x$$.

Real transcripts have the same shape. In both cases $$t$$ and $$c$$ are uniform, and $$s$$ is the one value that makes the check hold. So a transcript contains nothing that the verifier could not have produced alone. That is the zero-knowledge property, in the form of a simulator.

The simulator picked $$c$$ before $$t$$. A real verifier picks $$c$$ after seeing $$t$$, so a prover without $$x$$ can only guess $$c$$ in advance, with probability 1 in 11. That is soundness. In the toy it is weak. At $$q \approx 2^{256}$$ it is negligible.

> This argument covers a verifier that picks $$c$$ at random. RFC 8235 makes the same assumption of an honest verifier [\[4\]](#ref-4).
{: .prompt-warning }

## 08. Reuse a nonce and x falls out

Suppose the prover uses $$k = 4$$ twice, so $$t = 16$$ both times. The verifier asks $$c_1 = 5$$ once and $$c_2 = 9$$ the other time. The responses are

$$
s_1 = (4 + 5 \cdot 7) \bmod 11 = 6, \qquad s_2 = (4 + 9 \cdot 7) \bmod 11 = 1
$$

Both pass the check. Subtract them. The nonce cancels:

$$
s_1 - s_2 = (c_1 - c_2)\,x \pmod{q}
$$

Then divide by $$c_1 - c_2$$ modulo 11. Here $$s_1 - s_2 = 5$$, and $$c_1 - c_2 = -4 \equiv 7$$. The inverse of 7 modulo 11 is 8, because $$7 \cdot 8 = 56 = 5 \cdot 11 + 1$$. So

$$
x = 5 \cdot 8 \bmod 11 = 40 \bmod 11 = 7
$$

That is the secret. The nonce follows too: $$k = s_1 - c_1 x = 6 - 35 \equiv 4 \pmod{11}$$. RFC 8235 gives the same formula and requires a secure random number generator for $$k$$ [\[4\]](#ref-4). A nonce must be fresh on every run.

The same subtraction explains why this is a proof of knowledge. A prover who could answer two different challenges for one $$t$$ could compute $$x$$ this way. So any prover that passes reliably must know $$x$$.

## 09. Remove the verifier with a hash

The three moves need a verifier who is online and who picks $$c$$ at random. Fiat and Shamir showed how to drop the second requirement [\[5\]](#ref-5). The prover computes the challenge itself, as a hash of what it has committed to:

$$
c = H(g, y, t) \bmod q
$$

The proof is the pair $$(t, s)$$. The verifier recomputes $$c$$ from $$t$$ and runs the same check. RFC 8235 hashes $$g$$, $$V$$, $$A$$, a user ID and optional context with SHA-256 or SHA3-256 [\[4\]](#ref-4). It models the hash as a random oracle that plays the honest verifier [\[4\]](#ref-4).

The toy hashes the text `2,13,6` (that is $$g$$, $$y$$, $$t$$ in decimal) with SHA-256 and reduces the 256-bit result modulo 11.

The prover picks $$k = 9$$, so $$t = 2^9 \bmod 23 = 6$$. The hash of `2,13,6` is

```text
00223fe57732cfc1581b078e7249b7bd529dab9a6ce0e4c768d5f733b883e4c3
```

Taken as a number modulo 11 it is 3, so $$c = 3$$. Then

$$
s = (9 + 3 \cdot 7) \bmod 11 = 30 \bmod 11 = 8
$$

The proof is $$(t, s) = (6, 8)$$. The verifier hashes `2,13,6`, gets $$c = 3$$, and compares $$g^s = 2^8 \bmod 23 = 3$$ with $$t \cdot y^c = 6 \cdot 13^3 \bmod 23 = 6 \cdot 12 \bmod 23 = 3$$. They match.

A forger who does not know $$x$$ can try pairs $$(s, c)$$, set $$t = g^s \cdot y^{-c}$$, and hope that the hash of $$t$$ gives back $$c$$. I tried all 121 pairs. Exactly 11 pass, one in 11, and the first was found at attempt 8: $$t = 18$$, $$s = 0$$, $$c = 7$$. That is why the challenge space has to be huge. RFC 8235 asks for a hash output at least as long as $$q$$ [\[4\]](#ref-4).

> Anyone who sees $$(t, s)$$ can show it to another verifier. RFC 8235 puts a user ID and optional context in the hash so that a proof is bound to the party it was made for [\[4\]](#ref-4).
{: .prompt-warning }

## 10. The same proof as a signature

Put a message $$m$$ into the hash and the proof is tied to $$m$$:

$$
c = H(g, y, t, m) \bmod q
$$

The pair $$(t, s)$$ is then a Schnorr signature on $$m$$ [\[3\]](#ref-3). BIP 340 specifies it for the curve secp256k1. It computes $$e = H(R \Vert P \Vert m) \bmod n$$ and $$s = (k + e\,d) \bmod n$$, and the verifier checks $$R = s \cdot G - e \cdot P$$. A signature is 64 bytes, $$R$$ and $$s$$ [\[6\]](#ref-6). That is the equation from section 04 in additive notation, with the hash supplying $$c$$.

## 11. Try it

The toy group, the hash challenge and the check, in plain Python. It needs no install.

```python
import hashlib, secrets

p, q, g = 23, 11, 2                      # toy group: g has order 11 modulo 23
x = 7                                    # the secret
y = pow(g, x, p)                         # the public key, 13

def H(*parts):                           # challenge: hash, then reduce mod q
    data = ",".join(map(str, parts)).encode()
    return int.from_bytes(hashlib.sha256(data).digest(), "big") % q

def prove(x):
    k = secrets.randbelow(q)             # a fresh nonce on every run
    t = pow(g, k, p)                     # move 1: commitment
    c = H(g, y, t)                       # move 2: challenge from the hash
    return t, (k + c * x) % q            # move 3: response

def verify(y, t, s):
    assert pow(y, q, p) == 1             # y must lie in the subgroup
    return pow(g, s, p) == t * pow(y, H(g, y, t), p) % p

t, s = prove(x)
print(verify(y, t, s))                   # True
print(verify(y, t, (s + 1) % q))         # False: a wrong response is rejected
```

The output is `True`, then `False`.

## Sources

<span id="ref-1"></span>\[1\] Goldwasser, S., Micali, S., & Rackoff, C. (1989). The knowledge complexity of interactive proof systems. _SIAM Journal on Computing_, 18(1), 186-208. [https://doi.org/10.1137/0218012](https://doi.org/10.1137/0218012)

<span id="ref-2"></span>\[2\] Quisquater, J.-J., Quisquater, M., Quisquater, M., Quisquater, M., Guillou, L., Guillou, M. A., Guillou, G., Guillou, A., Guillou, G., & Guillou, S. (1989). How to explain zero-knowledge protocols to your children. In _Advances in Cryptology: CRYPTO '89 Proceedings_ (pp. 628-631). Springer. [https://doi.org/10.1007/0-387-34805-0_60](https://doi.org/10.1007/0-387-34805-0_60)

<span id="ref-3"></span>\[3\] Schnorr, C. P. (1991). Efficient signature generation by smart cards. _Journal of Cryptology_, 4(3), 161-174. [https://doi.org/10.1007/BF00196725](https://doi.org/10.1007/BF00196725)

<span id="ref-4"></span>\[4\] Hao, F. (Ed.). (2017). _Schnorr non-interactive zero-knowledge proof_. RFC 8235, IETF. [https://www.rfc-editor.org/rfc/rfc8235](https://www.rfc-editor.org/rfc/rfc8235)

<span id="ref-5"></span>\[5\] Fiat, A., & Shamir, A. (1986). How to prove yourself: practical solutions to identification and signature problems. In _Advances in Cryptology: CRYPTO '86_ (pp. 186-194). Springer. [https://doi.org/10.1007/3-540-47721-7_12](https://doi.org/10.1007/3-540-47721-7_12)

<span id="ref-6"></span>\[6\] Wuille, P., Nick, J., & Ruffing, T. _BIP 340: Schnorr signatures for secp256k1_. [https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki)
