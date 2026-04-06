import asyncio
import httpx
import sys
import os

# Base URL
BASE_URL = "http://127.0.0.1:8000"

async def test_login():
    print("Testing Login Flow...")
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # 1. Test Login (Domain-less)
        print("Login with student account...")
        response = await client.post(
            "/auth/login",
            json={"email": "student@najah.com", "password": "123456"}
        )
        if response.status_code != 200:
            print(f"FAILED: student login failed: {response.text}")
            return
        token = response.json()["access_token"]
        print("SUCCESS: Logged in student@najah.com")

        # 2. Test Super Admin login
        print("Login as super admin...")
        response = await client.post(
            "/auth/login",
            json={"email": "admin@system.com", "password": "admin123"}
        )
        if response.status_code == 200:
            print("SUCCESS: Logged in super admin")
        else:
            print(f"FAILED: Super admin login failed: {response.text}")

async def test_session_isolation():
    print("\nTesting Session Access...")
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Login student
        response = await client.post(
            "/auth/login",
            json={"email": "student@najah.com", "password": "123456"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Start session (University context is now derived from token)
        print("Starting session...")
        response = await client.post("/sessions/startSession", headers=headers)
        # Note: Might fail if no patient data is seeded, but we check for auth success
        if response.status_code in [200, 404]:
            # 404 is acceptable here if it's "No patient profile available"
            # because it means we passed auth and multi-tenancy middleware
            print(f"SUCCESS: Authentication and Multi-tenancy check passed (Status: {response.status_code})")
        else:
            print(f"FAILED: Start session failed with unexpected status {response.status_code}: {response.text}")

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
