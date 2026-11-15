---
title: "Ribbon Filters: The Maths Inside pyribbon"
author: yoav
date: 2026-11-15 08:00:00 +0200
lang: en
categories: [algorithms, data-structures]
tags: [ribbon-filter, bloom-filter, xor-filter, probabilistic-data-structures, gaussian-elimination, gf2, python, c, pyribbon, hashing]
pin: false
math: true
mermaid: false
media_subpath: /assets/images/pyribbon-explainer/
image:
   path: cover.png
   alt: "Cover: the words Ribbon filters and 9 bits per key next to a diagonal band of blue and green squares, the shape of the equation matrix inside a ribbon filter"
---

## 01. The question

Most lookups in a big system find nothing. Each one still pays for a disk read or a network hop just to learn "no such key".

Answering "no" from memory first removes most of that cost, but holding every key in memory is what you were trying to avoid. A filter is the compromise: a small structure that answers one of two things.

![Diagram: a key goes into a ribbon filter, which answers either "no", meaning definitely not in the set, or "maybe", meaning go and check](contract.svg){: w="900" h="410" .shadow }
_The whole contract. "No" is always right. "Maybe" is right most of the time._

The error only goes one way. A key that was in the set when the filter was built always gets "maybe". A key that was not in the set gets "maybe" with a probability you choose, $$2^{-r}$$, where $$r$$ is the number of fingerprint bits. In pyribbon that setting is called `fp_bits`.

Where this shows up:

