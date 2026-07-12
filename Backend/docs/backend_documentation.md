# 🚀 TransitOps Backend Documentation

Welcome to the backend documentation for **TransitOps** – a Smart Transport Operations Platform. This backend powers the entire fleet management ecosystem, ensuring high performance, scalability, and strict business rule enforcement.

## 🏗️ Architecture: Clean Architecture
This project strictly follows the **Clean Architecture** pattern to separate concerns and make the codebase modular, testable, and maintainable.

### The Flow of Data
`HTTP Request` ➔ `Route` ➔ `Service` ➔ `Repository` ➔ `Database`

1. **Routes (Controllers):** Located in `app/api/routes/`. Responsible ONLY for receiving HTTP requests, validating them via Pydantic schemas, calling the appropriate Service, and returning the response. They contain **zero** business logic.
2. **Services (Business Logic):** Located in `app/services/`. This is the brain of the application. All business rules (e.g., verifying a driver's license isn't expired before a trip) live here.
3. **Repositories (Data Access):** Located in `app/repositories/`. Responsible ONLY for communicating with the database (CRUD operations). They isolate SQLModel queries from the rest of the app.
4. **Models (Database Schema):** Located in `app/models/`. Define the SQL tables using SQLModel.
5. **Schemas (Data Transfer Objects):** Located in `app/schemas/`. Pydantic models used for strictly typing and validating API requests and responses.

## 🛠️ Technology Stack
* **Language:** Python 3.11+
* **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Extremely fast, modern, async-capable)
* **ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) (Combines SQLAlchemy for DB interaction and Pydantic for validation)
* **Authentication:** OAuth2 with JWT (JSON Web Tokens)
* **Database:** SQLite (Local Dev) & Neon DB / PostgreSQL (Production)
* **Server:** Uvicorn (ASGI web server)

## 📁 Project Structure
```text
Backend/
├── app/
│   ├── api/            # FastAPI Routes (endpoints) and dependencies
│   ├── core/           # Config, logging, DB engine, and security
│   ├── models/         # SQLModel database tables
│   ├── repositories/   # Database access layer (CRUD)
│   ├── schemas/        # Pydantic validation schemas
│   ├── seed/           # Demo data initialization
│   ├── services/       # Core business logic and rules
│   └── tests/          # Integration and unit tests
├── docs/               # Project documentation
├── .env                # Environment variables
├── docker-compose.yml  # Docker deployment configuration
├── main.py             # FastAPI application entry point
└── requirements.txt    # Python dependencies
```

## 🚀 How to Run the Backend

### Local Setup
1. **Create Virtual Environment:** `python3 -m venv .venv`
2. **Activate it:** `source .venv/bin/activate`
3. **Install Dependencies:** `pip install -r requirements.txt`
4. **Run Server:** `uvicorn app.main:app --reload --port 8000`

### Docker Setup
1. Simply run: `docker-compose up --build -d`
2. The server will be accessible at `http://localhost:8000`

## 🛡️ Error Handling
The backend uses standard HTTP status codes combined with strict Pydantic validation:
* **422 Unprocessable Entity:** Automatically returned if a request body is malformed or missing required fields.
* **404 Not Found:** Returned if a requested resource (like a specific Trip ID) doesn't exist.
* **409 Conflict:** Returned by the Services if a business rule is violated (e.g., Vehicle is already in maintenance).
* **403 Forbidden:** Returned if the user's role does not have permission for the endpoint.
