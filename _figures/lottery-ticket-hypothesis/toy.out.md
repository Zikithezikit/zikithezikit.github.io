<!-- init seed 8; first seed where dense and ticket succeed and none of 5 reinits does -->

### Initial weights (theta_0)

| W1 at init | x1 | x2 | 1 |
|---|---:|---:|---:|
| unit 1 | -1.22 | -0.94 | -0.95 |
| unit 2 | -0.25 | -1.62 | -0.13 |
| unit 3 | -0.67 | +0.63 | +0.67 |
| unit 4 | +0.97 | +0.54 | -0.04 |
| unit 5 | +0.60 | +1.05 | -0.46 |
| unit 6 | +0.43 | -0.03 | +1.01 |
| unit 7 | -0.59 | -0.21 | +0.25 |
| unit 8 | +0.18 | -1.15 | +0.25 |

| w2 at init | unit 1 | unit 2 | unit 3 | unit 4 | unit 5 | unit 6 | unit 7 | unit 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| value | -0.08 | -0.17 | -0.11 | +0.15 | -1.27 | +1.09 | -0.60 | -1.57 |

### Trained dense weights (rounded to 2 decimals for display)

| W1 trained | x1 | x2 | 1 |
|---|---:|---:|---:|
| unit 1 | -1.65 | -1.51 | -0.43 |
| unit 2 | -0.01 | -1.70 | -0.09 |
| unit 3 | -1.48 | +1.47 | +0.13 |
| unit 4 | +1.06 | +0.94 | -0.10 |
| unit 5 | +2.38 | +2.32 | -0.38 |
| unit 6 | +0.61 | -0.44 | +1.90 |
| unit 7 | -1.05 | -0.92 | -0.16 |
| unit 8 | -1.77 | -1.57 | -0.33 |

| w2 trained | unit 1 | unit 2 | unit 3 | unit 4 | unit 5 | unit 6 | unit 7 | unit 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| value | -1.39 | +0.47 | +1.77 | -0.92 | -3.33 | +2.04 | -1.37 | -2.58 |

dense: first success at step 25, loss 0.002, accuracy 100% after 600 steps

### Ranking by magnitude

hidden layer, 24 magnitudes sorted, smallest first:

pruned (12): 0.010, 0.085, 0.100, 0.127, 0.157, 0.329, 0.376, 0.433, 0.436, 0.609, 0.918, 0.944
kept (12):   1.050, 1.065, 1.473, 1.481, 1.510, 1.572, 1.649, 1.696, 1.773, 1.901, 2.325, 2.375

cut between 0.944 and 1.050

output layer, 8 magnitudes sorted, smallest first:

pruned (4): 0.471, 0.916, 1.365, 1.389
kept (4):   1.766, 2.036, 2.579, 3.329

cut between 1.389 and 1.766

### Mask

| mask W1 | x1 | x2 | 1 |
|---|---:|---:|---:|
| unit 1 | 1 | 1 | 0 |
| unit 2 | 0 | 1 | 0 |
| unit 3 | 1 | 1 | 0 |
| unit 4 | 1 | 0 | 0 |
| unit 5 | 1 | 1 | 0 |
| unit 6 | 0 | 0 | 1 |
| unit 7 | 1 | 0 | 0 |
| unit 8 | 1 | 1 | 0 |

| mask w2 | unit 1 | unit 2 | unit 3 | unit 4 | unit 5 | unit 6 | unit 7 | unit 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| value | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 |

weights kept: 16 of 32

### Rewound ticket (mask times theta_0)

| W1 rewound | x1 | x2 | 1 |
|---|---:|---:|---:|
| unit 1 | -1.22 | -0.94 | 0 |
| unit 2 | 0 | -1.62 | 0 |
| unit 3 | -0.67 | +0.63 | 0 |
| unit 4 | +0.97 | 0 | 0 |
| unit 5 | +0.60 | +1.05 | 0 |
| unit 6 | 0 | 0 | +1.01 |
| unit 7 | -0.59 | 0 | 0 |
| unit 8 | +0.18 | -1.15 | 0 |

| w2 rewound | unit 1 | unit 2 | unit 3 | unit 4 | unit 5 | unit 6 | unit 7 | unit 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| value | 0 | 0 | -0.11 | 0 | -1.27 | +1.09 | 0 | -1.57 |

### Retraining, same 600 steps

| step | dense from theta_0 | ticket (rewound) | same mask, fresh init |
|---:|---|---|---|
| 0 | loss 0.827, acc 25% | loss 0.739, acc 62% | loss 0.989, acc 50% |
| 25 | loss 0.097, acc 100% | loss 0.117, acc 100% | loss 0.539, acc 50% |
| 50 | loss 0.042, acc 100% | loss 0.052, acc 100% | loss 0.379, acc 75% |
| 100 | loss 0.016, acc 100% | loss 0.021, acc 100% | loss 0.355, acc 75% |
| 200 | loss 0.006, acc 100% | loss 0.008, acc 100% | loss 0.349, acc 75% |
| 600 | loss 0.002, acc 100% | loss 0.002, acc 100% | loss 0.347, acc 75% |

