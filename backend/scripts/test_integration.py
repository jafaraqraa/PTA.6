import asyncio
import httpx
import sys
import os

# Base URL
BASE_URL = "http://127.0.0.1:8000"

async def test_login():
    print("Testing Login Flow...")
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # 1. Test Login with Najah Domain
        print("Login with najah domain...")
        response = await client.post(
            "/auth/login?domain=najah",
            json={"email": "student@najah.com", "password": "123456"}
        )
        if response.status_code != 200:
            print(f"FAILED: student login failed: {response.text}")
            return
        token = response.json()["access_token"]
        print("SUCCESS: Logged in student@najah.com")

        # 2. Test Login with Hebron Domain (should fail for najah user)
        print("Login with hebron domain for najah user...")
        response = await client.post(
            "/auth/login?domain=hebron",
            json={"email": "student@najah.com", "password": "123456"}
        )
        if response.status_code == 403:
            print("SUCCESS: Correctly denied najah user on hebron domain")
        else:
            print(f"FAILED: Expected 403, got {response.status_code}: {response.text}")

        # 3. Test Super Admin login
        print("Login as super admin...")
        response = await client.post(
            "/auth/login?domain=najah",
            json={"email": "admin@system.com", "password": "admin123"}
        )
        if response.status_code == 200:
            print("SUCCESS: Logged in super admin")
        else:
            print(f"FAILED: Super admin login failed: {response.text}")

async def test_session_isolation():
    print("\nTesting Session Isolation...")
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Login student
        response = await client.post(
            "/auth/login?domain=najah",
            json={"email": "student@najah.com", "password": "123456"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Start session on najah domain
        print("Starting session on najah domain...")
        response = await client.post("/sessions/startSession?domain=najah", headers=headers)
        if response.status_code == 200:
            print("SUCCESS: Session started for student on najah domain")
        else:
            print(f"FAILED: Start session failed: {response.text}")

        # Try to start session on hebron domain with same token
        print("Starting session on hebron domain with najah student token...")
        response = await client.post("/sessions/startSession?domain=hebron", headers=headers)
        if response.status_code == 403:
            print("SUCCESS: Correctly denied cross-university session start")
        else:
            print(f"FAILED: Expected 403, got {response.status_code}: {response.text}")

if __name__ == "__main__":
    import uvicorn
    import multiprocessing
    import time

    # Run the tests
    async def run_tests():
        # Wait for server to start
        time.sleep(2)
        try:
            await test_login()
            await test_session_isolation()
        except Exception as e:
            print(f"Error during tests: {e}")

    # Helper function to start uvicorn
    def start_server():
        # Set PYTHONPATH to include backend
        backend_path = os.path.join(os.getcwd(), "backend")
        sys.path.append(backend_path)
        os.chdir(backend_path)
        from app.main import app
        uvicorn.run(app, host="127.0.0.1", port=8000)

    # Start server in a separate process
    server_process = multiprocessing.Process(target=start_server)
    server_process.start()

    # Run async tests
    try:
        asyncio.run(run_tests())
    finally:
        # Stop the server
        server_process.terminate()
        server_process.join()
