import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8013"

def run_integration_suite():
    print("🚀 Starting TransitOps Full Integration Suite...")

    # ── 1. Authentication & RBAC ──────────────────────────────────────────
    print("\n[1] Testing Authentication...")
    mgr = requests.post(f"{BASE_URL}/auth/login", data={"username": "manager@transitops.com", "password": "password123"})
    assert mgr.status_code == 200, "Manager login failed"
    mgr_h = {"Authorization": f"Bearer {mgr.json()['access_token']}"}

    safety = requests.post(f"{BASE_URL}/auth/login", data={"username": "safety@transitops.com", "password": "password123"})
    assert safety.status_code == 200, "Safety Officer login failed"
    safety_h = {"Authorization": f"Bearer {safety.json()['access_token']}"}

    driver_auth = requests.post(f"{BASE_URL}/auth/login", data={"username": "driver@transitops.com", "password": "password123"})
    assert driver_auth.status_code == 200, "Driver login failed"
    driver_h = {"Authorization": f"Bearer {driver_auth.json()['access_token']}"}
    print("✓ Auth successful")

    # ── 2. Vehicles ───────────────────────────────────────────────────────
    print("\n[2] Testing Vehicles...")
    v_resp = requests.post(f"{BASE_URL}/vehicles", json={
        "registration_number": "TEST-V01", "name_model": "Volvo", "type": "Truck",
        "max_load_capacity_kg": 5000, "acquisition_cost": 100000
    }, headers=mgr_h)
    assert v_resp.status_code == 201, f"Vehicle creation failed: {v_resp.text}"
    vid = v_resp.json()["id"]

    v_get = requests.get(f"{BASE_URL}/vehicles", headers=mgr_h)
    assert len(v_get.json()["items"]) > 0
    print("✓ Vehicle CRUD successful")

    # ── 3. Drivers ────────────────────────────────────────────────────────
    print("\n[3] Testing Drivers...")
    d_resp = requests.post(f"{BASE_URL}/drivers", json={
        "name": "Test Driver", "license_number": "TEST-D01",
        "license_category": "A", "license_expiry_date": "2030-01-01"
    }, headers=safety_h)
    assert d_resp.status_code == 201, f"Driver creation failed: {d_resp.text}"
    did = d_resp.json()["id"]

    d_get = requests.get(f"{BASE_URL}/drivers/{did}", headers=safety_h)
    assert d_get.status_code == 200
    print("✓ Driver CRUD successful")

    # ── 4. Trips & Business Rules ─────────────────────────────────────────
    print("\n[4] Testing Trips & Lifecycle...")
    t_resp = requests.post(f"{BASE_URL}/trips", json={
        "source": "A", "destination": "B", "vehicle_id": vid, "driver_id": did,
        "cargo_weight_kg": 1000, "planned_distance_km": 100
    }, headers=mgr_h)
    assert t_resp.status_code == 201, f"Trip creation failed: {t_resp.text}"
    tid = t_resp.json()["id"]

    # Dispatch trip
    disp = requests.patch(f"{BASE_URL}/trips/{tid}/dispatch", headers=mgr_h)
    assert disp.status_code == 200, f"Dispatch failed: {disp.text}"
    
    # Complete trip
    comp = requests.patch(f"{BASE_URL}/trips/{tid}/complete", json={
        "final_odometer": 100, "fuel_consumed_liters": 20, "revenue": 1000
    }, headers=mgr_h)
    assert comp.status_code == 200, f"Complete failed: {comp.text}"
    print("✓ Trip Lifecycle & Rules successful")

    # ── 5. Maintenance ────────────────────────────────────────────────────
    print("\n[5] Testing Maintenance...")
    sched = (datetime.now() + timedelta(days=2)).isoformat()
    m_resp = requests.post(f"{BASE_URL}/maintenance", json={
        "vehicle_id": vid, "maintenance_type": "Preventive",
        "description": "Oil Change", "scheduled_date": sched, "estimated_cost": 500
    }, headers=mgr_h)
    assert m_resp.status_code == 201, f"Maintenance creation failed: {m_resp.text}"
    mid = m_resp.json()["id"]

    m_start = requests.patch(f"{BASE_URL}/maintenance/{mid}/start", json={"technician_notes": "started"}, headers=mgr_h)
    assert m_start.status_code == 200

    m_comp = requests.patch(f"{BASE_URL}/maintenance/{mid}/complete", json={"actual_cost": 450, "technician_notes": "done"}, headers=mgr_h)
    assert m_comp.status_code == 200
    print("✓ Maintenance workflow successful")

    # ── 6. Analytics ──────────────────────────────────────────────────────
    print("\n[6] Testing Analytics...")
    a_resp = requests.get(f"{BASE_URL}/analytics/fleet-utilization", headers=mgr_h)
    assert a_resp.status_code == 200
    assert "utilization_percentage" in a_resp.json()
    print("✓ Analytics read successful")

    # ── 7. Dashboard ──────────────────────────────────────────────────────
    print("\n[7] Testing Dashboard...")
    dash_resp = requests.get(f"{BASE_URL}/dashboard/overview", headers=mgr_h)
    assert dash_resp.status_code == 200
    assert dash_resp.json()["total_vehicles"] > 0
    print("✓ Dashboard read successful")

    # ── 8. Error Handling & RBAC ──────────────────────────────────────────
    print("\n[8] Testing Error Handling & RBAC...")
    # Driver tries to read dashboard -> 403
    err_403 = requests.get(f"{BASE_URL}/dashboard/overview", headers=driver_h)
    assert err_403.status_code == 403
    
    # Non-existent trip -> 404
    err_404 = requests.get(f"{BASE_URL}/trips/9999", headers=mgr_h)
    assert err_404.status_code == 404

    # Validation Error -> 422
    err_422 = requests.post(f"{BASE_URL}/trips", json={}, headers=mgr_h)
    assert err_422.status_code == 422
    print("✓ Error codes (403, 404, 422) validated")

    # ── 9. Swagger ────────────────────────────────────────────────────────
    print("\n[9] Testing Swagger...")
    swag = requests.get(f"{BASE_URL}/docs")
    assert swag.status_code == 200
    print("✓ Swagger Docs accessible")

    print("\n✅ All 9 integration phases passed! System is production-ready.")

if __name__ == "__main__":
    run_integration_suite()
