@echo off
git --version
py --version 1>nul && goto :pyinstall ||^
python --version 1>nul && goto :pythoninstall ||^
python3 --version 1>nul && goto :python3install
echo Errors encountered during install

:pyinstall
git clone https://github.com/SeabassTheFish03/NetGeo.git && cd NetGeo
py -m venv .\netgeo_venv &&^
.\netgeo_venv\Scripts\activate &&^
py -m pip install -r requirements.txt
goto :endofscript

:pythoninstall
git clone https://github.com/SeabassTheFish03/NetGeo.git && cd NetGeo
python -m venv .\netgeo_venv &&^
.\netgeo_venv\Scripts\activate &&^
python -m pip install -r requirements.txt
goto :endofscript

:python3install
git clone https://github.com/SeabassTheFish03/NetGeo.git && cd NetGeo
python3 -m venv .\netgeo_venv &&^
.\netgeo_venv\Scripts\activate &&^
python3 -m pip install -r requirements.txt
goto :endofscript

:endofscript
echo Install complete.
