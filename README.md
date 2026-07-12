<div align="center">
  <h1>🚛 TransitOps Platform</h1>
  <p><strong>A Modern, Full-Stack Smart Transport Operations & Fleet Management System.</strong></p>
</div>

---

## 📖 What is TransitOps?
TransitOps is an end-to-end web platform designed to solve the logistical and financial tracking challenges of modern fleet management. It eliminates manual spreadsheets by uniting asset management, personnel assignment, real-time trip lifecycle tracking, automated financial logs, and predictive maintenance into one seamless interface.

## ✨ Core Features
* 🔒 **Role-Based Access Control (RBAC):** Distinct interfaces and permissions for Fleet Managers, Safety Officers, Financial Analysts, and Drivers.
* 🧠 **Business Rule Engine:** Automatically prevents dangerous operational errors (e.g., dispatching an overloaded truck, or assigning a trip to an expired driver).
* 🗺️ **Trip Lifecycle Management:** A robust state machine that transitions deliveries from Draft ➔ Dispatched ➔ Completed.
* 🔧 **Maintenance Tracking:** Keeps track of repairs and intelligently blocks broken vehicles from being dispatched.
* ⛽ **Automated Financials:** Instantly generates fuel expense logs the moment a trip completes.
* 📊 **Live Analytics Dashboard:** Interactive data visualizations calculating ROI, Fuel Efficiency, and Fleet Utilization.

## 🏗️ Technology Stack

**Frontend**
* **React 19 & TypeScript:** Strongly typed, modern UI.
* **Vite:** Lightning-fast frontend build tool.
* **Tailwind CSS V4:** Sleek, responsive, and utility-first styling.
* **Zustand & React-Hook-Form:** Lightweight state and robust form management.

**Backend**
* **Python (FastAPI):** High-performance, asynchronous REST API.
* **SQLModel / SQLAlchemy:** Robust ORM ensuring strict relational integrity.
* **Neon DB (PostgreSQL):** Cloud-hosted, serverless database for production.

---

## 🚀 Getting Started

To run the entire TransitOps platform on your local machine, you will need two terminal windows (one for the Backend, one for the Frontend).

### 1. Start the Backend
The backend runs on `http://localhost:8000`.
```bash
# 1. Navigate into the backend directory
cd Backend

# 2. Create a virtual environment and activate it
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the FastAPI Server
uvicorn app.main:app --reload --port 8000
```
*(The backend will automatically initialize the Neon database schema and seed the initial demo data on its first startup!)*

### 2. Start the Frontend
The frontend runs on `http://localhost:5173`.
```bash
# 1. Navigate into the frontend directory (in a new terminal)
cd Frontend

# 2. Install Node modules
npm install

# 3. Start the Vite development server
npm run dev
```

### 3. Log In!
Open `http://localhost:5173` in your browser. You can log in using one of the automatically seeded demo accounts:
* **Fleet Manager:** `manager@transitops.com` / `password123`
* **Driver:** `driver@transitops.com` / `password123`

---

## 📚 Documentation
For detailed insights into how this project was built, check out the documentation folders:
* 🗄️ [Backend API & DB Docs](./Backend/docs/)
* 🎨 [Frontend Architecture Docs](./Frontend/docs/)
* 🚀 [Full Project Overview](./PROJECT_OVERVIEW.md)