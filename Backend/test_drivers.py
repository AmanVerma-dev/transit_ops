import requests

BASE_URL = "http://127.0.0.1:8004"

def run_tests():
    # Login as Safety Officer (admin for drivers)
    login_res = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "safety@transitops.com", "password": "password123"}
    )
    admin_token = login_res.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Login as Driver (normal user, read only)
    login_res2 = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "driver@transitops.com", "password": "password123"}
    )
    user_token = login_res2.json().get("access_token")
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # 1. Create Driver
    driver_data = {
        "name": "Jane Doe",
        "license_number": "LIC-12345",
        "license_category": "Class A",
        "license_expiry_date": "2030-01-01"
    }
    create_res = requests.post(f"{BASE_URL}/drivers", json=driver_data, headers=admin_headers)
    assert create_res.status_code == 201, f"Create failed: {create_res.text}"
    driver_id = create_res.json()["id"]
    print("✓ Create Driver")

    # 2. Duplicate License
    dup_res = requests.post(f"{BASE_URL}/drivers", json=driver_data, headers=admin_headers)
    assert dup_res.status_code == 409, "Duplicate did not return 409"
    print("✓ Duplicate License returns 409")

    # 3. Update Driver
    up_res = requests.put(f"{BASE_URL}/drivers/{driver_id}", json={"safety_score": 95.5}, headers=admin_headers)
    assert up_res.status_code == 200, f"Update failed: {up_res.text}"
    print("✓ Update Driver")

    # 4. Get Driver (User)
    get_res = requests.get(f"{BASE_URL}/drivers/{driver_id}", headers=user_headers)
    assert get_res.status_code == 200
    print("✓ Get Driver (Read endpoint works for authenticated users)")

    # 5. List Drivers
    list_res = requests.get(f"{BASE_URL}/drivers", headers=user_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1
    print("✓ List Drivers")

    # 6. Filtering
    list_res2 = requests.get(f"{BASE_URL}/drivers?search_name=Jane", headers=user_headers)
    assert list_res2.json()["total"] == 1
    print("✓ Filtering")

    # 7. Unauthorized / Forbidden Access
    fail_create = requests.post(f"{BASE_URL}/drivers", json=driver_data, headers=user_headers)
    assert fail_create.status_code == 403, "Driver shouldn't be able to create driver"
    print("✓ Forbidden Access (Safety Officer permissions work)")

    # 8. Suspend Driver
    suspend_res = requests.patch(f"{BASE_URL}/drivers/{driver_id}/suspend", headers=admin_headers)
    assert suspend_res.status_code == 200
    assert suspend_res.json()["status"] == "SUSPENDED"
    print("✓ Suspend Driver")

    # 9. Reinstate Driver
    reinstate_res = requests.patch(f"{BASE_URL}/drivers/{driver_id}/reinstate", headers=admin_headers)
    assert reinstate_res.status_code == 200
    assert reinstate_res.json()["status"] == "AVAILABLE"
    print("✓ Reinstate Driver")

    # 10. Soft Delete
    del_res = requests.delete(f"{BASE_URL}/drivers/{driver_id}", headers=admin_headers)
    assert del_res.status_code == 204
    list_res3 = requests.get(f"{BASE_URL}/drivers", headers=user_headers)
    assert list_res3.json()["total"] == 0
    print("✓ Soft Delete works")

if __name__ == "__main__":
    run_tests()