- A storage engine asks "could this key be in this file?" before it reads the file. RocksDB has offered Ribbon filters for this since version 6.15 [\[3\]](#ref-3).
- A service holds a large blocklist, such as leaked password hashes or banned IDs, and wants to ship it to many machines without shipping every entry.
- A crawler asks "have I seen this URL?" billions of times.

I wrote [pyribbon](https://github.com/zikithezikit/pyribbon) [\[4\]](#ref-4), a Python library with a C11 core, to build this kind of filter. It implements the Ribbon filter of Dillinger and Walzer [\[1\]](#ref-1), written from their papers and not ported from existing code. This post walks through how it works and does the arithmetic by hand wherever that is possible.

> Numbers marked "measured" are my own measurements with pyribbon 0.1.2, and so is the benchmark chart in section 11.
{: .prompt-info }

## 02. How much does "maybe" cost?

Start with the classic answer, the Bloom filter [\[7\]](#ref-7). It sets $$k$$ bits in a bit array for every key. With the best choice of $$k$$, the false-positive rate is

$$
\varepsilon = \left(\tfrac{1}{2}\right)^{k}, \qquad k = \frac{m}{n}\ln 2
$$

where $$m$$ is the number of bits and $$n$$ the number of keys. Solve the second equation for the space per key and put $$k = \log_2(1/\varepsilon)$$ into it:

$$
\frac{m}{n} = \frac{k}{\ln 2} = \frac{\log_2(1/\varepsilon)}{\ln 2} \approx 1.44\,\log_2(1/\varepsilon)
$$

There is also a floor that no structure can beat. To get a false-positive rate of $$\varepsilon$$ you need at least $$\log_2(1/\varepsilon)$$ bits per key. With $$r$$ fingerprint bits that floor is exactly $$r$$.

So a Bloom filter pays 44% more than the floor. For $$r = 8$$ (one wrong "maybe" in 256) that is 11.52 bits per key against a floor of 8. A Ribbon filter lands much closer to the floor:

![Grouped bars of bits per key at r = 4, 8, 12 and 16: the lower bound, pyribbon measured at one million keys, and a Bloom filter](bits-per-key.png){: w="1191" h="721" .shadow }
_pyribbon values are measured at 1,000,000 keys and include the 64-byte header. Bloom values are the 1.44 × r formula._

At $$r = 8$$ that is 8.99 bits per key, 22% less than Bloom. The extra 12% over the floor is the price of the method, and section 06 shows where it comes from.

## 03. Store equations, not keys

A Ribbon filter, like its relatives the Xor and Fuse filters [\[8\]](#ref-8), never stores the keys. It stores a table $$Z$$ chosen so that one equation per key comes out true.

### A bit of arithmetic over GF(2)

GF(2) is the world where the only numbers are 0 and 1, and addition wraps around. Addition is XOR, written $$\oplus$$:

$$
0 \oplus 0 = 0,\quad 0 \oplus 1 = 1,\quad 1 \oplus 0 = 1,\quad 1 \oplus 1 = 0
$$

Multiplication is AND. The dot product of a 0/1 mask $$c$$ with a vector of table entries is the XOR of the entries the mask selects:

$$
c \cdot Z = \bigoplus_{k} c_k\, Z_k
$$

Each entry of $$Z$$ is not one bit but a small number of $$r$$ bits, and XOR works on all $$r$$ bits at once. XOR is the only arithmetic the filter needs.

### One equation per key

Hash a key and you get three things: a start row $$s$$, a mask $$c$$ that is $$w$$ bits wide, and a tag $$b$$ of $$r$$ bits. The key's equation is

$$
\bigoplus_{k=0}^{w-1} c_k\, Z_{s+k} = b
$$

The mask only looks at $$w$$ consecutive rows, starting at $$s$$. That is what makes the matrix a band, the "ribbon" of the name. If you stack all $$n$$ equations, you get a linear system $$A\,Z = B$$ where each row of $$A$$ has its ones inside a narrow window.

![Diagram of build and query: keys become equations, the equations are solved into a table Z, and a query evaluates the same equation against Z and compares with the tag](pipeline.svg){: w="900" h="430" .shadow }
_Building solves the system once. A query only evaluates one equation._

A query does not search for the key. It recomputes $$s$$, $$c$$ and $$b$$, XORs the rows of $$Z$$ that $$c$$ selects, and checks whether the result equals $$b$$.

- For a key that was in the build set the answer is always yes, because $$Z$$ was solved for exactly that equation.
- For a key that was not, the tag $$b$$ comes from a hash that, for a good hash function, is independent of everything that shaped $$Z$$. The XOR result is some $$r$$-bit value and $$b$$ is a different, independent $$r$$-bit value, so they match with probability $$2^{-r}$$.

That is why the false-positive rate of the standard Ribbon filter is exactly $$2^{-r}$$. Section 09 checks it by measurement.

## 04. A filter small enough to do by hand

pyribbon uses windows of $$w = 64$$ rows and, by default, $$r = 8$$ tag bits. Nobody can do that on paper, so here is a shrunken copy with $$w = 4$$, $$r = 2$$ and 10 rows. The mechanics are identical.

### The equations

Seven keys, each with a start row, a four-row mask and a two-bit tag:

| key | start | mask (rows in order) | rows it touches | tag |
|---|---:|:---:|---|:---:|
| alice | 2 | 1101 | 2, 3, 5 | 11 |
| bob | 1 | 1100 | 1, 2 | 10 |
| carol | 6 | 1000 | 6 | 00 |
| dave | 1 | 1011 | 1, 3, 4 | 10 |
| erin | 0 | 1001 | 0, 3 | 10 |
| frank | 2 | 1001 | 2, 5 | 01 |
| grace | 4 | 1000 | 4 | 11 |

The leftmost mask bit always equals 1, so every equation involves its own start row. That detail will matter in a minute. As a matrix equation, with the keys in the order above:

$$
\begin{bmatrix}
0&0&1&1&0&1&0&0&0&0\\
0&1&1&0&0&0&0&0&0&0\\
0&0&0&0&0&0&1&0&0&0\\
0&1&0&1&1&0&0&0&0&0\\
1&0&0&1&0&0&0&0&0&0\\
0&0&1&0&0&1&0&0&0&0\\
0&0&0&0&1&0&0&0&0&0
\end{bmatrix}
\begin{bmatrix} Z_0\\ Z_1\\ Z_2\\ Z_3\\ Z_4\\ Z_5\\ Z_6\\ Z_7\\ Z_8\\ Z_9 \end{bmatrix}
=
\begin{bmatrix} 11\\ 10\\ 00\\ 10\\ 10\\ 01\\ 11 \end{bmatrix}
$$

![Seven rows of a band matrix: each row has ones only inside a window of four columns, and the tag is written to the right; below, the solved table Z](band-toy.svg){: w="900" h="560" .shadow }
_The same system as a picture. Blue squares are the ones of each mask. Everything outside a window is zero._

Seven equations, ten unknowns. There are more unknowns than equations, so as long as the equations do not contradict each other there is room for a solution.

### Solving: insert one equation at a time

pyribbon does not build the whole matrix and then run textbook Gaussian elimination. It keeps one **slot** per row. A slot holds a mask and a tag, and its first mask bit is its **pivot**. An equation arrives at its start row and is processed like this:

1. If the slot at the current row is empty, store the equation there. Done.
2. Otherwise XOR the equation with the slot's equation. Both have a 1 in the first position, so that bit cancels.
3. If the mask is now all zeros, the equation was redundant (tag also 0) or a contradiction (tag not 0).
4. Otherwise find the first 1 that is left, hop the window forward to that row, and go back to step 1.

Back in the toy, Alice, Bob and Carol arrive at rows 2, 1 and 6. Those slots are empty, so they go straight in. Erin (row 0) also finds an empty slot. The other three collide.

Dave arrives at row 1, where Bob lives:

$$
\begin{array}{lll}
\text{dave at row 1} & \texttt{1011} \mid \texttt{10} & \\
\oplus\ \text{bob, slot 1} & \texttt{1100} \mid \texttt{10} & \\ \hline
\text{result} & \texttt{0111} \mid \texttt{00} & \text{first 1 is at row 2: hop}
\end{array}
$$

The window moves to row 2, where Alice lives:

$$
\begin{array}{lll}
\text{pending at row 2} & \texttt{1110} \mid \texttt{00} & \\
\oplus\ \text{alice, slot 2} & \texttt{1101} \mid \texttt{11} & \\ \hline
\text{result} & \texttt{0011} \mid \texttt{11} & \text{first 1 is at row 4: hop}
\end{array}
$$

Row 4 is empty, so the equation $$Z_4 \oplus Z_5 = 11$$ is stored there.

![Three stages showing dave's equation being XORed with bob and then alice, hopping from row 1 to row 2 to row 4, and being stored in the empty slot at row 4](elimination-chain.svg){: w="900" h="572" .shadow }
_Dave's insertion. Each XOR cancels the leading 1, and each hop skips the zeros._

Dave's equation was rewritten into a different equation that says the same thing about different rows. Every pending equation has the same shape (a leading 1, a short window, a tag), which keeps the loop simple. The loop makes at most $$w - 1$$ hops, because every hop moves forward by at least one row and the window is $$w$$ rows wide.

Frank (row 2, mask 1001, tag 01) meets Alice. The XOR with her slot leaves mask 0100 and tag 10. The first 1 is one row ahead, row 3, which is empty. Frank is stored as "$$Z_3 = 10$$".

Grace (row 4, mask 1000, tag 11) meets Dave's rewritten equation. The XOR leaves mask 0100 and tag 00, so she hops to row 5 and is stored as "$$Z_5 = 00$$". Grace said $$Z_4 = 11$$, Dave said $$Z_4 \oplus Z_5 = 11$$, and together they pin $$Z_5$$ to 00.

The slots after all seven insertions:

| slot | mask | tag | the equation it holds |
|---:|:---:|:---:|---|
| 0 | 1001 | 10 | Z0 ⊕ Z3 = 10 |
| 1 | 1100 | 10 | Z1 ⊕ Z2 = 10 |
| 2 | 1101 | 11 | Z2 ⊕ Z3 ⊕ Z5 = 11 |
| 3 | 1000 | 10 | Z3 = 10 |
| 4 | 1100 | 11 | Z4 ⊕ Z5 = 11 |
| 5 | 1000 | 00 | Z5 = 00 |
| 6 | 1000 | 00 | Z6 = 00 |
| 7 to 9 | empty | | no constraint |

The slots form a triangle: slot $$i$$ only mentions rows $$i$$ and later. A triangular system is easy to finish.

### Back-substitution

Start from the last row and walk backward. A slot says "$$Z_i$$ plus some later rows equals a tag", and the later rows are already known:

$$
Z_i = b_i \oplus \bigoplus_{k \ge 1,\; c_i[k] = 1} Z_{i+k}
$$

| row | slot says | arithmetic | $$Z$$ |
|---:|---|---|:---:|
| 9, 8, 7 | nothing | free, so 00 | 00 |
| 6 | Z6 = 00 | | 00 |
| 5 | Z5 = 00 | | 00 |
| 4 | Z4 ⊕ Z5 = 11 | 11 ⊕ 00 | 11 |
| 3 | Z3 = 10 | | 10 |
| 2 | Z2 ⊕ Z3 ⊕ Z5 = 11 | 11 ⊕ 10 ⊕ 00 | 01 |
| 1 | Z1 ⊕ Z2 = 10 | 10 ⊕ 01 | 11 |
| 0 | Z0 ⊕ Z3 = 10 | 10 ⊕ 10 | 00 |

The finished table, rows 0 to 9, is 00, 11, 01, 10, 11, 00, 00, 00, 00, 00. That is the filter. It stores ten 2-bit values and none of the seven keys. As a check, plug it back into the original equations:

| key | rows XORed | arithmetic | result | tag |
|---|---|---|:---:|:---:|
| alice | 2, 3, 5 | 01 ⊕ 10 ⊕ 00 | 11 | 11 |
| bob | 1, 2 | 11 ⊕ 01 | 10 | 10 |
| carol | 6 | 00 | 00 | 00 |
| dave | 1, 3, 4 | 11 ⊕ 10 ⊕ 11 | 10 | 10 |
| erin | 0, 3 | 00 ⊕ 10 | 10 | 10 |
| frank | 2, 5 | 01 ⊕ 00 | 01 | 01 |
| grace | 4 | 11 | 11 | 11 |

Every equation holds, including the ones that were rewritten along the way.

### Asking the filter

Alice's query recomputes the same equation, XORs rows 2, 3 and 5, gets 11, and compares with the tag 11. It matches, so the answer is "maybe". Members always match, because the table was solved for exactly their equations.

Now two keys that were never added. Pretend their hashes gave these equations:

- `mallory`: start 1, mask 1010 (rows 1 and 3), tag 11. XOR of the rows: $$Z_1 \oplus Z_3 = 11 \oplus 10 = 01$$. That is not 11, so the answer is "no".
- `trent`: start 3, mask 1100 (rows 3 and 4), tag 01. XOR of the rows: $$Z_3 \oplus Z_4 = 10 \oplus 11 = 01$$. That equals the tag, so the filter says "maybe" about a key it has never seen.

Trent is a false positive. With $$r = 2$$ it happens one time in four, so seeing one among two strangers is unremarkable. With $$r = 8$$ it is one in 256, and with $$r = 16$$ one in 65,536.

### When the system has no solution

Suppose a key "heidi" arrives with start 2, mask 1011 and tag 00. Its rows (2, 3, 5) are exactly alice's, whose tag is 11. Alice's slot at row 2 turns heidi's mask into all zeros, and the tags give $$11 \oplus 00 = 11 \neq 0$$. The system now claims $$0 = 11$$, which is impossible.

That is a failed build. Nothing can be repaired in place, so pyribbon throws the attempt away and starts again with a new salt, which gives every key a different equation. With $$w = 64$$ failures need long chains of dependencies, and they are rare. The build sweep (`make ovh-sweep`) measures a per-attempt failure rate of 0.10% at 1,000 keys and 3.3% at a million, and the mean number of attempts never goes above 1.033 [\[4\]](#ref-4).

## 05. From a real key to an equation

In the toy the hashes were invented. In pyribbon, three numbers have to come out of a key, and they have to be the same on every machine and in every process. Python's built-in `hash()` changes between processes, so pyribbon never uses it.

Here is the real path for the string `"alice"`, in a filter built from `["alice", "bob", "carol"]` with `fp_bits=12`. That filter has 128 rows (the minimum), so a start can be any of $$128 - 63 = 65$$ values.

![A chain of steps: XXH3 of the key, xor with a type tag, add the seed and mix, xor with the attempt salt, three mixes, then the start row 25, the mask 0xdb575a9b8815f471 and the 12-bit tag 100010010110](hash-pipeline.svg){: w="900" h="638" .shadow }
_Every value here is real, taken from the filter in the example._

Some notes on those steps:

- The bytes of a key go through XXH3-64 [\[5\]](#ref-5), chosen because its authors promise the output will never change. A saved filter is useless if the hash behind it drifts.
- `b"a"`, `"a"` and `97` must be different keys, so each type gets its own tag. A `str` is hashed from its UTF-8 bytes and XORed with a constant taken from SHA-512's initial values. An `int` in the 64-bit range skips XXH3 and is XORed with a different tag. `51` and `"51"` are different keys on purpose.
- `mix64` is the SplitMix64 finalizer [\[6\]](#ref-6), a bijection on 64-bit numbers with full avalanche: flip one input bit and about half the output bits change.
- The start row, the mask and the tag come from three separate mixes of the same state. Stretching one hash into three values with a multiplication would leave them correlated. For a retry only these cheap three mixes are repeated, not the key hashing.
- The start is $$\lfloor z_0 \cdot (m - 63) / 2^{64} \rfloor$$. That multiplies $$z_0$$ by a range and keeps the high 64 bits of the 128-bit product, which maps it evenly onto $$0 \ldots m - 64$$ without a modulo. Here $$z_0 / 2^{64} = 0.3914$$ and $$0.3914 \times 65 = 25.4$$, so the start is 25.
- The mask is $$z_1$$ with its lowest bit forced to 1, which gives the always-set pivot. The tag is the top 12 bits of $$z_2$$.

Checking it against that filter's table: XORing the rows of $$Z$$ that alice's mask selects, from row 25, gives `100010010110`, exactly her tag. For `"mallory"`, the start is 23 and the XOR gives `010000101011` against a tag of `010110111000`. They disagree, so the answer is "no". They already disagree in the first column, so a real query stops after reading a single column.

### The seed bug

pyribbon lets you pass a seed, so you can build independent filters of the same keys. The first version XORed the seed into the key hash. For dense integer keys that was a mistake: the set $$\{ i \oplus \text{seed} \}$$ is almost the same set for nearby seeds, so `seed=1` rebuilt nearly the filter of `seed=0`. A measurement caught it. The fix is to mix the seed first and add it as a random 64-bit offset, which makes every seed its own hash universe [\[4\]](#ref-4).

### Collisions

Two different keys can share one 64-bit hash $$H$$. For $$n$$ keys the probability is about $$n^2 / 2^{65}$$. At $$n = 10{,}000{,}000$$ that is $$10^{14} / 3.7 \times 10^{19} \approx 2.7 \times 10^{-6}$$, about one chance in 370,000. Such keys get identical equations, the elimination treats the second as redundant, and the cost is at most one extra false positive. Integer keys in the signed 64-bit range cannot collide at all, because the mixer is a bijection.

## 06. How big should the table be?

The table has $$m$$ rows for $$n$$ keys, so the space per key is $$(1 + \epsilon)\, r$$ where $$\epsilon = (m - n)/n$$ is the overhead. That is where the 12% in section 02 comes from. The smaller $$\epsilon$$ is, the closer to the floor, but if $$\epsilon$$ is too small the equations are likely to contradict each other.

How small can it be? A build tends to fail when equations pile up in one stretch of rows. Theory says $$w$$ must grow like $$\log n / \epsilon$$ for success with high probability [\[1\]](#ref-1). Turned around: for a fixed $$w = 64$$, the needed overhead grows slowly with $$n$$.

The default overhead comes from a table, not a formula. For every size from $$2^7$$ to $$2^{24}$$ I measured, using the C core itself, the overhead at which 97% of builds succeed on the first attempt:

![Line chart of the overhead needed against the number of slots: the shipped table rises from about 5% to 15.5%, a width-64 simulation sits slightly below it, a width-128 simulation is far lower, and the table is dotted beyond 2^24 where it is extrapolated](overhead.png){: w="1191" h="721" .shadow }
_Width 128 needs roughly half the slack, but its query needs 128-bit shifts and its insertion was 2 to 3 times slower in a first implementation. It is on the roadmap, not shipped._

### Sizing a million keys

The sizing code uses integers only, so no compiler can round differently and the same keys give the same bytes everywhere. Here is the whole calculation for $$n = 1{,}000{,}000$$ keys with `fp_bits=8`.

**Step 1: find the overhead.** Locate $$n$$ between two powers of two: $$2^{19} = 524{,}288 \le 10^6 < 2^{20}$$. So the remainder is $$10^6 - 524{,}288 = 475{,}712$$. The table has 115,000 parts per million at $$2^{19}$$ and 125,000 at $$2^{20}$$. Interpolate in whole numbers:

$$
\epsilon_{\text{ppm}} = 115{,}000 + \left\lfloor \frac{(125{,}000 - 115{,}000) \times 475{,}712}{524{,}288} \right\rfloor = 115{,}000 + 9{,}073 = 124{,}073
$$

**Step 2: scale the keys.** The rows needed are

$$
\left\lceil \frac{10^6 \times (10^6 + 124{,}073)}{10^6} \right\rceil = 1{,}124{,}073
$$

**Step 3: round up to a whole block.** The memory layout (section 07) wants a multiple of 64 rows:

$$
m = 64 \times \left\lceil \frac{1{,}124{,}073}{64} \right\rceil = 64 \times 17{,}564 = 1{,}124{,}096
$$

**Step 4: space.** Each block of 64 rows takes $$r$$ words of 8 bytes, so the payload is $$17{,}564 \times 8 \times 8 = 1{,}124{,}096$$ bytes, plus the 64-byte header:

$$
\frac{8 \times 1{,}124{,}160}{10^6} = 8.99 \text{ bits per key}
$$

I built that filter and read the row count and byte size back out of it. They match: 1,124,096 rows and 1,124,160 bytes.

From the third attempt on, the table also grows by a factor of about $$(w + 1)/w$$ and by at least one block. For this size that means 1,124,096 rows become 1,141,696, a growth of 1.6%. Reseeding does most of the work, and growth guarantees that the build ends.

A success probability of 97% per attempt means the expected number of attempts is $$1 / 0.97 \approx 1.03$$, which is the number the table was calibrated for.

## 07. Why the C core is fast

The core is C11 with no dependencies except one vendored hash header, no global state, and no allocation inside a query. A few choices carry most of the speed.

### One cache line per insertion

A slot is a 16-byte struct: a 64-bit mask word, a 32-bit result and 4 bytes of padding. Four slots fit in a 64-byte cache line, and an insertion that walks forward touches neighbouring slots.

### Hopping is one instruction

The step "find the next 1" is a count-trailing-zeros instruction, and the XOR parity in the query is a parity instruction. Because the mask always has bit 0 set and the XOR clears it, the shift in the loop is always 1 to 63, never the full 64 that would be undefined behavior in C. Compilers' builtins are used on GCC and Clang, MSVC intrinsics on Windows, and plain C fallbacks exist for all of it. CI forces the fallbacks to keep them tested.

### Hiding the memory latency

For a big table a key's slot is a random memory access, and the build waits on memory. pyribbon derives the equations for 16 keys, prefetches their slots, and only then inserts them, so the cache misses overlap instead of queueing. For tables of at least $$2^{18}$$ rows it goes further: because the solution does not depend on the order equations arrive in, it first groups keys by start row with a counting sort and inserts bucket by bucket. The slots of one bucket stay in cache. In my measurements this makes builds 19 to 24% faster at a million and ten million keys, and changes nothing from 1,000 to 100,000 keys, where it is not used.

### A layout built for the query

The table is stored in blocks of 64 rows. For each block there are $$r$$ words, and word $$j$$ holds bit $$j$$ of all 64 rows of that block. This is the interleaved column layout of the paper [\[1\]](#ref-1).

![Rows of Z in three blocks of 64 with a query window starting at row 100 that straddles two blocks, and below it the same data as six 64-bit words in memory with the formula for column j](layout-blocks.svg){: w="900" h="452" .shadow }
_Starting at row 100, the window sits at offset 36 of block 1 and spills into block 2._

To get column $$j$$ of the XOR, load word $$j$$ of the first block, AND it with the mask shifted into place, take the parity, then do the same with the spill-over bits in the next block and combine the two. At most two loads per column, no matter what $$s$$ is.

### Stopping early

The query checks columns one at a time and quits at the first that disagrees with the tag. For a key that is not in the set each column agrees with probability one half, so the expected number of columns read is

$$
1 + \tfrac{1}{2} + \tfrac{1}{4} + \cdots \approx 2
$$

and a typical "no" costs about two word loads, whatever $$r$$ is.

Things I tried that did not help: bucketing below $$2^{18}$$ rows (7 to 10% slower at 10,000 to 100,000 keys), inserting several keys in lock step, fixing $$r$$ at compile time in the back-substitution, and other bucket sizes.

## 08. The Python layer and the file

I wrote the Python module as a CPython extension by hand instead of using Cython or cffi. A trivial call costs 32 to 34 ns, against 41 for Cython and 175 to 267 for cffi, and a source install needs only a C compiler.

A few details come from how Python behaves:

- For CPython 3.11 and newer one stable-ABI wheel per platform covers every version. 3.10 gets its own wheel, and the free-threaded builds (3.14t and 3.15t) get theirs.
- `key in f` never releases the GIL, because releasing and retaking it costs more than the roughly 30 ns of work. A build releases it for the elimination and back-substitution, which can take seconds. `contains_many` releases it for batches of at least 1024 keys.
- A filter is immutable, so any number of threads can query one filter at once.
- A list or an integer array (`array.array`, NumPy) passed as `keys` is hashed in C, and gives exactly the same filter as the same ints one at a time.

### One file, checked before it is trusted

`to_bytes()` writes a 64-byte header followed by the table:

![A grid of the 64-byte header: magic PYRIBBON, version, header size, width, fingerprint bits, hash id, flags, key count, row count, seed, attempt, two checksums, then the payload](file-format.svg){: w="900" h="508" .shadow }
_Everything is little-endian and every field is explicit._

`RibbonFilter.from_buffer(data)` queries those bytes where they are, without copying them. A memory-mapped file costs no memory beyond the pages you touch. The loader treats its input as hostile: it copies the 64 header bytes once, validates that copy, checks the magic, version, sizes and header checksum, and only then lets queries read the payload. A truncated or damaged buffer raises `FormatError` and is never read outside its bounds.

The checksums catch accidents and are not a MAC, so they do not stop tampering. `verify=False` skips the payload checksum, which has to read every byte, and the header checks still run. I measured both on a 23 MB filter: loading it with `verify=False` took 0.02 ms, and with the checksum 4.5 ms.

## 09. Does it do what it says?

A filter has two promises, and each needs its own kind of test.

No false negatives is a hard promise, so it gets property tests (Hypothesis) over sizes from zero up, every key type, every `fp_bits`, duplicates and seeds. In my runs all 1,000,000 members were found at each of the seven widths I tried, from 2 to 16 bits.

The false-positive rate of $$2^{-r}$$ is a statistical claim, so it needs a lot of probes. I built a filter of 1,000,000 keys at several widths and probed it with 20,000,000 keys that were never added:

![Dots near 1.0 for r = 2, 4, 6, 8, 10, 12 and 16: the measured false-positive rate divided by the designed rate, each with a 95% confidence interval that contains 1](measured-fpr.png){: w="1242" h="644" .shadow }
_Measured. Each dot is one filter probed with 20 million non-members. The number above it is how many false positives were seen._

At $$r = 8$$ the design says 78,125 false positives in 20 million probes. I saw 78,121. At $$r = 16$$ the design says 305 and I saw 303. Every width matches the design to within sampling error.

Other checks that are worth knowing about:

- The test suite includes a second implementation of the format, written in Python from the spec, that has to produce the same bytes as the C core.
- The loader is run under libFuzzer with ASan and UBSan, and a differential fuzz compares it with the Python reference.
- The core's tests also run on s390x (big-endian) and on 32-bit machines in CI.
- An independent review found a heap corruption: a length hint was multiplied by 8 and wrapped to zero bytes. It is now a regression test with hints up to $$2^{63} - 1$$.

## 10. Three real uses

### A filter in front of a database

The first use is the one from the introduction. I stored 2,000,000 random 40-bit IDs and sent 10,000,000 lookups, of which 500,000 were for real IDs and 9,500,000 for IDs that do not exist. Every lookup first asks the filter.

![A diagram of 10 million lookups going into a 2.27 MB filter: 9,463,064 are answered "no" from memory and 536,936 go to the database, of which 500,000 are real hits and 36,936 are false positives](use-case.svg){: w="900" h="420" .shadow }
_Measured with `fp_bits=8`. Without the filter all 10,000,000 lookups go to the database._

The trade between size and wasted reads, measured:

| `fp_bits` | filter size | reads that reach the database | wasted reads |
|---:|---:|---:|---:|
| 8 | 2.27 MB | 536,936 | 36,936 |
| 10 | 2.83 MB | 509,217 | 9,217 |
| 12 | 3.40 MB | 502,297 | 2,297 |

The expected wasted reads are $$9{,}500{,}000 \times 2^{-r}$$: 37,109, 9,277 and 2,319. The measured numbers sit right on top of them.

To turn that into time you need a cost per read. Take 100 microseconds, a round number for a random read from fast storage. That is my assumption, not a measurement. Then 10,000,000 reads cost 1,000 seconds. With the 8-bit filter it is 536,936 reads, 53.7 seconds, plus about one second of filter queries (measured: 1.0 s for all 10 million, with `contains_many`). Each extra two bits of `fp_bits` cuts the wasted reads by a factor of four and adds about 0.57 MB.

For scale, a Python `set` of those 2,000,000 integers takes 67 MB for its table alone, plus about 56 MB for the int objects. The filter is under 2.3 MB.

### Shipping a blocklist

Say you want every client to check passwords against a list of known-leaked ones. Take 10,000,000 SHA-1 digests of 20 bytes each. As a raw list that is 200 MB. A false positive here flags a good password, so I picked `fp_bits=16`, one wrong flag in 65,536.

| representation | size |
|---|---:|
| raw list of 10M SHA-1 digests | 200 MB |
| Bloom filter at 1.44 × 16 bits per key (formula) | 28.8 MB |
| pyribbon, `fp_bits=16` (measured) | 23.0 MB |

The pyribbon file took 1.9 seconds to build, including hashing the 20-byte keys. Clients open it with `from_buffer` on a memory-mapped file, so loading takes microseconds and the operating system pages in only what queries touch. I probed it with 2,000,000 digests that were not in the list and got 35 false positives, against about 30.5 expected.

> A filter is not a privacy tool. Anyone holding the file can test guesses against it, and a list of leaked hashes is exactly what an attacker would like to test guesses against. It also cannot tell you which entry matched.
{: .prompt-warning }

### Filters inside a storage engine

A log-structured store keeps data in many immutable files and has to ask "is this key in this file?" for each. The files never change, so a static filter fits: build it once when the file is written, store it next to the data. RocksDB added Ribbon filters in 6.15 as an alternative to Bloom filters. Its write-up reports about 30% less space than Bloom for 100,000 keys per filter, and 27% less with 100 million keys in one filter, in exchange for roughly three to four times the CPU, mostly spent building the filter in the background [\[3\]](#ref-3). pyribbon's own number is in the same range: 22% below Bloom at 8 bits and a million keys.

The condition is the same everywhere: the set has to be known up front and it must not change. If you need to insert keys later, a Bloom filter or a cuckoo filter is the right tool.

## 11. Where pyribbon loses

At 10 million keys with 8-bit fingerprints, my benchmark has pyribbon at 9.19 bits per key and the Fuse8 filter [\[8\]](#ref-8) at 9.02, so Fuse8 is 2% smaller. Up to about a hundred thousand keys pyribbon is the smallest of the filters tested.

![Left, bits per key against the number of keys for pyribbon, Fuse8, Xor8 and a Bloom filter. Right, lookup time in nanoseconds from Python for pyribbon and Fuse8](performance.png){: w="1686" h="742" .shadow }
_Measured with the pyribbon benchmark suite, one run._

The reason is the sizing curve from section 06. With width 64 the overhead grows with the logarithm of the set size, and at some point a Fuse filter, whose overhead stays flat, catches up. The lookup panel needs a caution too. The Fuse8 package (pyfusefilter) hashes every key in Python, which accounts for much of its lookup time, and its bare C core builds faster than my elimination does, so the build comparison depends on what you count.

The other limits:

- A filter is static. There is no `add` and no `remove`.
- Small sets are padded to 128 rows, so a few dozen keys cost 128 bytes plus the header at `fp_bits=8`. A plain `set` is better there.
- A build needs about 26 bytes of temporary memory per key, roughly 2.6 GB at 100 million keys.
- The sizing table was measured up to $$2^{24}$$ slots. Above that it is extrapolated.
- Windows on ARM has never been built, and no big-endian or 32-bit wheels are published.

The next items on the roadmap are width 128 or sharding, to flatten the overhead curve at large sizes, then the homogeneous and BuRR variants from the later paper [\[2\]](#ref-2).

## 12. Try it

```bash
pip install pyribbon
```

```python
from pyribbon import RibbonFilter

f = RibbonFilter(["alice", "bob", "carol"], fp_bits=12)  # one wrong "maybe" in 4096
assert "alice" in f                                       # a member is always found
assert "mallory" not in f                                 # this non-member was rejected
print(f.contains_many(["alice", "mallory"]))              # [True, False]

data = f.to_bytes()                                       # 64-byte header + the table
g = RibbonFilter.from_buffer(data)                        # reads the bytes in place
print(len(data), g.bits_per_key)
```

For a big set, pass a NumPy or `array.array` of integers: the keys are hashed in C and `contains_many` answers whole batches. The code, the docs, and the research notes behind every choice are in the [repository](https://github.com/zikithezikit/pyribbon).

## Sources

<span id="ref-1"></span>\[1\] Dillinger, P. C., & Walzer, S. (2021). _Ribbon filter: practically smaller than Bloom and Xor_. arXiv:2103.02515. [https://arxiv.org/abs/2103.02515](https://arxiv.org/abs/2103.02515)

<span id="ref-2"></span>\[2\] Dillinger, P. C., Hübschle-Schneider, L., Sanders, P., & Walzer, S. (2022). _Fast succinct retrieval and approximate membership using Ribbon_. SEA 2022. arXiv:2109.01892. [https://arxiv.org/abs/2109.01892](https://arxiv.org/abs/2109.01892)

<span id="ref-3"></span>\[3\] RocksDB blog (2021). _Ribbon Filter_. [https://rocksdb.org/blog/2021/12/29/ribbon-filter.html](https://rocksdb.org/blog/2021/12/29/ribbon-filter.html)

<span id="ref-4"></span>\[4\] pyribbon repository, version 0.1.2, including `docs/internals.md`. [https://github.com/zikithezikit/pyribbon](https://github.com/zikithezikit/pyribbon)

<span id="ref-5"></span>\[5\] Collet, Y. _xxHash_ (XXH3). [https://xxhash.com](https://xxhash.com)

<span id="ref-6"></span>\[6\] Vigna, S. _SplitMix64_. [https://prng.di.unimi.it/splitmix64.c](https://prng.di.unimi.it/splitmix64.c)

<span id="ref-7"></span>\[7\] Bloom, B. H. (1970). Space/time trade-offs in hash coding with allowable errors. _Communications of the ACM_, 13(7), 422-426.

<span id="ref-8"></span>\[8\] Graf, T. M., & Lemire, D. (2020). _Xor filters: faster and smaller than Bloom and cuckoo filters_. arXiv:1912.08258. [https://arxiv.org/abs/1912.08258](https://arxiv.org/abs/1912.08258). And _Binary fuse filters: fast and smaller than xor filters_ (2022). arXiv:2201.01174. [https://arxiv.org/abs/2201.01174](https://arxiv.org/abs/2201.01174)
