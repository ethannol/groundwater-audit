"""Explicit unit and chemical-definition conversions.

Every conversion used anywhere in the project is defined here so it can be
tested in isolation. Nothing in this module guesses: unknown unit strings
raise.
"""
from __future__ import annotations

# Atomic masses (IUPAC 2021 conventional values).
M_N = 14.007
M_O = 15.999
M_NO3 = M_N + 3 * M_O  # 62.004

# Factor converting "mg/L as NO3" to "mg/L as N".
NO3_TO_N = M_N / M_NO3  # 0.22589...

# Canonical units for each constituent family.
CANONICAL_UNIT = {
    "arsenic": "ug/L",
    "nitrate_as_n": "mg/L as N",
    "no3_no2_as_n": "mg/L as N",
}

# (source unit string as it appears in WQP, constituent family) -> factor
_FACTORS = {
    ("ug/l", "arsenic"): 1.0,
    ("mg/l", "arsenic"): 1000.0,
    ("mg/l as n", "nitrate_as_n"): 1.0,
    ("mg/l asno3", "nitrate_as_n"): NO3_TO_N,
    ("mg/l as no3", "nitrate_as_n"): NO3_TO_N,
    ("mg/l as n", "no3_no2_as_n"): 1.0,
}


class UnitError(ValueError):
    pass


def factor_to_canonical(unit: str, family: str) -> float:
    """Multiplicative factor taking a value in `unit` to the family's canonical unit."""
    key = (unit.strip().lower(), family)
    if key not in _FACTORS:
        raise UnitError(f"no conversion defined for unit {unit!r} in family {family!r}")
    return _FACTORS[key]


def convert(value: float, unit: str, family: str) -> float:
    return value * factor_to_canonical(unit, family)
