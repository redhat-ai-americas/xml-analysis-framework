#! /bin/bash

# This script is used to publish the xml-analysis-framework to PyPI.
python -m build
python -m twine upload dist/*
