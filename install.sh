#!/usr/bin/env bash
py --version && pyinstall() ||
python --version && pythoninstall() ||
python3 --version && python3install() ||
echo "Errors occured during installation"

pyinstall() {
	py -m venv ./netgeo_venv &&
	./netgeo_venv/Scripts/activate
	py -m pip install -r requirements.txt
	echo "Install complete"
}

pythoninstall() {
	python -m venv ./netgeo_venv &&
	./netgeo_venv/Scripts/activate
	python -m pip install -r requirements.txt
	echo "Install complete"
}

python3install() {
	python3 -m venv ./netgeo_venv &&
	./netgeo_venv/Scripts/activate
	python3 -m pip install -r requirements.txt
	echo "Install complete"
}
