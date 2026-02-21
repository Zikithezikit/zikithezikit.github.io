---
title: "Using AI for Data Compression: A Theoretical Perspective"
author: yoav
description: Explore the theoretical foundations of AI-powered data compression - from rate-distortion theory to the deep connection between understanding and compression.
date: 2026-02-17 12:00:00 +0200
categories: [AI, Technology, Data Science]
tags: [AI, machine learning, data compression, neural compression, information theory, entropy]
pin: false
math: true
mermaid: true
image:
    path: /assets/images/ai-data-compression.jpg
    alt: AI-powered data compression neural network visualization
summary: Discover the theoretical foundations behind AI transforming data compression - the elegant connection between understanding data and compressing it.
---

## Introduction

Every time you stream a video, load a webpage, or send a message, data compression makes it possible. Without compression, a single minute of high-definition video would require gigabytes of storage, which is impractical for any network or device.

Think of compression like taking detailed notes versus summarizing. The full video is like writing down every single frame exactly as it appears. A summary is like writing "this scene shows a car driving through a city at sunset" - much shorter, but you lose some details. Compression algorithms do this automatically, finding the shortest way to represent the original data while keeping what matters most.

For decades, we relied on carefully engineered algorithms like JPEG for images, MP3 for audio, and H.264 for video. These exploit statistical patterns: neighboring pixels share similar colors, certain audio frequencies are more important to human perception than others. JPEG, for example, notices that nearby pixels in most photos are almost the same color, so it only stores the color once and marks nearby pixels to copy it. This is like summarizing "the sky is blue" instead of writing "the sky is blue, the sky is blue, the sky is blue..." for every pixel.

But there is a fundamental limitation. These algorithms treat data as raw symbols without understanding what they mean. They see pixels, not pictures. They do not know that a photo contains a cat, a face, or a sunset. They only know that pixel 100 is similar to pixel 101.

Machine learning offers something different. Neural networks learn the underlying structure of data, including its patterns, constraints, and semantics. This learned understanding enables compression beyond what manual algorithms achieve. It is the difference between a human summarizing a movie (who understands the plot, characters, and emotions) versus a computer just noticing that certain pixel patterns repeat.

The central thesis is this. Compression and understanding are the same phenomenon. Just as a language model that predicts well has understood language, a model that understands data can compress it more efficiently.

---

## Information Theory Foundations

### Lossless vs. Lossy Compression

At its core, compression represents information using fewer bits. Think of it like packing a suitcase. You can either pack everything perfectly (lossless) or decide what you really need and leave some things behind (lossy). We distinguish two types.

> **Lossless compression**: The original data can be perfectly reconstructed. Used for text, executables, and any data where every bit matters. This is like making a perfect copy of a document - no information is lost.

> **Lossy compression**: Some information is deliberately discarded to achieve smaller sizes. Used for images, audio, and video where human perception fills in the gaps. This is like summarizing a book into a short review - you lose some details but keep the main points.

### The Rate-Distortion Function

Claude Shannon's landmark 1948 paper, "A Mathematical Theory of Communication,"[^shannon] established the fundamental limits: what is the minimum number of bits needed to represent data at a given quality level? 

Think of this like a speed limit on a highway. Shannon discovered the mathematical speed limit for compression - you cannot go faster no matter how good your car (algorithm) is. His rate-distortion function tells you the minimum speed (bits) needed to reach a certain destination quality.

The **rate-distortion function** R(D) provides the answer. It tells us the minimum average bits per sample required to represent a source X with expected distortion no greater than D:

$$R(D) = \min_{p(\hat{x}\mid x): \mathbb{E}[d(X, \hat{X})] \leq D} I(X; \hat{X})$$

$$= \min_{p(\hat{x}\mid x): \mathbb{E}[d(X, \hat{X})] \leq D} \sum_{x,\hat{x}} p(x) p(\hat{x}\mid x) \log_2 \frac{p(\hat{x}\mid x)}{p(\hat{x})}$$

Breaking this down:

- $\min_{p(\hat{x}\mid x)}$ means "find the best encoding strategy"
- $\mathbb{E}[d(X, \hat{X})] \leq D$ means "while keeping distortion below D"
- $I(X; \hat{X})$ is the mutual information (bits needed)

