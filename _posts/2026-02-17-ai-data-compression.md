---
title: "Compression and Prediction: The Maths of Learned Codecs"
author: yoav
description: "A learned image codec saves 59.8% of the bits JPEG uses at equal PSNR on the Kodak images. The maths behind it: entropy, the rate-distortion function, a loss of rate plus λ times distortion, and a model that predicts probabilities."
date: 2026-02-17 12:00:00 +0200
lang: en
categories: [AI, Technology, Data Science]
tags: [data-compression, information-theory, entropy, rate-distortion, learned-compression, machine-learning]
pin: false
math: true
mermaid: false
image:
    path: /assets/images/ai-data-compression.jpg
    alt: AI-powered data compression neural network visualization
---

## 01. The question

A photo is millions of numbers. Sending them as they are costs bits, and most of those bits carry nothing new. Compression sends fewer.

There are two kinds. Lossless compression gives back exactly the input. Lossy compression gives back something close and drops the rest. Both need a probability for each thing they might have to send. A neural network is a good way to produce those probabilities.

This post covers three things: how many bits a source needs, what a small loss of quality buys, and how a learned image codec is built and trained on top of that. It ends with language models, which use the same idea on text.

> Numbers marked "made up" were chosen for the example. Every other computed number was printed by a short Python script, `toy.py`, kept in the site repository. Numbers with a citation come from the cited paper.
{: .prompt-info }

## 02. How few bits does lossless coding need?

