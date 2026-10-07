"""Download the source snapshot from the Water Quality Portal and write a manifest.

Usage:
    python -m gwaudit.acquire            # downloads into data/raw/
    python -m gwaudit.acquire --verify   # recomputes checksums of the existing snapshot

The query is read from data/raw/query.json so the retrieval is reproducible.
The downloaded files are never modified by the rest of the pipeline.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
QUERY = RAW / "query.json"
MANIFEST = RAW / "manifest.json"
FILES = {"result": "wqp_result.csv", "station": "wqp_station.csv"}

ATTRIBUTION = (
    "Data retrieved from the Water Quality Portal (https://www.waterqualitydata.us), "
    "a cooperative service of the USGS, EPA and NWQMC. All records in this snapshot are "
    "USGS National Water Information System (NWIS) data (OrganizationIdentifier USGS-CA), "
    "which are public domain U.S. Government works. Suggested citation: "
    "National Water Quality Monitoring Council, Water Quality Portal, accessed "
    "{date}, https://www.waterqualitydata.us."
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def count_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.reader(f)) - 1


def build_params(q: dict, which: str) -> list[tuple[str, str]]:
    params: list[tuple[str, str]] = []
    for k, v in q["params"].items():
        if isinstance(v, list):
            params.extend((k, item) for item in v)
        else:
            params.append((k, v))
    if which == "result":
        params.append(("dataProfile", q["result_profile"]))
    return params


def download() -> None:
    q = json.loads(QUERY.read_text())
    manifest = {
        "download_date_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "query": q,
        "attribution": ATTRIBUTION.format(date=dt.date.today().isoformat()),
        "files": {},
    }
    for which, fname in FILES.items():
        url = q["base_url"] + q["endpoints"][which]
        params = build_params(q, which)
        print(f"GET {url} {params}", file=sys.stderr)
        r = requests.get(url, params=params, timeout=600)
        r.raise_for_status()
        out = RAW / fname
        out.write_bytes(r.content)
        counts = {k: v for k, v in r.headers.items() if k.lower().startswith("total-")}
        manifest["files"][fname] = {
            "url": r.url,
            "http_status": r.status_code,
            "bytes": len(r.content),
            "sha256": sha256(out),
            "portal_count_headers": counts,
            "rows_excluding_header": count_rows(out),
        }
        print(f"  -> {out.name}: {len(r.content)} bytes, headers {counts}", file=sys.stderr)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {MANIFEST}", file=sys.stderr)


def verify() -> int:
    manifest = json.loads(MANIFEST.read_text())
    ok = True
    for fname, meta in manifest["files"].items():
        actual = sha256(RAW / fname)
        status = "OK" if actual == meta["sha256"] else "MISMATCH"
        ok &= status == "OK"
        print(f"{status}  {fname}  {actual}")
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    sys.exit(verify() if a.verify else download())
