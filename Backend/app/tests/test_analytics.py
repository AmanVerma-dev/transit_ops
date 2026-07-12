import requests
BASE_URL = "http://127.0.0.1:8011"

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

    # Seed data
    v1 = requests.post(f"{BASE_URL}/vehicles", json={"registration_number": "AN-001", "name_model": "Volvo", "type": "Truck", "max_load_capacity_kg": 5000, "acquisition_cost": 100000}, headers=mgr_h).json()["id"]
    v2 = requests.post(f"{BASE_URL}/vehicles", json={"registration_number": "AN-002", "name_model": "Scania", "type": "Bus", "max_load_capacity_kg": 3000, "acquisition_cost": 80000}, headers=mgr_h).json()["id"]

    d1 = requests.post(f"{BASE_URL}/drivers", json={"name": "Alice", "license_number": "AN-LIC-1", "license_category": "A", "license_expiry_date": "2030-01-01"}, headers=safety_h).json()["id"]
    d2 = requests.post(f"{BASE_URL}/drivers", json={"name": "Bob", "license_number": "AN-LIC-2", "license_category": "B", "license_expiry_date": "2030-01-01"}, headers=safety_h).json()["id"]

    # Create + dispatch + complete trips
    for i, (vid, did, cargo, dist, rev, fuel, odo) in enumerate([
        (v1, d1, 1000, 300, 5000, 40, 300),
        (v1, d1, 1500, 500, 8000, 70, 800),
        (v2, d2, 800, 200, 3000, 30, 200),
    ]):
        t = requests.post(f"{BASE_URL}/trips", json={"source": f"S{i}", "destination": f"D{i}", "vehicle_id": vid, "driver_id": did, "cargo_weight_kg": cargo, "planned_distance_km": dist}, headers=mgr_h)
        tid = t.json()["id"]
        requests.patch(f"{BASE_URL}/trips/{tid}/dispatch", headers=mgr_h)
        requests.patch(f"{BASE_URL}/trips/{tid}/complete", json={"final_odometer": odo, "fuel_consumed_liters": fuel, "revenue": rev}, headers=mgr_h)

    # Schedule + complete maintenance
    from datetime import datetime, timedelta
    sched = (datetime.now() + timedelta(days=5)).isoformat()
    m = requests.post(f"{BASE_URL}/maintenance", json={"vehicle_id": v1, "maintenance_type": "Preventive", "description": "Brakes", "scheduled_date": sched, "estimated_cost": 500}, headers=mgr_h)
    mid = m.json()["id"]
    requests.patch(f"{BASE_URL}/maintenance/{mid}/start", json={"technician_notes": "go"}, headers=mgr_h)
    requests.patch(f"{BASE_URL}/maintenance/{mid}/complete", json={"actual_cost": 450, "technician_notes": "done"}, headers=mgr_h)

    # ═══ Analytics ═══
    # 1. Fleet Utilization
    r = requests.get(f"{BASE_URL}/analytics/fleet-utilization", headers=mgr_h)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["total_vehicles"] == 2
    assert data["vehicles_with_completed_trips"] == 2
    assert data["utilization_percentage"] == 100.0
    assert data["total_completed_trips"] == 3
    print("✓ Fleet Utilization")

    # 2. Fuel Efficiency
    r = requests.get(f"{BASE_URL}/analytics/fuel-efficiency", headers=mgr_h)
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["fleet_avg_efficiency"] > 0
    print(f"✓ Fuel Efficiency (fleet avg: {data['fleet_avg_efficiency']} km/L)")

    # 3. Operational Cost
    r = requests.get(f"{BASE_URL}/analytics/operational-cost", headers=mgr_h)
    assert r.status_code == 200
    data = r.json()
    assert data["total_maintenance_cost"] == 450
    assert data["total_cost"] > 0
    print(f"✓ Operational Cost (total: ${data['total_cost']})")

    # 4. Vehicle ROI
    r = requests.get(f"{BASE_URL}/analytics/vehicle-roi", headers=mgr_h)
    assert r.status_code == 200
    data = r.json()
    assert data["fleet_total_revenue"] == 16000
    assert data["fleet_net_roi"] > 0
    print(f"✓ Vehicle ROI (fleet net: ${data['fleet_net_roi']})")

    # 5. Trip Summary
    r = requests.get(f"{BASE_URL}/analytics/trip-summary", headers=mgr_h)
    assert r.status_code == 200
    data = r.json()
    assert data["completed_trips"] == 3
    assert data["average_revenue"] > 0
    print(f"✓ Trip Summary (avg revenue: ${data['average_revenue']})")

    # 6. Filter by vehicle
    r = requests.get(f"{BASE_URL}/analytics/fuel-efficiency?vehicle_id={v1}", headers=mgr_h)
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1
    print("✓ Filtering by vehicle_id")

    # 7. RBAC — Financial Analyst can access
    r = requests.get(f"{BASE_URL}/analytics/fleet-utilization", headers=finance_h)
    assert r.status_code == 200
    print("✓ RBAC: Financial Analyst allowed")

    # 8. RBAC — Safety Officer can access
    r = requests.get(f"{BASE_URL}/analytics/trip-summary", headers=safety_h)
    assert r.status_code == 200
    print("✓ RBAC: Safety Officer allowed")

    # 9. RBAC — Driver blocked
    r = requests.get(f"{BASE_URL}/analytics/fleet-utilization", headers=driver_h)
    assert r.status_code == 403
    print("✓ RBAC: Driver blocked (403)")

    # 10. CSV Export — Trips
    r = requests.get(f"{BASE_URL}/reports/export/trips", headers=mgr_h)
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    lines = r.text.strip().split("\n")
    assert len(lines) == 4  # header + 3 trips
    print("✓ CSV Export: Trips")

    # 11. CSV Export — Fuel
    r = requests.get(f"{BASE_URL}/reports/export/fuel", headers=mgr_h)
    assert r.status_code == 200
    lines = r.text.strip().split("\n")
    assert len(lines) >= 4  # header + fuel logs
    print("✓ CSV Export: Fuel")

    # 12. CSV Export — Maintenance
    r = requests.get(f"{BASE_URL}/reports/export/maintenance", headers=mgr_h)
    assert r.status_code == 200
    lines = r.text.strip().split("\n")
    assert len(lines) >= 2
    print("✓ CSV Export: Maintenance")

    # 13. CSV RBAC — Driver blocked
    r = requests.get(f"{BASE_URL}/reports/export/trips", headers=driver_h)
    assert r.status_code == 403
    print("✓ CSV RBAC: Driver blocked")

    # 14. Swagger
    r = requests.get(f"{BASE_URL}/docs")
    assert r.status_code == 200
    print("✓ Swagger accessible")

    print("\n✅ All Phase 7 tests pass!")

if __name__ == "__main__":
    run()