first step with loss < 0.1 and 100% accuracy: dense 25, ticket 29, fresh init None

### Retrained ticket weights (rounded to 2 decimals)

| W1 ticket | x1 | x2 | 1 |
|---|---:|---:|---:|
| unit 1 | -1.22 | -0.94 | 0 |
| unit 2 | 0 | -1.62 | 0 |
| unit 3 | -1.53 | +1.35 | 0 |
| unit 4 | +0.97 | 0 | 0 |
| unit 5 | +2.21 | +2.71 | 0 |
| unit 6 | 0 | 0 | +2.40 |
| unit 7 | -0.59 | 0 | 0 |
| unit 8 | -2.65 | -1.88 | 0 |

| w2 ticket | unit 1 | unit 2 | unit 3 | unit 4 | unit 5 | unit 6 | unit 7 | unit 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| value | 0 | 0 | +1.83 | 0 | -3.51 | +2.44 | 0 | -3.39 |

### Forward passes, rounded ticket weights

x = (+1, +1, 1), class 0:

- unit 3: pre = (-1.53)(+1) + (+1.35)(+1) = -0.18, relu = 0.00, times w2 +1.83 = +0.00
- unit 5: pre = (+2.21)(+1) + (+2.71)(+1) = +4.92, relu = 4.92, times w2 -3.51 = -17.27
- unit 6: pre = (+2.40)(+1) = +2.40, relu = 2.40, times w2 +2.44 = +5.86
- unit 8: pre = (-2.65)(+1) + (-1.88)(+1) = -4.53, relu = 0.00, times w2 -3.39 = +0.00

logit = -11.41, probability of class 1 = 0.000

x = (+1, -1, 1), class 1:

- unit 3: pre = (-1.53)(+1) + (+1.35)(-1) = -2.88, relu = 0.00, times w2 +1.83 = +0.00
- unit 5: pre = (+2.21)(+1) + (+2.71)(-1) = -0.50, relu = 0.00, times w2 -3.51 = +0.00
- unit 6: pre = (+2.40)(+1) = +2.40, relu = 2.40, times w2 +2.44 = +5.86
- unit 8: pre = (-2.65)(+1) + (-1.88)(-1) = -0.77, relu = 0.00, times w2 -3.39 = +0.00

logit = +5.86, probability of class 1 = 0.997

### What the mask kept

- hidden weights kept: 12, of which 7 sit on a unit whose output weight was also kept
- weights that can still change the output: 11 of 32
- kept weights whose trained value has the same sign as the initial value: 14 of 16
- pruned weights whose trained value has the same sign as the initial value: 12 of 16

### Over 60 initializations

- dense network reaches the target: 53 of 60
- rewound ticket reaches the target: 47 of 60
- among the 53 initializations where dense succeeded: ticket 47 of 53; same mask with a fresh init 66 of 265
- same mask with a fresh init (5 fresh inits per seed, all seeds): 70 of 300

### Compact tables

| unit | θ0 (x1, x2, 1) | θT after training | mask | m ⊙ θ0 |
|---|---|---|:---:|---|
| 1 | -1.22, -0.94, -0.95 | -1.65, -1.51, -0.43 | 1 1 0 | -1.22, -0.94, 0 |
| 2 | -0.25, -1.62, -0.13 | -0.01, -1.70, -0.09 | 0 1 0 | 0, -1.62, 0 |
| 3 | -0.67, 0.63, 0.67 | -1.48, 1.47, 0.13 | 1 1 0 | -0.67, 0.63, 0 |
| 4 | 0.97, 0.54, -0.04 | 1.06, 0.94, -0.10 | 1 0 0 | 0.97, 0, 0 |
| 5 | 0.60, 1.05, -0.46 | 2.38, 2.32, -0.38 | 1 1 0 | 0.60, 1.05, 0 |
| 6 | 0.43, -0.03, 1.01 | 0.61, -0.44, 1.90 | 0 0 1 | 0, 0, 1.01 |
| 7 | -0.59, -0.21, 0.25 | -1.05, -0.92, -0.16 | 1 0 0 | -0.59, 0, 0 |
| 8 | 0.18, -1.15, 0.25 | -1.77, -1.57, -0.33 | 1 1 0 | 0.18, -1.15, 0 |

| output weight | u1 | u2 | u3 | u4 | u5 | u6 | u7 | u8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| θ0 | -0.08 | -0.17 | -0.11 | 0.15 | -1.27 | 1.09 | -0.60 | -1.57 |
| θT | -1.39 | 0.47 | 1.77 | -0.92 | -3.33 | 2.04 | -1.37 | -2.58 |
| mask | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 |
| m ⊙ θ0 | 0 | 0 | -0.11 | 0 | -1.27 | 1.09 | 0 | -1.57 |
