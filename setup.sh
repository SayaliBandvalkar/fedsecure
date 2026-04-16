#!/bin/bash
echo "========================================"
echo " FedSecure - Privacy-Preserving IDS"
echo " Setup Script (Linux/Mac)"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Install it via: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[2/5] Installing dependencies..."
pip install -r requirements.txt

echo "[3/5] Running database migrations..."
python manage.py migrate

echo "[4/5] Seeding demo data..."
python manage.py seed_data

echo "[5/5] Starting development server..."
echo ""
echo "========================================"
echo " FedSecure is running!"
echo " Open: http://127.0.0.1:8000/"
echo " Admin:   admin / admin123"
echo " Analyst: analyst / analyst123"
echo "========================================"
echo ""
python manage.py runserver
