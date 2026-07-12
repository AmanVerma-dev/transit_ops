# 🌐 TransitOps API Documentation

The TransitOps API is a RESTful interface built with FastAPI. It provides all necessary operations to manage fleets, drivers, trips, maintenance, and analytics.

## 🔗 Base URL
* **Localhost:** `http://localhost:8000`
* **Swagger UI:** `http://localhost:8000/docs` *(Interactive API Explorer)*
* **ReDoc:** `http://localhost:8000/redoc`

## 🔒 Authentication & Authorization
The API uses **OAuth2 with JWT (JSON Web Tokens)**.
1. Send a `POST` request to `/auth/login` with your `username` and `password`.
2. Receive an `access_token` in the response.
3. For all subsequent requests, include the token in the headers:
   `Authorization: Bearer <your_access_token>`

### Role-Based Access Control (RBAC)
The API enforces strict permissions based on 4 roles:
* **Fleet Manager:** Full access to CRUD operations, dispatching, and analytics.
* **Safety Officer:** Access to manage Drivers, Vehicles, and view Safety KPIs.
* **Financial Analyst:** Read-only access to Dashboards, Analytics, and Trip Financials.
* **Driver:** Limited access (can only view their own assignments and statuses).

---

## 📡 Core API Modules

### 1. Authentication (`/auth`)
* `POST /auth/login` - Authenticate user and receive JWT.
* `GET /auth/me` - Retrieve current logged-in user profile.

### 2. Vehicles (`/vehicles`)
* `POST /vehicles` - Register a new vehicle.
* `GET /vehicles` - List all vehicles (supports filtering by status).
* `GET /vehicles/{id}` - Get vehicle details.
* `PATCH /vehicles/{id}` - Update vehicle properties.
* `DELETE /vehicles/{id}` - Soft delete a vehicle.

### 3. Drivers (`/drivers`)
* `POST /drivers` - Register a new driver.
* `GET /drivers` - List drivers.
* `PATCH /drivers/{id}/suspend` - Suspend a driver (Safety Officers only).
* `PATCH /drivers/{id}/reinstate` - Reinstate a suspended driver.

### 4. Trips (`/trips`)
* `POST /trips` - Create a new trip (Starts in `DRAFT` status).
* `PATCH /trips/{id}` - Update draft trip details.
* `PATCH /trips/{id}/dispatch` - Dispatch a trip (triggers Business Rules Engine).
* `PATCH /trips/{id}/complete` - Mark a trip as completed and log fuel/revenue.
* `PATCH /trips/{id}/cancel` - Cancel a trip.

### 5. Maintenance (`/maintenance`)
* `POST /maintenance` - Schedule vehicle maintenance.
* `PATCH /maintenance/{id}/start` - Begin maintenance work.
* `PATCH /maintenance/{id}/complete` - Complete maintenance (makes vehicle AVAILABLE again).

### 6. Analytics (`/analytics`) *(Read-Only)*
* `GET /analytics/fleet-utilization` - Returns % of fleet currently active.
* `GET /analytics/fuel-efficiency` - Calculates fleet-wide `km/L`.
* `GET /analytics/financial/roi` - Compares revenue vs fuel/maintenance costs.
* `GET /analytics/export/{entity}` - Downloads a `.csv` export of data.

### 7. Dashboard (`/dashboard`) *(Read-Only)*
* `GET /dashboard/overview` - High-level counts of vehicles and statuses.
* `GET /dashboard/kpis` - Quick metrics for the frontend overview.
* `GET /dashboard/recent-trips` - Latest 10 active/completed trips.

---

## 🛑 Standard HTTP Responses
* **200 OK:** Request successful.
* **201 Created:** Resource successfully created.
* **401 Unauthorized:** Missing or invalid JWT token.
* **403 Forbidden:** User lacks the required role.
* **404 Not Found:** The requested resource ID does not exist.
* **409 Conflict:** Business rule violation (e.g. dispatching a vehicle currently in maintenance).
* **422 Unprocessable Entity:** Validation error (e.g. missing required JSON field).
