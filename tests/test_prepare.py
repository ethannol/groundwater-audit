"""Tests of consequential preparation steps on tiny hand-built tables."""
import numpy as np
import pandas as pd
import pytest

from gwaudit import prepare as P

RESULT_COLS = ["raw_row"] + list(P.COLS.values())


def row(**kw):
    base = {c: "" for c in P.COLS.values()}
    base.update({
        "MonitoringLocationIdentifier": "USGS-1", "ActivityIdentifier": "a1",
        "ActivityTypeCode": "Sample-Routine", "ActivityMediaName": "Water",
        "ActivityMediaSubdivisionName": "Groundwater", "ActivityStartDate": "2010-05-01",
        "CharacteristicName": "Arsenic", "ResultSampleFractionText": "Dissolved",
        "ResultMeasureValue": "3.0", "ResultMeasure/MeasureUnitCode": "ug/l",
        "USGSPCode": "01000", "ResultValueTypeName": "Actual", "ResultStatusIdentifier": "Accepted",
    })
    base.update(kw)
    return base


def station(ids):
    cols = list(P.STATION_COLS.values())
    return pd.DataFrame([{c: ("" if c != "MonitoringLocationIdentifier" else i) for c in cols} | {"MonitoringLocationName": f"name-{i}"} for i in ids])


def raw(rows):
    df = pd.DataFrame(rows)
    df.insert(0, "raw_row", np.arange(2, len(df) + 2))
    return df


def test_nondetect_builds_interval_from_limit_in_limit_units():
    df = raw([row(ResultMeasureValue="", **{"ResultMeasure/MeasureUnitCode": ""},
                  ResultDetectionConditionText="Not Detected",
                  **{"DetectionQuantitationLimitMeasure/MeasureValue": "0.002",
                     "DetectionQuantitationLimitMeasure/MeasureUnitCode": "mg/l"})])
    c = P.canonicalize(df)
    assert bool(c.loc[0, "censored"])
    assert c.loc[0, "lower"] == 0.0
    assert c.loc[0, "upper"] == pytest.approx(2.0)  # 0.002 mg/L -> 2 ug/L
    assert c.loc[0, "unit"] == "ug/L"


def test_nitrate_as_no3_is_converted_to_as_n():
    df = raw([row(CharacteristicName="Nitrate", USGSPCode="71851", ResultMeasureValue="44.27",
                  **{"ResultMeasure/MeasureUnitCode": "mg/l asNO3"})])
    c = P.canonicalize(df)
    assert c.loc[0, "value"] == pytest.approx(10.0, abs=0.01)
    assert c.loc[0, "pcode_role"] == "derived_duplicate"


def test_derived_duplicate_rows_are_dropped_not_double_counted():
    rows = [row(ActivityIdentifier="a1", CharacteristicName="Nitrate", USGSPCode="00618", ResultMeasureValue="2.0",
                **{"ResultMeasure/MeasureUnitCode": "mg/l as N"}),
            row(ActivityIdentifier="a1", CharacteristicName="Nitrate", USGSPCode="71851", ResultMeasureValue="8.9",
                **{"ResultMeasure/MeasureUnitCode": "mg/l asNO3"})]
    # ten activities so the ratio check has pairs
    rows = [dict(r, ActivityIdentifier=f"a{i}") for i in range(10) for r in rows]
    out = P.prepare(raw(rows), station(["USGS-1"]), write=False)
    assert len(out["analysis"]) == 10
    assert (out["analysis"]["pcode"] == "00618").all()
    step = out["log"].set_index("step").loc["derived_duplicates"]
    assert step["rows_removed"] == 10


def test_derived_rows_that_do_not_match_source_raise():
    rows = []
    for i in range(10):
        rows.append(row(ActivityIdentifier=f"a{i}", CharacteristicName="Nitrate", USGSPCode="00618", ResultMeasureValue="2.0",
                        **{"ResultMeasure/MeasureUnitCode": "mg/l as N"}))
        rows.append(row(ActivityIdentifier=f"a{i}", CharacteristicName="Nitrate", USGSPCode="71851", ResultMeasureValue="2.0",
                        **{"ResultMeasure/MeasureUnitCode": "mg/l asNO3"}))
    with pytest.raises(AssertionError):
        P.prepare(raw(rows), station(["USGS-1"]), write=False)


def test_non_groundwater_media_and_qc_records_are_excluded_and_logged():
    rows = [row(ActivityIdentifier="a1"),
            row(ActivityIdentifier="a2", ActivityMediaSubdivisionName="Leachate"),
            row(ActivityIdentifier="a3", ActivityTypeCode="Quality Control Sample-Field Replicate"),
            row(ActivityIdentifier="a4", ActivityTypeCode="Not determined")]
    out = P.prepare(raw(rows), station(["USGS-1"]), write=False)
    assert len(out["analysis"]) == 1
    assert len(out["replicates"]) == 1
    log = out["log"].set_index("step")
    assert log.loc["medium", "rows_removed"] == 1
    assert log.loc["activity_type", "rows_removed"] == 2  # replicate + not determined
    assert out["summary"]["media_removed"] == {"Leachate": 1}


def test_station_join_cannot_multiply_rows():
    rows = [row(ActivityIdentifier="a1"), row(ActivityIdentifier="a2", MonitoringLocationIdentifier="USGS-2")]
    st = station(["USGS-1", "USGS-2"])
    out = P.prepare(raw(rows), st, write=False)
    assert len(out["analysis"]) == 2
    assert out["summary"]["unmatched_station_rows"] == 0
    dup_station = pd.concat([st, st.iloc[[0]]], ignore_index=True)
    with pytest.raises(AssertionError):
        P.prepare(raw(rows), dup_station, write=False)


def test_duplicate_activity_pcode_rows_are_refused():
    rows = [row(ActivityIdentifier="a1"), row(ActivityIdentifier="a1", ResultMeasureValue="4.0")]
    with pytest.raises(AssertionError):
        P.prepare(raw(rows), station(["USGS-1"]), write=False)


def test_total_fraction_kept_in_clean_but_out_of_analysis():
    rows = [row(ActivityIdentifier="a1"), row(ActivityIdentifier="a2", USGSPCode="01002", ResultSampleFractionText="Total")]
    out = P.prepare(raw(rows), station(["USGS-1"]), write=False)
    assert len(out["clean"]) == 2 and len(out["analysis"]) == 1