Where:
- $I(X; \hat{X})$ is **mutual information**, which is the amount of information shared between the original $X$ and reconstructed $\hat{X}$. Think of it as how much knowledge about the original is preserved.
- $d(X, \hat{X})$ is the **distortion function**, which is a measure of how different the reconstructed data is from the original. For images, this is often mean-squared error (MSE), which averages the squared differences between each pixel value. Lower MSE means less distortion and higher quality.
- The minimization finds the best encoding strategy $p(\hat{x}\mid x)$ achieving the desired distortion level

This function represents the theoretical speed limit. No algorithm can beat this bound for a given distortion level. It is like knowing the absolute minimum amount of ink needed to write a summary - you might get close, but you cannot use less ink than this theoretical minimum.

### The Gaussian Source

For important special cases, we have elegant closed-form solutions. Consider a memoryless Gaussian source, where each data point is drawn from a normal distribution with variance $\sigma^2$. A Gaussian (also called "normal") distribution is the classic bell curve - most values are near the average, with fewer and fewer values as you get further away.

Think of heights of adult humans. Most people are around average height (say 5'7"), very few are very short (4') or very tall (6'9"). The "variance" tells us how spread out the heights are. A low variance means everyone is almost the same height. A high variance means there is a big range of heights.

The formula:

$$R(D) = \begin{cases} \frac{1}{2} \log_2\left(\frac{\sigma^2}{D}\right) & D < \sigma^2 \\ 0 & D \geq \sigma^2 \end{cases}$$

This says: if you allow some distortion D that is smaller than the variance, you need half of log2(variance/D) bits. If you allow distortion larger than the variance, you need zero bits - just output zeros.

For example, if our source has variance $\sigma^2 = 4$ and we allow distortion $D = 1$, the minimum rate is:

$$\frac{1}{2} \log_2\left(\frac{4}{1}\right) = \frac{1}{2} \cdot 2 = 1 \text{ bit per sample}$$

This means we can represent each data point with 1 bit on average while keeping the reconstruction error below 1. If we try to compress more aggressively with $D = 4$ (equal to the variance), we get $R(4) = 0$, meaning we can simply output zeros since the signal is too noisy to matter.

When distortion is low (high quality), we need approximately $\log_2(\sigma^2/D)$ bits per sample. When distortion exceeds variance, we can simply output zeros, because the signal is too noisy to matter.

The **reverse water-filling** algorithm generalizes this to multiple dimensions. Imagine pouring water (bits) into containers (dimensions) with different capacities (variances). We fill until the water level $\theta$ reaches equilibrium, allocating more bits to dimensions with higher signal variance.

### Entropy and the Lossless Limit

At zero distortion (lossless compression), the bound becomes **entropy** H(X). Entropy is a measure of randomness or surprise. Think of it like this: a coin that always lands heads has zero entropy (not random at all). A fair coin has maximum entropy for two outcomes.

$$H(X) = -\mathbb{E}[\log_2 p(X)]$$

The negative sign is there because log of a probability less than 1 gives a negative number, and we want entropy to be positive.

Entropy measures the fundamental uncertainty in the data. A source with low entropy (predictable) compresses well. Random data with high entropy is incompressible. It is like the difference between a book with repeated patterns (easy to summarize) versus random noise (impossible to compress).

For example, consider a data source that emits four symbols with probabilities: A (50%), B (25%), C (12.5%), D (12.5%). The entropy is:

$$H(X) = -(0.5 \log_2 0.5 + 0.25 \log_2 0.25 + 0.125 \log_2 0.125 + 0.125 \log_2 0.125)$$

$$= -(0.5 \cdot (-1) + 0.25 \cdot (-2) + 0.125 \cdot (-3) + 0.125 \cdot (-3))$$

$$= 1.75 \text{ bits per symbol}$$

Breaking this down:

- $0.5 \cdot \log_2 0.5 = 0.5 \cdot (-1) = -0.5$
- $0.25 \cdot \log_2 0.25 = 0.25 \cdot (-2) = -0.5$
- $0.125 \cdot \log_2 0.125 = 0.125 \cdot (-3) = -0.375$
- Summing: $-(0.5 + 0.5 + 0.375 + 0.375) = -1.75$

So: $H(X) = 1.75$ bits per symbol.

This means we need at least 1.75 bits per symbol to represent this source losslessly. A uniform distribution over four symbols would have entropy 2 bits (since each has probability 0.25), showing that predictability reduces the bits needed.

For those familiar with large language models, perplexity is 2 to the power of H(X), which is a measure of how surprised the model is by the data. Lower perplexity implies better prediction, which implies lower entropy, which implies better compressibility.

**Arithmetic coding** is the workhorse of lossless compression. It achieves compression within one bit of entropy by assigning shorter binary codes to more probable symbols.

For instance, with our four-symbol source above, we might assign: A (3 bits), B (4 bits), C (5 bits), D (5 bits). This differs from fixed-length codes (which would always use 2 bits) by using fewer bits for common symbols and more for rare ones.

Given a perfect probability model, it assigns "the" (common) a 3-bit code and "quixotic" (rare) a 15-bit code. The better your probability model, the better your compression.

---

## The Transform Coding Framework

### From Fixed to Learned Transforms

**Transform coding** is the process of converting data into a different representation that is easier to compress. It is like translating a book from English to a shorter language - the meaning stays the same but it takes less space to write. Traditional approaches use fixed mathematical transforms.

- JPEG uses the Discrete Cosine Transform (DCT), which converts spatial pixel data into frequency coefficients. This is like taking a photo and asking "how much red is there, how much blue, how much green" instead of "what color is each individual pixel."
- JPEG2000 uses wavelets, which is a multi-resolution decomposition. This is like looking at an image from different distances - up close you see details, far away you see the overall shape.

These transforms are hand-designed based on mathematical properties (DCT concentrates energy in few coefficients) and human perception (we are less sensitive to high-frequency detail). They work well but have a ceiling - they cannot learn anything new about your specific data.

**Learned transform coding** generalizes this framework. The encoder and decoder become neural networks, with all components jointly optimized end-to-end. Rather than using DCT, we learn a transform specifically tailored to the data distribution. This is like having a translator who has read millions of books in both languages and learned all the best ways to compress meaning - they do a better job than a generic rule-based translator.

### The Pipeline

The compression pipeline consists of four stages. Think of it like sending a package through the mail:

1. **Analysis transform** $y = g_a(x; \phi)$: The encoder network maps input to a **latent representation**, which is a compact, continuous vector that captures the essential information in the data. Think of this as the neural network's understanding of the input. This is like taking everything in a box, figuring out what really matters, and writing it down on a single sheet of paper.

2. **Quantization** $\hat{y} = Q(y)$: **Quantization** discretizes the continuous latent space by rounding real-valued numbers to a finite set. This is the main source of lossiness, similar to reducing image colors from 16 million (24-bit) to 256 (8-bit). This is like rounding your notes to the nearest whole number - you lose some precision but it still conveys the main idea.

3. **Entropy coding**: Uses a learned probability model to compress the quantized latents into bits. This is lossless, like zipping already-compressed data. This is like using a good shorthand - once you have your notes, you can write them in an even more compact form.

4. **Synthesis transform** $\hat{x} = g_s(\hat{y}; \theta)$: The decoder network reconstructs the original from quantized latents. This is like taking your shorthand notes and expanding them back into full sentences.

For example, suppose we have a tiny 2x2 grayscale image patch with pixel values [120, 125, 80, 85]. After the analysis transform (a simple averaging for illustration), we might get latents $y = [102.5, -4.5]$. The quantization step rounds these to integers: $\hat{y} = [103, -5]$. The entropy coder then represents [103, -5] as bits using a probability model. At decode time, the synthesis transform maps [103, -5] back to the reconstructed image.

The encoding flow:

$$
\underbrace{x}_{\text{Input}} 
\;\xrightarrow{\;g_a(\cdot)\;}\;
\underbrace{y}_{\text{Latent}}
\;\xrightarrow{\;Q(\cdot)\;}\;
\underbrace{\hat{y}}_{\text{Quantized}}
\;\xrightarrow{\;\text{Entropy coding}\;}\;
\underbrace{\text{bits}}_{\text{Compressed}}
$$

And decoding:

$$
\underbrace{\text{bits}}_{\text{Compressed}}
\;\xrightarrow{\;\text{Entropy decoding}\;}\;
\underbrace{\hat{y}}_{\text{Quantized}}
\;\xrightarrow{\;g_s(\cdot)\;}\;
\underbrace{\hat{x}}_{\text{Reconstructed}}
$$

### Rate-Distortion Optimization

Training minimizes a **Lagrangian**, which is a way to balance two competing objectives using a single scalar parameter:

$$\mathcal{L}(\phi, \theta) = \mathbb{E}_{x \sim p_{\text{data}}}\left[ -\log_2 p_\psi(\hat{y}) + \lambda \cdot d(x, \hat{x}) \right]$$

$$= \frac{1}{N} \sum_{i=1}^{N} \left[ -\log_2 p_\psi(\hat{y}_i) + \lambda \cdot (x_i - \hat{x}_i)^2 \right]$$

Breaking this down:

- $\mathbb{E}_{x \sim p_{\text{data}}}$ means "the expected value over training data"
- $-\log_2 p_\psi(\hat{y})$ is the **rate** (bits needed)
- $d(x, \hat{x})$ is the **distortion** (reconstruction error)
- $\lambda$ is the balance between them

Where:
- The first term $-\log_2 p_\psi(\hat{y})$ is the **rate**, which is the expected number of bits needed to represent the quantized latents according to our probability model $p_\psi$. This is the entropy of the quantized representation.
- The second term $d(x, \hat{x})$ is the **distortion**, which is the expected reconstruction error (for example, MSE between original and reconstructed).
- $\lambda$ is the **Lagrange multiplier**, which is a scalar that controls the tradeoff. Think of it as a compression dial. High lambda means prioritize quality (less distortion). Low lambda means prioritize compression (fewer bits).

For example, training with $\lambda = 0.1$ might produce a model that uses 0.2 bits per pixel with 2% MSE distortion, while $\lambda = 10$ might use 0.8 bits per pixel with only 0.5% MSE distortion. The lower $\lambda$ version compresses more but loses more detail. By varying $\lambda$ across different training runs, we trace the entire **rate-distortion curve**, which is the neural codec's approximation to Shannon's theoretical $R(D)$ function.

---

## The Variational Connection

### Variational Autoencoders as Compressors

The compression objective is mathematically identical to training a **Variational Autoencoder (VAE)**[^balle2017]. This connection transformed compression from engineering to optimization.

Think of a VAE like a sketch artist. When someone shows you a photo, you do not memorize every pixel - you create a mental sketch that captures the essential features (the person's face, the background, the lighting). Later, you can recreate a version of the photo from your sketch. The sketch is smaller than the photo (compressed), but contains enough information to recognize what was in the original.

A VAE consists of three components:

- A **prior** $p(z)$ is the assumed distribution over latent variables before seeing any data, typically a standard Gaussian $\mathcal{N}(0,1)$. This is the blank slate assumption about what the latent space should look like. It is like deciding that all sketches should use the same type of paper and pencils - standardization makes them easier to work with.
- A **likelihood** $p(x\mid z)$ is the probability of observing data $x$ given latent $z$. This is the decoder's job. It tells us how likely we are to reconstruct the original from a given latent representation. Given a sketch (latent), how good is the resulting photo?
- An **encoder** $q(z\mid x)$ is the approximate posterior, which is the network that maps input to latent space. It is called an approximate posterior because computing the exact posterior is intractable. It is the process of creating the sketch from the photo.

The **evidence lower bound (ELBO)**, which is the objective that VAEs maximize:

$$\text{ELBO} = \mathbb{E}_{q(z\mid x)}[\log p(x\mid z)] - D_{\text{KL}}(q(z\mid x) \Vert p(z))$$

$$= \mathbb{E}_{q(z\mid x)}[\log p(x\mid z)] - \mathbb{E}_{q(z\mid x)}\left[\log \frac{q(z\mid x)}{p(z)}\right]$$

Breaking this down:

- $\mathbb{E}_{q(z\mid x)}$ means "expected value over the encoder's distribution"
- $\log p(x\mid z)$ is reconstruction quality (higher = better)
- $D_{\text{KL}}$ is the KL divergence (penalty for straying from the prior)

Where:
- The first term $\mathbb{E}_{q(z\mid x)}[\log p(x\mid z)]$ is reconstruction quality, which is the expected log-likelihood of reconstructing the input from its latent representation. Higher means better reconstruction and less distortion.
- The second term $D_{\text{KL}}(q(z \mid x) \Vert p(z))$ is the **KL divergence**, which is a measure of how different the encoder's distribution is from the prior. This acts as a regularizer, pushing the latent space toward the simple prior distribution. Lower KL means more compact latent space and less rate in compression terms. This is like telling the artist "keep your sketches simple and consistent - do not get too creative or detailed."

For a simple 1D Gaussian case, if our encoder outputs $q(z) = \mathcal{N}(\mu=0.2, \sigma^2=0.5)$ and the prior is $p(z) = \mathcal{N}(0, 1)$, the KL divergence tells us how much information we lose by using this learned distribution instead of the standard Gaussian. This penalizes the encoder from producing latents that stray too far from what the entropy coder expects.

> **The connection**: Minimizing ELBO equals minimizing rate-distortion loss. The same mathematics describes both.

### Learned Latent Representations

The encoder discovers a latent space with desirable properties:

- **Redundant information is discarded** - this is compression.
- **Essential information is preserved** in compact form.
- **Distribution matches the prior** - enabling efficient entropy coding.

This is analogous to how neural networks learn efficient representations for downstream tasks.

---

## Entropy Modeling

### The Importance of Probability Models

**Entropy coding** (like arithmetic coding) can achieve compression near the entropy limit, but only with an accurate probability model. The more accurately we predict each symbol's probability, the fewer bits we need.

Think of it like predicting the weather. If you say "it will rain tomorrow" every single day, you will be right sometimes (rainy days) but wrong most of time (sunny days). Your prediction is not very useful. But if you study weather patterns and notice that July is always sunny in California, you can predict "it will be sunny" with high confidence - and that confident, accurate prediction is worth more.

The same applies to compression. If you predict "the" has 10% probability and it appears 10% of the time, you need about 3.3 bits. If your model is better and predicts "the" has 15% probability (closer to reality), you only need about 2.7 bits. Better predictions = fewer bits = better compression.

In large language models, this is the vocabulary probability distribution from the softmax output. When GPT predicts the next word, it outputs a probability for every word in its vocabulary. The more accurate these probabilities, the better the compression when you encode the actual word that appears.

### The Scale Hyperprior

Ball et al. (2018)[^balle2018] introduced the **scale hyperprior**, which is a second network predicting the variance (scale) of each latent element:

$$\hat{y}_i \sim \mathcal{N}(\mu_i, \sigma_i^2)$$

where $\sigma_i = h(y)_i$ is predicted by the hypernetwork (the hyper refers to it being a network about the main network). Regions with complex textures (high variance) receive more bits. Flat regions receive fewer.

Think of this like a photographer adjusting exposure. In bright, flat areas (like a clear sky), not much information is needed - you can just say "it's all blue." In areas with lots of detail (like a busy street), you need more words to describe everything. The scale hyperprior automatically allocates more bits to complex areas and fewer bits to simple areas.

This is analogous to attention. Different parts of the input require different bits budgets based on their complexity.

### Autoregressive Context

Minnen et al. (2018)[^minnen2018] added **autoregressive modeling**, which predicts each latent conditioned on previously decoded ones:

$$p(\hat{y}_i \mid \hat{y}_{<i})$$

This means: "what is the probability of this piece, given all the pieces we have already decoded?"

This is precisely how autoregressive language models operate. They predict each token based on previous tokens. After decoding "the", predicting "cat" becomes easier. It is like reading a sentence word by word - once you have read "the cat sat on the", you have a good idea what might come next (like "mat" or "floor").

> **Key insight**: Context reduces uncertainty, which reduces entropy, which reduces bits. Every dependency modeled is bits saved. The more context you have, the better you can predict what comes next, and the fewer bits you need to encode it.

Combining hyperpriors with autoregressive context achieves 59.8% bit savings over JPEG, 35% over JPEG2000, and 8.4% over BPG.

---

## The Quantization Bridge

### Discrete Symbols from Continuous Networks

Compression requires discrete symbols, but neural networks compute with continuous real numbers. **Quantization** bridges this gap. It is like rounding your GPS coordinates from "37.7749 degrees north, 122.4194 degrees west" to "38 degrees north, 122 degrees west" - you lose some precision but still get close enough to find your destination.

$$y_{\text{quantized}} = \text{round}(y)$$

This is conceptually similar to quantization in LLMs (INT8, INT4 weights), which reduces precision while preserving what matters for the task. When ChatGPT runs on your phone, it does not use full 32-bit numbers for everything - it rounds to 8-bit or 4-bit numbers to fit in memory.

**Uniform scalar quantization** divides the range into K equally-spaced bins, representing each by log 2 of K bits. For example, 256 levels (8 bits) can represent values from 0 to 255. This is like using a measuring cup with 256 markings - each measurement gets rounded to the nearest marking.

For example, given latent values [0.7, 1.2, 3.9, 4.5], uniform quantization to integers yields [1, 1, 4, 5]. The difference (0.3, 0.2, -0.1, -0.5) is the information lost. A smarter codec might learn to use non-uniform bins that allocate more precision where values cluster densely. This is like having a thermometer with more markings around room temperature (where we care most) and fewer markings at extreme temperatures.

However, uniform quantization is suboptimal when values are not uniformly distributed. Neural codecs learn better discretizations during training.

### Training vs. Inference

During training, quantization is nondifferentiable (the gradient is zero almost everywhere). This is a problem because neural networks learn by calculating gradients (they need to know which direction to improve). To maintain gradients, we approximate quantization with **additive uniform noise**:

$$y_{\text{noisy}} = y + u, \quad u \sim U(-0.5, 0.5)$$

This adds random noise between -0.5 and 0.5 to the values during training. It makes quantization act like a smooth function so gradients can flow through. Think of it like practicing with a slightly fuzzy target - it helps you learn even though the real target is sharp.

At inference time (when we actually use the model), actual quantization is applied. This is like taking the real test after practicing with fuzzy targets.

---

## The Understanding-Compression Duality

### Predictive Models as Compressors

Consider any model predicting data. Given past symbols, what comes next? The better it predicts, the lower the surprise (measured by $\log p(x)$), meaning fewer bits to encode.

Think of it like guessing the next word in a sentence. If someone says "the sky is ___", you can easily guess "blue" because it is the most common answer. But if someone says "the quantum entang__", you might not know the next letter - it could be many things.

For example, consider the sequence "the cat sat on the ___". A language model might assign 40% probability to "mat", 20% to "floor", 10% to "bed", and 30% distributed across other words. Encoding "mat" requires $-\log_2(0.4) \approx 1.3$ bits, while "floor" takes $-\log_2(0.2) \approx 2.3$ bits. The better our model predicts what comes next, the fewer bits we need to transmit.

The connection is: surprise equals $-\log_2 p(x)$, which equals bits. Lower surprise means fewer bits. It is like the difference between a predictable friend (easy to summarize) versus a surprising friend (hard to predict).

This holds for any sequence: text, images, audio, video. The model does not care what it is predicting. Only prediction accuracy matters.

### Large Language Models as Universal Compressors

Li et al. (2025)[^li2025] demonstrated this empirically. An LLM trained on diverse data compresses any sequence, including images, audio, video, and text, better than specialized codecs.

Think about what an LLM knows after training on the entire internet. It has seen billions of images, watched countless videos, read millions of books, and listened to lots of audio. It has learned patterns about how the world works - that faces have two eyes, that sentences flow grammatically, that music has rhythm.

**LMCompress achieves:**
- **2x better compression** than JPEG-XL for images
- **2x better compression** than FLAC for audio  
- **2x better compression** than H.264 for video
- **One-third** the compression rates of zpaq for text

The key insight is that an LLM has already learned a model of the world. It understands images because it has seen images in training data. It understands audio because it has learned temporal patterns. Internal representations capture structure, and structure enables compression. It is like having read millions of books - you can summarize any new book much better than someone who has never read anything.

> **"Understanding is compression"** is not a metaphor. It is a mathematical identity. Low surprise implies low entropy, which implies compressibility.

### The Bits-Back Hypothesis

This suggests something profound. All learning is compression. By finding patterns in data, we build compressed models that can reconstruct. This is precisely what intelligence does. It builds compact models of environments.

The **bits-back hypothesis** formalizes this idea. An agent can transmit data by first generating it from its model, then telling the receiver only the parts where its model was wrong. Suppose the agent and receiver both have a language model. The agent generates the first half of a message, sees which tokens the model predicted correctly, and only transmits corrections for the rest. The receiver, using the same model, reconstructs the full message. This "bits back" from shared understanding is the compression gain.

---

## Theoretical Limits and Open Questions

### Distance from Theoretical Limits

Classical rate-distortion theory provides lower bounds, but computing true R(D) for complex distributions (like natural images) is intractable. We do not know how close neural codecs are to these limits.

It is like knowing the fastest possible time for a marathon (the theoretical limit) but not knowing how close current world records are to that limit. We know we cannot beat the theoretical minimum bits, but we are not sure if we are 1% away or 50% away.

Recent work[^theoretical2026] decomposes the gap into three components:

1. **Variance estimation** - accuracy of entropy model predictions for latent variances. Like how well a weather forecast predicts uncertainty.
2. **Quantization strategy** - optimal allocation of discrete levels. Like choosing the best number of colors for a painting.
3. **Context modeling** - dependencies captured by autoregressive structure. Like how much previous context helps predict what comes next.

### The Amortization Gap

Neural encoders use a single forward pass to map input to latents. However, the optimal encoding for a specific sample may differ from the network is output.

Think of this like a factory vs. a custom craftsman. A neural network is like a factory - it makes thousands of items quickly using the same process. But for one special item, a custom craftsman could do a better job by spending extra time perfecting it. The amortization gap is the difference between the factory's quick product and what the craftsman could achieve.

The difference between what the network gives and what is theoretically optimal is the **amortization gap**. It is named because the network amortizes computation over many samples, but this efficiency comes at the cost of per-sample optimality. Solving this requires per-sample optimization at inference time, which is computationally expensive but theoretically significant.

### Goal-Oriented Compression

For any compressible distribution, there is a rate-distortion curve. But the curve depends on the **distortion metric**. MSE may not capture what matters for human perception.

This is like grading an essay. An algorithm might use simple metrics like word count or sentence length (like MSE for images), but these do not capture what humans actually care about - the quality of writing and ideas. 

**Goal-oriented compression** optimizes for downstream tasks (classification accuracy, detection rate) rather than reconstruction quality. Instead of minimizing MSE, we minimize task loss, which is the error rate of a classifier run on compressed data. If you are compressing images for a self-driving car, you do not care if the image looks good to humans - you care if the car can still see pedestrians and stop signs.

---

## Conclusion

AI-based compression represents a fundamental reconception, from symbol manipulation to model-based inference.

The mathematical framework is elegant. Rate-distortion theory, variational inference, and entropy coding combine into end-to-end optimizable systems. The theoretical insights are profound. Understanding and compression are the same phenomenon viewed through different lenses.

What makes this compelling is not merely the empirical results, though 2x improvements over classical methods are significant. It is the unification. The same mathematics explaining neural networks explains compression. The same principles making machines intelligent make them efficient. When a model learns to understand images, it is simultaneously learning to compress them. When a language model learns to predict the next word, it is learning to compress text. These are not separate achievements - they are the same achievement.

We lack complete theoretical understanding. The bounds are fuzzy, the gaps are real, the challenges remain. But the trajectory is clear. As our models of data improve, so will our ability to compress. The future of compression is not better engineering - it is better understanding.

---

## References

[^shannon]: Shannon, C.E. "A Mathematical Theory of Communication." *Bell System Technical Journal*, 1948.

[^balle2017]: Ballé, J., Laparra, V., & Simoncelli, E.P. "End-to-end Optimized Image Compression." *ICLR 2017*.

[^balle2018]: Ballé, J., Minnen, D., Singh, S., Hwang, S.J., & Johnston, N. "Variational image compression with a scale hyperprior." *ICLR 2018*.

[^minnen2018]: Minnen, D., Ballé, J., & Toderici, G. "Joint Autoregressive and Hierarchical Priors for Learned Image Compression." *NeurIPS 2018*.

[^li2025]: Li, Z., Huang, C., Wang, X., et al. "Lossless data compression by large models." *Nature Machine Intelligence*, 2025.

[^theoretical2026]: "A Theoretical Framework for Rate-Distortion Limits in Learned Image Compression." *arXiv:2601.09254*, 2026.

---

**See Also:**

- Chen et al. "Information Compression in the AI Era: Recent Advances and Future Challenges" - arXiv:2406.10036
- "Neural Climate Data Compression" - DeepMind, 2024
- Habibian et al. "Video Compression With Rate-Distortion Autoencoders" - ICCV 2019

---
