"""Toy rolling-code scheme for the car-keys post.

code = first 4 bytes of HMAC-SHA256(key, counter), counter is 16 bits.
The fob sends only the code. The receiver tries the counters just after the
last one it accepted. Prints the Markdown tables that are pasted into the post.
"""
import hashlib
import hmac

KEY = b"made-up-key-0001"      # made up for the example
W = 4                          # single-press window (the real HCS301 uses 16)
R = 64                         # resynchronization window (toy value, the HCS301 uses 32K)


def code(counter):
    msg = counter.to_bytes(2, "big")
    return hmac.new(KEY, msg, hashlib.sha256).digest()[:4].hex()


class Receiver:
    def __init__(self, last=0):
        self.last = last       # last accepted counter
        self.pending = None    # first code seen in the resync window

    def press(self, c):
        # a press inside the single window opens the car
        for n in range(self.last + 1, self.last + W + 1):
            if code(n) == c:
                self.last, self.pending = n, None
                return f"accept, counter {n}"
        # a press that continues a pending resync opens the car
        if self.pending is not None and code(self.pending + 1) == c:
            self.last, self.pending = self.pending + 1, None
            return f"accept after resync, counter {self.last}"
        # a press farther ahead is held until the next press confirms it
        for n in range(self.last + W + 1, self.last + R + 1):
            if code(n) == c:
                self.pending = n
                return f"held, counter {n}"
        return "reject"


def fixed_code_receiver():
    secret = "a1b2c3d4"
    return lambda c: "accept" if c == secret else "reject", secret


if __name__ == "__main__":
    rx = Receiver(last=0)
    events = [
        ("fob press 1", code(1)),
        ("replay of press 1", code(1)),
        ("fob presses 2 and 3, out of range", None),
        ("fob press 4", code(4)),
        ("replay of press 2 (never heard)", code(2)),
        ("replay of press 4", code(4)),
        ("fob presses 5 to 13, out of range", None),
        ("fob press 14", code(14)),
        ("fob press 15", code(15)),
        ("fob press 16", code(16)),
    ]
    print("| event | code sent | receiver | last accepted counter |")
    print("|---|---|---|---|")
    for label, c in events:
        if c is None:
            print(f"| {label} | not heard | none | {rx.last} |")
            continue
        res = rx.press(c)
        print(f"| {label} | `{c}` | {res} | {rx.last} |")

    print()
    fixed, secret = fixed_code_receiver()
    print("fixed code, first press:", fixed(secret), "| replay:", fixed(secret))

    print()
    late = Receiver(last=1).press(code(3))
    print("receiver at counter 1 hears press 3 first:", late)

    print()
    bits = 32
    for w in (W, 16):
        print(f"guess probability per attempt, window {w}: {w}/2^{bits} = {w / 2**bits:.2e}")
    print("counter values:", 2**16)

    # checks
    rx = Receiver(last=0)
    assert rx.press(code(1)).startswith("accept")
    assert rx.press(code(1)) == "reject"
    assert rx.press(code(4)).startswith("accept")
    assert rx.press(code(2)) == "reject"
    assert rx.press(code(14)).startswith("held")
    assert rx.press(code(15)).startswith("accept after resync")
