#!/bin/bash
python -m flake8 src/ --max-line-length=100 --ignore=E203,W503
