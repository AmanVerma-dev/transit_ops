# TransitOps Backend - Smart Transport Operations Platform

## Project Overview
TransitOps is a centralized, smart transport operations platform designed to digitize vehicle, driver, dispatch, maintenance, and expense management while enforcing strict business rules and providing real-time operational insights. 

This repository houses the backend codebase for the platform, initialized using a clean architecture pattern with FastAPI and SQLModel.

## Tech Stack
- **Python**: 3.11+
- **FastAPI**: Modern, fast web framework for building APIs.
- **SQLModel**: An ORM combining SQLAlchemy and Pydantic.
- **PostgreSQL**: Robust, relational SQL database.
- **Docker & Docker Compose**: Containerized environment for local development and deployment.
- **Pydantic Settings**: Environment and settings management.
- **Uvicorn**: Lightning-fast ASGI server implementation.

## Folder Structure
```
transitops-backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── dependencies/
│   │   │   └── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── repositories/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── utils/
│   │   └── __init__.py
│   ├── seed/
│   │   └── __init__.py
│   ├── tests/
│   │   └── .gitkeep
│   └── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example
```

## Installation & Setup

### Local Development Setup

1. **Create and Activate a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Required Packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and adjust the variables if needed:
   ```bash
   cp .env.example .env
   ```

4. **Run the Database:**
   Ensure PostgreSQL is running locally and matches the `DATABASE_URL` in `.env`. Alternatively, use Docker Compose to start the database:
   ```bash
   docker compose up -d db
   ```

5. **Start the Uvicorn Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Compose Setup
To spin up both the database and the FastAPI application in Docker containers, run:
```bash
docker compose up --build -d
```

### Swagger Documentation
Once the server is running, the interactive API documentation can be accessed at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Future Development Phases
- **Phase 1: Database Schemas & Migrations**: Define SQLModel models and database schema definitions. Setup Alembic for handling migrations.
- **Phase 2: Authentication & RBAC**: Implement secure login, JWT authentication, and Role-Based Access Control (Fleet Manager, Driver).
- **Phase 3: Core CRUD Modules**: Build CRUD interfaces for Vehicles, Drivers, and Maintenance management.
- **Phase 4: Trip Dispatch Logic & Rules Engine**: Implement trip dispatch flow, checking capacity constraints, license validations, and status updates.
- **Phase 5: Fuel Logging, Expense Tracking, & Analytics**: Implement fuel and cost management, and write backend logic for Dashboard KPIs and analytics.
