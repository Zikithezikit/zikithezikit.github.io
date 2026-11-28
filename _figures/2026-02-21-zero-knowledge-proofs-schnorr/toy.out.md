## group
p=23 q=11 p-1=22 = 11 * 2  g=2  g^q mod p = 1
| e | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| g^e mod p | 1 | 2 | 4 | 8 | 16 | 9 | 18 | 13 | 3 | 6 | 12 | 1 |
subgroup elements (sorted): [1, 2, 3, 4, 6, 8, 9, 12, 13, 16, 18]

## keys
x=7 y=g^x mod p=13  y^q mod p=1
table lookup of y=13 gives x=7

## interactive run
k=4 t=g^k mod p=16
c=5
c*x=35  k+c*x=39  s=(k+c*x) mod q=6
g^s mod p=18  y^c mod p=4  t*y^c=64  t*y^c mod p=18
integer sum without mod q: 39  divided by c: 7.8

## why s hides x: fixed x and c, every k
k: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
s: [2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1]

## simulated transcript, no x
c=3 s=9 t=g^s*y^-c mod p=12
check: g^s mod p=6  t*y^c mod p=6

## nonce reuse
k=4 t=16 c1=5 s1=6 c2=9 s2=1
s1-s2 mod q=5  c1-c2 mod q=7  inverse of c1-c2 mod q=8  check 7*8=56=1 mod q
x=(s1-s2)*inv mod q=7
k=s1-c1*x mod q=4

## Fiat-Shamir
k=9 t=6 input='2,13,6' sha256=00223fe57732cfc1581b078e7249b7bd529dab9a6ce0e4c768d5f733b883e4c3
first 8 hex digits 00223fe5  full hash mod q = 3  c=3
s=(k+c*x) mod q = (9+3*7) mod 11 = 8
g^s mod p=3  y^c mod p=12  t*y^c mod p=3
proof=(t=6, s=8)
wrong s+1 passes? False

## forging without x (grind over c, s)
pairs tried=121  passing pairs=11  first success at attempt 8: t=18 s=0 c=7
passing: [(18, 0, 7), (12, 1, 5), (13, 1, 7), (1, 2, 5), (9, 3, 6), (3, 4, 1), (8, 5, 5), (2, 6, 7), (6, 8, 3), (16, 10, 4), (4, 10, 9)]

## cave odds
2^-20 = 9.5367431640625e-07  1/2^20 = 1048576
