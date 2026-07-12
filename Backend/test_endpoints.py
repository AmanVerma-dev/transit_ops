import requests

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    res = requests.get(f"{BASE_URL}/health")
    print("Health:", res.status_code, res.json())

def test_login():
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": "manager@transitops.com", "password": "password123"})
    print("Login:", res.status_code, res.json())
    return res.json().get("access_token")

def test_me(token):
    res = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
    print("Me:", res.status_code, res.json())

if __name__ == "__main__":
    test_health()
    token = test_login()
    if token:
        test_me(token)
