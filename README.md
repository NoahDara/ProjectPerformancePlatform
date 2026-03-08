# IntelliProject — Intelligent Project Performance Analytics Platform

> A web-based analytics platform for multi-discipline engineering consulting firms — unifying project data across Engineering, Quantity Surveying, Land Surveying, and Architecture into a single real-time performance management system.

---

## Overview

Engineering consulting firms manage complex, multi-discipline projects simultaneously. Yet most internal performance tracking remains manual, fragmented, and reactive — relying on spreadsheets, periodic meetings, and hand-written reports.

**IntelliProject** solves this by providing a centralised platform that:

- Consolidates project data across all professional disciplines into a single source of truth
- Delivers real-time performance dashboards using Earned Value Management (EVM) metrics
- Automates professional PDF project status report generation on demand
- Benchmarks new projects against historical data for evidence-based planning

This system is the artefact developed as part of a Master of Science in Information Systems research study, following a **Design Science Research (DSR)** methodology.

---

## Key Features

| Feature | Description |
|---|---|
| 🏗️ **Multi-Discipline Data Model** | Unified project data schema supporting Engineering, Quantity Surveying, Land Surveying, and Architecture |
| 📊 **Real-Time EVM Dashboards** | Interactive dashboards displaying SPI, CPI, and discipline-level completion rates |
| 📄 **Automated PDF Reporting** | On-demand, data-populated professional project status reports via WeasyPrint |
| 🔍 **Historical Benchmarking** | Planning guidance — duration estimates, team sizing, risk patterns — drawn from completed projects |
| 🔐 **Role-Based Access Control** | Granular permission system with content-type-aware custom permissions per role |
| 👷 **Employee & Task Management** | Tasks assigned to employees with flexible measurement types — units, linear, hours, percentage, lump sum |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 4.x (Python) |
| Database | SQLite (dev) / MySQL (production) |
| Data Processing | Pandas, NumPy |
| Visualisation | Plotly / Chart.js |
| Report Generation | WeasyPrint |
| Frontend | Django Templates + Bootstrap 5 |
| Authentication | Django Allauth + Custom Role & Permission System |
| Deployment | Docker + Railway / Render |

---

## Project Structure

```
ProjectPerformancePlatform/
│
├── accounts/            # CustomUser model — extends AbstractUser with role FK
├── roles/               # Role, CustomPermission — content-type-aware RBAC
├── helpers/             # BaseModel (UUID pk, is_active, is_deleted, created, updated)
├── core/                # Shared utilities, mixins, base views
│
├── branch/              # Branch model — office/regional branches
├── clients/             # Client model — linked to projects
├── disciplines/         # Discipline + Position models — inferred employee discipline
├── employees/           # Employee model — links to CustomUser (optional), Branch, Position
│
├── projects/            # Project, ProjectDiscipline — core project data & EVM baseline
├── tasks/               # Task, TaskUpdate — flexible measurement types & daily progress logs
│
├── dashboard/           # EVM metric calculations, KPI views, Plotly/Chart.js dashboards
├── benchmarking/        # ProjectSnapshot — historical benchmarking engine
│
├── static/              # CSS, JS, Bootstrap 5 assets
├── templates/           # Django HTML templates
│
├── requirements.txt     # Python dependencies
├── manage.py
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- SQLite (built-in, zero config — for development)
- MySQL 8+ (for production only)
- Git

### Local Development Setup

**1. Clone the repository**

```bash
git clone https://github.com/NoahDara/ProjectPerformancePlatform.git
cd ProjectPerformancePlatform
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```dotenv
# Django
DJANGO_SECRET_KEY="your-secret-key-here"
DEBUG=1

# Database
# Set USE_MYSQL=False to use SQLite in development (no DB setup needed)
USE_MYSQL=False
MYSQL_DB_NAME=""
MYSQL_DB_USER=""
MYSQL_DB_PASSWORD=""
MYSQL_DB_HOST=""
MYSQL_DB_PORT=""

# Email
EMAIL_HOST=""
EMAIL_PORT=587
EMAIL_HOST_USER=""
DEFAULT_FROM_EMAIL=""
EMAIL_HOST_PASSWORD=""
EMAIL_USE_TLS=True
DEFAULT_RECIPIENT=""
```

> ✅ For local development, `USE_MYSQL=False` is all you need — SQLite runs with zero configuration.

**5. Apply migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

**6. Create a superuser**

```bash
python manage.py createsuperuser
```

> The first superuser is automatically assigned a **System Administrator** role with all permissions.

