# 🛡️ FedSecure — Privacy-Preserving Intrusion Detection System

A full-stack Django web application that simulates **Federated Learning** for intrusion detection across distributed network nodes — without sharing raw data.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip

### Option A: One-Command Setup (Linux/Mac)
```bash
chmod +x setup.sh
./setup.sh
```

### Option B: One-Command Setup (Windows)
```
Double-click: setup_windows.bat
```

### Option C: Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv venv

# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate.bat

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create database tables
python manage.py migrate

# 4. Seed demo data (clients, rounds, logs)
python manage.py seed_data

# 5. Start server
python manage.py runserver
```

Then open: **http://127.0.0.1:8000/**

---

## 🔑 Login Credentials

| Role    | Username | Password   |
|---------|----------|------------|
| Admin   | admin    | admin123   |
| Analyst | analyst  | analyst123 |

Django Admin panel: http://127.0.0.1:8000/admin/

---

## 🌐 Application Pages

| Page | URL | Description |
|------|-----|-------------|
| Login | `/login/` | Authentication |
| Dashboard | `/dashboard/` | Overview: stats, charts, live alerts |
| Client Nodes | `/clients/` | View all federated nodes + network diagram |
| FL Training Monitor | `/training/` | Run training rounds, see convergence |
| Intrusion Detection | `/detection/` | Test traffic samples for attacks |
| Attack Logs | `/logs/` | Browse all detected intrusions |
| Model Performance | `/performance/` | Accuracy, precision, recall, confusion matrix |
| Admin | `/admin/` | Django admin (superuser only) |

---

## 🧠 How Federated Learning Works (in this app)

```
┌─────────────┐    model updates only    ┌─────────────────┐
│  Hospital   │ ─────────────────────►  │                 │
│  Node Alpha │ ◄─────────────────────  │   FL Server     │
└─────────────┘    global model          │  (FedAvg)       │
                                         │                 │
┌─────────────┐    model updates only    │                 │
│  Bank       │ ─────────────────────►  │                 │
│  Node Beta  │ ◄─────────────────────  └─────────────────┘
└─────────────┘    global model
```

1. **Local Training**: Each client trains on its own network data
2. **Gradient Sharing**: Only model gradients (not raw data) are sent to server
3. **FedAvg Aggregation**: Server averages updates weighted by sample count
4. **Global Model**: Updated model is pushed back to all clients
5. **Privacy Preserved**: Raw network traffic never leaves each node

---

## 📁 Project Structure

```
fedsecure/
├── manage.py                    # Django entry point
├── requirements.txt             # Python dependencies
├── setup.sh                     # Linux/Mac quick setup
├── setup_windows.bat            # Windows quick setup
├── db.sqlite3                   # SQLite database (auto-created)
│
├── fedsecure/                   # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── core/                        # Main application
│   ├── models.py                # Database models
│   ├── views.py                 # Page & API views
│   ├── urls.py                  # URL routing
│   ├── admin.py                 # Admin config
│   ├── federated.py             # FL simulation engine
│   └── management/commands/
│       └── seed_data.py         # Demo data seeder
│
├── templates/core/              # HTML templates
│   ├── base.html                # Layout with sidebar
│   ├── login.html
│   ├── dashboard.html
│   ├── clients.html
│   ├── federated_training.html
│   ├── intrusion_detection.html
│   ├── attack_logs.html
│   └── performance.html
│
└── static/                      # CSS, JS assets
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 (Python) |
| Database | SQLite (zero config) |
| Frontend | HTML5 + CSS3 + JavaScript |
| Charts | Chart.js 4.4 |
| Fonts | Space Grotesk + JetBrains Mono |
| FL Engine | Custom Python simulation (federated.py) |

---

## 📊 Attack Types Detected

- **DoS** — Denial of Service (high volume traffic)
- **Port Scan** — Reconnaissance (many ports, low bytes)
- **Brute Force** — Repeated auth attempts (SSH/RDP ports)
- **Botnet** — C&C communication (IRC ports)
- **SQL Injection** — Database attack patterns
- **XSS** — Web-based cross-site scripting

---

## 🔒 Privacy Features

- Raw network traffic **never leaves** the client node
- Only **gradient updates** (model weights) are transmitted
- FedAvg aggregation runs on the central server
- Differential privacy noise simulation built-in
- No central data lake required

---

## 🧪 How to Use

1. **Login** at `/login/` with `admin / admin123`
2. **Dashboard** shows overview of the FL-IDS system
3. **Clients** page shows all participant nodes and network topology
4. **Training** page — click "Start Federated Training" to run rounds
5. **Detection** — test traffic samples using quick presets (DoS, Port Scan, etc.)
6. **Logs** — filter and browse all detected intrusions
7. **Performance** — review confusion matrix and ML metrics

---

## 📝 Notes

- The FL simulation is educational — it doesn't require TensorFlow/PyTorch
- The detection engine uses heuristic scoring to simulate ML predictions
- All data is stored locally in `db.sqlite3`
- To reset all data: `python manage.py flush` then `python manage.py seed_data`
