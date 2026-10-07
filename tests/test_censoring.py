import numpy as np
import pytest
from gwaudit.censoring import km_left_censored, km_quantile, interval_compare, substitute


def test_km_with_no_censoring_is_the_empirical_cdf():
    v = [1.0, 2.0, 3.0, 4.0]
    xs, F = km_left_censored(v, v)
    assert list(xs) == v
    assert np.allclose(F, [0.25, 0.5, 0.75, 1.0])


def test_km_hand_calculation_with_one_nondetect():
    # Observations: <2 (ND), 3, 5, 8.  Flip with M=9: times 7(cens), 6, 4, 1.
    # Sorted flipped: 1(ev), 4(ev), 6(ev), 7(cens).  S: 3/4, 1/2, 1/4, 1/4.
    # On the original scale: P(X<8)=3/4, P(X<5)=1/2, P(X<3)=1/4.
    # F(x)=P(X<=x): F(8)=1, F(5)=3/4, F(3)=1/2.
    lower = [0.0, 3.0, 5.0, 8.0]
    upper = [2.0, 3.0, 5.0, 8.0]
    xs, F = km_left_censored(lower, upper)
    assert list(xs) == [3.0, 5.0, 8.0]
    assert np.allclose(F, [0.5, 0.75, 1.0])


def test_km_nondetect_above_a_detect_redistributes_mass():
    # <6 (ND), 3, 5, 8. Flip M=9: 3(cens), 6(ev), 4(ev), 1(ev).
    # Sorted: 1(ev) S=3/4; 3(cens) at_risk 3->2; 4(ev) S=3/4*1/2=3/8; 6(ev) S=3/8*0=0.
    # P(X<8)=3/4, P(X<5)=3/8, P(X<3)=0 -> F(3)=3/8, F(5)=3/4, F(8)=1.
    xs, F = km_left_censored([0, 3, 5, 8], [6, 3, 5, 8])
    assert list(xs) == [3.0, 5.0, 8.0]
    assert np.allclose(F, [0.375, 0.75, 1.0])


def test_km_median_identifiable_and_not():
    lower = [0.0, 3.0, 5.0, 8.0]
    upper = [2.0, 3.0, 5.0, 8.0]
    # F(3)=0.5 so the median is 3.
    assert km_quantile(lower, upper, 0.5) == 3.0
    # Three of four below the lowest detect: median is in the censored region.
    assert km_quantile([0, 0, 0, 8.0], [2, 2, 2, 8.0], 0.5) is None
    # but the 90th percentile is still identifiable
    assert km_quantile([0, 0, 0, 8.0], [2, 2, 2, 8.0], 0.9) == 8.0


def test_interval_compare():
    assert interval_compare(5, 5, 3, 3) == "decline"
    assert interval_compare(5, 5, 7, 7) == "increase"
    assert interval_compare(5, 5, 5, 5) == "indeterminate"
    # ND <2 then detected 1.5: indeterminate because 1.5 lies inside [0,2]
    assert interval_compare(0, 2, 1.5, 1.5) == "indeterminate"
    # ND <2 then detected 9: increase
    assert interval_compare(0, 2, 9, 9) == "increase"
    # detected 9 then ND <2: decline
    assert interval_compare(9, 9, 0, 2) == "decline"
    # ND <2 then ND <5: indeterminate
    assert interval_compare(0, 2, 0, 5) == "indeterminate"


def test_substitution_is_explicit():
    lo, hi = [0.0, 4.0], [2.0, 4.0]
    assert list(substitute(lo, hi, "zero")) == [0.0, 4.0]
    assert list(substitute(lo, hi, "half")) == [1.0, 4.0]
    assert list(substitute(lo, hi, "limit")) == [2.0, 4.0]
    with pytest.raises(ValueError):
        substitute(lo, hi, "mean")


def test_bounds_validation():
    with pytest.raises(ValueError):
        km_left_censored([3.0], [2.0])


def test_all_censored_is_not_identifiable():
    xs, F = km_left_censored([0, 0, 0], [2, 2, 5])
    assert len(xs) == 0
    assert km_quantile([0, 0, 0], [2, 2, 5], 0.5) is None
