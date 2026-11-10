---
title: "Israeli Taxing Wonders"
author: yoav
description: "A short guide to the Kohelet Policy Forum paper that measures how much tax each Israeli household pays and how many services and benefits it gets back. Charts, method, results in USD, and what the numbers do not say."
date: 2026-11-10 09:00:00 +0200
lang: en
categories: [economics, public-policy]
tags: [taxes, net-transfers, households, kohelet, israel, household-expenditure-survey, vat, inequality]
pin: false
math: false
mermaid: false
media_subpath: /assets/images/taxes-explainer-en/
image:
   path: cover.png
   alt: "Bar chart of taxes paid, services received and net transfer per household, by income decile, in USD"
---

## 01. What the paper is

"On Taxes and Wonders" (Hebrew title: "על המיסים ועל הנפלאות") is a paper by Ariel Karlinsky, Tom Sadeh, Eran Yogev and Michael Sarel ([Karlinsky et al., 2024](#ref-paper)). The research was done while all four worked at the Kohelet Policy Forum, a think tank in Jerusalem. The version I read was accepted on 24 June 2024 by the journal _HaRevaon LeKalkala_ (The Economic Quarterly).

It measures two things for Israeli households in 2018:

- How much tax each household really pays.
- How much it gets back, in cash benefits and in public services like schools and health care.

The paper is about 47 pages, with 34 charts and one big table. I read it chart by chart, plus the 85-page technical appendix ([Technical appendix, 2025](#ref-appendix)). Here is the short version.

All numbers come from the paper. When I calculated something myself, I say so. Charts marked "my chart" are my redraws of the paper's values, not the originals.

> Money in this post: the paper uses shekels (NIS). I convert to US dollars at 3.18 NIS per $, the current rate. The data is from 2018, so this mixes 2018 shekels with today's exchange rate and ignores inflation and purchasing power. Treat dollars as a rough feel for size. All figures are rounded.
{: .prompt-info }

## 02. The question

The paper asks who pays the state, who gets from it, and how big the gap is. Two things make this hard.

First, the one who sends the tax is not always the one who bears it. A shopper never meets the tax authority, but pays VAT inside every price.

Second, most of what the state gives is not cash. It is a school, a clinic, a bus subsidy. A benefit shows up in your bank account. A teacher's salary does not.

So the paper assigns each household a tax burden and a value of services received, then subtracts.

The paper's own example ([Karlinsky et al., 2024, p. 3](#ref-paper)): the Cohen family gets $790 a month from the state in cash. Another family gets no cash, but its kids go to a public school that costs the state the same $790 a month in teacher pay. For the treasury these are the same. For a payslip they look very different. The paper counts both.

## 03. The headline result

The paper's summary ([Karlinsky et al., 2024, p. 2](#ref-paper)), per household per month:

- Non-Haredi Jewish household: pays about $1,900 more than it gets back. About 70% of these households pay more than they get.
- Haredi (ultra-Orthodox) household: gets about $1,300 more than it pays. About 80% get more.
- Arab household: gets about $310 more. About 60% get more.

> The paper is positive, not normative. It describes what is, and does not say if it is fair or right ([Karlinsky et al., 2024, p. 4](#ref-paper)).
{: .prompt-info }

## 04. Terms

- Net transfer => services and benefits received, minus taxes borne. Positive means a household gets more than it pays. Negative means it pays more.
- Decile => ten equal groups of households, ranked by income. Decile 1 is the lowest, decile 10 the highest.
- Standard person => the paper adjusts for household size. A second person in the house does not double the cost of living, since you share rent and electricity. It uses the square root of household size. A household of 4 counts as 2 standard people. A household of 9 counts as 3 (my calculation).
- Tax burden (incidence) => who actually carries a tax in the end, even if someone else sends it to the state.
- Haredi => ultra-Orthodox Jews. The "Arab" group includes Arab, Bedouin and Druze citizens. Circassians are counted with non-Haredi Jews.[^circassians]
- CBS => Israel's Central Bureau of Statistics.

## 05. Where the numbers come from

The data is the CBS Household Expenditure Survey ([CBS, 2023](#ref-cbs)). Households keep a spending diary, and CBS also records their income. The authors pooled three years, 2016 to 2018: 26,664 households, standing for about 2.6 million households and 8.6 million people ([Karlinsky et al., 2024, p. 6](#ref-paper)).

Why not newer years? The response rate fell from about 75% to about 64% in 2019 and 44% in 2020 and 2021. CBS also changed its method in 2019, which breaks the series. And Covid distorted 2020 and 2021.

The survey alone is not enough. People under-report what they spend, so the survey finds less VAT than the state collected. The fix is simple. The authors take the official total, divide it by the survey total, and multiply every household by that factor.

![Diagram: survey VAT of $23.3bn and official VAT of $31.4bn give a scaling factor of about 1.35, so a household that reports $310 is counted at about $420](scaling-flow.svg){: w="900" h="330" .shadow }
_My chart. The two totals are from Table 1 of the paper. The $310 household is made up._

For VAT the factor is about 1.35 (my calculation: 99.87 divided by 73.97, in shekel billions). A household that reports $310 of VAT gets counted at about $420.

> This assumes everybody under-reports by the same share. If richer households under-report more, the same factor does not fix it. I found no test of this in the paper or the appendix ([Technical appendix, 2025](#ref-appendix)).
{: .prompt-warning }

## 06. Who bears each tax

The paper has to decide who carries each tax. These are its choices:

- Income tax => the worker.
- VAT and fuel excise => the consumer.
- Social insurance (National Insurance and health tax) => the employee, including the part the law puts on the employer. The paper treats the split as a fiction.
- Corporate tax => one third on consumers (higher prices), one third on workers (lower pay), one third on owners of capital (lower profits).
- Diesel tax and the business share of vehicle tax => like corporate tax.
- Property tax on homes => the household. Property tax on businesses => like corporate tax.

![Diagram: corporate tax is split one third to consumers, one third to workers and one third to owners of capital, then assigned to each household by its share of spending, wages and capital income](corporate-tax-thirds.svg){: w="900" h="400" .shadow }
_My chart of the paper's assumption._

Why thirds for corporate tax? The literature gives wide ranges, and the authors split the difference. The paper admits this is an approximation. For example, exporters pay less, and part of the tax falls on foreigners ([Karlinsky et al., 2024, note 9](#ref-paper)).

Cash benefits and services are counted by who uses them. Schools by the ages of the kids in the house. Health care by an age-based formula per person, whether or not they visited a doctor. Higher education by students.

## 07. The main chart: taxes, services, net

Taxes counted in the main analysis: $127.5bn. Services counted: $84.2bn. The paper's tax total covers about 96% of what the state collects. Its spending total covers about 50% of what the state spends. Earlier studies, the authors say, covered about 27% of taxes and 14% of spending ([Karlinsky et al., 2024, p. 46](#ref-paper)).

Here are the values for each income decile (charts 6, 17 and 2 of the paper):

![Bar chart by income decile: taxes rising from about $1,190 to about $11,470 a month, services falling slowly from about $3,320 to about $2,450, and net transfer going from +$2,130 to −$9,020](net-by-decile.svg){: w="900" h="490" .shadow }
_My chart, from charts 2, 6 and 17 of the paper. USD per household per month, rounded._

We can read three things:

- Taxes climb steeply, from about $1,190 in decile 1 to about $11,470 in decile 10.
- Services are almost flat. Decile 1 gets about $3,320 and decile 10 about $2,450.
- The net transfer is the gap between the two. It turns negative at decile 5.

The top decile's net of −$9,020 a month is the biggest bar.

> This does not mean the top decile "funds" the bottom one. Taxes also pay for things the paper does not count, like defense and interest. That is why taxes ($127.5bn) are bigger than the services counted ($84.2bn). The gap is about $43bn a year.[^gap]
{: .prompt-warning }

## 08. The same chart, by group

The paper splits households into three groups: non-Haredi Jews, Haredi Jews and Arab citizens (chart 3).

![Two bar panels. Per household per month: non-Haredi Jews −$1,920, Haredi Jews +$1,290, Arab citizens +$330. Total per year: −$47.4bn, +$2.6bn, +$1.5bn](net-by-sector.svg){: w="900" h="380" .shadow }
_My chart, from chart 3 of the paper. Without defense and infrastructure, and without the cost of military service._

Look at both panels. The Haredi group gets +$1,290 per household, but only +$2.6bn in total. The reason is size. The yearly total depends on how many households are in the group. Working back (my calculation), that is about 168,000 Haredi households, about 378,000 Arab households and about 2.06 million non-Haredi Jewish households.

Where do the percentages from the summary come from? The paper also splits each group into its own ten deciles (chart 4). Net transfers turn negative from decile 4 for non-Haredi Jews, decile 7 for Arab citizens and decile 9 for Haredi Jews. So about 30%, 60% and 80% of these groups respectively are net receivers.

> A group's decile is inside that group. Decile 10 of the Arab group is not the national top decile.
{: .prompt-tip }

> Military service is not in the numbers. Conscription is a hidden tax, because conscripts earn less than their economic cost. A separate study ([Geibel & Sarel, 2020](#ref-geibel)) puts it at about 3.7% of GDP, about $15bn in 2018.[^military] The survey has no data on service, so the paper cannot assign it. The authors say the burden falls mostly on non-Haredi Jews, so their negative figure would be larger ([Karlinsky et al., 2024, p. 36](#ref-paper)).
{: .prompt-warning }

## 09. Taxes: who pays what

Taxes are not equal in how they scale with income. This chart shows how many times more the top decile pays than the bottom decile, for each tax.

![Horizontal bars: income tax ×733 (bar cut), National Insurance and health tax ×16.6, corporate tax and related ×7.4, business property tax ×7.0, residential property tax ×4.3, fees ×4.0, excise ×3.6, VAT ×3.2, customs ×2.3](tax-ratio.svg){: w="900" h="430" .shadow }
_My chart. Each bar is the decile 10 value divided by the decile 1 value, from charts 8 to 16 of the paper._

Income tax and social insurance grow fast with income. VAT, excise and customs grow slowly. The reason is that the first group depends on income, and the second on spending. Spending moves less than income does.

Two examples (my calculation):

- VAT is 45% of the bottom decile's tax bill ($530 of $1,190).
- Income tax is 42% of the top decile's tax bill ($4,840 of $11,470).

The income tax ratio is huge because the bottom decile pays only about $7 a month. Most of them are under the tax threshold.

![Funds flow diagram in USD billions: revenue of about $128bn in counted taxes plus about $39bn of other revenue and borrowing flows into the state, which spends about $84bn on counted services and about $82bn on items not counted](composition.svg){: w="900" h="580" .shadow }
_My chart, from Table 1 of the paper ([Karlinsky et al., 2024, p. 38](#ref-paper)). The "other revenue, borrowing" bar is my calculation: total spending minus counted taxes._

Read it left to right. VAT ($31.4bn) and income tax ($30.0bn) are the two biggest taxes. National Insurance and health tax is third ($22.2bn). Counted taxes add up to about $128bn. The state spends about $166bn in total, so about $39bn comes from other revenue and borrowing. That figure is my subtraction, not the paper's.

On the right, the blue bars are the services the paper assigns to households. The gray bars are what it leaves out of the main analysis.

## 10. Spending: who gets what

Now the other side. This chart does the same trick for spending: the top decile's value divided by the bottom decile's.

![Horizontal bars: culture, sport and leisure ×3.49, health ×1.07, cash benefits ×0.99, higher education ×0.76, public transport ×0.48, welfare ×0.44, schools ×0.42, religion ×0.24, public housing ×0.03](spend-ratio.svg){: w="900" h="430" .shadow }
_My chart, from charts 19 to 27 of the paper. The dashed line is equal spending (×1)._

Most spending leans to the lower deciles. Three items do not:

- Health is about equal across deciles. Each person gets a sum based on age, sex and place of living, so income barely matters.
- Cash benefits are about equal, because the old-age pension reaches the upper deciles too.
- Culture, sport and leisure is the only item that clearly rises with income.

Schools are a strong example of the other direction. Decile 1 gets about $950 a month in education spending per household. Decile 10 gets about $400. The paper says there are more children in the lower deciles (next section).

What is left out, and why. The first two enter only a second, wider analysis. The third is not counted anywhere.

- Defense and internal security, about $30bn together. They are public goods. One person using them does not stop another. There is no agreed way to split them. The authors say the result of any split follows directly from the assumptions ([Karlinsky et al., 2024, p. 35](#ref-paper)).
- Infrastructure, about $14bn. It serves future generations too, and the price of water or power already includes building it.
- Interest on debt, about $10bn, and budget pensions. The debt was created in the past, so it is unclear who should carry today's payment.

## 11. Households: kids and age

Why does a low-income household get so much in services? Part of the answer is that it is bigger and has more children.

![Two stacked bars: decile 1 has 3.65 people, of which 46.7% children, 45.5% ages 18 to 64, 7.9% age 65 and over. Decile 10 has 2.89 people, 19.3% children, 64.3% adults, 16.4% age 65 and over](household-age.svg){: w="900" h="370" .shadow }
_My chart, from chart 28 of the paper. The length of each part is its share times the total (my calculation)._

A decile 1 household has about 1.7 children on average. A decile 10 household has about 0.56. That explains why school spending is higher at the bottom. Health and old-age benefits are higher at the top, because there are more older people there.

The paper also looks at couples by number of children (chart 30):

![Bar chart of net transfers to couples by number of children: 0 children −$1,520, 1 −$2,550, 2 −$2,520, 3 −$2,520, 4 −$300, 5 +$1,690, 6 or more +$3,930 per month](household-structure.svg){: w="900" h="410" .shadow }
_My chart, from chart 30 of the paper. Single parents (0, 1, 2, 3 or more children): −$410, −$320, +$320, +$2,560 a month._

Couples with up to 3 children pay net. With 4 they are about break-even. With 5 or more they receive net. Taxes rise until the third child and fall from the fourth. The paper notes the fall and does not explain it.

These charts are breakdowns, not explanations. They do not control for age, income or group.

## 12. Stress tests

The authors ask if the picture holds when the assumptions change.

### Expenditure deciles

Income in one year is a noisy sign of how well off a family is. Young and old households can have low income now and high spending. So the paper ranks households by spending too (chart 33). The shape is the same. The top decile's net is −$6,960 instead of −$9,020 a month.

### Gini index

Gini runs from 0 (full equality) to 1 (one household has everything). The paper computes it for different definitions of income.

![Bar chart of Gini: cash income after tax 0.351, total income after tax 0.326, central analysis 0.258, and with defense and infrastructure added 0.207 by person, 0.242 by spending, 0.284 by income](gini.svg){: w="900" h="380" .shadow }
_My chart, from the Gini chart on page 45 of the paper._

Adding the missing taxes and services lowers measured inequality, from 0.326 to 0.258. Adding defense and infrastructure moves it between 0.207 and 0.284, depending on how they are split. That range shows how much the unsettled choices matter.

### Sensitivity (appendix)

The appendix ([Technical appendix, 2025](#ref-appendix)) changes the assumptions one at a time, and then together:

- Add the missing spending, about $53bn, in three ways. Net-negative deciles shrink from 5 to 10 down to 8 to 10.
- Scale spending up so it matches taxes. Then only the top five deciles of non-Haredi Jews pay net.
- Split VAT three ways instead of all on the consumer. Deciles 7 to 10 pay more, 1 to 6 pay less.
- Split income tax half and half between worker and employer. Less progressive, but still progressive.
- Put all corporate tax on owners of capital. Almost no change.

The appendix describes its results in words, so I quote no numbers beyond the ones it gives. In all of these, deciles 1 to 4 still get more than they pay, and 5 to 10 still pay more.

Why is it so stable? Labor income, spending and capital income are tightly linked across deciles. A household that earns a lot also spends a lot and owns a lot. So moving a tax from one base to another changes little ([Technical appendix, 2025](#ref-appendix)).

## 13. What the paper does not say

- Net transfer is a gap between counted taxes and counted services. It is not a donation or a debt. The paper is positive, so any normative conclusion comes from the reader.
- Decile figures are averages. Two households in the same decile can be at very different stages of life.
- About $82bn of spending is not counted, and the answer depends on the choices made for it.
- The paper counts what a service costs the state, not what it is worth to the household ([Karlinsky et al., 2024, note 2](#ref-paper)).
- The data is 2018. The paper gives reasons, but there is no check against later years.
- The paper assumes households do not change behavior. It warns that simulations need care ([Karlinsky et al., 2024, p. 46](#ref-paper)).


> What I did not check: the top-decile values in chart 7 and chart 29 have no numbers I could read. I do not know if the spike in public housing at decile 5 (chart 25) is real. The appendix is the December 2025 print version and my main text is the 2024 accepted version, so small differences may exist.
{: .prompt-warning }

## 14. References

Karlinsky, A., Sadeh, T., Yogev, E., & Sarel, M. (2024). _On taxes and wonders: The distribution of government revenues and expenditures among households in Israel_ [Accepted for publication in _The Economic Quarterly_, 24 June 2024; Hebrew title: על המיסים ועל הנפלאות]. Kohelet Policy Forum. [https://z.calcalist.co.il/assets/pickerul/6b90f139-7ff2-4976-af70-01940ab73a94.pdf](https://z.calcalist.co.il/assets/pickerul/6b90f139-7ff2-4976-af70-01940ab73a94.pdf)
{: #ref-paper }

Technical appendix. (2025). _Appendix: On taxes and wonders_ [Print version of _The Economic Quarterly_, December 2025]. Bank of Israel. [https://boi.org.il/media/ysmh4ykd/appendix.pdf](https://boi.org.il/media/ysmh4ykd/appendix.pdf)
{: #ref-appendix }

Central Bureau of Statistics. (2023). _Household Expenditure Survey_. [https://www.cbs.gov.il/he/Surveys/Pages/סקר-הוצאות-משקי-בית.aspx](https://www.cbs.gov.il/he/Surveys/Pages/%D7%A1%D7%A7%D7%A8-%D7%94%D7%95%D7%A6%D7%90%D7%95%D7%AA-%D7%9E%D7%A9%D7%A7%D7%99-%D7%91%D7%99%D7%AA.aspx)
{: #ref-cbs }

Geibel, G., & Sarel, M. (2020). _Economic costs of mandatory military service in Israel_ [In Hebrew]. Kohelet Policy Forum. Cited in the paper, not read by me, and I found no link.
{: #ref-geibel }

The paper's other sources are in its own reference list ([Karlinsky et al., 2024, pp. 48 to 58](#ref-paper)).

[^circassians]: Per the appendix ([Technical appendix, 2025](#ref-appendix)). The survey has included Bedouin households since 2016.
[^gap]: In shekels, the paper puts the gap at about 138 billion ([Karlinsky et al., 2024, p. 8](#ref-paper)).
[^military]: In shekels, about 49 billion in 2018 ([Karlinsky et al., 2024, p. 36](#ref-paper)).
