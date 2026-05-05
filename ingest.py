"""
CMS Medicare Inpatient Charge Data — DuckDB Ingestion
"""

import duckdb
import pandas as pd
import os
import re
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────
RAW_DIR = "data/raw"
DB_PATH  = "data/cms_inpatient.duckdb"

COLUMN_MAP = {
    "rndrng_prvdr_ccn":          "provider_ccn",
    "rndrng_prvdr_org_name":     "provider_name",
    "rndrng_prvdr_city":         "provider_city",
    "rndrng_prvdr_st":           "provider_street",
    "rndrng_prvdr_state_fips":   "provider_fips",
    "rndrng_prvdr_zip5":         "provider_zip",
    "rndrng_prvdr_state_abrvtn": "provider_state",
    "rndrng_prvdr_ruca":         "provider_ruca",
    "rndrng_prvdr_ruca_desc":    "provider_ruca_desc",
    "drg_cd":                    "drg_code",
    "drg_desc":                  "drg_description",
    "tot_dschrgs":               "total_discharges",
    "avg_submtd_cvrd_chrg":      "avg_covered_charges",
    "avg_tot_pymt_amt":          "avg_total_payments",
    "avg_mdcr_pymt_amt":         "avg_medicare_payments",
}

REQUIRED_COLUMNS = [
    "provider_ccn",
    "drg_code",
    "total_discharges",
    "avg_covered_charges",
    "avg_total_payments",
    "avg_medicare_payments",
]


# ── Helpers ─────────────────────────────────────────────────────────────────
"""Pull a 4-digit year out of the filename."""
def extract_year_from_filename(filename: str) -> int | None:
    if filename:
        extractyear = filename.split("inpatient_")
        year = int(extractyear[1].split(".")[0])
        return year
    return None

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower().str.strip()
    df = df.rename(columns=COLUMN_MAP)
    return df

def validate_columns(df: pd.DataFrame, filename: str) -> bool:
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            log.warning(f"[{filename}] Missing column: {col}")
            return False
    return True


def clean_types(df: pd.DataFrame) -> pd.DataFrame:
    """Cast charges/payments to float, discharges to int, normalize CCN. DRG_Code to INT, DRG_DESC to str """
    df["avg_covered_charges"] = pd.to_numeric(df["avg_covered_charges"]).round(2)
    df["avg_total_payments"] = pd.to_numeric(df["avg_total_payments"]).round(2)
    df["avg_medicare_payments"] = pd.to_numeric(df["avg_medicare_payments"]).round(2)
    df["drg_code"] = pd.to_numeric(df["drg_code"]).astype(int)
    df["total_discharges"] = pd.to_numeric(df["total_discharges"]).astype(int)
    df["provider_ccn"] = df["provider_ccn"].astype(str).str.zfill(6)
    df["drg_description"] = df["drg_description"].str.strip()
    return df


# ── Main ingestion ───────────────────────────────────────────────────────────

def load_csv(filepath: str, fiscal_year: int) -> pd.DataFrame | None:
    """Load a single CSV, normalize, validate, and return a clean DataFrame."""
    df = pd.read_csv(filepath, dtype=str, encoding="latin-1")
    df = normalize_columns(df)
    if not validate_columns(df, filepath):
        return None
    df = clean_types(df)
    df["fiscal_year"] = fiscal_year
    return df


def ingest_all():
    """Find all CSVs in RAW_DIR, load each, union them, write to DuckDB.
    1. Find all csv
    2. loop over, get filenames and load all csv
    3. combine all data into 1
    4. write to duckdb
    """
    dir_names = os.listdir(RAW_DIR)
    csv_files = []
    frames = []
    
    for name in dir_names:
        if name.endswith(".csv"):
            csv_files.append(name)

    for csv in csv_files:
        filepath = os.path.join(RAW_DIR, csv)
        year = extract_year_from_filename(csv)
        if year is None:
            log.warning(f"Could not extract year from {csv}, skipping")
            continue
        df = load_csv(filepath, year)
        frames.append(df)

    combined = pd.concat(frames)
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE TABLE inpatient_raw AS SELECT * FROM combined")
    con.close()
    print("Executed code")

if __name__ == "__main__":
    ingest_all()
    