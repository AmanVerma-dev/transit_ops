import requests

BASE_URL = "http://127.0.0.1:8003"

def run_tests():
    # Login as Fleet Manager (admin)
    login_res = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "manager@transitops.com", "password": "password123"}
    )
    admin_token = login_res.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Login as Driver (normal user)
    login_res2 = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "driver@transitops.com", "password": "password123"}
    )
    user_token = login_res2.json().get("access_token")
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # 1. Create Vehicle
    veh_data = {
        "registration_number": "TRK-001",
        "name_model": "Volvo FH16",
        "type": "Heavy Truck",
        "max_load_capacity_kg": 20000.0,
        "acquisition_cost": 150000.0,
        "region": "North"
    }
    create_res = requests.post(f"{BASE_URL}/vehicles", json=veh_data, headers=admin_headers)
    assert create_res.status_code == 201, f"Create failed: {create_res.text}"
    veh_id = create_res.json()["id"]
    print("✓ Create Vehicle")

    # 2. Duplicate Registration
    dup_res = requests.post(f"{BASE_URL}/vehicles", json=veh_data, headers=admin_headers)
    assert dup_res.status_code == 409, "Duplicate did not return 409"
    print("✓ Duplicate Registration returns 409")

    # 3. Update Vehicle
    up_res = requests.patch(f"{BASE_URL}/vehicles/{veh_id}", json={"odometer_km": 150.5}, headers=admin_headers)
    # wait, I implemented PUT, let me test PUT
    up_res = requests.put(f"{BASE_URL}/vehicles/{veh_id}", json={"odometer_km": 150.5}, headers=admin_headers)
    assert up_res.status_code == 200, f"Update failed: {up_res.text}"
    print("✓ Update Vehicle")

    # 4. Get Vehicle (User)
    get_res = requests.get(f"{BASE_URL}/vehicles/{veh_id}", headers=user_headers)
    assert get_res.status_code == 200
    print("✓ Get Vehicle (Read endpoint works for authenticated users)")

    # 5. List Vehicles
    list_res = requests.get(f"{BASE_URL}/vehicles", headers=user_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1
    print("✓ List Vehicles")

    # 6. Filtering
    list_res2 = requests.get(f"{BASE_URL}/vehicles?region=South", headers=user_headers)
    assert list_res2.json()["total"] == 0
    print("✓ Filtering")

    # 7. Unauthorized / Forbidden Access
    fail_create = requests.post(f"{BASE_URL}/vehicles", json=veh_data, headers=user_headers)
    assert fail_create.status_code == 403, "Driver shouldn't be able to create vehicle"
    print("✓ Forbidden Access (Fleet Manager permissions work)")

    # 8. Retire Vehicle
    retire_res = requests.patch(f"{BASE_URL}/vehicles/{veh_id}/retire", headers=admin_headers)
    assert retire_res.status_code == 200
    assert retire_res.json()["status"] == "RETIRED"
    print("✓ Retire Vehicle")

    # 9. Soft Delete
    del_res = requests.delete(f"{BASE_URL}/vehicles/{veh_id}", headers=admin_headers)
    assert del_res.status_code == 204
    list_res3 = requests.get(f"{BASE_URL}/vehicles", headers=user_headers)
    assert list_res3.json()["total"] == 0
    print("✓ Soft Delete works")

if __name__ == "__main__":
    run_tests()
