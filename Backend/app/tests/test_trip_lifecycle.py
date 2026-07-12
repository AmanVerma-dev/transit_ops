import requests

BASE_URL = "http://127.0.0.1:8006"

def run_tests():
    # Login as Fleet Manager
    login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "manager@transitops.com", "password": "password123"})
    admin_headers = {"Authorization": f"Bearer {login_res.json().get('access_token')}"}
    
    # Login as Safety Officer to create Driver
    login_res_safety = requests.post(f"{BASE_URL}/auth/login", data={"username": "safety@transitops.com", "password": "password123"})
    safety_headers = {"Authorization": f"Bearer {login_res_safety.json().get('access_token')}"}
    
    veh_res = requests.post(f"{BASE_URL}/vehicles", json={"registration_number": "TRK-005", "name_model": "Volvo", "type": "Truck", "max_load_capacity_kg": 20000, "acquisition_cost": 150000}, headers=admin_headers)
    veh_id = veh_res.json()["id"]
    
    drv_res = requests.post(f"{BASE_URL}/drivers", json={"name": "Jane", "license_number": "LIC-5", "license_category": "A", "license_expiry_date": "2030-01-01"}, headers=safety_headers)
    drv_id = drv_res.json()["id"]

    # 1. Create Trip
    trip_data = {"source": "New York", "destination": "Boston", "vehicle_id": veh_id, "driver_id": drv_id, "cargo_weight_kg": 500.0, "planned_distance_km": 350.0}
    create_res = requests.post(f"{BASE_URL}/trips", json=trip_data, headers=admin_headers)
    assert create_res.status_code == 201, create_res.text
    trip_id = create_res.json()["id"]
    
    # 2. Dispatch
    dispatch_res = requests.patch(f"{BASE_URL}/trips/{trip_id}/dispatch", headers=admin_headers)
    assert dispatch_res.status_code == 200, dispatch_res.text
    assert dispatch_res.json()["status"] == "DISPATCHED"
    assert dispatch_res.json()["dispatched_at"] is not None
    print("✓ Dispatch works")

    # 3. Invalid Transition (Dispatch again)
    dispatch_err = requests.patch(f"{BASE_URL}/trips/{trip_id}/dispatch", headers=admin_headers)
    assert dispatch_err.status_code == 409
    print("✓ Invalid transitions return 409")

    # 4. Complete
    complete_res = requests.patch(f"{BASE_URL}/trips/{trip_id}/complete", json={"final_odometer": 360, "fuel_consumed_liters": 50, "revenue": 1000}, headers=admin_headers)
    assert complete_res.status_code == 200, complete_res.text
    assert complete_res.json()["status"] == "COMPLETED"
    assert complete_res.json()["completed_at"] is not None
    assert complete_res.json()["revenue"] == 1000
    print("✓ Complete works")

    # 5. Cancel (from Complete should fail)
    cancel_err = requests.patch(f"{BASE_URL}/trips/{trip_id}/cancel", headers=admin_headers)
    assert cancel_err.status_code == 409
    print("✓ Cancel from COMPLETED fails with 409")
    
    # 6. Create & Cancel
    create_res2 = requests.post(f"{BASE_URL}/trips", json=trip_data, headers=admin_headers)
    trip_id2 = create_res2.json()["id"]
    cancel_res = requests.patch(f"{BASE_URL}/trips/{trip_id2}/cancel", headers=admin_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"
    print("✓ Cancel works")

if __name__ == "__main__":
    run_tests()
