if command -v py &> /dev/null; then
    py -m venv ./netgeo_venv &&
    source ./netgeo_venv/Scripts/activate
    py -m pip install -r requirements.txt
    echo "Install complete"
elif command -v python &> /dev/null; then
    python -m venv ./netgeo_venv &&
    source ./netgeo_venv/Scripts/activate
    python -m pip install -r requirements.txt
    echo "Install complete"
elif command -v python3 &> /dev/null; then
    python3 -m venv ./netgeo_venv &&
    source ./netgeo_venv/Scripts/activate
    python3 -m pip install -r requirements.txt
    echo "Install complete"
else
    echo "Could not find a valid Python installation"
fi
