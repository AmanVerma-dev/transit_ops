import requests
BASE_URL = "http://127.0.0.1:8012"

def run():
    # Auth
    mgr = requests.post(f"{BASE_URL}/auth/login", data={"username": "manager@transitops.com", "password": "password123"})
    mgr_h = {"Authorization": f"Bearer {mgr.json()['access_token']}"}
    safety = requests.post(f"{BASE_URL}/auth/login", data={"username": "safety@transitops.com", "password": "password123"})
    safety_h = {"Authorization": f"Bearer {safety.json()['access_token']}"}
    driver = requests.post(f"{BASE_URL}/auth/login", data={"username": "driver@transitops.com", "password": "password123"})
    driver_h = {"Authorization": f"Bearer {driver.json()['access_token']}"}
    finance = requests.post(f"{BASE_URL}/auth/login", data={"username": "finance@transitops.com", "password": "password123"})
    finance_h = {"Authorization": f"Bearer {finance.json()['access_token']}"}

    # Seed: 2 vehicles, 2 drivers, 3 trips (2 completed, 1 cancelled), 1 maintenance
    v1 = requests.post(f"{BASE_URL}/vehicles", json={"registration_number": "DB-001", "name_model": "Volvo", "type": "Truck", "max_load_capacity_kg": 5000, "acquisition_cost": 100000}, headers=mgr_h).json()["id"]
    v2 = requests.post(f"{BASE_URL}/vehicles", json={"registration_number": "DB-002", "name_model": "Scania", "type": "Bus", "max_load_capacity_kg": 3000, "acquisition_cost": 80000}, headers=mgr_h).json()["id"]

    d1 = requests.post(f"{BASE_URL}/drivers", json={"name": "Alice", "license_number": "DB-LIC-1", "license_category": "A", "license_expiry_date": "2030-01-01"}, headers=safety_h).json()["id"]
    d2 = requests.post(f"{BASE_URL}/drivers", json={"name": "Bob", "license_number": "DB-LIC-2", "license_category": "B", "license_expiry_date": "2020-01-01"}, headers=safety_h).json()["id"]

    # Trip 1: complete
    t1 = requests.post(f"{BASE_URL}/trips", json={"source": "A", "destination": "B", "vehicle_id": v1, "driver_id": d1, "cargo_weight_kg": 1000, "planned_distance_km": 300}, headers=mgr_h).json()["id"]
    requests.patch(f"{BASE_URL}/trips/{t1}/dispatch", headers=mgr_h)
    requests.patch(f"{BASE_URL}/trips/{t1}/complete", json={"final_odometer": 300, "fuel_consumed_liters": 40, "revenue": 5000}, headers=mgr_h)

    # Trip 2: complete
    t2 = requests.post(f"{BASE_URL}/trips", json={"source": "C", "destination": "D", "vehicle_id": v1, "driver_id": d1, "cargo_weight_kg": 800, "planned_distance_km": 200}, headers=mgr_h).json()["id"]
    requests.patch(f"{BASE_URL}/trips/{t2}/dispatch", headers=mgr_h)
    requests.patch(f"{BASE_URL}/trips/{t2}/complete", json={"final_odometer": 500, "fuel_consumed_liters": 30, "revenue": 3000}, headers=mgr_h)

    # Trip 3: cancel
    t3 = requests.post(f"{BASE_URL}/trips", json={"source": "E", "destination": "F", "vehicle_id": v1, "driver_id": d1, "cargo_weight_kg": 500, "planned_distance_km": 100}, headers=mgr_h).json()["id"]
    requests.patch(f"{BASE_URL}/trips/{t3}/cancel", headers=mgr_h)

    # Maintenance
    from datetime import datetime, timedelta
    sched = (datetime.now() + timedelta(days=5)).isoformat()
    m = requests.post(f"{BASE_URL}/maintenance", json={"vehicle_id": v1, "maintenance_type": "Preventive", "description": "Oil", "scheduled_date": sched, "estimated_cost": 500}, headers=mgr_h)
    mid = m.json()["id"]
    requests.patch(f"{BASE_URL}/maintenance/{mid}/start", json={"technician_notes": "go"}, headers=mgr_h)
    requests.patch(f"{BASE_URL}/maintenance/{mid}/complete", json={"actual_cost": 450, "technician_notes": "done"}, headers=mgr_h)

    # ═══ Dashboard Tests ═══
    # 1. Vehicle Overview
    r = requests.get(f"{BASE_URL}/dashboard/overview", headers=mgr_h)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["total_vehicles"] == 2
    assert d["available"] == 2
    print(f"✓ Vehicle Overview (total={d['total_vehicles']}, available={d['available']})")

    # 2. Driver Overview
    r = requests.get(f"{BASE_URL}/dashboard/drivers", headers=mgr_h)
    assert r.status_code == 200
    d = r.json()
    assert d["total_drivers"] == 2
    assert d["expired_licenses"] == 1  # Bob has expired license
    print(f"✓ Driver Overview (total={d['total_drivers']}, expired={d['expired_licenses']})")

    # 3. Trip Overview
    r = requests.get(f"{BASE_URL}/dashboard/trips", headers=mgr_h)
    assert r.status_code == 200
    d = r.json()
    assert d["completed"] == 2
    assert d["cancelled"] == 1
    assert d["todays_trips"] >= 3
    print(f"✓ Trip Overview (completed={d['completed']}, cancelled={d['cancelled']}, today={d['todays_trips']})")

    # 4. Maintenance Overview
    r = requests.get(f"{BASE_URL}/dashboard/maintenance", headers=mgr_h)
    assert r.status_code == 200
    d = r.json()
    assert d["completed"] == 1
    print(f"✓ Maintenance Overview (completed={d['completed']})")

    # 5. Financial Overview
    r = requests.get(f"{BASE_URL}/dashboard/finance", headers=mgr_h)
    assert r.status_code == 200
    d = r.json()
    assert d["total_revenue"] == 8000
    assert d["maintenance_cost"] == 450
    assert d["profit"] > 0
    print(f"✓ Financial Overview (revenue=${d['total_revenue']}, profit=${d['profit']})")

    # 6. Fleet KPIs
    r = requests.get(f"{BASE_URL}/dashboard/kpis", headers=mgr_h)
    assert r.status_code == 200
    d = r.json()
    assert d["total_completed_trips"] == 2
    assert d["fleet_utilization_pct"] > 0
    assert d["fuel_efficiency_km_per_l"] > 0
    print(f"✓ Fleet KPIs (utilization={d['fleet_utilization_pct']}%, efficiency={d['fuel_efficiency_km_per_l']} km/L)")

    # 7. Recent Trips
    r = requests.get(f"{BASE_URL}/dashboard/recent-trips", headers=mgr_h)
    assert r.status_code == 200
    assert len(r.json()["items"]) == 3
    print(f"✓ Recent Trips ({len(r.json()['items'])} items)")

    # 8. Recent Maintenance
    r = requests.get(f"{BASE_URL}/dashboard/recent-maintenance", headers=mgr_h)
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1
    print(f"✓ Recent Maintenance ({len(r.json()['items'])} items)")

    # 9. RBAC: Financial Analyst allowed
    r = requests.get(f"{BASE_URL}/dashboard/overview", headers=finance_h)
    assert r.status_code == 200
    print("✓ RBAC: Financial Analyst allowed")

    # 10. RBAC: Safety Officer allowed
    r = requests.get(f"{BASE_URL}/dashboard/kpis", headers=safety_h)
    assert r.status_code == 200
    print("✓ RBAC: Safety Officer allowed")

    # 11. RBAC: Driver blocked
    r = requests.get(f"{BASE_URL}/dashboard/overview", headers=driver_h)
    assert r.status_code == 403
    print("✓ RBAC: Driver blocked (403)")

    # 12. Swagger
    r = requests.get(f"{BASE_URL}/docs")
    assert r.status_code == 200
    print("✓ Swagger accessible")

    print("\n✅ All Phase 8 Dashboard tests pass!")

if __name__ == "__main__":
    run()
