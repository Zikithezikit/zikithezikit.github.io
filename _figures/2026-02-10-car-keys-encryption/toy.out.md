| event | code sent | receiver | last accepted counter |
|---|---|---|---|
| fob press 1 | `9be0050a` | accept, counter 1 | 1 |
| replay of press 1 | `9be0050a` | reject | 1 |
| fob presses 2 and 3, out of range | not heard | none | 1 |
| fob press 4 | `6d6ed41e` | accept, counter 4 | 4 |
| replay of press 2 (never heard) | `f9ef224c` | reject | 4 |
| replay of press 4 | `6d6ed41e` | reject | 4 |
| fob presses 5 to 13, out of range | not heard | none | 4 |
| fob press 14 | `862a3f8e` | held, counter 14 | 4 |
| fob press 15 | `f8e46ca1` | accept after resync, counter 15 | 15 |
| fob press 16 | `11c59cc3` | accept, counter 16 | 16 |

fixed code, first press: accept | replay: accept

receiver at counter 1 hears press 3 first: accept, counter 3

guess probability per attempt, window 4: 4/2^32 = 9.31e-10
guess probability per attempt, window 16: 16/2^32 = 3.73e-09
counter values: 65536
