# 📑 Frontend Pages Documentation

This document provides a detailed, simple-to-understand breakdown of every single page (view) within the TransitOps frontend application. All of these pages are located in the `src/routes/` directory.

---

### 1. 🔐 Login Page (`LoginPage.tsx`)
**What it does:** 
This is the gateway to the application. It authenticates users securely.
* **Features:** 
  * Collects the user's email/username and password.
  * Validates the input before sending it to the server.
  * On success, it securely stores the JWT (JSON Web Token) in the browser and redirects the user to the Dashboard.
  * Displays clear error messages if the credentials are wrong.

---

### 2. 🏠 Dashboard Page (`DashboardPage.tsx`)
**What it does:** 
The central command center. It gives fleet managers a bird's-eye view of their entire operation at a single glance.
* **Features:** 
  * **Top Metrics (KPIs):** Displays total active vehicles, trips currently en route, and pending maintenance tasks.
  * **Recent Activity:** Shows a quick table of the latest 10 trips (both active and recently completed).
  * **Quick Actions:** Buttons to instantly create a new trip or register a new vehicle without navigating away.

---

### 3. 🚚 Fleet Management Page (`FleetPage.tsx`)
**What it does:** 
The directory of all physical assets (Trucks, Vans, Buses).
* **Features:** 
  * Displays a grid or table of all registered vehicles.
  * Shows real-time statuses: `AVAILABLE`, `ON_TRIP`, or `IN_SHOP`.
  * Allows authorized users to click on a vehicle to see its specific odometer reading and capacity.
  * Contains a form to register new vehicles into the system.

---

### 4. 👨‍✈️ Drivers Page (`DriversPage.tsx`)
**What it does:** 
The personnel management screen for the fleet's drivers.
* **Features:** 
  * Lists all drivers alongside their current assignment status and Safety Score.
  * Flags drivers whose licenses are close to expiring.
  * Allows Safety Officers to quickly `SUSPEND` or `REINSTATE` a driver with a single click.

---

### 5. 🗺️ Trips Page (`TripsPage.tsx`)
**What it does:** 
The most critical page of the app. It handles the entire lifecycle of a delivery journey.
* **Features:** 
  * Shows a detailed table of all trips: `DRAFT`, `DISPATCHED`, `COMPLETED`, and `CANCELLED`.
  * **Create Trip Form:** Allows dispatchers to select an Available Vehicle, an Available Driver, and set the Source/Destination.
  * **Status Controls:** Dispatchers can click buttons to transition a trip from Draft -> Dispatched -> Completed. The backend's Business Rule Engine will automatically block this if rules are violated (e.g. overloaded truck).

---

### 6. 🔧 Maintenance Page (`MaintenancePage.tsx`)
**What it does:** 
Tracks the health and repair schedules of the fleet to prevent breakdowns.
* **Features:** 
  * Lists all repair tasks, categorized by `SCHEDULED`, `IN_PROGRESS`, and `COMPLETED`.
  * Displays estimated costs vs. actual costs for repairs.
  * Allows mechanics to mark a repair as finished, which automatically updates the vehicle's status back to `AVAILABLE`.

---

### 7. ⛽ Fuel & Expenses Page (`FuelExpensesPage.tsx`)
**What it does:** 
The financial ledger for operational costs.
* **Features:** 
  * Lists all automated fuel logs generated when trips are completed.
  * Shows the exact number of liters consumed per trip.
  * Helps financial analysts track the running operational costs of specific trucks.

---

### 8. 📈 Analytics Page (`AnalyticsPage.tsx`)
**What it does:** 
Transforms raw data into beautiful, visual insights for business intelligence.
* **Features:** 
  * Uses **Recharts** to draw interactive graphs.
  * **Fleet Utilization Graph:** Shows what percentage of the fleet is currently making money vs sitting idle.
  * **Financial ROI:** Compares the revenue generated against the fuel and maintenance costs.
  * **Safety Trends:** Visualizes average driver safety scores across the month.

---

### 9. ⚙️ Settings Page (`SettingsPage.tsx`)
**What it does:** 
User and application preferences.
* **Features:** 
  * Displays the logged-in user's profile and assigned Role (e.g., Fleet Manager).
  * Contains options to securely **Log Out** of the application.
  * Contains system-wide theme toggles (Dark/Light mode).
