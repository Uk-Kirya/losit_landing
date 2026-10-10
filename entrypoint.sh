#!/bin/bash
set -e

echo "Starting Uvicorn..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload