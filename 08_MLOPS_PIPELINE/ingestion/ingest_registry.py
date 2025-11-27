"""
Ingestion Registry for Sisi Lola MLOps Pipeline

Provides functions to ingest datasets declared in configs/datasets.yaml
and write them to data/external/<dataset_name>.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "configs"
EXTERNAL = ROOT / "data" / "external"


def load_config() -> Dict:
    with open(CONFIGS / "datasets.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def ingest_menyo20k(output_dir: Path) -> None:
    """Ingest MENYO-20k from GitHub into output_dir"""
    ensure_dir(output_dir)
    repo_url = "https://github.com/dadelani/menyo-20k_MT"
    target = output_dir / "menyo-20k_MT"
    if target.exists():
        print("MENYO-20k already present, skipping clone")
        return
    # Lazy clone via git command to avoid extra deps
    os.system(f"git clone {repo_url} \"{target.as_posix()}\"")


def ingest_fleurs(subsets: List[str], output_dir: Path) -> None:
    """Ingest Fleurs subsets via huggingface datasets"""
    ensure_dir(output_dir)
    try:
        from datasets import load_dataset
    except ImportError:
        print("Install: pip install datasets")
        raise
    for subset in subsets:
        print(f"Downloading Fleurs subset: {subset}")
        ds = load_dataset("google/fleurs", subset, trust_remote_code=True)
        subset_dir = output_dir / f"fleurs_{subset}"
        ds.save_to_disk(subset_dir.as_posix())


def ingest_masakhaner(subsets: List[str], output_dir: Path) -> None:
    """Ingest MasakhaNER subsets via huggingface datasets"""
    ensure_dir(output_dir)
    try:
        from datasets import load_dataset
    except ImportError:
        print("Install: pip install datasets")
        raise
    for subset in subsets:
        print(f"Downloading MasakhaNER subset: {subset}")
        ds = load_dataset("masakhane/masakhaner", subset, trust_remote_code=True)
        subset_dir = output_dir / f"masakhaner_{subset}"
        ds.save_to_disk(subset_dir.as_posix())


def ingest_common_voice(subsets: List[str], output_dir: Path, version: str = "17_0") -> None:
    """
    Ingest Mozilla Common Voice African language subsets.
    
    Technical: Downloads crowdsourced speech recordings with transcriptions.
    Layman: Gets real people's voice recordings in African languages for training.
    """
    ensure_dir(output_dir)
    try:
        from datasets import load_dataset
    except ImportError:
        print("Install: pip install datasets")
        raise
    
    for subset in subsets:
        print(f"Downloading Common Voice {version} subset: {subset}")
        try:
            ds = load_dataset(
                f"mozilla-foundation/common_voice_{version}",
                subset,
                trust_remote_code=True
            )
            subset_dir = output_dir / f"common_voice_{subset}"
            ds.save_to_disk(subset_dir.as_posix())
            print(f"  ✓ Saved to {subset_dir}")
        except Exception as e:
            print(f"  ✗ Failed to download {subset}: {e}")


def main(datasets: List[str] | None = None) -> None:
    cfg = load_config()
    selected = datasets or list(cfg.keys())
    for name in selected:
        spec = cfg[name]
        out_dir = EXTERNAL / name
        if name == "menyo20k":
            ingest_menyo20k(out_dir)
        elif name == "fleurs":
            ingest_fleurs(spec.get("subsets", []), out_dir)
        elif name == "masakhaner":
            ingest_masakhaner(spec.get("subsets", []), out_dir)
        elif name == "common_voice_africa":
            ingest_common_voice(spec.get("subsets", []), out_dir)
        else:
            print(f"[SKIP] {name} requires manual download or not automated yet")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest configured datasets")
    parser.add_argument("--only", nargs="*", help="Specific datasets to ingest")
    args = parser.parse_args()
    main(args.only)
