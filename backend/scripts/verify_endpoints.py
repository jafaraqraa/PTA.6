import requests
import sys

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("Testing Backend Endpoints...")

    # 1. Login to get token (Domain-less)
    login_data = {"email": "admin@system.com", "password": "admin123"}
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        response.raise_for_status()
        token = response.json()["access_token"]
        print("✓ Login successful")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Users
    try:
        response = requests.get(f"{BASE_URL}/users/", headers=headers)
        response.raise_for_status()
        print(f"✓ List Users successful: {len(response.json())} users found")
    except Exception as e:
        print(f"✗ List Users failed: {e}")

    # 3. Test Universities
    try:
        response = requests.get(f"{BASE_URL}/universities/", headers=headers)
        response.raise_for_status()
        print(f"✓ List Universities successful: {len(response.json())} universities found")
    except Exception as e:
        print(f"✗ List Universities failed: {e}")

    # 4. Test Subscriptions
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/", headers=headers)
        response.raise_for_status()
        print(f"✓ List Subscriptions successful: {len(response.json())} subscriptions found")
    except Exception as e:
        print(f"✗ List Subscriptions failed: {e}")

    # 5. Test Analytics
    try:
        response = requests.get(f"{BASE_URL}/analytics/", headers=headers)
        response.raise_for_status()
        print(f"✓ Analytics data retrieval successful: {response.json()}")
    except Exception as e:
        print(f"✗ Analytics data retrieval failed: {e}")

if __name__ == "__main__":
    test_endpoints()
