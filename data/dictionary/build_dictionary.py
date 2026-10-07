"""Build data/dictionary/wqp_fields.csv from the saved WQP user-guide text.

The guide lists each field name on one line followed by its definition on the next.
We keep only the fields that appear in the downloaded result and station CSVs.
Run: python data/dictionary/build_dictionary.py
"""
import csv
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE.parent / "raw"
guide = (HERE / "wqp_portal_userguide_2026-10-07.txt").read_text().split("\n")
lines = [l.strip() for l in guide if l.strip()]

defs = {}
for i in range(len(lines) - 1):
    name = lines[i].rstrip("*†").strip()
    if name and name[0].isupper() and " " not in name and 2 < len(name) < 70:
        if name not in defs:
            defs[name] = lines[i + 1]

rows = []
for fname, table in [("wqp_result.csv", "result"), ("wqp_station.csv", "station")]:
    with (RAW / fname).open(newline="") as f:
        header = next(csv.reader(f))
    for col in header:
        rows.append({"table": table, "field": col, "definition": defs.get(col, "")})

out = HERE / "wqp_fields.csv"
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["table", "field", "definition"])
    w.writeheader(); w.writerows(rows)
missing = [r["field"] for r in rows if not r["definition"]]
print(f"wrote {out} ({len(rows)} fields; {len(missing)} without a guide definition: {missing})")
