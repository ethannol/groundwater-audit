import math
import pytest
from gwaudit.units import convert, factor_to_canonical, UnitError, NO3_TO_N


def test_no3_to_n_factor_matches_hand_calculation():
    # 14.007 / (14.007 + 3*15.999) = 14.007 / 62.004
    assert math.isclose(NO3_TO_N, 14.007 / 62.004, rel_tol=1e-12)
    assert math.isclose(NO3_TO_N, 0.2259, abs_tol=5e-5)


def test_nitrate_as_no3_converts_to_as_n():
    # 44.3 mg/L as NO3 is 10.0 mg/L as N (the MCL), to 3 significant figures
    assert math.isclose(convert(44.27, "mg/l asNO3", "nitrate_as_n"), 10.0, abs_tol=0.01)


def test_arsenic_identity_and_mg_to_ug():
    assert convert(3.5, "ug/l", "arsenic") == 3.5
    assert convert(0.0035, "mg/l", "arsenic") == pytest.approx(3.5)


def test_unit_strings_are_case_and_space_insensitive():
    assert factor_to_canonical("MG/L AS N", "nitrate_as_n") == 1.0
    assert factor_to_canonical(" mg/l asNO3 ", "nitrate_as_n") == NO3_TO_N


def test_unknown_unit_raises_rather_than_guessing():
    with pytest.raises(UnitError):
        convert(1.0, "", "arsenic")
    with pytest.raises(UnitError):
        convert(1.0, "mg/l as N", "arsenic")
    with pytest.raises(UnitError):
        convert(1.0, "mg/l asNO3", "no3_no2_as_n")
