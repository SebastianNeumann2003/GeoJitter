@echo off
py --version 1>nul && goto :pyinstall ||^
python --version 1>nul && goto :pythoninstall ||^
python3 --version 1>nul && goto :python3install
echo Errors encountered during install

:pyinstall
py -m venv .\netgeo_venv &&^
.\netgeo_venv\Scripts\activate &&^
py -m pip install -r requirements.txt
goto :endofscript

:pythoninstall
python -m venv .\netgeo_venv &&^
.\netgeo_venv\Scripts\activate &&^
python -m pip install -r requirements.txt
goto :endofscript

:python3install
python3 -m venv .\netgeo_venv &&^
.\netgeo_venv\Scripts\activate &&^
python3 -m pip install -r requirements.txt
goto :endofscript

:endofscript
echo Install complete.
