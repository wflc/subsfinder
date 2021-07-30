:: pyinstaller build script
@echo off

del /S /Q  build dist  
pipenv run pyinstaller -n SubsFinder -F -p "../"  app.py