A source emits symbols with known probabilities. Shannon defined its entropy [\[1\]](#ref-1):

$$
H(X) = -\sum_x p(x)\log_2 p(x)
$$

A symbol with probability $$p$$ costs $$-\log_2 p$$ bits: probability $$\tfrac{1}{2}$$ costs 1 bit, probability $$\tfrac{1}{8}$$ costs 3 bits. Entropy is the average of these costs. No lossless code can use fewer bits per symbol on average [\[2, p. 3\]](#ref-2).

### By hand

Shannon's own example [\[1, p. 18\]](#ref-1) is a source with four letters, drawn independently:

| symbol | $$p$$ | $$-\log_2 p$$ | $$p \cdot (-\log_2 p)$$ |
|---|---:|---:|---:|
| A | 0.5 | 1 | 0.500 |
| B | 0.25 | 2 | 0.500 |
| C | 0.125 | 3 | 0.375 |
| D | 0.125 | 3 | 0.375 |

The last column adds up to $$H = 1.75$$ bits per symbol. Four equally likely symbols would have $$H = 2$$.

Give each symbol a bit string as long as its cost. That gives the code in the table below, and no string is the start of another, so the receiver needs no separators. Huffman's algorithm [\[3\]](#ref-3) builds the same lengths for this source.

| symbol | code | length |
|---|---|---:|
| A | 0 | 1 |
| B | 10 | 2 |
| C | 110 | 3 |
| D | 111 | 3 |

The average length is $$0.5 \cdot 1 + 0.25 \cdot 2 + 0.125 \cdot 3 + 0.125 \cdot 3 = 1.75$$ bits, equal to the entropy. The message AABACABD becomes 00100110010111, which is 14 bits. A fixed 2-bit code needs 16.

This is exact only because every probability is a power of $$\tfrac{1}{2}$$. Code lengths are whole numbers, and $$-\log_2 p$$ is a whole number only then. Arithmetic coding removes the limit. It codes a whole sequence at once and adds about one bit to the sequence, not one bit per symbol [\[2, p. 3\]](#ref-2).

### A wrong model costs bits

The coder needs probabilities. If it uses $$q$$ while the data follows $$p$$, the average length is the cross-entropy [\[2, p. 4\]](#ref-2):

$$
H(p, q) = -\sum_x p(x)\log_2 q(x)
$$

For the source above, with three made-up models $$q$$ for the symbols A to D:

| model $$q$$ | $$q$$ for A, B, C, D | bits per symbol | excess over $$H$$ |
|---|---|---:|---:|
| the true $$p$$ | 0.5, 0.25, 0.125, 0.125 | 1.750 | 0.000 |
| a mild guess | 0.4, 0.3, 0.2, 0.1 | 1.801 | 0.051 |
| uniform | 0.25, 0.25, 0.25, 0.25 | 2.000 | 0.250 |
| reversed | 0.125, 0.125, 0.25, 0.5 | 2.625 | 0.875 |

The data did not change. Only the model did. Everything below is about getting better probabilities.

## 03. What does a little loss buy?

For lossy coding you pick a distortion measure $$d(x, \hat{x})$$ between the original $$x$$ and the reconstruction $$\hat{x}$$. The usual choice for images is squared error.

Shannon defined the rate of a source for a given fidelity as the smallest mutual information between source and reconstruction, over all systems that meet the fidelity [\[1, pp. 49 to 50\]](#ref-1). In current notation:

$$
R(D) = \min_{p(\hat{x} \mid x)\,:\ \mathbb{E}[d(X, \hat{X})] \le D} I(X; \hat{X})
$$

$$I(X; \hat{X})$$ is the mutual information in bits: how much the reconstruction tells you about the original. Below $$R(D)$$ bits per sample, distortion $$D$$ cannot be reached [\[1, p. 50\]](#ref-1).

### The Gaussian case

For a Gaussian source with variance $$\sigma^2$$ and squared error, the minimum has a closed form [\[4\]](#ref-4):

$$
R(D) =
\begin{cases}
\tfrac{1}{2}\log_2\dfrac{\sigma^2}{D} & 0 \le D \le \sigma^2 \\
0 & D > \sigma^2
\end{cases}
$$

Take $$\sigma^2 = 4$$ and $$D = 1$$. Then $$R = \tfrac{1}{2}\log_2 4 = 1$$ bit per sample. To see where it comes from, write the source as $$X = \hat{X} + N$$ with $$\hat{X} \sim \mathcal{N}(0, \sigma^2 - D)$$ and $$N \sim \mathcal{N}(0, D)$$, independent. The squared error is $$\mathbb{E}[N^2] = D$$. Two jointly Gaussian variables with squared correlation $$\rho^2$$ share $$-\tfrac{1}{2}\log_2(1 - \rho^2)$$ bits, and here $$\rho^2 = (\sigma^2 - D)/\sigma^2 = 0.75$$. That gives 1.000 bits. I also drew 200,000 samples of this pair: the variance of $$X$$ came out at 4.00 and the mean squared error at 1.00.

| $$D$$ | 4 | 2 | 1 | 0.5 | 0.25 |
|---|---:|---:|---:|---:|---:|
| $$R(D)$$ in bits | 0.00 | 0.50 | 1.00 | 1.50 | 2.00 |

Each halving of $$D$$ costs half a bit. Put differently, each extra bit divides $$D$$ by 4: $$D = 1.0$$ at 1 bit and $$D = 0.25$$ at 2 bits. At $$D = \sigma^2$$ the rate is 0, because outputting the mean gives that distortion for free.

### Several components

Now take independent Gaussian components with variances $$\sigma_i^2$$ and one total distortion budget. The cheapest split gives component $$i$$ the distortion $$\min(\theta, \sigma_i^2)$$, with the level $$\theta$$ chosen so the distortions add up to the budget. A component with variance below $$\theta$$ gets no bits at all. This is called reverse water-filling [\[5\]](#ref-5).

An example with made-up variances 4, 1 and 0.25 and a budget of 1.25. The level is $$\theta = 0.5$$, so the distortions are 0.5, 0.5 and 0.25:

$$
R = \tfrac{1}{2}\log_2\frac{4}{0.5} + \tfrac{1}{2}\log_2\frac{1}{0.5} + 0 = 1.5 + 0.5 = 2.00 \text{ bits}
$$

Giving every component the same relative distortion instead costs 3.11 bits. A grid search over all splits that add up to 1.25 found a minimum of 2.00 bits at exactly (0.5, 0.5, 0.25).

This is why a good transform helps. If it moves almost all the variance into a few components, the others cost almost nothing.

## 04. Transform, quantize, code

A transform code has four steps. JPEG uses a discrete cosine transform on blocks of pixels and JPEG 2000 a wavelet transform [\[6, p. 2\]](#ref-6). A learned codec replaces the two transforms with neural networks and trains both together [\[6, p. 2\]](#ref-6).

1. Analysis transform: the encoder network maps the image to a latent vector, $$y = g_a(x; \phi)$$.
2. Quantization: $$\hat{y} = \text{round}(y)$$. This is where information is lost.
3. Entropy coding: a probability model $$p(\hat{y})$$ turns $$\hat{y}$$ into bits at a cost of $$-\log_2 p(\hat{y})$$ each, as in section 02. This step is lossless.
4. Synthesis transform: the decoder network maps back, $$\hat{x} = g_s(\hat{y}; \theta)$$.

The rate $$R$$ is the average $$-\log_2 p(\hat{y})$$ over images. The distortion $$D$$ is the average $$d(x, \hat{x})$$.

### A 2x2 patch by hand

To see the steps without a network, use a fixed transform. The patch is made up: four grey values, 121, 125, 80 and 85. The transform is the 2x2 Hadamard matrix, scaled so that it keeps sums of squares:

$$
y = \frac{1}{2}
\begin{bmatrix} 1&1&1&1 \\ 1&-1&1&-1 \\ 1&1&-1&-1 \\ 1&-1&-1&1 \end{bmatrix}
\begin{bmatrix} 121 \\ 125 \\ 80 \\ 85 \end{bmatrix}
=
\begin{bmatrix} 205.5 \\ -4.5 \\ 40.5 \\ 0.5 \end{bmatrix}
$$

The sum of squares is 43,891 for the pixels and 43,891 for the coefficients. The first coefficient holds 96.2% of it, which is the situation section 03 asked for.

Quantize with a step of 8: the indices are 26, −1, 5 and 0, which stand for 208, −8, 40 and 0. The inverse transform gives the pixels 120, 128, 80 and 88. The errors are −1, 3, 0 and 3, a total squared error of 19. The same 19 comes out in the coefficient domain, because the transform keeps sums of squares.

Four small integers are left for the entropy coder. How many bits they cost depends on the probability model. Section 06 is about that model.

## 05. How do you train through rounding?

Rate and distortion pull against each other. The codec minimizes one number that combines them [\[6, p. 4\]](#ref-6):

$$
\mathcal{L} = \mathbb{E}\big[-\log_2 p(\hat{y})\big] + \lambda\,\mathbb{E}\big[d(x, \hat{x})\big]
$$

$$\lambda$$ is the weight on distortion. A large $$\lambda$$ gives low distortion and a high rate. A small one gives the reverse. Each $$\lambda$$ gives its own trained model, and the set of models traces a rate-distortion curve. Ballé et al. trained 8 values of $$\lambda$$ [\[7, p. 7\]](#ref-7).

On the patch from section 04, take zero-mean Gaussian models with made-up scales 200, 5, 30 and 3 for the four coefficients. The rate is $$-\log_2$$ of the probability the model gives to the quantizer bin that holds each value. For five step sizes:

| step | rate $$R$$ in bits | distortion $$D$$ (squared error) |
|---:|---:|---:|
| 2 | 20.3 | 1 |
| 4 | 16.4 | 3 |
| 8 | 13.8 | 19 |
| 16 | 10.0 | 83 |
| 32 | 6.7 | 275 |

With $$\lambda = 1$$ the lowest $$\mathcal{L}$$ is at step 4 ($$\mathcal{L} = 19.4$$). With $$\lambda = 0.1$$ it is at step 8 (15.7). With $$\lambda = 0.01$$ it is at step 32 (9.4). A smaller weight on distortion accepts a coarser step.

### Rounding has no gradient

The derivative of rounding is zero almost everywhere, so gradient descent learns nothing through it [\[6, p. 4\]](#ref-6). During training, rounding is replaced by additive noise [\[6, p. 4\]](#ref-6):

$$
\tilde{y} = y + u, \qquad u \sim U(-0.5, 0.5)
$$

The noise has the width of one quantizer bin, and it approximates the quantization error in its mean and variance [\[6, p. 5\]](#ref-6). I checked the variance on 200,000 made-up values drawn from $$\mathcal{N}(0, 5^2)$$. The mean squared error of rounding was 0.0833. That of the noise was 0.0833. The exact value for both is $$1/12 = 0.0833$$. At test time the codec rounds for real.

### Relation to a VAE

With a Gaussian likelihood of variance $$1/(2\lambda)$$ and the unit-width uniform noise as the encoder's distribution, this loss becomes a variational autoencoder objective [\[6, pp. 5 to 6\]](#ref-6). Minimizing the KL divergence between that encoder distribution and the true posterior is the same as minimizing the rate-distortion loss. The uniform noise has constant entropy, so that term drops out. What remains is the squared error, weighted by $$\lambda$$, and the cross-entropy, which is the rate [\[7, p. 4\]](#ref-7).

## 06. Where do the probabilities come from?

Section 02 showed that the bits depend on $$p(\hat{y})$$. The first model used a fully factorized prior: the latent elements are modelled as independent, with distributions that stay fixed after training [\[6, p. 5\]](#ref-6). That ignores a visible pattern. Non-zero latents cluster around edges and textured regions [\[7, p. 4\]](#ref-7).

### The scale hyperprior

Ballé et al. add a second, small network [\[7, p. 5\]](#ref-7). It computes $$z = h_a(y)$$ from the latents. $$z$$ is quantized and sent as side information. The decoder turns $$\hat{z}$$ into a scale for every latent, $$\sigma = h_s(\hat{z})$$, and each latent is modelled as a zero-mean Gaussian with its own standard deviation:

$$
p(\hat{y}_i \mid \hat{z}) = \mathcal{N}(0, \sigma_i^2) \ast U(-\tfrac{1}{2}, \tfrac{1}{2})\ \text{evaluated at } \hat{y}_i
$$

The $$\ast U$$ part convolves the Gaussian with the unit-width uniform, which makes the density match the noise used in training [\[7, p. 5\]](#ref-7). The loss gets one more term, the bits for $$\hat{z}$$, so the network learns how much side information is worth sending [\[7, p. 5\]](#ref-7).

Why a scale is worth sending. With made-up scales and unit-width bins, the cost of one quantized value is:

| scale $$\sigma$$ | bits for the index 5 | bits for the index 0 |
|---:|---:|---:|
| 1 | 18.18 | 1.38 |
| 2 | 6.76 | 2.34 |
| 5 | 4.37 | 3.65 |
| 10 | 4.83 | 4.65 |

Now two made-up patches of 8 values. A flat patch has all indices 0. An edge patch has the indices 5, −4, 6, 5, −5, 4, 6 and −5. With a scale of 0.5 the flat patch costs 4.4 bits and the edge patch 514.9. With a scale of 5 the flat patch costs 29.2 bits and the edge patch 35.1. A scale that fits each region is worth a lot. One that is too small is ruinous.

### Context from decoded latents

Minnen et al. add a second source of information. Each latent is predicted from the latents already decoded, $$p(\hat{y}_i \mid \hat{y}_{<i})$$, using a 5x5 masked convolution, together with the hyperprior [\[8, p. 4\]](#ref-8). The network predicts a mean and a scale for each latent. The authors note that autoregressive models carry a significant computational cost [\[8, p. 1\]](#ref-8).

### What it gave

Minnen et al. report the average rate saving of each codec against JPEG (4:2:0) at equal PSNR, on the 24 Kodak images, over a PSNR range of 27.1 to 39.9 dB [\[8, p. 15\]](#ref-8):

| codec | fewer bits than JPEG |
|---|---:|
| WebP | 32.06% |
| JPEG 2000 (OpenJPEG) | 38.02% |
| scale hyperprior [\[7\]](#ref-7) | 52.52% |
| BPG (4:4:4) | 56.19% |
| hyperprior with autoregressive context | 59.84% |

_Source: Figure 11 of the paper [\[8, p. 15\]](#ref-8). Against BPG (4:4:4) the combined model saves 8.41% [\[8, p. 15\]](#ref-8)._

The hyperprior alone, trained for squared error, came close to BPG and was better at higher bit rates [\[7, p. 7\]](#ref-7).

## 07. Is a language model a compressor?

Section 02 applies to any model that gives probabilities. Feed a model's probability for each next symbol to an arithmetic coder and the code length is about $$-\log_2$$ of the probability of the whole sequence. The expected length is the cross-entropy, and it is the same quantity language models are trained to minimize [\[2, p. 4\]](#ref-2).

A made-up example. After "the cat sat on the", a model gives "mat" 0.4, "floor" 0.2, "bed" 0.1, and 0.01 to each of 30 other words. The costs are 1.32, 2.32, 3.32 and 6.64 bits. Over three tokens, a model that gave the actual tokens 0.4, 0.9 and 0.7 would pay 1.99 bits in total. One that gave 0.05, 0.1 and 0.1 would pay 10.97.

Delétang et al. used this to test large models as compressors [\[2, p. 6\]](#ref-2). Chinchilla 70B was trained on text, and here it compresses 1 GB each of text (enwik9), ImageNet patches and LibriSpeech audio. Rates are compressed size divided by raw size, so lower is better:

| compressor | enwik9 | ImageNet patches | LibriSpeech |
|---|---:|---:|---:|
| Chinchilla 70B, raw | 8.3% | 48.0% | 21.0% |
| Chinchilla 70B, adjusted for model size | 14,008.3% | 14,048.0% | 14,021.0% |
| LZMA2 | 23.0% | 57.9% | 29.9% |
| gzip | 32.3% | 70.7% | 36.4% |
| PNG | 42.9% | 58.5% | 32.2% |
| FLAC | 89.5% | 61.9% | 30.9% |

_Source: Table 1 of the paper [\[2, p. 6\]](#ref-2). Chinchilla works on chunks of 2,048 bytes. The other rows are the whole file at once. The paper's abstract gives 43.4% for ImageNet and 16.4% for LibriSpeech, lower than its own table. I use the table._

The raw row does not count the model. The adjusted row does, at 2 bytes per parameter [\[2, p. 5\]](#ref-2). That is 70 billion × 2 bytes = 140 GB against 1 GB of data, which adds 14,000 percentage points. The authors say a model this size reaches non-trivial adjusted rates only on datasets of terabytes or more [\[2, p. 6\]](#ref-2). Within the raw column, a better model does give fewer bits: enwik9 goes from 11.3% for Chinchilla 1B to 10.2% for 7B to 8.3% for 70B [\[2, p. 6\]](#ref-2).

Li et al. report a similar scheme, LMCompress. Their abstract says it doubles the lossless compression ratios of JPEG-XL on images, FLAC on audio and H.264 on video, and quadruples the ratio of bz2 on text [\[9\]](#ref-9). I have read only the abstract. It gives no running times.

## 08. Try it

No libraries are needed. This recomputes the entropy of section 02, the Gaussian rate of section 03 and the noise check of section 05:

```python
import math, random

p = [0.5, 0.25, 0.125, 0.125]
print(-sum(x * math.log2(x) for x in p))           # entropy: 1.75 bits per symbol

sigma2, D = 4, 1
print(0.5 * math.log2(sigma2 / D))                  # Gaussian R(D): 1.0 bit per sample

random.seed(7)
y = [random.gauss(0, 5) for _ in range(100_000)]
print(sum((round(v) - v) ** 2 for v in y) / len(y))                # rounding error, close to 1/12
print(sum(random.uniform(-0.5, 0.5) ** 2 for _ in y) / len(y))     # uniform noise, close to 1/12
```

The output I got:

```text
1.75
1.0
0.08317860315967486
0.0836296854947403
```

## Sources

<span id="ref-1"></span>\[1\] Shannon, C. E. (1948). _A mathematical theory of communication_. Bell System Technical Journal, 27, 379 to 423 and 623 to 656. Page numbers refer to the reprint with corrections. [https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)

<span id="ref-2"></span>\[2\] Delétang, G., Ruoss, A., Duquenne, P.-A., Catt, E., Genewein, T., Mattern, C., Grau-Moya, J., Wenliang, L. K., Aitchison, M., Orseau, L., Hutter, M., & Veness, J. (2024). _Language modeling is compression_. ICLR 2024. arXiv:2309.10668. [https://arxiv.org/abs/2309.10668](https://arxiv.org/abs/2309.10668)

<span id="ref-3"></span>\[3\] Huffman, D. A. (1952). _A method for the construction of minimum-redundancy codes_. Proceedings of the IRE, 40(9), 1098 to 1101. [https://ieeexplore.ieee.org/document/4051119](https://ieeexplore.ieee.org/document/4051119)

<span id="ref-4"></span>\[4\] Wikipedia. _Rate-distortion theory_, section on the Gaussian source. It cites Cover, T. M., & Thomas, J. A., _Elements of Information Theory_, 2nd ed., Wiley, chapter 10. Read 28 November 2026. [https://en.wikipedia.org/wiki/Rate%E2%80%93distortion_theory](https://en.wikipedia.org/wiki/Rate%E2%80%93distortion_theory)

<span id="ref-5"></span>\[5\] EE274: Data Compression course notes, Stanford University. _Transform coding theory_ (section 2.3 of the lossy compression chapter). Read 28 November 2026. [https://stanforddatacompressionclass.github.io/notes/lossy/transform_coding_theory.html](https://stanforddatacompressionclass.github.io/notes/lossy/transform_coding_theory.html)

<span id="ref-6"></span>\[6\] Ballé, J., Laparra, V., & Simoncelli, E. P. (2017). _End-to-end optimized image compression_. ICLR 2017. arXiv:1611.01704. [https://arxiv.org/abs/1611.01704](https://arxiv.org/abs/1611.01704)

<span id="ref-7"></span>\[7\] Ballé, J., Minnen, D., Singh, S., Hwang, S. J., & Johnston, N. (2018). _Variational image compression with a scale hyperprior_. ICLR 2018. arXiv:1802.01436. [https://arxiv.org/abs/1802.01436](https://arxiv.org/abs/1802.01436)

<span id="ref-8"></span>\[8\] Minnen, D., Ballé, J., & Toderici, G. (2018). _Joint autoregressive and hierarchical priors for learned image compression_. NeurIPS 2018. arXiv:1809.02736. [https://arxiv.org/abs/1809.02736](https://arxiv.org/abs/1809.02736)

<span id="ref-9"></span>\[9\] Li, Z., Huang, C., Wang, X., Hu, H., Wyeth, C., Bu, D., Yu, Q., Gao, W., Liu, X., & Li, M. (2025). _Lossless data compression by large models_. Nature Machine Intelligence. arXiv:2407.07723. [https://arxiv.org/abs/2407.07723](https://arxiv.org/abs/2407.07723)
