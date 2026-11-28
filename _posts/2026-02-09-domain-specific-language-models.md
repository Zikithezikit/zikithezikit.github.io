---
title: "Domain-Specific Language Models: Four Ways to Build One"
author: yoav
description: "A domain-specific language model is a general model adapted to one field, by training from scratch, continuing pretraining, fine-tuning or retrieval. What each costs, with numbers from BloombergGPT, Code Llama and Med-PaLM."
date: 2026-02-09 12:00:00 +0200
lang: en
categories: [AI, Machine Learning, Enterprise]
tags: [domain-specific-models, language-models, fine-tuning, continued-pretraining, retrieval-augmented-generation, llm]
pin: false
math: false
mermaid: false
image:
   path: /assets/images/domain-specific-ai.jpg
   alt: Domain-Specific Language Model Architecture
---

## 01. The question

A general language model is trained on text from everywhere. A bank, a hospital or a software team has one field and its own documents. The question is how to get a model that works well in that field.

The answer has a name: a domain-specific language model (DSLM). It is a language model whose training or inputs were chosen to fit one field. Published examples:

- BloombergGPT, for finance. 50 billion parameters, trained on financial and general text [\[1\]](#ref-1).
- Med-PaLM, for medical questions. Built by adapting an existing 540-billion-parameter model [\[2\]](#ref-2).
- Code Llama, for programming. Built from Llama 2 [\[3\]](#ref-3).

There is no single recipe. The three models above were built in three different ways. This post lists the ways, gives the numbers the papers report for each, and ends with a short decision example.

> Every number comes from a cited paper, or is marked "made up for the example". Scores are the authors' own and are not comparable across papers.
{: .prompt-info }

## 02. What are the four ways?

Each way changes a different thing.

- **Pretraining from scratch.** Start from random weights and train on a corpus that includes a large amount of domain text. BloombergGPT mixed financial and general text [\[1, p. 4\]](#ref-1).
- **Continued pretraining.** Start from a trained general model and keep training it on domain text, with the same next-word objective. Gururangan et al. call this domain-adaptive pretraining and tested it on four domains [\[4\]](#ref-4). Code Llama does this with code [\[3, p. 3\]](#ref-3).
- **Fine-tuning.** Start from a trained model and train it on a small set of examples of the task. Med-PaLM did this with a method called instruction prompt tuning [\[2\]](#ref-2). Low-rank adaptation (LoRA) freezes the original weights and trains small added matrices, so only a fraction of the parameters change [\[5\]](#ref-5).
- **Retrieval.** Do not change the model. At question time, fetch passages from a document store and give them to the model. Lewis et al. call the weights the parametric memory and the document store the non-parametric memory [\[6\]](#ref-6).

The first three change the weights. The fourth changes what the model sees.

## 03. What does training from scratch cost?

BloombergGPT is the clearest published case. The abstract gives two corpus sizes [\[1, p. 1\]](#ref-1):

- 363 billion tokens of financial data, built from Bloomberg's archives.
- 345 billion tokens from general datasets.

Those add up to 708 billion. The training text counts 709 billion tokens available, which I take to be rounding. The paper reports the financial part as 51.27% of training [\[1, p. 7\]](#ref-1).

The model did not read all of it. Training stopped after 139,200 steps, about 53 days, at 569 billion tokens out of the 709 billion available [\[1, p. 16\]](#ref-1). That is 569 / 709 = 0.80 of one pass over the data, which matches the paper's "about 80% of one epoch".

The paper's claim is that the mix gives a model that outperforms existing models on financial tasks, and is on par or better on general benchmarks [\[1, p. 4\]](#ref-1). The authors also say they built what they call the largest domain-specific dataset yet [\[1, p. 4\]](#ref-1).

Two things follow from the numbers. The corpus is hundreds of billions of tokens. And the paper says Bloomberg's analysts had collected financial documents over forty years [\[1, p. 4\]](#ref-1). Most teams do not have a corpus like that.

## 04. What does continued pretraining cost?

Code Llama starts from Llama 2 weights and trains on a code-heavy dataset. The 7B, 13B and 34B models saw 500 billion tokens. The 70B model saw 1 trillion [\[3, p. 3\]](#ref-3).

Llama 2 was trained on 2 trillion tokens [\[3, p. 7\]](#ref-3). So the extra training for the smaller models is 500 / 2,000 = 25% of the original token count.

The 500 billion tokens are mostly code, with some natural language around it [\[3, p. 5\]](#ref-3):

| Part of the dataset | Share |
|---|---:|
| Code | 85% |
| Natural language related to code | 8% |
| Natural language | 7% |

_Dataset mix for Code Llama at 500 billion tokens [\[3, p. 5\]](#ref-3)._

The authors report two results from this. Starting from Llama 2 beats the same architecture trained on code only, for the same budget [\[3, p. 1\]](#ref-3). And Llama 2 70B is roughly equivalent to Code Llama 7B on Python coding benchmarks [\[3, p. 7\]](#ref-3). The 70B model is 10 times the size of the 7B one.

## 05. What does fine-tuning change?

Fine-tuning trains on a set of task examples, not on a full corpus.

Med-PaLM is the example. The authors tested the 540-billion-parameter PaLM and its instruction-tuned version Flan-PaLM on a set of medical question benchmarks [\[2\]](#ref-2):

- Flan-PaLM scored 67.6% on MedQA, which uses US medical licensing exam questions. The authors say that beats the previous best by over 17%.
- Instruction prompt tuning of Flan-PaLM produced Med-PaLM.
- Human raters scored answers on factuality, precision, possible harm and bias. They found key gaps in Flan-PaLM's answers. The authors say Med-PaLM performs encouragingly but remains inferior to clinicians.

So a tuned model can score well on exam questions and still fall short of a clinician. The same paper reports that comprehension, recall and reasoning improved with model size and with tuning.

LoRA lowers the price of fine-tuning. For GPT-3 175B, the LoRA authors report 10,000 times fewer trainable parameters and 3 times less GPU memory than full fine-tuning with Adam [\[5\]](#ref-5).

## 06. What does retrieval change?

Retrieval leaves the weights alone. The document store can be read and updated without retraining [\[6\]](#ref-6). That fits knowledge that changes, such as prices, policies and manuals.

In the original paper, the store is a dense vector index of Wikipedia and the model is a pretrained sequence-to-sequence model. On three open-domain question answering tasks it beat parametric-only models. Its generated text was more specific, more diverse and more factual than a parametric-only baseline [\[6\]](#ref-6).

Retrieval has limits. They follow from how it works. If the right passage is not fetched, the model has nothing to use. And a passage can only give facts. It does not teach the model the field's vocabulary or its way of reasoning. This is my reasoning, not a result from the paper.

## 07. How do the four compare?

| | Changes the weights | What you need | Updating knowledge | Reported anchor |
|---|---|---|---|---|
| From scratch | Yes, all | A corpus of hundreds of billions of tokens | Retrain | 569B tokens, about 53 days [\[1, p. 16\]](#ref-1) |
| Continued pretraining | Yes, all | Billions of domain tokens | Continue training | 500B tokens on top of 2T [\[3, p. 3\]](#ref-3) |
| Fine-tuning | Yes, or a small part with LoRA | Labelled examples of the task | Tune again | 3 times less memory with LoRA [\[5\]](#ref-5) |
| Retrieval | No | A searchable document store | Edit the store | No retraining [\[6\]](#ref-6) |

_The first three columns are my summary of the papers. The last column quotes them. The "what you need" column is my reading, not a threshold any paper states._

The methods can be combined. BloombergGPT's paper contrasts its approach with models trained only on domain data and with models that adapt a very large general model, and cites Med-PaLM as one of the second kind [\[1, p. 4\]](#ref-1). Retrieval can sit on top of any of them.

## 08. Which one to pick?

A decision example. Everything in it is made up for the example.

A support team has 5,000 runbook pages. Each page averages 2,000 tokens. The pages change every week. The team wants answers that point to the page they came from.

The corpus is 5,000 × 2,000 = 10,000,000 tokens. BloombergGPT's financial data alone is 363 billion tokens [\[1, p. 1\]](#ref-1). That is 363,000,000,000 / 10,000,000 = 36,300 times more. Training from scratch is out, and so is continued pretraining on a corpus this small. I assume 10 million tokens is too little for it, based on the sizes in sections 03 and 04. No paper gives a minimum.

The steps:

1. The answers live in pages that change weekly, and the team wants citations. Start with retrieval. Editing a page updates the system, with no retraining [\[6\]](#ref-6).
2. Test on real questions with the right page already in the prompt. If the answers are right, stop here.
3. If they are wrong in a systematic way, such as a wrong output format or a misused term, collect examples of good answers and fine-tune, with LoRA if memory is the limit [\[5\]](#ref-5).
4. Whatever the choice, have a person who knows the field review a sample of answers. Flan-PaLM scored well on exam questions and still showed gaps under human review [\[2\]](#ref-2).

> The sizes in this example are made up. Replace them with your own page count and token count before comparing.
{: .prompt-warning }

## Sources

<span id="ref-1"></span>\[1\] Wu, S., Irsoy, O., Lu, S., Dabravolski, V., Dredze, M., Gehrmann, S., Kambadur, P., Rosenberg, D., & Mann, G. (2023). _BloombergGPT: A large language model for finance_. arXiv:2303.17564. [https://arxiv.org/abs/2303.17564](https://arxiv.org/abs/2303.17564)

<span id="ref-2"></span>\[2\] Singhal, K., Azizi, S., et al. (2022). _Large language models encode clinical knowledge_. arXiv:2212.13138. [https://arxiv.org/abs/2212.13138](https://arxiv.org/abs/2212.13138)

<span id="ref-3"></span>\[3\] Rozière, B., Gehring, J., Gloeckle, F., Sootla, S., et al. (2023). _Code Llama: Open foundation models for code_. arXiv:2308.12950. [https://arxiv.org/abs/2308.12950](https://arxiv.org/abs/2308.12950)

<span id="ref-4"></span>\[4\] Gururangan, S., Marasović, A., Swayamdipta, S., Lo, K., Beltagy, I., Downey, D., & Smith, N. A. (2020). _Don't stop pretraining: Adapt language models to domains and tasks_. ACL 2020. arXiv:2004.10964. [https://arxiv.org/abs/2004.10964](https://arxiv.org/abs/2004.10964)

<span id="ref-5"></span>\[5\] Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., & Chen, W. (2021). _LoRA: Low-rank adaptation of large language models_. arXiv:2106.09685. [https://arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)

<span id="ref-6"></span>\[6\] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). _Retrieval-augmented generation for knowledge-intensive NLP tasks_. NeurIPS 2020. arXiv:2005.11401. [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)
