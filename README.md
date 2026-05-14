# confinterval

<p align="center">
  <a href="https://pypi.org/project/confinterval/"><img src="https://img.shields.io/pypi/v/confinterval?color=blue" alt="PyPI version"></a>&nbsp;&nbsp;
  <a href="https://pypi.org/project/confinterval/"><img src="https://img.shields.io/pypi/pyversions/confinterval" alt="Python versions"></a>&nbsp;&nbsp;
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>&nbsp;&nbsp;
  <a href="https://pepy.tech/project/confinterval"><img src="https://pepy.tech/badge/confinterval" alt="Downloads"></a>
</p>

A lightweight Python toolkit for computing confidence intervals for means, medians, percentiles, and proportions. 

It supports:

- t confidence intervals for the mean
- normal approximation confidence intervals for the mean
- bootstrap confidence intervals for mean, median, standard deviation, IQR, and percentiles
- Wilson confidence intervals for proportions

## Installation 

Intsall confinterval from [PyPI](https://pypi.org/project/confinterval/)

```python
pip install confinterval
```

## Quick Start

```python
from confinterval import ci

data = [18, 19, 20, 21, 22, 20, 19, 21, 20, 22]

result = ci(data, confidence=0.95).t()

print(result)
```

Output:

    mean: 20.2
    95% t confidence interval: [19.384, 21.016]

You can also access the values directly:

```python
result.estimate
result.lower
result.upper
result.confidence
result.method
result.statistic
```

### Bootstrap intervals

Bootstrap intervals are useful for statistics like the median or percentiles.

```python
from confinterval import ci

data = [18, 19, 20, 21, 22, 20, 19, 21, 20, 22]

result = ci(data, confidence=0.95, random_state=42).bootstrap("median")

print(result)
```

Output:

    median: 20
    95% bootstrap confidence interval: [19, 21]

You can use: 

    ci(data).bootstrap("mean")
    ci(data).bootstrap("median")
    ci(data).bootstrap("std")
    ci(data).bootstrap("iqr")
    ci(data).bootstrap("p90")
    ci(data).bootstrap("p95")

### Proportion intervals

Use Wilson intervals for proportions, rates, or percentages.

```python
from confinterval import ci

result = ci.proportion(87, 100, confidence=0.95).wilson()

print(result)
```

This means 87 successes out of 100 total trials.

Output:

    proportion: 0.87
    95% wilson confidence interval: [0.790196, 0.922428]

## Confidence level 

The default confidence level is 95%. You can change it: 

```python
ci(data, confidence=0.90).t()
ci(data, confidence=0.99).bootstrap("median")
ci.proportion(87, 100, confidence=0.95).wilson()
```

Higher confidence gives a wider interval.

### Convert result to dictionary

```python
data = [18, 19, 20, 21, 22, 20, 19, 21, 20, 22]

result = ci(data).t()

result.to_dict()
```

Output:

    {'estimate': 20.2,
     'lower': 19.25818886972757,
     'upper': 21.14181113027243,
     'confidence': 0.95,
     'method': 't',
     'statistic': 'mean'}

## License
This project is under the MIT License.
