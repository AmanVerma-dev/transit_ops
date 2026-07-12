import requests

BASE_URL = "http://127.0.0.1:8007"

def run_tests():
    # Login
    login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "manager@transitops.com", "password": "password123"})
    admin_headers = {"Authorization": f"Bearer {login_res.json().get('access_token')}"}
    
    login_res_safety = requests.post(f"{BASE_URL}/auth/login", data={"username": "safety@transitops.com", "password": "password123"})
    safety_headers = {"Authorization": f"Bearer {login_res_safety.json().get('access_token')}"}
    
    # 1. Setup Vehicle & Driver
    veh_res = requests.post(f"{BASE_URL}/vehicles", json={"registration_number": "TRK-PH4C", "name_model": "Volvo", "type": "Truck", "max_load_capacity_kg": 2000, "acquisition_cost": 150000}, headers=admin_headers)
    veh_id = veh_res.json()["id"]
    
    drv_res = requests.post(f"{BASE_URL}/drivers", json={"name": "Jane", "license_number": "LIC-PH4C", "license_category": "A", "license_expiry_date": "2030-01-01"}, headers=safety_headers)
    drv_id = drv_res.json()["id"]

    # 2. Test Invalid Cargo (Create)
    trip_data_heavy = {"source": "New York", "destination": "Boston", "vehicle_id": veh_id, "driver_id": drv_id, "cargo_weight_kg": 2500.0, "planned_distance_km": 350.0}
    heavy_res = requests.post(f"{BASE_URL}/trips", json=trip_data_heavy, headers=admin_headers)
    assert heavy_res.status_code == 422, heavy_res.text
    print("✓ Cargo Too Heavy caught on Create")

    # 3. Create Valid Trip
    trip_data = {"source": "New York", "destination": "Boston", "vehicle_id": veh_id, "driver_id": drv_id, "cargo_weight_kg": 1500.0, "planned_distance_km": 350.0}
    create_res = requests.post(f"{BASE_URL}/trips", json=trip_data, headers=admin_headers)
    assert create_res.status_code == 201
    trip_id = create_res.json()["id"]

    # 4. Expired License Driver
    drv_exp = requests.post(f"{BASE_URL}/drivers", json={"name": "Expired", "license_number": "LIC-EXP", "license_category": "A", "license_expiry_date": "2020-01-01"}, headers=safety_headers)
    drv_exp_id = drv_exp.json()["id"]
    trip_exp_data = {"source": "New York", "destination": "Boston", "vehicle_id": veh_id, "driver_id": drv_exp_id, "cargo_weight_kg": 1500.0, "planned_distance_km": 350.0}
    trip_exp_res = requests.post(f"{BASE_URL}/trips", json=trip_exp_data, headers=admin_headers)
    dispatch_exp_res = requests.patch(f"{BASE_URL}/trips/{trip_exp_res.json()['id']}/dispatch", headers=admin_headers)
    assert dispatch_exp_res.status_code == 422, dispatch_exp_res.text
    print("✓ Dispatch caught Expired License")

    # 5. Dispatch
    dispatch_res = requests.patch(f"{BASE_URL}/trips/{trip_id}/dispatch", headers=admin_headers)
    assert dispatch_res.status_code == 200

    # 6. Check Vehicle/Driver Status
    veh_check = requests.get(f"{BASE_URL}/vehicles/{veh_id}", headers=admin_headers)
    assert veh_check.json()["status"] == "ON_TRIP"
    drv_check = requests.get(f"{BASE_URL}/drivers/{drv_id}", headers=admin_headers)
    assert drv_check.json()["status"] == "ON_TRIP"
    print("✓ Dispatch updates Vehicle/Driver status")

    # 7. Check Vehicle/Driver Busy
    trip_busy = requests.post(f"{BASE_URL}/trips", json=trip_data, headers=admin_headers)
    dispatch_busy = requests.patch(f"{BASE_URL}/trips/{trip_busy.json()['id']}/dispatch", headers=admin_headers)
    assert dispatch_busy.status_code == 409
    print("✓ Dispatch caught Busy Vehicle/Driver")

    # 8. Complete (Invalid Odometer)
    comp_fail = requests.patch(f"{BASE_URL}/trips/{trip_id}/complete", json={"final_odometer": -10, "fuel_consumed_liters": 50, "revenue": 1000}, headers=admin_headers)
    assert comp_fail.status_code == 422
    print("✓ Complete caught Invalid Odometer")

    # 9. Complete
    comp = requests.patch(f"{BASE_URL}/trips/{trip_id}/complete", json={"final_odometer": 400, "fuel_consumed_liters": 50, "revenue": 1000}, headers=admin_headers)
    assert comp.status_code == 200
    veh_check2 = requests.get(f"{BASE_URL}/vehicles/{veh_id}", headers=admin_headers)
    assert veh_check2.json()["status"] == "AVAILABLE"
    assert veh_check2.json()["odometer_km"] == 400
    drv_check2 = requests.get(f"{BASE_URL}/drivers/{drv_id}", headers=admin_headers)
    assert drv_check2.json()["status"] == "AVAILABLE"
    print("✓ Complete updates Odometer and frees Vehicle/Driver")

    print("✓ All Phase 4C business rules pass")

if __name__ == "__main__":
    run_tests()
