#!/bin/bash
cd /workspaces/sisi-lola-project
export PYTHONPATH=/workspaces/sisi-lola-project:$PYTHONPATH
python -m uvicorn sisi_lola_api.app.main:app --host 0.0.0.0 --port 8000 --log-level info
