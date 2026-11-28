---
title: "Car Key Codes: Rolling Codes and Relay Attacks"
author: yoav
description: "A car remote sends a code that changes on every press, and the car accepts a small window of counters. A toy rolling code in Python shows why a replay fails and a missed press still works, then the published weak points: short keys and relay attacks."
date: 2026-02-10 12:00:00 +0200
lang: en
categories: [Security, Automotive, Cryptography]
tags: [car-keys, rolling-codes, keyless-entry, relay-attacks, hmac, python]
pin: false
math: true
mermaid: false
image:
   path: /assets/images/car-keys-encryption.jpg
   alt: Modern car key encryption technology
---

## 01. The question

A car has to decide whether a radio message came from its key. Anyone nearby can record the message. So the message must be one that works only once, or one that only the key can produce on demand.

A remote key sends its message on UHF radio, at 315 or 433 MHz, with a typical range of 10 to 100 meters. A transponder chip in the key reads at short range on 120 to 135 kHz when you start the engine [\[1, Sec. 2\]](#ref-1).

> Numbers marked "made up" come from the toy scheme in sections 03 to 05. Every other number has a citation. Real systems differ by manufacturer, so the toy is a model of the idea and not of one product.
{: .prompt-info }

## 02. Why is a fixed code not enough?

A fixed code is a number the key sends on every press. The car compares it with the number it stored. A recording of one press opens the car on every later day.

In the toy, the fixed code is the made-up string `a1b2c3d4`. The first press is accepted, and so is the replay:

```text
fixed code, first press: accept | replay: accept
```

A rolling-code fob still sends some fixed data. The Microchip HCS301, a KeeLoq encoder, sends 66 bits: a 34-bit fixed part (28-bit serial number, 4-bit button code, 2-bit status) and a 32-bit hopping code [\[2, p. 1\]](#ref-2). The serial number goes out in the clear. Only the hopping code changes.

## 03. What changes on every press?

A counter. The fob and the car share a secret key $$K$$. The fob adds 1 to a counter $$n$$ on every press and sends a code computed from $$K$$ and $$n$$. Without $$K$$, nobody can compute the next code.

The toy computes the code as the first 4 bytes of an HMAC [\[3\]](#ref-3):

$$
\text{code}_n = \text{HMAC-SHA256}(K,\ n)\,[0:4]
$$

The key $$K$$ is `made-up-key-0001`, and $$n$$ is 16 bits wide. Two codes from the run:

| press | counter $$n$$ | code (hex) |
|---|---:|---|
| 1 | 1 | `9be0050a` |
| 4 | 4 | `6d6ed41e` |

The HCS301 does the same job with the KeeLoq cipher in place of HMAC. It has a 64-bit key, a 16-bit counter and a 32-bit hopping code, so the code is also 4 bytes [\[2, pp. 1, 7\]](#ref-2). A 16-bit counter has 65,536 values. The datasheet counts about 18 years before a value repeats at 10 operations a day [\[2, p. 7\]](#ref-2). My check: $$65{,}536 / (10 \times 365) = 17.96$$ years.

The toy fob sends only the code, not the counter. The car stores the last counter it accepted. It rejects a replay because the replayed code belongs to a counter it has already passed.

## 04. What if the car misses a press?

The fob works out of range. Press the button twice in a pocket and the fob's counter runs ahead of the car's. If the car accepted only $$n + 1$$, the next press from the driveway would fail.

So the car accepts any counter in a window of $$W$$ values after the last one it accepted. The toy uses $$W = 4$$. The car recomputes the codes for the next $$W$$ counters and compares each with what it heard.

Take the car at counter 1 and the fob at press 4:

1. The car computes the codes for counters 2, 3, 4 and 5.
2. The code for counter 4 matches `6d6ed41e`.
3. The car accepts and stores 4. Counters 2 and 3 are now behind it.

| event | code sent | receiver | last accepted counter |
|---|---|---|---|
| fob press 1 | `9be0050a` | accept, counter 1 | 1 |
| replay of press 1 | `9be0050a` | reject | 1 |
| fob presses 2 and 3, out of range | not heard | none | 1 |
| fob press 4 | `6d6ed41e` | accept, counter 4 | 4 |
| replay of press 2 | `f9ef224c` | reject | 4 |
| replay of press 4 | `6d6ed41e` | reject | 4 |

_Output of the toy script with $$W = 4$$. The key is made up._

The replay of press 1 is rejected because the car's window starts at counter 2. The window moves forward every time the car accepts a code, and it never moves back.

The price of tolerance is that a code the car has not heard yet stays valid until a later counter is accepted. In the toy, a car at counter 1 that hears press 3 first accepts it as counter 3.

The datasheet's typical decoder uses a "single operation" window of 16 codes and calls the window sizes optional [\[2, p. 16\]](#ref-2). It gets the counter by decrypting the hopping code [\[2, p. 15\]](#ref-2). The toy searches the window instead, which gives the same answers.

## 05. What if the fob is far ahead?

A fob pressed many times away from the car ends up outside the window. The HCS301 datasheet adds a second window for this, up to 32K codes ahead of the stored counter. A code in it is not acted on. The decoder waits for a second code with the next counter, then acts and stores it. Codes behind the stored counter sit in a "blocked window" and are ignored [\[2, p. 16\]](#ref-2). The datasheet notes that users press the button a second time anyway.

The toy copies the rule with a resynchronization window of $$R = 64$$:

| event | code sent | receiver | last accepted counter |
|---|---|---|---|
| fob presses 5 to 13, out of range | not heard | none | 4 |
| fob press 14 | `862a3f8e` | held, counter 14 | 4 |
| fob press 15 | `f8e46ca1` | accept after resync, counter 15 | 15 |
| fob press 16 | `11c59cc3` | accept, counter 16 | 16 |

_Same run, continued. Press 14 is 10 counters ahead of 4, outside $$W = 4$$ and inside $$R = 64$$._

Press 14 opens nothing. Press 15 is the next counter after the held one, so the car accepts it and moves its window to 15.

> The window rules are a design choice, and a wrong rule is a flaw. CVE-2021-46145, published on 6 January 2022, describes a replay attack for unlocking on 2012 Honda Civic key fobs. The entry ties it to a non-expiring rolling code and counter resynchronization [\[4\]](#ref-4).
{: .prompt-warning }

## 06. How likely is a blind guess?

Someone without $$K$$ can only send random 4-byte values. A guess passes if it equals any one of the $$W$$ valid codes, so the chance per attempt is

$$
p = \frac{W}{2^{32}}
$$

For the toy window $$W = 4$$ that is $$9.31 \times 10^{-10}$$ per attempt. For the HCS301 window $$W = 16$$ it is $$3.73 \times 10^{-9}$$. Both come from the formula, and both assume the code looks random to someone who does not know the key.

So a blind guess is not the practical threat. The published breaks are in the key, in the hardware and in the radio link, with the occasional bad window rule.

## 07. Where does the key leak?

A transponder in the key bow uses challenge and response. The car sends a fresh random challenge and the chip answers with a keyed function of it. A recorded answer is useless next time, because the challenge changes.

The Texas Instruments Digital Signature Transponder (DST) is a chip of this kind, used in car ignition keys and in fuel payment tags. It has a 40-bit key. The challenge is 40 bits and the response is 24 bits. Bono and co-authors recovered a key from two challenge and response pairs, using sixteen FPGAs for under an hour, and started a 2005 Ford Escape with a simulated chip [\[5\]](#ref-5).

The arithmetic shows why two pairs were enough. There are $$2^{40} = 1{,}099{,}511{,}627{,}776$$ keys. A wrong key reproduces a 24-bit response with probability $$2^{-24}$$. After one pair about $$2^{40} / 2^{24} = 65{,}536$$ keys survive. After two pairs about $$2^{40} / 2^{48} = 1/256$$ of a wrong key survives, so one key is left. That is my calculation, and it assumes responses behave like random values.

The short key is the weakness. The cipher was also proprietary, and the authors reverse engineered it from a device [\[5\]](#ref-5).

KeeLoq has a different weak point, the hardware. Eisenbarth and co-authors used power analysis on commercial KeeLoq products. They recovered the secret key of a remote and the manufacturer key stored in a receiver. A remote could be cloned from ten power traces. With the manufacturer key, two eavesdropped messages from a remote were enough to get its key [\[6\]](#ref-6). A manufacturer key matters because a receiver typically derives each remote's key from its serial number [\[2, p. 15\]](#ref-2).

The relay paper sums up the pattern: breaks in remote key systems often come from keys that are too short, from ciphers that were never publicly reviewed, or from side channels. It notes a move toward established ciphers such as AES [\[1, Sec. 7\]](#ref-1).

## 08. What changes with keyless entry?

A passive keyless entry and start (PKES) key needs no button. The car sends a beacon on low frequency. If the key hears it, the key answers on UHF, and the car checks the answer. In one variant the beacon is already a challenge that carries the car's identifier [\[1, Sec. 2.3\]](#ref-1).

The low-frequency link reaches about 1 to 2 m from the car. The UHF link reaches 10 to 100 m [\[1, Sec. 2.3\]](#ref-1).

The car treats "I can hear the right key" as "the key is next to me". The relay paper calls that assumption true only when nobody is attacking: the ability to communicate does not prove that the key is close [\[1, Sec. 1\]](#ref-1).

## 09. Why does a relay beat the cipher?

A relay passes the two messages along. One device sits near the key and one near the car. The car's challenge reaches the key and the key's answer reaches the car. Both are fresh and valid. Nothing is replayed, decoded or changed, so counters, windows and strong ciphers do not help [\[1, Sec. 7\]](#ref-1).

What Francillon, Danev and Capkun measured in 2011 [\[1, abstract\]](#ref-1):

- 10 car models from 8 manufacturers. One of the 10 was an aftermarket system tested in the lab only, so 9 are cars.
- The true distance between key and car was up to 50 m, without line of sight.
- The key could be woken from up to 8 m away.
- Their relay setups cost between 100 and 1,000 USD.

The paper does not name the models. It describes how the tested systems work and says similar designs are likely open to the same attack [\[1\]](#ref-1). Prices and distances are from 2011.

## 10. What defences exist?

### What an owner can do

The relay paper lists these [\[1, Sec. 6\]](#ref-1):

- Keep the key in a metal case that works as a Faraday cage, and take it out at the car. The paper warns that a good cage is hard to build and that an attacker may raise the transmit power.
- Remove the battery from the key. Without the UHF radio, the car opens with the physical key hidden in the fob, and starts through the short-range link at a spot such as the start button.

Each of these gives up some of the convenience that the keyless system was built for. The paper also suggests two changes a maker could ship: a software change where the lock button on the fob turns passive entry off until the open button is pressed, and a hardware switch in the key. A jammer is a separate problem: it blocks the lock signal so the car stays open, but it cannot start the car [\[1, Sec. 7\]](#ref-1). Check that the car locked.

### What a maker can do

Signal strength is a weak check, because a relay can copy the expected levels [\[1, Sec. 6.3\]](#ref-1). The paper's proposal is distance bounding. The car times a challenge and response exchange and works out an upper bound on the distance from the round trip time.

A relay adds delay. The paper's calculation for a 30 m coaxial cable is 250 ns, and it needs the standard deviation of the round trip time to stay under 6 ns to bound the distance to 1 m [\[1, Sec. 6.4\]](#ref-1).

Ultra-wideband ranging measures distance from signal timing in this way. It does not close the gap completely. The Ghost Peak attack shortened a measured distance from 12 m to 0 m between Apple U1 chips, with a success probability of up to 4% and a device costing about 65 USD [\[7\]](#ref-7).

## 11. Try it

The toy as plain Python, with no install:

```python
import hashlib, hmac

KEY, W = b"made-up-key-0001", 4          # made-up key, window of 4 counters

def code(counter):                        # first 4 bytes of HMAC-SHA256(key, counter)
    return hmac.new(KEY, counter.to_bytes(2, "big"), hashlib.sha256).digest()[:4].hex()

last = 0                                  # the car's last accepted counter
def car(c):
    global last
    for n in range(last + 1, last + W + 1):
        if code(n) == c:
            last = n
            return True
    return False

print(car(code(1)))   # True: first press
print(car(code(1)))   # False: a replay is rejected
print(car(code(4)))   # True: presses 2 and 3 were missed, 4 is inside the window
print(car(code(2)))   # False: an older counter is outside the window
```

Output:

```text
True
False
True
False
```

Change `W` to 1 and the output becomes `True False False True`. The car then accepts only the next counter, so press 4 is rejected and the unheard press 2 is accepted.

## Sources

<span id="ref-1"></span>\[1\] Francillon, A., Danev, B., & Capkun, S. (2011). _Relay attacks on passive keyless entry and start systems in modern cars_. NDSS Symposium 2011. [https://www.ndss-symposium.org/ndss2011/relay-attacks-on-passive-keyless-entry-and-start-systems-in-modern-cars/](https://www.ndss-symposium.org/ndss2011/relay-attacks-on-passive-keyless-entry-and-start-systems-in-modern-cars/)

<span id="ref-2"></span>\[2\] Microchip Technology. (2001). _HCS301 KEELOQ code hopping encoder_ (DS21143B). [https://ww1.microchip.com/downloads/en/devicedoc/21143b.pdf](https://ww1.microchip.com/downloads/en/devicedoc/21143b.pdf)

<span id="ref-3"></span>\[3\] Krawczyk, H., Bellare, M., & Canetti, R. (1997). _HMAC: Keyed-hashing for message authentication_. RFC 2104. [https://www.rfc-editor.org/rfc/rfc2104](https://www.rfc-editor.org/rfc/rfc2104)

<span id="ref-4"></span>\[4\] NIST National Vulnerability Database. (2022). _CVE-2021-46145_. [https://nvd.nist.gov/vuln/detail/CVE-2021-46145](https://nvd.nist.gov/vuln/detail/CVE-2021-46145)

<span id="ref-5"></span>\[5\] Bono, S., Green, M., Stubblefield, A., Juels, A., Rubin, A., & Szydlo, M. (2005). _Security analysis of a cryptographically-enabled RFID device_. 14th USENIX Security Symposium. [https://www.usenix.org/legacy/events/sec05/tech/bono/bono_html/index.html](https://www.usenix.org/legacy/events/sec05/tech/bono/bono_html/index.html)

<span id="ref-6"></span>\[6\] Eisenbarth, T., Kasper, T., Moradi, A., Paar, C., Salmasizadeh, M., & Manzuri Shalmani, M. T. (2008). _Physical cryptanalysis of KeeLoq code hopping applications_. IACR Cryptology ePrint Archive, 2008/058. [https://eprint.iacr.org/2008/058](https://eprint.iacr.org/2008/058)

<span id="ref-7"></span>\[7\] Leu, P., Camurati, G., Heinrich, A., Roeschlin, M., Anliker, C., Hollick, M., Capkun, S., & Classen, J. (2021). _Ghost Peak: Practical distance reduction attacks against HRP UWB ranging_. arXiv:2111.05313. [https://arxiv.org/abs/2111.05313](https://arxiv.org/abs/2111.05313)
