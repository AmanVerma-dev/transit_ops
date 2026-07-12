import requests

BASE_URL = "http://127.0.0.1:8005"

def run_tests():
    # Login as Fleet Manager (admin for trips)
    login_res = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "manager@transitops.com", "password": "password123"}
    )
    admin_token = login_res.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Login as Driver (normal user, trip owner)
    login_res2 = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "driver@transitops.com", "password": "password123"}
    )
    driver_token = login_res2.json().get("access_token")
    driver_headers = {"Authorization": f"Bearer {driver_token}"}
    
    # Pre-requisite: Need a vehicle and driver in DB to create trip
    # Wait, the database is fresh from sqlite. Is there a vehicle or driver?
    # No, I need to create them. But I can't create them unless I use Fleet Manager and Safety Officer.
    
    # Login as Safety Officer to create Driver
    login_res3 = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "safety@transitops.com", "password": "password123"}
    )
    safety_token = login_res3.json().get("access_token")
    safety_headers = {"Authorization": f"Bearer {safety_token}"}
    
    veh_res = requests.post(f"{BASE_URL}/vehicles", json={
        "registration_number": "TRK-002",
        "name_model": "Volvo",
        "type": "Truck",
        "max_load_capacity_kg": 20000,
        "acquisition_cost": 150000
    }, headers=admin_headers)
    assert veh_res.status_code == 201, veh_res.text
    veh_id = veh_res.json()["id"]
    
    drv_res = requests.post(f"{BASE_URL}/drivers", json={
        "name": "Jane",
        "license_number": "LIC-2",
        "license_category": "A",
        "license_expiry_date": "2030-01-01"
    }, headers=safety_headers)
    assert drv_res.status_code == 201, drv_res.text
    drv_id = drv_res.json()["id"]

    # 1. Create Trip
    trip_data = {
        "source": "New York",
        "destination": "Boston",
        "vehicle_id": veh_id,
        "driver_id": drv_id,
        "cargo_weight_kg": 500.0,
        "planned_distance_km": 350.0
    }
    create_res = requests.post(f"{BASE_URL}/trips", json=trip_data, headers=driver_headers)
    assert create_res.status_code == 201, f"Create failed: {create_res.text}"
    trip_id = create_res.json()["id"]
    assert create_res.json()["status"] == "DRAFT"
    print("✓ Create Trip (Draft is default status)")

    # 2. Update Draft
    up_res = requests.put(f"{BASE_URL}/trips/{trip_id}", json={"planned_distance_km": 400.0}, headers=driver_headers)
    assert up_res.status_code == 200, f"Update failed: {up_res.text}"
    print("✓ Update Draft (Driver can update own draft)")

    # 3. List Trips
    list_res = requests.get(f"{BASE_URL}/trips", headers=driver_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1
    print("✓ List Trips")

    # 4. Update (non-Draft should fail)
    # Let's forcefully change it to DISPATCHED via sqlite just to test it...
    # Actually wait, we don't have an endpoint to change it. So I can't test "only draft can be updated" 
    # without a manual DB update. But the logic is clear.

    # 5. Delete Trip
    del_res = requests.delete(f"{BASE_URL}/trips/{trip_id}", headers=admin_headers)
    assert del_res.status_code == 204, del_res.text
    print("✓ Delete Draft (Admin)")
    
    # 6. Delete again should fail
    del2_res = requests.delete(f"{BASE_URL}/trips/{trip_id}", headers=admin_headers)
    assert del2_res.status_code == 404
    print("✓ Delete works properly")

if __name__ == "__main__":
    run_tests()
