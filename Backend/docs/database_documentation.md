# 🗄️ Database Documentation

TransitOps uses a robust relational database schema managed by **SQLModel** (which leverages SQLAlchemy under the hood). This guarantees strict data integrity, foreign key constraints, and clean object-relational mapping.

## ⚙️ Database Engine
* **Development:** SQLite (`transitops.db` file)
* **Production:** Neon DB (Serverless PostgreSQL in the Cloud)

## 🗺️ Core Database Entities (Tables)

### 1. `Role`
Defines the permissions within the system.
* **Fields:** `id` (PK), `name` (Unique String)
* **Seed Data:** "Fleet Manager", "Driver", "Safety Officer", "Financial Analyst"

### 2. `User`
Stores authentication credentials and links to a specific role.
* **Fields:** `id` (PK), `name`, `email` (Unique), `password_hash`, `role_id` (FK -> Role), `is_active`

### 3. `Vehicle`
Represents physical fleet assets (Trucks, Vans, Buses).
* **Fields:** `id` (PK), `registration_number` (Unique), `name_model`, `type`, `max_load_capacity_kg`, `acquisition_cost`, `odometer_km`, `status`
* **Status Enum:** `AVAILABLE`, `ON_TRIP`, `IN_SHOP`, `RETIRED`

### 4. `Driver`
Represents the personnel operating the vehicles.
* **Fields:** `id` (PK), `name`, `license_number` (Unique), `license_expiry_date`, `safety_score`, `status`
* **Status Enum:** `AVAILABLE`, `ON_TRIP`, `SUSPENDED`, `INACTIVE`

### 5. `Trip`
The core operational entity. Connects a Vehicle and Driver to a specific journey.
* **Fields:** `id` (PK), `source`, `destination`, `vehicle_id` (FK), `driver_id` (FK), `cargo_weight_kg`, `planned_distance_km`, `status`, `fuel_consumed_liters`, `revenue`, timestamps.
* **Status Enum:** `DRAFT`, `DISPATCHED`, `COMPLETED`, `CANCELLED`

### 6. `Maintenance`
Records scheduled and completed servicing of vehicles.
* **Fields:** `id` (PK), `vehicle_id` (FK), `maintenance_type`, `description`, `scheduled_date`, `estimated_cost`, `actual_cost`, `status`.
* **Status Enum:** `SCHEDULED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`

### 7. `FuelLog`
Automatically tracks fuel consumption tied to specific trips and vehicles.
* **Fields:** `id` (PK), `vehicle_id` (FK), `trip_id` (FK), `liters`, `recorded_at`

---

## 🔗 Relationships & Integrity Rules

1. **Trip Dependency:** A `Trip` cannot exist without a valid `Vehicle` and `Driver`. If a Vehicle is deleted, it is **Soft Deleted** (marked inactive) so historical Trip data is preserved.
2. **Maintenance Block:** If a `Vehicle` has an active `Maintenance` record (`SCHEDULED` or `IN_PROGRESS`), the Business Rules Engine will block the creation/dispatch of a `Trip` for that vehicle.
3. **Automated Logs:** When a `Trip` is marked as `COMPLETED`, the system automatically:
   * Updates the `Vehicle.odometer_km`.
   * Generates a `FuelLog` entry linked to the Trip and Vehicle.
   * Sets the `Vehicle` and `Driver` status back to `AVAILABLE`.
