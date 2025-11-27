"""
Prefect flow: Ingest + Preprocess pipeline for multilingual datasets.
"""
from __future__ import annotations

from pathlib import Path
from prefect import flow, task

ROOT = Path(__file__).resolve().parents[1]


@task
def ingest_task(datasets: list[str] | None = None):
    import sys
    sys.path.append((ROOT / "ingestion").as_posix())
    from ingest_registry import main as ingest_main
    ingest_main(datasets)


@task
def preprocess_task():
    # Placeholder: ensure processed dirs exist
    for code in ["yo", "pcm", "ig", "ha", "sw_KE", "sw_TZ", "fr_WA", "ak", "en_NG", "en_GH", "en_LR"]:
        p = ROOT / "data" / "processed" / code
        p.mkdir(parents=True, exist_ok=True)


@flow(name="sisi-lola-ingest-preprocess")
def ingest_preprocess_flow(datasets: list[str] | None = None):
    ingest_task.submit(datasets)
    preprocess_task.submit()


if __name__ == "__main__":
    ingest_preprocess_flow()
