#!/usr/bin/env bash
set -e

# Quick smoke test: setup venv, install deps, list datasets, run ingest

cd "$(dirname "$0")/.."

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m cli.main datasets
python -m cli.main ingest menyo20k

mkdir -p data/processed/yo
echo "Báwo ni? Èmi ni Sisi Lola!" > data/interim/yo_sample.txt
python -m preprocessing.code_switch data/interim/yo_sample.txt data/processed/yo/segments.csv

echo "Smoke test complete: data/processed/yo/segments.csv"
