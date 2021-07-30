#!/usr/bin/env bash

# pyinstaller build script

rm -rf build dist
pipenv run pyinstaller -n SubsFinder -F -p "../"  app.py
