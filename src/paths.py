"""Project paths and small helpers to read the raw data.

Usage (in a notebook or script):
    from src.paths import load_ccep, runs, electrodes_tsv, channels_tsv, load_connectome, load_lut
"""
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Raw data
DATA_DIR = PROJECT_ROOT / "data"
BIDS_DIR = DATA_DIR / "raw" / "ccep"                     # OpenNeuro ds004080 (BIDS)
CCEP_MAT = BIDS_DIR / "derivatives" / "av_ccep" / "ccepData_V2.mat"
CONNECTOME_DIR = DATA_DIR / "raw" / "connectome"         # 50 MICA-MICs matrices + LUT
LUT_CSV = CONNECTOME_DIR / "lut_aparc-a2009s_mics.csv"
PROCESSED_DIR = DATA_DIR / "processed"

# Outputs
RESULTS_DIR = PROJECT_ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"
TABLE_DIR = RESULTS_DIR / "tables"
CACHE_DIR = RESULTS_DIR / "cache"


def load_ccep():
    """ccepData_V2.mat -> list of 74 patients (one dict per patient)."""
    return sio.loadmat(CCEP_MAT, simplify_cells=True)["ccepData"]


def runs(patient: dict) -> list:
    """Return the patient's runs, always as a list.
    (simplify_cells=True turns a single run into a dict instead of a list.)"""
    r = patient["run"]
    return r if isinstance(r, list) else [r]


def _ieeg_dir(patient_id: str, ses: str) -> Path:
    # Some patients use session 'ses-1b' (e.g. UMCU09, UMCU62)
    if not ses.startswith("ses-"):
        ses = f"ses-{ses}"
    return BIDS_DIR / patient_id / ses / "ieeg"


def electrodes_tsv(patient_id: str, ses: str = "ses-1") -> pd.DataFrame:
    f = _ieeg_dir(patient_id, ses) / f"{patient_id}_{ses}_electrodes.tsv"
    return pd.read_csv(f, sep="\t", na_values=["n/a"])


def channels_tsv(patient_id: str, ses: str, run_name: str) -> pd.DataFrame:
    """run_name: the runName from ccepData (e.g. '..._run-021448_averageCCEPs.mat')
    or just 'run-021448'."""
    run = run_name.split("_run-")[-1].split("_")[0] if "_run-" in run_name else run_name.replace("run-", "")
    f = _ieeg_dir(patient_id, ses) / f"{patient_id}_{ses}_task-SPESclin_run-{run}_channels.tsv"
    return pd.read_csv(f, sep="\t", na_values=["n/a"])


def connectome_files():
    return sorted(CONNECTOME_DIR.glob("sub-HC*_desc-sc.txt"))


def load_connectome(path) -> np.ndarray:
    """One MICA-MICs connectivity matrix, as stored (only the upper triangle is filled)."""
    return np.loadtxt(path, delimiter=",")


def load_lut() -> pd.DataFrame:
    lut = pd.read_csv(LUT_CSV)
    lut.columns = lut.columns.str.strip()
    return lut
