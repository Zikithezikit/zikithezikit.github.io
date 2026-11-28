---
title: "Kyber and ML-KEM: Key Exchange From Noisy Equations"
author: yoav
description: "ML-KEM, the NIST standard derived from Kyber, builds a shared key from noisy linear equations. A 3-dimensional toy shows the whole round trip by hand. The real ML-KEM-768 public key is 1,184 bytes."
date: 2026-02-07 12:00:00 +0200
lang: en
categories: [Cryptography, Security, Quantum Computing]
tags: [ml-kem, kyber, post-quantum-cryptography, lattice-cryptography, learning-with-errors, key-encapsulation, nist, python]
pin: false
math: true
mermaid: false
image:
   path: /assets/images/quantum-cryptography-kyber.jpg
   alt: Image of Kyber Crystals from Star Wars
---

## 01. The question

Two parties who have never met need a shared secret key. Today they get it from RSA or from Diffie-Hellman. Shor's algorithm factors integers and computes discrete logarithms in polynomial time on a quantum computer [\[1\]](#ref-1). Those are the two problems that RSA and Diffie-Hellman rest on. NIST says key establishment built on them is vulnerable to a sufficiently capable quantum computer [\[2, p. 1\]](#ref-2).

ML-KEM is the replacement NIST standardised in FIPS 203, published on 13 August 2024 [\[2\]](#ref-2). It is derived from a scheme called Kyber. ML-KEM is a key-encapsulation mechanism (KEM), so it does not encrypt a message. It produces a shared key. The standard describes the steps [\[2, p. i\]](#ref-2):

1. Alice generates an encapsulation key and a decapsulation key. She keeps the decapsulation key private and sends the encapsulation key to Bob.
2. Bob uses the encapsulation key to make a shared secret key and a ciphertext.
3. Bob sends the ciphertext to Alice.
4. Alice uses the ciphertext and her decapsulation key to compute the same shared secret key.

This post shows the idea inside, with a toy small enough to compute by hand. Then it lists what the real scheme changes.

> The toy numbers are made up for the example. Sizes and parameters of ML-KEM come from FIPS 203 and carry a page number. Anything marked "my calculation" is arithmetic I did on those values.
{: .prompt-info }

## 02. Where does Kyber come from?

NIST issued a call for post-quantum algorithms in December 2016. By the November 2017 deadline 82 candidates had been submitted, and 69 met the requirements for the first round [\[3, p. 1\]](#ref-3). The rest of the path:

| Date | Step | Source |
|---|---|---|
| January 2019 | 26 algorithms move to round 2 | [\[3, p. 1\]](#ref-3) |
| July 2020 | 15 algorithms move to round 3: 7 finalists and 8 alternates | [\[3, p. 1\]](#ref-3) |
| 5 July 2022 | CRYSTALS-KYBER is selected for key establishment | [\[4\]](#ref-4) |
| 13 August 2024 | FIPS 203 (ML-KEM) is published | [\[2\]](#ref-2) |

Kyber was designed by the CRYSTALS team and described in a 2018 paper by Bos et al. [\[5\]](#ref-5). CRYSTALS stands for "Cryptographic Suite for Algebraic Lattices" [\[6\]](#ref-6). ML-KEM is derived from the round-three version of Kyber, and Appendix C of the standard lists the differences [\[2, p. 1\]](#ref-2). The name ML-KEM stands for module-lattice-based KEM [\[2, p. 13\]](#ref-2).

Kyber is a KEM only. Signatures are other standards: NIST selected CRYSTALS-Dilithium, FALCON and SPHINCS+ for them in the same 2022 announcement [\[4\]](#ref-4).

## 03. What is a noisy linear equation?

Take a secret vector $$\mathbf{s}$$ of $$n$$ small numbers and a public $$n \times n$$ matrix $$\mathbf{A}$$ of numbers modulo $$q$$. The product $$\mathbf{A}\mathbf{s}$$ is easy to compute. Given $$\mathbf{A}$$ and $$\mathbf{A}\mathbf{s}$$, finding $$\mathbf{s}$$ is a linear system, and Gaussian elimination solves it.

Now add a small random error vector $$\mathbf{e}$$ to the result:

$$
\mathbf{b} = \mathbf{A}\mathbf{s} + \mathbf{e} \pmod{q}
$$

Everyone sees $$\mathbf{A}$$ and $$\mathbf{b}$$. Only the key owner knows $$\mathbf{s}$$ and $$\mathbf{e}$$. The task of recovering $$\mathbf{s}$$ from $$(\mathbf{A}, \mathbf{b})$$ is the Learning With Errors (LWE) problem, introduced by Regev in 2005. In the standard's words, the noise is such that standard algorithms such as Gaussian elimination are intractable [\[2, p. 13\]](#ref-2).

ML-KEM uses a variant called Module-LWE (MLWE). The numbers in $$\mathbf{s}$$, $$\mathbf{A}$$ and $$\mathbf{e}$$ are replaced by polynomials from a ring $$R_q$$ [\[2, p. 13\]](#ref-2). Section 06 gives the sizes. The structure of the equations stays the same.

The scheme is believed to be secure, not proven. FIPS 203 says it is "believed" to be secure, even against adversaries with a quantum computer [\[2, p. i\]](#ref-2).

## 04. How do two parties end up with the same bit?

The public-key part of ML-KEM follows the pattern below. This is plain LWE with one bit, the shape of K-PKE in FIPS 203 (Algorithms 13 to 15 [\[2, pp. 29-31\]](#ref-2)) without the ring structure.

**Key generation (Alice).** She picks a small secret $$\mathbf{s}$$ and a small error $$\mathbf{e}$$ and publishes

$$
(\mathbf{A},\ \mathbf{b}), \qquad \mathbf{b} = \mathbf{A}\mathbf{s} + \mathbf{e} \pmod{q}
$$

**Encryption of one bit $$m$$ (Bob).** He picks a fresh small vector $$\mathbf{r}$$ and small errors $$\mathbf{e}_1$$ and $$e_2$$. He sends

$$
\mathbf{u} = \mathbf{A}^{T}\mathbf{r} + \mathbf{e}_1, \qquad
v = \mathbf{b}^{T}\mathbf{r} + e_2 + m \cdot \lfloor q/2 \rfloor \qquad \pmod{q}
$$

The bit is stored as 0 or $$\lfloor q/2 \rfloor$$, the two values farthest apart modulo $$q$$.

**Decryption (Alice).** She computes $$w = v - \mathbf{s}^{T}\mathbf{u}$$. Put $$\mathbf{b} = \mathbf{A}\mathbf{s} + \mathbf{e}$$ into $$v$$ and expand:

$$
\begin{aligned}
w &= (\mathbf{A}\mathbf{s} + \mathbf{e})^{T}\mathbf{r} + e_2 + m\lfloor q/2 \rfloor - \mathbf{s}^{T}(\mathbf{A}^{T}\mathbf{r} + \mathbf{e}_1) \\
  &= \underbrace{\mathbf{e}^{T}\mathbf{r} + e_2 - \mathbf{s}^{T}\mathbf{e}_1}_{\text{noise}} + m\lfloor q/2 \rfloor
\end{aligned}
$$

The big terms $$\mathbf{s}^{T}\mathbf{A}^{T}\mathbf{r}$$ cancel. What is left is a sum of products of small numbers, plus the encoded bit. If the noise is smaller than $$q/4$$ in absolute value, $$w$$ is closer to $$m\lfloor q/2 \rfloor$$ than to the other encoding, and Alice reads the bit by taking the nearer one.

An eavesdropper sees $$\mathbf{A}$$, $$\mathbf{b}$$, $$\mathbf{u}$$ and $$v$$. To subtract the same big term she needs $$\mathbf{s}$$.

## 05. A toy small enough to do by hand

ML-KEM-768 uses $$q = 3329$$, vectors of $$k = 3$$ polynomials with 256 coefficients each, and small values from a centered binomial distribution with $$\eta_1 = \eta_2 = 2$$ [\[2, pp. 23, 39\]](#ref-2). The toy uses $$n = 3$$ numbers, $$q = 97$$ and small values in $$\{-1, 0, 1\}$$. The steps are the same as in section 04.

Inputs, all made up for the example:

$$
\mathbf{A} = \begin{bmatrix} 31 & 58 & 12 \\ 76 & 5 & 90 \\ 44 & 63 & 27 \end{bmatrix},\quad
\mathbf{s} = \begin{bmatrix} 1 \\ -1 \\ 1 \end{bmatrix},\quad
\mathbf{e} = \begin{bmatrix} 1 \\ 0 \\ -1 \end{bmatrix}
$$

### Alice makes the key

Each row of $$\mathbf{A}$$ times $$\mathbf{s}$$:

$$
\mathbf{A}\mathbf{s} =
\begin{bmatrix} 31 - 58 + 12 \\ 76 - 5 + 90 \\ 44 - 63 + 27 \end{bmatrix} =
\begin{bmatrix} -15 \\ 161 \\ 8 \end{bmatrix}
$$

Add $$\mathbf{e}$$ and reduce modulo 97:

$$
\mathbf{b} = \begin{bmatrix} -14 \\ 161 \\ 7 \end{bmatrix} \bmod 97 = \begin{bmatrix} 83 \\ 64 \\ 7 \end{bmatrix}
$$

The public key is $$(\mathbf{A}, \mathbf{b})$$. The secret is $$\mathbf{s}$$.

### Bob encrypts the bit 1

The bit 1 is encoded as $$\lfloor 97/2 \rfloor = 48$$. Bob picks $$\mathbf{r} = (1, 1, 0)$$, $$\mathbf{e}_1 = (0, 1, -1)$$ and $$e_2 = 1$$.

The vector $$\mathbf{A}^{T}\mathbf{r}$$ is the sum of the first two rows of $$\mathbf{A}$$, since $$\mathbf{r}$$ selects them:

$$
\mathbf{A}^{T}\mathbf{r} = \begin{bmatrix} 31 + 76 \\ 58 + 5 \\ 12 + 90 \end{bmatrix} = \begin{bmatrix} 107 \\ 63 \\ 102 \end{bmatrix},
\qquad
\mathbf{u} = \begin{bmatrix} 107 \\ 64 \\ 101 \end{bmatrix} \bmod 97 = \begin{bmatrix} 10 \\ 64 \\ 4 \end{bmatrix}
$$

For the second part, $$\mathbf{b}^{T}\mathbf{r} = 83 + 64 = 147$$, so

$$
v = 147 + 1 + 48 = 196 \bmod 97 = 2
$$

Bob sends $$(\mathbf{u}, v) = ((10, 64, 4),\ 2)$$.

### Alice decrypts

$$
\mathbf{s}^{T}\mathbf{u} = 10 - 64 + 4 = -50, \qquad w = 2 - (-50) = 52
$$

The distance from 52 to 0 is 45. The distance from 52 to 48 is 4. The nearer one is 48, so Alice reads the bit 1.

The noise in $$w$$ is $$52 - 48 = 4$$. The formula from section 04 gives the same value:

$$
\mathbf{e}^{T}\mathbf{r} + e_2 - \mathbf{s}^{T}\mathbf{e}_1 = 1 + 1 - (-2) = 4
$$

### Will it always decode?

Every entry of $$\mathbf{e}$$, $$\mathbf{r}$$, $$\mathbf{s}$$, $$\mathbf{e}_1$$ and $$e_2$$ is in $$\{-1, 0, 1\}$$. So the noise is at most $$3 + 1 + 3 = 7$$ in absolute value. That is below $$q/4 = 24.25$$ (my calculation).

I also ran every choice of $$\mathbf{r}$$, $$\mathbf{e}_1$$, $$e_2$$ and bit for this key: $$3^3 \cdot 3^3 \cdot 3 \cdot 2 = 4{,}374$$ encryptions. All 4,374 decoded correctly (measured with `_figures/2026-02-07-kyber-crystal-cryptography/toy.py` in the site repository).

### What the toy does not have

The toy is not secure. With $$n = 3$$ there are only 27 ternary secrets. A loop over all of them, keeping those where $$\mathbf{b} - \mathbf{A}\mathbf{s}$$ has every entry in $$\{-1, 0, 1\}$$, returns exactly one: $$\mathbf{s} = (1, -1, 1)$$. At the real sizes the search space and the lattice problem are far larger, and the standard bases its claim on the hardness of MLWE [\[2, p. 13\]](#ref-2).

## 06. What does ML-KEM change?

Four things, all from FIPS 203.

- **Polynomials instead of numbers.** Each entry is a polynomial with $$n = 256$$ coefficients modulo $$q = 3329$$. The vectors have $$k$$ entries, with $$k = 3$$ for ML-KEM-768 [\[2, p. 39\]](#ref-2).
- **256 bits at once.** The message in K-PKE.Encrypt is 32 bytes, one bit per coefficient [\[2, pp. 30-31\]](#ref-2).
- **Compression.** The ciphertext parts $$\mathbf{u}$$ and $$v$$ are compressed with parameters $$d_u$$ and $$d_v$$. The ciphertext is $$32(d_u k + d_v)$$ bytes [\[2, p. 30\]](#ref-2).
- **A transform on top.** ML-KEM first builds an encryption scheme from MLWE, then applies the Fujisaki-Okamoto transform to get a KEM. The result is secure in a significantly more general attack model than the encryption scheme alone, and is believed to be IND-CCA2 secure [\[2, p. 13\]](#ref-2).

For ML-KEM-768 the formulas reproduce the sizes in the standard. The encapsulation key is $$384k + 32 = 1{,}184$$ bytes (the formula is from Algorithm 14 [\[2, p. 30\]](#ref-2)). The ciphertext is $$32(10 \cdot 3 + 4) = 1{,}088$$ bytes, with $$d_u = 10$$ and $$d_v = 4$$ (my calculation).

## 07. How big are the keys?

Sizes in bytes, from Tables 2 and 3 of FIPS 203 [\[2, p. 39\]](#ref-2):

| Parameter set | $$k$$ | Encapsulation key | Decapsulation key | Ciphertext | Shared secret |
|---|---:|---:|---:|---:|---:|
| ML-KEM-512 | 2 | 800 | 1,632 | 768 | 32 |
| ML-KEM-768 | 3 | 1,184 | 2,400 | 1,088 | 32 |
| ML-KEM-1024 | 4 | 1,568 | 3,168 | 1,568 | 32 |

The standard claims security category 1, 3 and 5 for the three sets, in that order, and NIST recommends ML-KEM-768 as the default [\[2, p. 40\]](#ref-2). The Kyber authors recommend the same set, and recommend using Kyber together with an established pre-quantum scheme such as elliptic-curve Diffie-Hellman [\[6\]](#ref-6).

An RSA-2048 public key contains a 2,048-bit modulus, which is 256 bytes (formula: 2,048 / 8). The ML-KEM-768 encapsulation key is 1,184 bytes, about 4.6 times as large (my calculation). This post gives no timings. I did not measure them, and the reference implementations report cycle counts per platform [\[6\]](#ref-6).

## 08. What software has it?

- OpenSSL 3.5.0, released on 8 April 2025, lists support for ML-KEM, ML-DSA and SLH-DSA [\[7\]](#ref-7).
- liboqs is an open source C library for quantum-safe algorithms. Its KEM list includes ML-KEM [\[8\]](#ref-8).
- kyber-py is a pure Python implementation of ML-KEM. Its README says it is an educational project and must not be used for cryptographic applications [\[9\]](#ref-9).

## 09. Try it

The real scheme, with kyber-py [\[9\]](#ref-9). Educational use only.

```bash
pip install kyber-py
```

```python
from kyber_py.ml_kem import ML_KEM_768

ek, dk = ML_KEM_768.keygen()            # Alice: encapsulation key (public), decapsulation key (secret)
key, c = ML_KEM_768.encaps(ek)          # Bob: shared secret and ciphertext
assert ML_KEM_768.decaps(dk, c) == key  # Alice gets the same shared secret
print(len(ek), len(dk), len(c), len(key))
```

Output with kyber-py 1.2.0 (measured):

```
1184 2400 1088 32
```

The four sizes match Table 3 of the standard. The toy from section 05, in plain Python:

```python
q, half = 97, 48
A = [[31, 58, 12], [76, 5, 90], [44, 63, 27]]
s, e = [1, -1, 1], [1, 0, -1]                    # secret and key error
b = [(sum(A[i][j] * s[j] for j in range(3)) + e[i]) % q for i in range(3)]

r, e1, e2, bit = [1, 1, 0], [0, 1, -1], 1, 1     # Bob: randomness, errors, the bit
u = [(sum(A[i][j] * r[i] for i in range(3)) + e1[j]) % q for j in range(3)]
v = (sum(b[i] * r[i] for i in range(3)) + e2 + bit * half) % q

w = (v - sum(u[j] * s[j] for j in range(3))) % q # Alice
print(b, u, v, w)                                # [83, 64, 7] [10, 64, 4] 2 52
print(1 if abs(w - half) < min(w, q - w) else 0) # 1
```

Set `bit` to 0 and `w` becomes 4, nearest to 0, so the script prints 0 (measured). Set `r` to `[30, 1, 0]` and the noise passes 24: both bits then decode wrongly (measured).

## Sources

<span id="ref-1"></span>\[1\] Shor, P. W. (1997). _Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer_. SIAM J. Comput. 26, 1484. arXiv:quant-ph/9508027. [https://arxiv.org/abs/quant-ph/9508027](https://arxiv.org/abs/quant-ph/9508027)

<span id="ref-2"></span>\[2\] NIST (2024). _FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard_. [https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf)

<span id="ref-3"></span>\[3\] Alagic, G., et al. (2022). _Status Report on the Third Round of the NIST Post-Quantum Cryptography Standardization Process_. NIST IR 8413-upd1. [https://doi.org/10.6028/NIST.IR.8413-upd1](https://doi.org/10.6028/NIST.IR.8413-upd1)

<span id="ref-4"></span>\[4\] NIST (2022). _PQC candidates to be standardized and round 4 advancers_, news item of 5 July 2022. [https://csrc.nist.gov/news/2022/pqc-candidates-to-be-standardized-and-round-4](https://csrc.nist.gov/news/2022/pqc-candidates-to-be-standardized-and-round-4)

<span id="ref-5"></span>\[5\] Bos, J., Ducas, L., Kiltz, E., Lepoint, T., Lyubashevsky, V., Schanck, J. M., Schwabe, P., Seiler, G., & Stehlé, D. (2018). _CRYSTALS-Kyber: a CCA-secure module-lattice-based KEM_. IEEE EuroS&P 2018. [https://eprint.iacr.org/2017/634](https://eprint.iacr.org/2017/634)

<span id="ref-6"></span>\[6\] CRYSTALS team. _Kyber_. [https://pq-crystals.org/kyber/index.shtml](https://pq-crystals.org/kyber/index.shtml)

<span id="ref-7"></span>\[7\] OpenSSL project. _OpenSSL 3.5 release notes_. [https://openssl-library.org/news/openssl-3.5-notes/](https://openssl-library.org/news/openssl-3.5-notes/)

<span id="ref-8"></span>\[8\] Open Quantum Safe project. _liboqs_. [https://openquantumsafe.org/liboqs/](https://openquantumsafe.org/liboqs/)

<span id="ref-9"></span>\[9\] Pope, G. _kyber-py_. [https://github.com/GiacomoPope/kyber-py](https://github.com/GiacomoPope/kyber-py)
