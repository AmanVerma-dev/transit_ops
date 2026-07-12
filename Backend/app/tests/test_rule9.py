import requests
BASE_URL = "http://127.0.0.1:8010"

def run():
    # Login as Fleet Manager
    mgr = requests.post(f"{BASE_URL}/auth/login", data={"username": "manager@transitops.com", "password": "password123"})
    mgr_h = {"Authorization": f"Bearer {mgr.json()['access_token']}"}

    # Login as Safety Officer (for driver creation)
    safety = requests.post(f"{BASE_URL}/auth/login", data={"username": "safety@transitops.com", "password": "password123"})
    safety_h = {"Authorization": f"Bearer {safety.json()['access_token']}"}

    # Create vehicle & driver
    v = requests.post(f"{BASE_URL}/vehicles", json={"registration_number": "R9-001", "name_model": "Volvo", "type": "Truck", "max_load_capacity_kg": 5000, "acquisition_cost": 100000}, headers=mgr_h)
    vid = v.json()["id"]

    d = requests.post(f"{BASE_URL}/drivers", json={"name": "TestDriver", "license_number": "R9-LIC", "license_category": "A", "license_expiry_date": "2030-01-01"}, headers=safety_h)
    did = d.json()["id"]

    # Schedule maintenance for this vehicle
    from datetime import datetime, timedelta
    sched = (datetime.now() + timedelta(days=5)).isoformat()
    m = requests.post(f"{BASE_URL}/maintenance", json={"vehicle_id": vid, "maintenance_type": "Preventive", "description": "Oil change", "scheduled_date": sched, "estimated_cost": 100}, headers=mgr_h)
    mid = m.json()["id"]
    assert m.status_code == 201, m.text

    # Create trip and try to dispatch — should be blocked by Rule 9
    t = requests.post(f"{BASE_URL}/trips", json={"source": "A", "destination": "B", "vehicle_id": vid, "driver_id": did, "cargo_weight_kg": 1000, "planned_distance_km": 200}, headers=mgr_h)
    tid = t.json()["id"]
    disp = requests.patch(f"{BASE_URL}/trips/{tid}/dispatch", headers=mgr_h)
    assert disp.status_code == 409, f"Expected 409, got {disp.status_code}: {disp.text}"
    assert "maintenance" in disp.json()["detail"].lower()
    print("✓ Rule 9: Dispatch blocked by SCHEDULED maintenance")

    # Cancel the maintenance
    cancel_m = requests.patch(f"{BASE_URL}/maintenance/{mid}/cancel", json={"reason": "Test"}, headers=mgr_h)
    assert cancel_m.status_code == 200

    # Now dispatch should succeed
    disp2 = requests.patch(f"{BASE_URL}/trips/{tid}/dispatch", headers=mgr_h)
    assert disp2.status_code == 200, f"Expected 200, got {disp2.status_code}: {disp2.text}"
    assert disp2.json()["status"] == "DISPATCHED"
    print("✓ Rule 9: Dispatch allowed after maintenance cancelled")

    # Complete trip to restore vehicle
    comp = requests.patch(f"{BASE_URL}/trips/{tid}/complete", json={"final_odometer": 300, "fuel_consumed_liters": 40, "revenue": 800}, headers=mgr_h)
    assert comp.status_code == 200
    print("✓ Complete works with all Phase 4C rules")

    # Test IN_PROGRESS maintenance also blocks dispatch
    t2 = requests.post(f"{BASE_URL}/trips", json={"source": "C", "destination": "D", "vehicle_id": vid, "driver_id": did, "cargo_weight_kg": 500, "planned_distance_km": 100}, headers=mgr_h)
    tid2 = t2.json()["id"]

    m2 = requests.post(f"{BASE_URL}/maintenance", json={"vehicle_id": vid, "maintenance_type": "Emergency", "description": "Brake fix", "scheduled_date": sched, "estimated_cost": 500}, headers=mgr_h)
    mid2 = m2.json()["id"]
    requests.patch(f"{BASE_URL}/maintenance/{mid2}/start", json={"technician_notes": "Starting"}, headers=mgr_h)

    disp3 = requests.patch(f"{BASE_URL}/trips/{tid2}/dispatch", headers=mgr_h)
    assert disp3.status_code == 409, f"Expected 409, got {disp3.status_code}: {disp3.text}"
    print("✓ Rule 9: Dispatch blocked by IN_PROGRESS maintenance")

    print("\n✅ All Rule 9 tests pass. Phase 4C is now 17/17.")

if __name__ == "__main__":
    run()
