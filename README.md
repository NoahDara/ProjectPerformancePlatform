# IntelliProject — Intelligent Project Performance Analytics Platform

> A web-based analytics platform for multi-discipline engineering consulting firms — unifying project data across Engineering, Quantity Surveying, Land Surveying, and Architecture into a single real-time performance management system.

---

## Overview

Engineering consulting firms manage complex, multi-discipline projects simultaneously. Yet most internal performance tracking remains manual, fragmented, and reactive — relying on spreadsheets, periodic meetings, and hand-written reports.

**IntelliProject** solves this by providing a centralised platform that:

- Consolidates project data across all professional disciplines
- Delivers real-time performance dashboards using Earned Value Management (EVM) metrics
- Automates professional PDF project status report generation
- Benchmarks new projects against historical data for evidence-based planning

This system is the artefact developed as part of a Master of Science in Information Systems research study, following a **Design Science Research (DSR)** methodology.

---

## Key Features

| Feature | Description |
|---|---|
| 🏗️ **Multi-Discipline Data Model** | Unified project data schema supporting Engineering, Surveying, and Architecture workflows |
| 📊 **Real-Time EVM Dashboards** | Interactive dashboards displaying SPI, CPI, and discipline-level completion rates |
| 📄 **Automated PDF Reporting** | On-demand, data-populated professional project status reports via WeasyPrint |
| 🔍 **Historical Benchmarking** | Planning guidance — duration estimates, team sizing, risk patterns — drawn from past projects |
| 🔐 **Role-Based Access Control** | Separate views and permissions for Administrators, Project Managers, and Discipline Leads |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 4.x (Python) |
| Database | PostgreSQL |
| Data Processing | Pandas, NumPy |
| Visualisation | Plotly / Chart.js |
| Report Generation | WeasyPrint |
| Frontend | Django Templates + Bootstrap 5 |
| Authentication | Django Allauth |
| Deployment | Docker + Railway / Render |

---

## Project Structure

```
intelliproject/
├── config/                  # Django project settings (base, dev, prod)
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/            # User authentication & role-based access (Django Allauth)
│   ├── projects/            # Core project & discipline data model
│   ├── dashboards/          # EVM metrics, KPI calculations, Plotly/Chart.js views
│   ├── reports/             # Automated PDF report generation (WeasyPrint)
│   └── benchmarking/        # Historical project analysis & planning guidance engine
│
├── static/                  # CSS, JS, Bootstrap 5 assets
├── templates/               # Django HTML templates
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── docker-compose.yml
├── Dockerfile
├── manage.py
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (recommended)

### Local Development Setup

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/intelliproject.git
cd intelliproject
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements/development.txt
```

**4. Configure environment variables**

```bash
cp .env.example .env
# Edit .env with your database credentials and secret key
```

**5. Apply database migrations**

```bash
python manage.py migrate
```

**6. Create a superuser**

```bash
python manage.py createsuperuser
```

**7. Run the development server**

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

### Docker Setup

```bash
docker-compose up --build
```

---

## User Roles

| Role | Access |
|---|---|
| **Administrator** | Full system access — manage users, projects, disciplines, and settings |
| **Project Manager** | View all projects, manage assigned projects, generate reports |
| **Discipline Lead** | Update progress and data for their assigned discipline on a project |

---

## EVM Metrics

The platform implements core **Earned Value Management** indicators:

| Metric | Formula | Meaning |
|---|---|---|
| **SPI** (Schedule Performance Index) | EV / PV | >1.0 ahead of schedule; <1.0 behind |
| **CPI** (Cost Performance Index) | EV / AC | >1.0 under budget; <1.0 over budget |
| **CV** (Cost Variance) | EV − AC | Positive = under budget |
| **SV** (Schedule Variance) | EV − PV | Positive = ahead of schedule |
| **EAC** (Estimate at Completion) | BAC / CPI | Forecast final cost |

---

## Research Context

This platform is developed as a Masters-level research artefact under a **Design Science Research** methodology, guided by the following objectives:

- **O1** — Unify multi-discipline project data into a standardised data model
- **O2** — Deliver real-time performance monitoring via interactive dashboards
- **O3** — Automate professional project status report generation
- **O4** — Enable historical project benchmarking for evidence-based planning

The research extends the application of EVM and Case-Based Reasoning (CBR) methodologies to professional consulting firms — a context that has received limited academic attention.

---

## Development Roadmap

- [x] Repository initialised
- [ ] Phase 1 — Data model & core backend
- [ ] Phase 2 — EVM dashboards & reporting engine
- [ ] Phase 3 — Benchmarking module
- [ ] System evaluation & user testing
- [ ] Dissertation submission

---

## Contributing

This repository is currently a research project. Contributions, feedback, and issues are welcome once the initial development phase is complete.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**[Your Full Name]**
MSc Information Systems Candidate
[University Name] · 2026
