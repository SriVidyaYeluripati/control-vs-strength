"""Download all raw data for the project into data/raw/.

Run from the repo root:
    python scripts/download_data.py

1. Patient data (OpenNeuro ds004080): ccepData_V2.mat + all electrodes.tsv
   and channels.tsv files (no raw recordings).
2. Healthy connectomes (MICA-MICs): HC001-HC050, Destrieux atlas.
3. Region label table: lut_aparc-a2009s_mics.csv (micapipe repo).

Files that already exist are skipped, so it is safe to run again.
"""

from pathlib import Path
import urllib.request

import openneuro  # pip install openneuro-py

ROOT = Path(__file__).resolve().parents[1]
CCEP_DIR = ROOT / "data" / "raw" / "ccep"
CONN_DIR = ROOT / "data" / "raw" / "connectome"

MICA_URL = (
    "https://sftp.conp.ca/users/MICA/MICs_release/derivatives/micapipe/"
    "sub-{s}/ses-01/dwi/sub-{s}_ses-01_space-dwinative_atlas-aparca2009s_desc-sc.txt"
)
LUT_URL = (
    "https://raw.githubusercontent.com/MICA-MNI/micapipe/master/"
    "parcellations/lut/lut_aparc-a2009s_mics.csv"
)


def fetch(url: str, out: Path) -> None:
    """Download one file unless it already exists."""
    if out.exists():
        print(f"  skip (exists): {out.name}")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(url, out)
        print(f"  ok: {out.name}")
    except Exception as err:  # keep going if one file fails
        print(f"  FAILED: {out.name} -> {err}")


def download_ccep() -> None:
    print("1/3 Patient data (OpenNeuro ds004080)")
    openneuro.download(
        dataset="ds004080",
        target_dir=CCEP_DIR,
        include=[
            "derivatives/av_ccep/ccepData_V2.mat",
            "sub-*/ses-*/ieeg/*_electrodes.tsv",
            "sub-*/ses-*/ieeg/*_channels.tsv",
        ],
    )


def download_connectomes() -> None:
    print("2/3 Healthy connectomes (MICA-MICs, HC001-HC050)")
    for i in range(1, 51):
        s = f"HC{i:03d}"
        fetch(MICA_URL.format(s=s), CONN_DIR / f"sub-{s}_ses-01_space-dwinative_atlas-aparca2009s_desc-sc.txt")


def download_lut() -> None:
    print("3/3 Region label table")
    fetch(LUT_URL, CONN_DIR / "lut_aparc-a2009s_mics.csv")


if __name__ == "__main__":
    download_ccep()
    download_connectomes()
    download_lut()
    n_conn = len(list(CONN_DIR.glob("sub-HC*_desc-sc.txt")))
    n_elec = len(list(CCEP_DIR.glob("sub-*/ses-*/ieeg/*_electrodes.tsv")))
    print(f"\nDone: {n_elec} electrodes.tsv, {n_conn}/50 connectomes.")
