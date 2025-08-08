#!/bin/bash
# Run with fastapi
# fastapi dev src/main.py

# Run with uvicorn
cd src && uvicorn main:app --host 0.0.0.0 --port 8081 --reload --workers 1 --log-level info