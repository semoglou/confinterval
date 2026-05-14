from dataclasses import dataclass

import numpy as np
from scipy import stats

@dataclass
class Result:
    estimate: float
    lower: float
    upper: float
    confidence: float
    method: str
    statistic: str

    def to_dict(self):
        return {
            "estimate": self.estimate,
            "lower": self.lower,
            "upper": self.upper,
            "confidence": self.confidence,
            "method": self.method,
            "statistic": self.statistic,
        }

    def summary(self):
        pct = self.confidence * 100
        return (
            f"{self.statistic}: {self.estimate:.6g}\n"
            f"{pct:.0f}% {self.method} confidence interval: "
            f"[{self.lower:.6g}, {self.upper:.6g}]"
        )

    def __repr__(self):
        return self.summary()


class ci:
    def __init__(self, data=None, confidence=0.95, random_state=None):
        if not 0 < confidence < 1:
            raise ValueError("confidence must be between 0 and 1")

        self.data = None if data is None else np.asarray(data, dtype=float)
        self.confidence = confidence
        self.random_state = random_state

        if self.data is not None:
            if self.data.ndim != 1:
                raise ValueError("data must be one-dimensional")
            if len(self.data) == 0:
                raise ValueError("data cannot be empty")
            if np.isnan(self.data).any():
                raise ValueError("data cannot contain NaN values")

    def t(self):
        """Confidence interval for the mean using the t distribution."""
        x = self._data()
        n = len(x)

        if n < 2:
            raise ValueError("t interval needs at least two values")

        mean = np.mean(x)
        se = np.std(x, ddof=1) / np.sqrt(n)

        alpha = 1 - self.confidence
        critical = stats.t.ppf(1 - alpha / 2, df=n - 1)

        lower = mean - critical * se
        upper = mean + critical * se

        return Result(
            estimate=float(mean),
            lower=float(lower),
            upper=float(upper),
            confidence=self.confidence,
            method="t",
            statistic="mean",
        )

    def normal(self):
        """Confidence interval for the mean using the normal approximation."""
        x = self._data()
        n = len(x)

        if n < 2:
            raise ValueError("normal interval needs at least two values")

        mean = np.mean(x)
        se = np.std(x, ddof=1) / np.sqrt(n)

        alpha = 1 - self.confidence
        critical = stats.norm.ppf(1 - alpha / 2)

        lower = mean - critical * se
        upper = mean + critical * se

        return Result(
            estimate=float(mean),
            lower=float(lower),
            upper=float(upper),
            confidence=self.confidence,
            method="normal",
            statistic="mean",
        )

    def bootstrap(self, statistic="mean", n_resamples=10000):
        """Bootstrap confidence interval for mean, median, std, iqr, or pXX."""
        x = self._data()

        if n_resamples <= 0:
            raise ValueError("n_resamples must be greater than 0")

        rng = np.random.default_rng(self.random_state)

        estimate = self._statistic(x, statistic)
        values = []

        for _ in range(n_resamples):
            sample = rng.choice(x, size=len(x), replace=True)
            values.append(self._statistic(sample, statistic))

        alpha = 1 - self.confidence
        lower = np.percentile(values, 100 * alpha / 2)
        upper = np.percentile(values, 100 * (1 - alpha / 2))

        return Result(
            estimate=float(estimate),
            lower=float(lower),
            upper=float(upper),
            confidence=self.confidence,
            method="bootstrap",
            statistic=statistic,
        )

    @classmethod
    def proportion(cls, successes, total, confidence=0.95):
        """Create a proportion interval from successes and total trials."""
        if total <= 0:
            raise ValueError("total must be greater than 0")
        if successes < 0 or successes > total:
            raise ValueError("successes must be between 0 and total")

        obj = cls(None, confidence=confidence)
        obj.successes = successes
        obj.total = total
        return obj

    def wilson(self):
        """Wilson confidence interval for a proportion."""
        successes, total = self._proportion_data()

        p = successes / total
        alpha = 1 - self.confidence
        z = stats.norm.ppf(1 - alpha / 2)

        denominator = 1 + z**2 / total
        center = (p + z**2 / (2 * total)) / denominator
        margin = z * np.sqrt(
            p * (1 - p) / total + z**2 / (4 * total**2)
        ) / denominator

        lower = max(0, center - margin)
        upper = min(1, center + margin)

        return Result(
            estimate=float(p),
            lower=float(lower),
            upper=float(upper),
            confidence=self.confidence,
            method="wilson",
            statistic="proportion",
        )

    def _data(self):
        if self.data is None:
            raise ValueError("no data was provided")
        return self.data

    def _proportion_data(self):
        if not hasattr(self, "successes") or not hasattr(self, "total"):
            raise ValueError("use ci.proportion(successes, total).wilson()")
        return self.successes, self.total

    def _statistic(self, x, statistic):
        statistic = statistic.lower()

        if statistic == "mean":
            return np.mean(x)

        if statistic == "median":
            return np.median(x)

        if statistic == "std":
            return np.std(x, ddof=1)

        if statistic == "iqr":
            q75, q25 = np.percentile(x, [75, 25])
            return q75 - q25

        if statistic.startswith("p"):
            q = float(statistic[1:])
            return np.percentile(x, q)

        raise ValueError("statistic must be mean, median, std, iqr, p90, p95, etc.")
