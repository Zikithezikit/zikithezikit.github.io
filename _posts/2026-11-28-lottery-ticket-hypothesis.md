---
title: "The Lottery Ticket Hypothesis: Small Networks Hidden in Big Ones"
date: 2026-11-28 08:00:00 +0200
author: yoav
description: "In my NumPy run, a LeNet-300-100 pruned to 7% of its weights and rewound to its initial values matched the dense network (98.03% against 97.92%). The same mask with new random weights reached 96.11%."
lang: en
categories: [machine-learning, deep-learning]
tags: [lottery-ticket-hypothesis, pruning, neural-networks, magnitude-pruning, sparsity, mnist, numpy, model-compression]
pin: false
math: true
mermaid: false
media_subpath: /assets/images/lottery-ticket-hypothesis/
image:
  path: cover.png
  alt: "Cover: the words Lottery Ticket Hypothesis and 7% of the weights, same accuracy, beside a 10 by 10 grid of squares where 7 are blue and 93 are grey, standing for the weights a mask keeps"
---

## 01. The question

A trained neural network can lose most of its weights and keep its accuracy. Han et al. pruned LeNet-300-100 on MNIST from 267,000 weights to 22,000. The test error went from 1.64% to 1.59% [\[1, p. 4\]](#ref-1).

That raises a question. If 22,000 weights are enough, why train the other 245,000? The obvious experiment is to build the small network and train it from scratch. Frankle and Carbin sum up the usual outcome: the architectures that pruning finds are harder to train from the start, and reach lower accuracy than the original [\[2, p. 1\]](#ref-2). Han et al. had already advised keeping the surviving weights instead of re-initializing them [\[1, p. 3\]](#ref-1).

Frankle and Carbin changed one detail. After pruning, they did not draw new random weights for the survivors. They put each survivor back to the value it had before training started, and trained that. The small network then reached the accuracy of the big one. Their name for it is a winning ticket: the big network contains a small one whose starting values make training easy, and that small one won the initialization lottery.

This post states the hypothesis precisely, does one prune-and-rewind round by hand on a 32-weight network, goes through what the papers measured, and then repeats the experiment myself in plain NumPy. The last sections cover where it stops working and what it is good for.

> Numbers marked "measured" come from my own runs, described in section 06 and in `_figures/lottery-ticket-hypothesis/` in the site's repository. Every other number cites a paper and a page.
{: .prompt-info }

## 02. How magnitude pruning works

Han et al. prune in three steps [\[1, p. 3\]](#ref-1). Train the network. Remove every connection whose weight is below a threshold. Retrain what is left. The size of a weight, $$\lvert w \rvert$$, is its magnitude, and removing a weight means holding it at zero for the rest of training.

In code, a mask $$m$$ of zeros and ones multiplies the weights, and the network computes with $$m \odot \theta$$, where $$\odot$$ multiplies entry by entry. Gradients of masked weights are zeroed too, so they stay zero.

The network used in most of this post is LeNet-300-100: 784 inputs, a hidden layer of 300 units, one of 100, and 10 outputs. The papers count 266K to 267K parameters. Without biases the count is

$$
784 \times 300 + 300 \times 100 + 100 \times 10 = 266{,}200
$$

weights, and 266,610 with the 410 biases. Frankle and Carbin prune it in rounds [\[2, p. 3\]](#ref-2). In each round they remove 20% of the surviving weights of each hidden layer and 10% of the output layer, which is half the rate. Each layer is ranked on its own. After $$r$$ rounds the fraction of weights remaining, which the paper calls $$P_m$$, is

$$
P_m(r) = \frac{(235{,}200 + 30{,}000)\cdot 0.8^{r} + 1{,}000 \cdot 0.9^{r}}{266{,}200}
$$

The curves in the paper are labelled 100%, 51.3%, 21.1%, 7.0%, 3.6% and 1.9% [\[2, p. 4\]](#ref-2). The formula gives the same numbers:

| rounds $$r$$ | 0 | 3 | 7 | 12 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|
| weights remaining | 100% | 51.3% | 21.1% | 7.0% | 3.6% | 2.9% |

The last column is the deepest round of my run. The paper's 1.9% is round 18.

## 03. The hypothesis, stated precisely

Take a network $$f(x; \theta)$$ with weights $$\theta$$, starting from $$\theta_0$$ drawn from an initialization distribution. Train it on a training set. It reaches its minimum validation loss at iteration $$j$$, with test accuracy $$a$$. Now train $$f(x; m \odot \theta_0)$$ on the same data, with a fixed mask $$m \in \{0,1\}^{\lvert\theta\rvert}$$. It reaches its minimum validation loss at iteration $$j'$$ with test accuracy $$a'$$. The hypothesis [\[2, p. 2\]](#ref-2) is that a mask exists with

$$
j' \le j, \qquad a' \ge a, \qquad \lVert m \rVert_0 \ll \lvert \theta \rvert
$$

The masked network learns at least as fast, is at least as accurate, and has far fewer weights. $$\lVert m \rVert_0$$ counts the ones in the mask.

The statement only says that such a mask exists. The paper finds one with this procedure [\[2, p. 2\]](#ref-2):

1. Initialize $$\theta_0$$ at random.
2. Train for $$j$$ iterations. The trained weights are $$\theta_T$$.
3. Prune the $$p\%$$ smallest-magnitude weights of $$\theta_T$$. The result is the mask $$m$$.
4. Reset the survivors to their values in $$\theta_0$$. The result is the winning ticket $$f(x; m \odot \theta_0)$$.

Repeating steps 2 to 4, each round pruning more, is iterative pruning. The paper uses it for everything after the first few plots, because it finds smaller tickets than pruning once [\[2, p. 5\]](#ref-2).

![Diagram of one round: random weights theta 0 are trained, the smallest 20% of weights are pruned to make a mask, the survivors are rewound to theta 0, and the rewound network is retrained and pruned again; a control keeps the mask but draws fresh random weights](ticket-loop.svg){: w="900" h="470" .shadow }
_The procedure of Frankle and Carbin [\[2, p. 2\]](#ref-2), with the random-reinitialization control they use [\[2, p. 4\]](#ref-2)._

The control matters as much as the procedure. Keep the mask and draw new random weights, giving $$f(x; m \odot \theta_0'')$$, where $$\theta_0''$$ comes from the same initialization distribution. If only the structure of the mask mattered, this network would do as well as the ticket. If the starting values matter, it should do worse.

### Rewinding

The claim holds for small networks and fails for bigger ones (section 07). Frankle et al. changed what step 4 resets to. Instead of $$\theta_0$$, the survivors go back to $$\theta_k$$, the weights of the dense run after $$k$$ iterations [\[3, p. 5\]](#ref-3). Their revised statement [\[4, p. 2\]](#ref-4): there are an iteration $$k$$ much smaller than the full training time and a mask $$m$$ such that $$m \odot \theta_k$$ trains to at least the dense accuracy in no more iterations than remain. They stop calling these winning tickets, since the weights are no longer a random initialization, and call them matching subnetworks [\[3, p. 5\]](#ref-3).

## 04. A network small enough to do by hand

The real network has 266,200 weights and is pruned for 16 rounds. The toy has 32 weights and is pruned once. The steps are the same.

The toy network takes two inputs and a constant 1 (so the bias is a weight), has 8 ReLU units, and returns one number, the logit. That is $$8 \times 3 = 24$$ weights in the first layer and 8 in the second. The task is XOR: class 1 when $$x_1$$ and $$x_2$$ have different signs. There are 16 points, four around each corner $$(\pm 1, \pm 1)$$, with noise of 0.25. The points are made up for the example. Training is full-batch gradient descent with learning rate 0.5 for 600 steps. I call a run "trained" when the loss is below 0.1 and all 16 points are right. Everything below is computed by `_figures/lottery-ticket-hypothesis/toy.py`, and weights are shown to two decimals.

### Train the dense network

The starting weights $$\theta_0$$ are drawn from a Gaussian with standard deviation 0.7 and rounded to two decimals. They are in the table below, next to the weights after training. The dense network first passes the test at step 25 and ends at loss 0.002 with all 16 points right.

### Rank and prune

Each layer is ranked on its own by the magnitude of the trained weights, and the smaller half is pruned.

- First layer, 24 magnitudes. The smallest 12 are 0.010, 0.085, 0.100, 0.127, 0.157, 0.329, 0.376, 0.433, 0.436, 0.609, 0.918, 0.944. The largest 12 start at 1.050 and end at 2.375. The cut falls between 0.944 and 1.050.
- Output layer, 8 magnitudes. The smallest 4 are 0.471, 0.916, 1.365, 1.389. The largest 4 are 1.766, 2.036, 2.579, 3.329.

### Rewind

The mask is 1 where a weight survived and 0 where it was pruned. The ticket is the mask times the original weights, $$m \odot \theta_0$$.

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

Look at unit 3's output weight. It started at -0.11 and ended at +1.77. It survived because training pushed it far from where it began. The ticket still starts it at -0.11.

The mask keeps 16 of 32 weights, but only 11 of them can change the output. Units 1, 2, 4 and 7 lost their output weight, so their 5 surviving first-layer weights feed nothing. Magnitude pruning ranks one layer at a time and does not know that. Han et al. note that a neuron with no input or no output connections can be deleted [\[1, p. 4\]](#ref-1).

### Retrain

Train the ticket, with the mask fixed, for the same 600 steps. As a control, train the same mask from a fresh random start (the first of five I drew). Loss and accuracy on the 16 points:

| step | dense, from θ0 | ticket, m ⊙ θ0 | same mask, fresh init |
|---:|---|---|---|
| 0 | loss 0.827, acc 25% | loss 0.739, acc 62% | loss 0.989, acc 50% |
| 25 | loss 0.097, acc 100% | loss 0.117, acc 100% | loss 0.539, acc 50% |
| 50 | loss 0.042, acc 100% | loss 0.052, acc 100% | loss 0.379, acc 75% |
| 100 | loss 0.016, acc 100% | loss 0.021, acc 100% | loss 0.355, acc 75% |
| 200 | loss 0.006, acc 100% | loss 0.008, acc 100% | loss 0.349, acc 75% |
| 600 | loss 0.002, acc 100% | loss 0.002, acc 100% | loss 0.347, acc 75% |

The dense network first passes the test at step 25 and the ticket at step 29. The fresh-start network never does. After 600 steps it still gets 4 of the 16 points wrong.

To check the ticket by hand, take the retrained weights, rounded to two decimals. Only units 3, 5, 6 and 8 have an output weight. The ReLU of a unit is its input sum if that is positive, and 0 otherwise.

For $$x = (1, 1)$$, which is class 0:

- unit 3: $$(-1.53)(1) + (1.35)(1) = -0.18$$, so ReLU gives 0.
- unit 5: $$(2.21)(1) + (2.71)(1) = 4.92$$, times its output weight $$-3.51$$ gives $$-17.27$$.
- unit 6: only its bias weight is left, $$2.40$$, times $$2.44$$ gives $$5.86$$.
- unit 8: $$(-2.65)(1) + (-1.88)(1) = -4.53$$, so ReLU gives 0.

The logit is $$-17.27 + 5.86 = -11.41$$, which is class 0. For $$x = (1, -1)$$, class 1, units 3, 5 and 8 are all off and only unit 6 contributes. The logit is $$+5.86$$, and the probability of class 1 is 0.997.

### One initialization is not a result

I picked this example. It is the first of my 60 initializations where the dense network trains, the ticket trains, and none of five fresh starts does. Over all 60 initializations:

- The dense network trained in 53 of 60 initializations.
- The rewound ticket trained in 47 of 60. Among the 53 where the dense network trained, it trained in 47.
- The same mask with a fresh random start trained in 70 of 300 tries (23%). Among the 53 good initializations, 66 of 265 (25%).

So rewinding made a working network about three times as likely in this toy, and a fresh start still worked one time in four. With 4 or 6 hidden units, half the weights were rarely enough to solve XOR at all, which is why the toy has 8. In the real run the same steps repeat for 16 rounds on 266,200 weights. The ranking is a sort, as in the snippet in section 10.

## 05. What the paper measured

The paper trains LeNet-300-100 with Adam at learning rate 0.0012, for 50,000 iterations with batches of 60, from a Gaussian Glorot initialization [\[2, p. 3\]](#ref-2). Each result is the average of five trials, with error bars at the minimum and maximum [\[2, p. 4\]](#ref-2). Under iterative pruning:

- The tickets learn faster as weights are removed, until 21% remain. There early stopping comes 38% earlier than for the dense network. With fewer weights learning slows again, and at 3.6% it is back at the dense network's speed [\[2, p. 4\]](#ref-2).
- Test accuracy rises by more than 0.3 percentage points when 13.5% remain, and falls back to the dense level at 3.6% [\[2, p. 4\]](#ref-2).
- The control loses accuracy early. Reinitialized networks drop below the original accuracy at 21.1% remaining. The tickets do so at 2.9%. At 21%, the ticket reaches its minimum validation loss 2.51 times faster than the reinitialized network and is half a percentage point more accurate [\[2, p. 4\]](#ref-2).
- Pruning once instead of in rounds also finds tickets that stop earlier than the dense network, when 67.5% to 17.6% remain. The iterative ones are smaller and learn faster [\[2, p. 5\]](#ref-2).
- On CIFAR-10, the convolutional networks Conv-2, Conv-4 and Conv-6 reach their minimum validation loss up to 3.5, 3.5 and 2.5 times faster, with test accuracy up by as much as 3.4, 3.5 and 3.3 points [\[2, p. 6\]](#ref-2).
- Across the fully connected and convolutional networks they tried, the tickets are 10 to 20% of the original size, or less [\[2, p. 2\]](#ref-2).

> "Faster" in the paper means the iteration of minimum validation loss, which stands in for when early stopping would end training [\[2, p. 1\]](#ref-2). It is not wall-clock time.
{: .prompt-info }

One result rules out a simple explanation. If the ticket's starting values were already close to the trained ones, rewinding would be trivial. The paper checks and finds the opposite: the weights of a winning ticket move further during training than other weights [\[2, p. 9\]](#ref-2).

## 06. My own run

I repeated the experiment before writing about it. There is no deep-learning framework on my machine, so I wrote LeNet-300-100 and the Adam optimizer in NumPy (`_figures/lottery-ticket-hypothesis/experiment.py`, about 240 lines). The setup follows the paper where I could:

- Data: MNIST [\[5\]](#ref-5), split into 55,000 images for training, 5,000 for validation and 10,000 for test. The validation set finds the early-stopping iteration.
- Network: 784-300-100-10 with ReLU, Gaussian Glorot initialization and biases at zero.
- Training: Adam with learning rate 0.0012, batches of 256, 1,500 iterations, which is about 7 epochs. The paper trains for 50,000 iterations with batches of 60 [\[2, p. 3\]](#ref-2), so my runs see about 8 times fewer examples.
- Pruning: the schedule from section 02, ranked by trained magnitude within each layer, survivors rewound to $$\theta_0$$. 16 rounds, ending at 2.9% of the weights.
- Controls: the winning-ticket mask with a fresh random initialization, and a random mask with the same number of survivors in every layer and the original initial values.
- 5 seeds. Each seed has its own $$\theta_0$$, its own data order and its own controls.

> Numbers marked "measured" are means over the 5 seeds, with the minimum and maximum in brackets. My training budget is about 8 times shorter than the paper's, so compare the shapes of the curves, not the exact values.
{: .prompt-info }

![Test accuracy against the share of weights remaining, five seeds each. The winning ticket stays between 97.6% and 98.2% from 100% down to 2.9% of the weights. The same masks with new random weights fall to 95.2%, and random masks to 92.6%](accuracy-vs-sparsity.png){: w="1200" h="735" .shadow }
_Measured. LeNet-300-100 on MNIST, 5 seeds, 17 training runs per ticket. Pruning schedule of Frankle and Carbin [\[2, p. 3\]](#ref-2). Test accuracy at the iteration of minimum validation loss._

The dense network reaches 97.92% (97.82 to 98.05). The ticket stays at that level for a long way. At 26.3% of the weights it reaches 98.18% (98.14 to 98.25). At 7.0% it reaches 98.03% (97.95 to 98.15). Its mean stays at or above the dense mean down to 5.6%, where it is 97.94%, and I call those tickets matching. Below that it slips: 97.78% at 3.6% and 97.62% at 2.9% (97.46 to 97.73).

The controls fall away much sooner. At 7.0% remaining the same mask with new random weights reaches 96.11% and the random mask 94.70%, against 98.03% for the ticket. At 3.6% the three numbers are 95.26%, 93.36% and 97.78%.

The two controls let me split the gap at 7.0% into two parts. Going from a random mask to the learned mask, with the same kind of start, gains 1.41 points (96.11 minus 94.70). Going from new random weights to the original initial weights, on the same mask, gains another 1.92 points (98.03 minus 96.11). Both the structure and the starting values matter in my run. That is my calculation from the means above.

![Iteration of minimum validation loss against the share of weights remaining. The winning ticket falls from 1,390 for the dense network to 930 at 26.3% remaining, then climbs back to 1,490 at 2.9%. The same masks with new random weights stay between 1,330 and 1,500, the end of training](early-stop-iteration.png){: w="1200" h="675" .shadow }
_Measured, same runs as the chart above. Every network trains for 1,500 iterations, so a value near 1,500 means the validation loss was still falling when training stopped._

The dense network reaches its minimum validation loss at iteration 1,390 on average. The ticket gets there at 1,050 with 51.3% of the weights and at 930 with 26.3%, which is 33% earlier (my calculation). It is back at 1,390 at 7.0%, and at 1,490 at 2.9%. The paper has early stopping 38% earlier at 21% and back at the dense speed at 3.6% [\[2, p. 4\]](#ref-2). The shape is the same. The minimum sits at a different sparsity.

Two limits of my run, both from the short training budget:

- The controls reach their best validation loss at 1,330 to 1,500 iterations, at the end of training. They were still improving when training stopped, so their gap in speed is larger than the chart shows, and part of their gap in accuracy may close with longer training. In the paper the reinitialized network holds the original accuracy until 21.1% remains [\[2, p. 4\]](#ref-2). Mine falls below the dense accuracy at the first rounds, for example 97.69% against 97.92% at 64.1%. I think the budget is the reason, but I did not test that.
- The tickets beat the dense mean by 0.26 points at 26.3%. To see if the dense network was simply undertrained, I trained it from the same 5 initializations for 6,000 iterations. At the early-stopping iteration it gets 97.97% (97.88 to 98.07), the same as before, and its validation minimum comes at about iteration 1,460 (1,200 to 1,700). At the end of the 6,000 iterations its accuracy is 98.18% (97.84 to 98.44). So the ticket at 26.3% matches a long-trained dense network and learns it sooner. I did not train tickets for longer, so I cannot say they generalize better.



## 07. Where it breaks, and late rewinding

The paper itself reports where the recipe stops working. For VGG-19 on CIFAR-10, iterative pruning at the standard learning rate of 0.1 found no winning tickets, and the subnetworks did no better than the same subnetworks with random weights [\[2, p. 8\]](#ref-2). At 0.01 the usual pattern came back: subnetworks stayed within 1 percentage point of the original accuracy down to 3.5% of the weights, but did not match it. Linear warmup over 10,000 iterations made it possible to find tickets at 0.1, down to 1.5% of the weights [\[2, p. 8\]](#ref-2). For ResNet-18 the best tickets at the lower rate reached 89.5%, short of the 90.5% of the dense network at the standard rate, and the authors found no settings that gave winning tickets at 0.1 [\[2, p. 8\]](#ref-2).

Liu et al. ran the comparison with their own settings and reached the opposite reading. With the best learning rate, they found that the winning-ticket initialization does not improve on random initialization [\[6, p. 1\]](#ref-6). In their unstructured-pruning runs on CIFAR-10, the ticket only helped at learning rate 0.01, and that rate gave lower accuracy than the common 0.1 [\[6, p. 11\]](#ref-6). They list the differences from the original setup: deeper networks, momentum SGD with a large learning rate against Adam with a small one, and ImageNet. For unstructured pruning on CIFAR-10 they trace the disagreement to the learning rate [\[6, p. 10\]](#ref-6).

Frankle et al. then asked why tickets work at some scales and not others [\[3\]](#ref-3). Their tool is instability analysis. Train two copies of one network from the same start with different data orders. Evaluate the networks on the straight line between the two sets of trained weights. The instability is the largest increase in error along that line [\[3, p. 2\]](#ref-3). If it is near zero, both copies ended in the same linearly connected minimum.

They run iterative magnitude pruning (IMP), the procedure of section 03, and find that a pruned subnetwork only reaches full accuracy when it is stable in this sense [\[3, p. 5\]](#ref-3). The pruned subnetworks of LeNet on MNIST are stable and matching at initialization [\[3, p. 5\]](#ref-3). Bigger networks become stable a little way into training. At the most extreme sparsities where they find matching subnetworks, ResNet-20 and VGG-16 become stable at iterations 500 and 1,000, and ResNet-50 and Inception-v3 at epochs 5 and 6 [\[3, p. 7\]](#ref-3). The unpruned ResNet-50 needs until epoch 18 [\[3, p. 7\]](#ref-3).

That is the case for rewinding. If the survivors go back to the weights from the point where the network became stable, the subnetwork is matching. IMP with rewinding found subnetworks of ResNet-50 with 80% of the weights removed, taken at epoch 6 of 90, with no loss of accuracy on ImageNet [\[4, p. 2\]](#ref-4).

> Rewinding to epoch 6 is not a lottery ticket in the original sense. The weights are not an initialization, and the mask comes from a network that was trained to the end first.
{: .prompt-warning }

My run is on the small end, where LeNet is stable at initialization, so it cannot show any of this.

## 08. What the mask keeps

Zhou et al. split the procedure into three choices [\[7, p. 2\]](#ref-7). The mask criterion decides which weights survive. The mask-1 action decides what happens to the survivors, which in the original is a reset to their initial values. The mask-0 action decides what happens to the pruned weights, which in the original is zero and frozen. They varied each one.

- The criterion. Keeping the largest final magnitude works, and so does keeping the weights that grew the most, $$\lvert w_f \rvert - \lvert w_i \rvert$$ [\[7, p. 4\]](#ref-7).
- The survivors. Fresh random values trained poorly, as in the original. But fresh values given the same sign as the original initial weight trained well. Setting every survivor in a layer to a constant, plus or minus the standard deviation of that layer's initialization, with the original sign, also worked [\[7, p. 4\]](#ref-7). Their reading is that a good start is mostly a good choice of signs.
- The pruned weights. Freezing them at zero beat freezing them at their initial values [\[7, p. 5\]](#ref-7). Their explanation is that magnitude pruning zeros the weights that were already moving toward zero, so masking acts like a step of training [\[7, p. 6\]](#ref-7).

### Masks that classify without training

If masking is a kind of training, how far can it go? Zhou et al. applied masks to untrained networks and called good ones supermasks. A mask that keeps large final weights that also kept their sign gave 80% test accuracy on MNIST and 24% on CIFAR-10 with no training. With the survivors set to signed constants it gave up to 86% on MNIST and 41% on CIFAR-10 [\[7, p. 7\]](#ref-7). Training the mask by gradient descent, with the weights frozen at random values, gave up to 95.3% on MNIST and 65.4% on CIFAR-10 [\[7, p. 7\]](#ref-7).

Ramanujan et al. pushed the same idea to ImageNet. They found a subnetwork of a randomly weighted Wide ResNet-50 that is smaller than a trained ResNet-34 and matches its accuracy, without ever changing a weight [\[8, p. 1\]](#ref-8).

I checked the supermask claim on my own network. From each of the 5 initializations I trained a dense LeNet-300-100, built one-shot masks from the initial and the trained weights, and measured the test accuracy of the untrained initial network with the mask applied. The same fraction is kept in every layer.

![Test accuracy of an untrained network with a mask against the share of weights kept. Random masks stay near 10%. Keeping the largest final weights peaks at 74.5% with 40% kept. Keeping large weights that kept their sign reaches 81.2% with 40% kept, and 86.7% when the survivors are set to signed constants](supermask.png){: w="1200" h="795" .shadow }
_Measured, 5 seeds. One-shot masks built from the weights before and after training one dense network, then applied to the untrained initial weights. Criteria from Zhou et al. [\[7, p. 7\]](#ref-7)._

A random mask scores about 10%, which is chance for ten classes. Keeping the largest final weights gives 74.5% when 40% of the weights are kept. Keeping the large final weights that also kept their sign gives 81.2% at 40%, and 86.7% when the survivors are set to signed constants. The paper reports 80% and 86% on MNIST [\[7, p. 7\]](#ref-7). These are untrained networks, scored on test images.

## 09. What it is good for

Finding a ticket is expensive. The paper says so in its limitations: iterative pruning needs 15 or more consecutive training runs, for several trials [\[2, p. 9\]](#ref-2). In my run, a ticket at 2.9% of the weights took 17 trainings in a row, one for the dense network and one for each of 16 rounds. A single training took about 9 seconds when it ran alone on my machine, so the chain costs about 2.5 minutes against 9 seconds for the dense network (my calculation, 17 times 9). The whole experiment, 245 trainings counting the controls, took 1,166 seconds on a four-core CPU.

The result is also not a faster network. Frankle and Carbin note that unstructured pruning gives sparse weights that are not optimized for current libraries or hardware [\[2, p. 9\]](#ref-2). My own code stores the ticket as a dense matrix times a mask, so a training step costs the same as for the dense network.

What the hypothesis does give:

- It shows that a mask and a starting point exist that train as well as the full network, at 3.6% of the weights for LeNet-300-100 [\[2, p. 4\]](#ref-2). That is evidence the dense network is far larger than the function needs.
- Pruning itself is useful and older. Han et al. get 9 to 13 times fewer parameters on AlexNet and VGG-16 with no loss of accuracy, and they do it by keeping the trained weights, not by rewinding [\[1, p. 4\]](#ref-1).
- Rewinding has found uses beyond the hypothesis. Frankle et al. report that subnetworks found with rewinding transfer between vision tasks, and that rewinding reaches state-of-the-art sparsities, citing other authors' work [\[3, p. 9\]](#ref-3). I have not read those papers.
- The counterpoint is that the weights may not be the valuable part. Liu et al. find that for structured pruning, a pruned architecture trained from random initialization matches the fine-tuned one, so pruning works as a way to find an architecture [\[6, p. 1\]](#ref-6).

## 10. Try it

The core operation is a few lines of NumPy. This takes the output-layer weights from the toy, before and after training, and prunes half.

```python
import numpy as np

def prune_and_rewind(w0, wT, mask, rate):
    alive = np.abs(wT[mask > 0])                       # only weights that survived so far
    cut = np.sort(alive)[int(rate * alive.size) - 1]   # largest magnitude that gets pruned
    mask = mask * (np.abs(wT) > cut)                   # new mask keeps the larger ones
    return mask, np.where(mask > 0, w0, 0.0)           # rewound weights: m * theta_0

w0 = np.array([-0.08, -0.17, -0.11, 0.15, -1.27, 1.09, -0.60, -1.57])  # output layer at init
wT = np.array([-1.39, 0.47, 1.77, -0.92, -3.33, 2.04, -1.37, -2.58])   # after training
mask, rewound = prune_and_rewind(w0, wT, np.ones(8), rate=0.5)
print(mask)       # [0. 0. 1. 0. 1. 1. 0. 1.]
print(rewound)
```

Output:

```
[0. 0. 1. 0. 1. 1. 0. 1.]
[ 0.    0.   -0.11  0.   -1.27  1.09  0.   -1.57]
```

The whole experiment is in the site's repository, in [`_figures/lottery-ticket-hypothesis/`](https://github.com/Zikithezikit/zikithezikit.github.io/tree/main/_figures/lottery-ticket-hypothesis). It needs only NumPy, downloads MNIST on the first run and writes `results.json` and `results.csv`. `toy.py` in the same folder prints every number of section 04.

```bash
python3 _figures/lottery-ticket-hypothesis/experiment.py --quick   # 1 seed, 4 rounds, about 2 minutes
python3 _figures/lottery-ticket-hypothesis/experiment.py           # 5 seeds, 16 rounds, about 20 minutes
```

## Sources

<span id="ref-1"></span>\[1\] Han, S., Pool, J., Tran, J., & Dally, W. J. (2015). _Learning both weights and connections for efficient neural networks_. NeurIPS 2015. arXiv:1506.02626. [https://arxiv.org/abs/1506.02626](https://arxiv.org/abs/1506.02626)

<span id="ref-2"></span>\[2\] Frankle, J., & Carbin, M. (2019). _The lottery ticket hypothesis: Finding sparse, trainable neural networks_. ICLR 2019. arXiv:1803.03635. [https://arxiv.org/abs/1803.03635](https://arxiv.org/abs/1803.03635)

<span id="ref-3"></span>\[3\] Frankle, J., Dziugaite, G. K., Roy, D. M., & Carbin, M. (2020). _Linear mode connectivity and the lottery ticket hypothesis_. ICML 2020. arXiv:1912.05671. [https://arxiv.org/abs/1912.05671](https://arxiv.org/abs/1912.05671)

<span id="ref-4"></span>\[4\] Frankle, J., Dziugaite, G. K., Roy, D. M., & Carbin, M. (2020). _Stabilizing the lottery ticket hypothesis_. arXiv:1903.01611 (v3). [https://arxiv.org/abs/1903.01611](https://arxiv.org/abs/1903.01611)

<span id="ref-5"></span>\[5\] LeCun, Y., Cortes, C., & Burges, C. J. C. _The MNIST database of handwritten digits_. Files downloaded from the CVDF mirror: [https://storage.googleapis.com/cvdf-datasets/mnist/](https://storage.googleapis.com/cvdf-datasets/mnist/)

<span id="ref-6"></span>\[6\] Liu, Z., Sun, M., Zhou, T., Huang, G., & Darrell, T. (2019). _Rethinking the value of network pruning_. ICLR 2019. arXiv:1810.05270. [https://arxiv.org/abs/1810.05270](https://arxiv.org/abs/1810.05270)

<span id="ref-7"></span>\[7\] Zhou, H., Lan, J., Liu, R., & Yosinski, J. (2019). _Deconstructing lottery tickets: Zeros, signs, and the supermask_. NeurIPS 2019. arXiv:1905.01067. [https://arxiv.org/abs/1905.01067](https://arxiv.org/abs/1905.01067)

<span id="ref-8"></span>\[8\] Ramanujan, V., Wortsman, M., Kembhavi, A., Farhadi, A., & Rastegari, M. (2020). _What's hidden in a randomly weighted neural network?_ arXiv:1911.13299 (v2). [https://arxiv.org/abs/1911.13299](https://arxiv.org/abs/1911.13299)