**7. Run the development server**

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000`

---

## App Overview

| App | Responsibility |
|---|---|
| `accounts` | CustomUser with UUID pk and Role FK |
| `roles` | Role, CustomPermission, AutoPermissionMixin, post_migrate signal |
| `helpers` | Abstract BaseModel inherited by all models |
| `core` | Shared utilities and base class views |
| `branch` | Office branches — projects and employees belong to a branch |
| `clients` | Client records linked to projects |
| `disciplines` | Discipline (e.g. Engineering) and Position (e.g. Structural Engineer) |
| `employees` | Employee records — optionally linked to a system user account |
| `projects` | Project and ProjectDiscipline — EVM baseline fields included |
| `tasks` | Task with flexible measurement types + TaskUpdate for daily progress logging |
| `dashboard` | EVM calculations (SPI, CPI, EV, PV, AC) and interactive dashboards |
| `benchmarking` | ProjectSnapshot — auto-captured on project completion for planning guidance |

---

## Data Model Summary

```
Branch ───────────────────────────────────────────┐
                                                   │
Discipline → Position → Employee → CustomUser      │
                            │                      │
                            └──── Branch ──────────┤
                                                   │
Client ───────────────────────────────────────────►Project
                                          (project_manager FK → Employee)
                                          (deputy_manager FK → Employee)
                                                   │
                                         ProjectDiscipline
                                         (lead FK → Employee)
                                                   │
                                                 Task
                                         (assigned_to FK → Employee)
                                         (collaborators M2M → Employee)
                                                   │
                                             TaskUpdate
                                      (value_achieved + actual_cost)
```

---

## Task Measurement Types

Tasks support multiple ways of tracking progress — each calculates `percent_complete` differently:

| Type | How Progress Is Calculated | Example |
|---|---|---|
| `percentage` | Latest update value IS the cumulative % | Design drawings — 65% done |
| `units` | Sum of all updates ÷ target × 100 | 120 of 200 piles driven |
| `linear` | Sum of all updates ÷ target × 100 | 400m of 1000m road paved |
| `hours` | Sum of all updates ÷ target × 100 | 80 of 200 hours logged |
| `lump_sum` | Done or not done — binary (0 or 1) | Site clearance complete |

Task `percent_complete` is a computed `@property` — never stored, always calculated from `TaskUpdate` records.

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

> Baseline values (`baseline_budget`, `baseline_start_date`, `baseline_end_date`) are locked on the `Project` model when a project moves from Planning → Active via `project.lock_baseline()`. EVM always measures against the original agreed plan, not revised values.

---

## Role & Permission System

Permissions are automatically generated per model via `AutoPermissionMixin` triggered on `post_migrate`. Each model receives `read_<model>` and `write_<model>` permissions, tied to Django's `ContentType` framework.

Roles are assigned to users via `CustomUser.role` (FK). The first superuser is automatically assigned a **System Administrator** role with all permissions via a `post_save` signal.

**Protecting a class-based view:**

```python
from roles.mixins import RequiredPermissionMixin

class ProjectListView(RequiredPermissionMixin, ListView):
    def required_permissions(self):
        return ["read_project"]
```

**Adding custom permissions to a model:**

```python
class Task(AutoPermissionMixin, BaseModel):
    @classmethod
    def extra_permissions(cls):
        return ["Approve", "Export"]
```

---

## Research Context

This platform is developed as a Masters-level research artefact under a **Design Science Research** methodology, guided by the following objectives:

| Objective | Description |
|---|---|
| **O1** | Unify multi-discipline project data into a standardised data model |
| **O2** | Deliver real-time performance monitoring via interactive EVM dashboards |
| **O3** | Automate professional project status report generation |
| **O4** | Enable historical project benchmarking for evidence-based planning |

The research extends the application of EVM and Case-Based Reasoning (CBR) methodologies to professional consulting firms — a context that has received limited scholarly attention.

---

## Development Roadmap

- [x] Repository initialised
- [x] Custom RBAC system — Role, CustomPermission, AutoPermissionMixin
- [x] Core data model — Branch, Client, Discipline, Position, Employee, Project, Task
- [ ] Phase 1 — Migrations, admin registration, seed data
- [ ] Phase 2 — EVM dashboard views and Chart.js / Plotly integration
- [ ] Phase 3 — Automated PDF report generation (WeasyPrint)
- [ ] Phase 4 — Benchmarking module (ProjectSnapshot + query engine)
- [ ] System evaluation & user testing
- [ ] Dissertation submission

---

## Contributing

This repository is a Masters research project. It is open for review and feedback. Pull requests are welcome once the core development phase is complete.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**Noah Dara**  
MSc Information Systems Candidate · 2026  
[github.com/NoahDara](https://github.com/NoahDara)