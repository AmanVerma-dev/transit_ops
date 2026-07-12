# 🚀 TransitOps – Smart Transport Operations Platform

**TransitOps** is a comprehensive, modular backend solution for managing end-to-end transport fleet operations. Built with modern Python (FastAPI, SQLModel) under a strict Clean Architecture pattern, it provides robust APIs for authentication, vehicle and driver lifecycle management, trip scheduling with strict business rules, maintenance workflows, operational analytics, and live dashboards.

---

## ✨ Features

- **Authentication & RBAC:** Secure JWT-based auth with four distinct roles (`Fleet Manager`, `Safety Officer`, `Financial Analyst`, `Driver`).
- **Vehicle Management:** Track fleet assets, specifications, acquisition costs, and dynamic statuses (`AVAILABLE`, `ON_TRIP`, `IN_SHOP`, `RETIRED`).
- **Driver Management:** Manage personnel, monitor license expiries, track safety scores, and enforce driver suspension workflows.
- **Trip Lifecycle & Dispatch Rules:** Full state machine (`DRAFT` → `DISPATCHED` → `COMPLETED` / `CANCELLED`). Includes a robust 17-point Business Rule Engine preventing invalid dispatch (e.g., driver license expired, vehicle in maintenance, cargo exceeding capacity).
- **Maintenance Tracking:** Schedule and execute vehicle servicing (`PREVENTIVE`, `CORRECTIVE`, `EMERGENCY`). Auto-blocks vehicles from being dispatched while in the shop.
- **Fuel & Expense Logging:** Track fuel consumption and maintenance costs to calculate operational overhead.
- **Analytics & Reporting:** Rich read-only metrics including Fleet Utilization, Fuel Efficiency, Operational Cost, and Vehicle ROI. Supports CSV data exports.
- **Live Dashboards:** Aggregated key performance indicators (KPIs) and recent activity streams for real-time operational visibility.

---

## 🏗️ Architecture

TransitOps strictly adheres to Clean Architecture principles, ensuring separation of concerns:

```text
HTTP Request → Routes → Services (Business Logic) → Repositories (DB Access) → Database
```

### Folder Structure

```text
Backend/
├── app/
│   ├── api/            # FastAPI Routers and Dependencies (Controllers)
│   ├── core/           # Configuration, Security, Logging, and Database Setup
│   ├── models/         # SQLModel Database Entities
│   ├── repositories/   # Data Access Layer (CRUD operations)
│   ├── schemas/        # Pydantic Models for Request/Response Validation
│   ├── seed/           # Initial Data Seeding (Roles, Users, Demo Data)
│   └── services/       # Core Business Logic and Rules Engine
├── Dockerfile          # Container Definition
├── docker-compose.yml  # Multi-container Orchestration (API + PostgreSQL)
└── requirements.txt    # Python Dependencies
```

---

## 🛠️ Technology Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (High performance, async Python framework)
- **Database ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic)
- **Database Engine:** PostgreSQL (Production/Docker) & SQLite (Local Development)
- **Authentication:** OAuth2 with JWT (jose, passlib)
- **Containerization:** Docker & Docker Compose
- **Language:** Python 3.11+

---

## 🚀 Installation & Setup

### Option 1: Docker Compose (Recommended)

1. **Clone the repository.**
2. **Navigate to the Backend directory.**
3. **Run Docker Compose:**
   ```bash
   docker-compose up --build -d
   ```
4. The API will be available at `http://localhost:8000`.

### Option 2: Local Development (SQLite)

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment:**
   Copy `.env.example` to `.env` (Defaults to SQLite for easy testing).
4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

## 📚 API Documentation

FastAPI automatically generates interactive OpenAPI documentation.

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 🔑 Demo Credentials

Upon startup, the system automatically seeds demo data (Vehicles, Drivers, Trips, Maintenance) and creates the following test users. Use these to log in via the `/auth/login` endpoint to receive a JWT.

| Role | Username | Password |
| :--- | :--- | :--- |
| **Fleet Manager** | `manager@transitops.com` | `password123` |
| **Driver** | `driver@transitops.com` | `password123` |
| **Safety Officer**| `safety@transitops.com` | `password123` |
| **Financial Analyst**| `finance@transitops.com` | `password123` |

---

## 🔮 Future Improvements

- Integration with external GPS/Telematics APIs for live tracking.
- Automated email/SMS notifications for scheduled maintenance and license expiries.
- Enhanced financial module with invoice generation and billing integrations.
- Machine Learning models for predictive maintenance scheduling.
