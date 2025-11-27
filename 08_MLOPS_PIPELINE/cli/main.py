"""
Sisi Lola MLOps CLI

Commands:
- datasets list
- ingest [all|menyo20k|fleurs|masakhaner]
- preprocess [--lang yo] [--lower]
- report coverage
"""
from __future__ import annotations

import sys
from pathlib import Path
import typer
import yaml

APP = typer.Typer(add_completion=False)
ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "configs"
EXTERNAL = ROOT / "data" / "external"
PROCESSED = ROOT / "data" / "processed"


@APP.command("datasets")
def datasets_cmd(action: str = typer.Argument("list")):
    if action != "list":
        typer.echo("Usage: datasets list")
        raise typer.Exit(code=1)
    cfg = yaml.safe_load((CONFIGS / "datasets.yaml").read_text(encoding="utf-8"))
    for name, spec in cfg.items():
        typer.echo(f"- {name}: {spec.get('languages', [])} [{spec.get('type')}] -> {spec.get('source')}")


@APP.command("ingest")
def ingest_cmd(dataset: str = typer.Argument("all")):
    sys.path.append((ROOT / "ingestion").as_posix())
    from ingest_registry import main as ingest_main
    if dataset == "all":
        ingest_main(None)
    else:
        ingest_main([dataset])


@APP.command("preprocess")
def preprocess_cmd(lang: str = typer.Option(None, help="Language code to preprocess"), lower: bool = typer.Option(False)):
    # Example: simply ensure lang directory exists
    target = PROCESSED / (lang or "all")
    target.mkdir(parents=True, exist_ok=True)
    typer.echo(f"Prepared processed dir: {target}")


@APP.command("report")
def report_cmd(what: str = typer.Argument("coverage")):
    if what != "coverage":
        typer.echo("Usage: report coverage")
        raise typer.Exit(code=1)
    # Simple coverage report placeholder
    for d in PROCESSED.glob("*"):
        if d.is_dir():
            typer.echo(f"- {d.name}: {len(list(d.rglob('*')))} files")


if __name__ == "__main__":
    APP()
