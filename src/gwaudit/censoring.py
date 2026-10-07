"""Censored-data helpers.

Observations are intervals [lower, upper]. A detected value v is [v, v]; a
non-detect with reporting limit L is [0, L]. Nothing here substitutes a point
value for a non-detect unless a function name says so.

Functions
---------
km_left_censored(lower, upper)      Kaplan-Meier survival estimate for left-censored data
                                    (flip method, Helsel 2012), returning the estimated
                                    distribution function evaluated at the detected values.
km_quantile(lower, upper, q)        Quantile of the KM distribution; None when not identifiable.
interval_compare(a_lo, a_hi, b_lo, b_hi)  'decline' / 'increase' / 'indeterminate' for b vs a.
substitute(lower, upper, how)       Explicit substitution (for sensitivity analysis only).
"""
from __future__ import annotations

from typing import Literal

import numpy as np

Direction = Literal["decline", "increase", "indeterminate"]


def _check(lower, upper):
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)
    if lower.shape != upper.shape:
        raise ValueError("lower and upper must have the same shape")
    if np.any(lower > upper):
        raise ValueError("lower bound above upper bound")
    if np.any(np.isnan(lower)) or np.any(np.isnan(upper)):
        raise ValueError("NaN bounds")
    return lower, upper


def km_left_censored(lower, upper):
    """Kaplan-Meier estimate of F(x) = P(X <= x) for left-censored data.

    Left-censored data (non-detects) become right-censored after flipping
    x -> M - x, where M is any constant above the largest bound. The standard
    KM survival estimate on the flipped data is then F on the original scale.

    Returns (x_sorted, F_at_x) over the distinct uncensored values, where
    F_at_x[i] is the estimated probability that X <= x_sorted[i].
    Censored values below the smallest detected value make F non-identifiable
    below that point; the estimate starts at the smallest detected value.
    """
    lower, upper = _check(lower, upper)
    censored = lower < upper
    value = np.where(censored, upper, lower)  # non-detect contributes its limit
    M = value.max() + 1.0
    t = M - value  # flipped times; censored => right-censored at t
    event = ~censored
    order = np.argsort(t, kind="stable")
    t, event = t[order], event[order]
    n = len(t)
    at_risk = n
    S = 1.0
    xs, Fs = [], []
    i = 0
    while i < n:
        j = i
        while j < n and t[j] == t[i]:
            j += 1
        d = event[i:j].sum()
        if d > 0:
            S *= 1.0 - d / at_risk
            xs.append(M - t[i])
            Fs.append(S)
        at_risk -= j - i
        i = j
    xs = np.array(xs[::-1])
    Fs = np.array(Fs[::-1])
    if len(xs) == 0:  # no detected values at all: F is not identifiable anywhere
        return xs, Fs
    # S after processing all flipped events down to x is P(flipped > t) = P(X < x);
    # on the original scale we report F(x) = P(X <= x) using the step just above.
    # For the flipped KM, S(t_i) = P(T > t_i) = P(X < x_i). We want P(X <= x_i),
    # which is S just before the step at t_i: recover by shifting.
    F_le = np.empty_like(Fs)
    F_le[:-1] = Fs[1:]
    F_le[-1] = 1.0
    return xs, F_le


def km_quantile(lower, upper, q: float):
    """q-th quantile of the KM distribution, or None if not identifiable.

    The quantile is the smallest detected value x with F(x) >= q. If the mass
    below the smallest detected value already exceeds q, the quantile lies in
    the censored region and is reported as None.
    """
    xs, F = km_left_censored(lower, upper)
    if len(xs) == 0:
        return None
    lower = np.asarray(lower, float); upper = np.asarray(upper, float)
    n = len(lower)
    detected = lower == upper
    # Mass the KM estimate places below the smallest detected value comes only from
    # non-detects whose limit is at or below that value (they are never redistributed upward).
    xmin = xs[0]
    nd_at_or_below = np.sum((~detected) & (upper <= xmin))
    F_below_min = nd_at_or_below / n
    if q <= F_below_min:
        return None
    idx = np.searchsorted(F, q - 1e-9, side="left")  # tolerate floating error in the KM product
    if idx >= len(xs):
        return float(xs[-1])
    return float(xs[idx])


def interval_compare(a_lo: float, a_hi: float, b_lo: float, b_hi: float) -> Direction:
    """Direction of change from observation a (earlier) to b (later)."""
    if b_hi < a_lo:
        return "decline"
    if b_lo > a_hi:
        return "increase"
    return "indeterminate"


def substitute(lower, upper, how: Literal["zero", "half", "limit"]):
    """Point values with explicit substitution for non-detects. Sensitivity use only."""
    lower, upper = _check(lower, upper)
    censored = lower < upper
    if how == "zero":
        sub = 0.0 * upper
    elif how == "half":
        sub = 0.5 * upper
    elif how == "limit":
        sub = upper
    else:
        raise ValueError(how)
    return np.where(censored, sub, lower)
