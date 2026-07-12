import requests
import json
import time

BASE_URL = "http://127.0.0.1:8002"

def run_tests():
    reg_res = requests.post(
        f"{BASE_URL}/auth/register",
        json={"name": "Test User", "email": "testdriver2@transitops.com", "password": "password123"}
    )
    if reg_res.status_code == 201:
        print("Register: SUCCESS")
    elif reg_res.status_code == 400 and "already exists" in reg_res.text:
        print("Register: Already Exists (SUCCESS)")
    else:
        print("Register: FAILED", reg_res.status_code, reg_res.text)

    login_res = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "testdriver2@transitops.com", "password": "password123"}
    )
    if login_res.status_code == 200:
        token = login_res.json()["access_token"]
        print("Login: SUCCESS")
    else:
        print("Login: FAILED", login_res.status_code)
        return

    me_res = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    if me_res.status_code == 200:
        print("Me: SUCCESS. Role ID:", me_res.json()["role_id"])
    else:
        print("Me: FAILED", me_res.status_code)

    inv_res = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}INVALID"}
    )
    if inv_res.status_code == 401 and "WWW-Authenticate" in inv_res.headers:
        print("Invalid Token: SUCCESS (401)")
    else:
        print("Invalid Token: FAILED", inv_res.status_code)

    miss_res = requests.get(f"{BASE_URL}/auth/me")
    if miss_res.status_code == 401:
        print("Missing Token: SUCCESS (401)")
    else:
        print("Missing Token: FAILED", miss_res.status_code)

if __name__ == "__main__":
    run_tests()
