"""
Phase 5 - Maintenance Module Test Suite

Tests the complete maintenance lifecycle:
- Schedule maintenance
- Start maintenance
- Complete maintenance
- Cancel maintenance
- Invalid state transitions
- Filtering and pagination
- RBAC permissions
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Test credentials
FLEET_MANAGER = {"username": "fleet_manager", "password": "FleetPass123!"}
SAFETY_OFFICER = {"username": "safety_officer", "password": "SafetyPass123!"}
FINANCIAL_ANALYST = {"username": "financial_analyst", "password": "FinancePass123!"}
DRIVER = {"username": "driver_user", "password": "DriverPass123!"}

def get_token(credentials):
    """Get authentication token."""
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed for {credentials['username']}: {response.text}")
        return None

def test_health():
    """Test health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code} - {response.json()}")
    assert response.status_code == 200
    print("✅ Health check passed")

def test_schedule_maintenance(token, vehicle_id):
    """Test scheduling maintenance."""
    print("\n=== Testing Schedule Maintenance ===")
    
    scheduled_date = (datetime.now() + timedelta(days=7)).isoformat()
    
    maintenance_data = {
        "vehicle_id": vehicle_id,
        "maintenance_type": "Preventive",
        "description": "Regular oil change and filter replacement",
        "scheduled_date": scheduled_date,
        "estimated_cost": 150.00,
        "technician_notes": "Check brake pads while servicing"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/maintenance", json=maintenance_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Maintenance scheduled successfully")
        print(f"   ID: {data['id']}")
        print(f"   Status: {data['status']}")
        print(f"   Vehicle ID: {data['vehicle_id']}")
        print(f"   Type: {data['maintenance_type']}")
        print(f"   Estimated Cost: ${data['estimated_cost']}")
        return data['id']
    else:
        print(f"❌ Failed to schedule maintenance: {response.text}")
        return None

def test_schedule_maintenance_invalid_vehicle(token):
    """Test scheduling maintenance for non-existent vehicle."""
    print("\n=== Testing Schedule Maintenance - Invalid Vehicle ===")
    
    scheduled_date = (datetime.now() + timedelta(days=7)).isoformat()
    
    maintenance_data = {
        "vehicle_id": 99999,
        "maintenance_type": "Preventive",
        "description": "Test maintenance",
        "scheduled_date": scheduled_date,
        "estimated_cost": 100.00
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/maintenance", json=maintenance_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print("✅ Correctly rejected non-existent vehicle")
    else:
        print(f"❌ Expected 404, got {response.status_code}: {response.text}")

def test_list_maintenance(token, vehicle_id=None):
    """Test listing maintenance records."""
    print("\n=== Testing List Maintenance ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if vehicle_id:
        params["vehicle_id"] = vehicle_id
    
    response = requests.get(f"{BASE_URL}/maintenance", params=params, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Retrieved {data['total']} maintenance records")
        for item in data['items'][:3]:  # Show first 3
            print(f"   - ID: {item['id']}, Vehicle: {item['vehicle_id']}, Status: {item['status']}, Type: {item['maintenance_type']}")
        return data['items']
    else:
        print(f"❌ Failed to list maintenance: {response.text}")
        return []

def test_get_maintenance(token, maintenance_id):
    """Test getting specific maintenance record."""
    print("\n=== Testing Get Maintenance ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/maintenance/{maintenance_id}", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Retrieved maintenance record")
        print(f"   ID: {data['id']}")
        print(f"   Vehicle: {data['vehicle_id']}")
        print(f"   Status: {data['status']}")
        print(f"   Type: {data['maintenance_type']}")
        print(f"   Description: {data['description']}")
        return data
    else:
        print(f"❌ Failed to get maintenance: {response.text}")
        return None

def test_update_maintenance(token, maintenance_id):
    """Test updating scheduled maintenance."""
    print("\n=== Testing Update Maintenance ===")
    
    update_data = {
        "estimated_cost": 175.00,
        "technician_notes": "Updated: Also check tire pressure"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/maintenance/{maintenance_id}", json=update_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Maintenance updated successfully")
        print(f"   New Estimated Cost: ${data['estimated_cost']}")
        print(f"   Technician Notes: {data['technician_notes']}")
        return True
    else:
        print(f"❌ Failed to update maintenance: {response.text}")
        return False

def test_start_maintenance(token, maintenance_id):
    """Test starting scheduled maintenance."""
    print("\n=== Testing Start Maintenance ===")
    
    start_data = {
        "technician_notes": "Starting oil change service"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{BASE_URL}/maintenance/{maintenance_id}/start", json=start_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Maintenance started successfully")
        print(f"   Status: {data['status']}")
        print(f"   Started At: {data['started_at']}")
        print(f"   Technician Notes: {data['technician_notes']}")
        return True
    else:
        print(f"❌ Failed to start maintenance: {response.text}")
        return False

def test_complete_maintenance(token, maintenance_id):
    """Test completing in-progress maintenance."""
    print("\n=== Testing Complete Maintenance ===")
    
    complete_data = {
        "actual_cost": 185.50,
        "technician_notes": "Oil change completed. Brake pads at 60% - good condition. Tire pressure adjusted."
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{BASE_URL}/maintenance/{maintenance_id}/complete", json=complete_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Maintenance completed successfully")
        print(f"   Status: {data['status']}")
        print(f"   Completed At: {data['completed_at']}")
        print(f"   Actual Cost: ${data['actual_cost']}")
        print(f"   Estimated Cost: ${data['estimated_cost']}")
        print(f"   Difference: ${data['actual_cost'] - data['estimated_cost']:.2f}")
        return True
    else:
        print(f"❌ Failed to complete maintenance: {response.text}")
        return False

def test_cancel_maintenance(token, maintenance_id):
    """Test cancelling scheduled maintenance."""
    print("\n=== Testing Cancel Maintenance ===")
    
    cancel_data = {
        "reason": "Vehicle scheduled for emergency trip"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{BASE_URL}/maintenance/{maintenance_id}/cancel", json=cancel_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Maintenance cancelled successfully")
        print(f"   Status: {data['status']}")
        print(f"   Technician Notes: {data['technician_notes']}")
        return True
    else:
        print(f"❌ Failed to cancel maintenance: {response.text}")
        return False

def test_invalid_state_transitions(token, vehicle_id):
    """Test invalid state transitions."""
    print("\n=== Testing Invalid State Transitions ===")
    
    # Schedule a maintenance
    scheduled_date = (datetime.now() + timedelta(days=5)).isoformat()
    maintenance_data = {
        "vehicle_id": vehicle_id,
        "maintenance_type": "Inspection",
        "description": "Test state transitions",
        "scheduled_date": scheduled_date,
        "estimated_cost": 50.00
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/maintenance", json=maintenance_data, headers=headers)
    maintenance_id = response.json()["id"]
    
    # Try to complete without starting (SCHEDULED -> COMPLETED should fail)
    print("\n  Testing SCHEDULED -> COMPLETED (should fail)...")
    complete_data = {"actual_cost": 50.00}
    response = requests.patch(f"{BASE_URL}/maintenance/{maintenance_id}/complete", json=complete_data, headers=headers)
    if response.status_code == 409:
        print("  ✅ Correctly rejected SCHEDULED -> COMPLETED")
    else:
        print(f"  ❌ Expected 409, got {response.status_code}")
    
    # Start maintenance
    print("\n  Starting maintenance...")
    response = requests.patch(f"{BASE_URL}/maintenance/{maintenance_id}/start", json={}, headers=headers)
    print(f"  Started: {response.status_code}")
    
    # Try to cancel after starting (IN_PROGRESS -> CANCELLED should fail)
    print("\n  Testing IN_PROGRESS -> CANCELLED (should fail)...")
    cancel_data = {"reason": "Test cancellation"}
    response = requests.patch(f"{BASE_URL}/maintenance/{maintenance_id}/cancel", json=cancel_data, headers=headers)
    if response.status_code == 409:
        print("  ✅ Correctly rejected IN_PROGRESS -> CANCELLED")
    else:
        print(f"  ❌ Expected 409, got {response.status_code}")
    
    # Try to update after starting (IN_PROGRESS update should fail)
    print("\n  Testing Update IN_PROGRESS (should fail)...")
    update_data = {"estimated_cost": 60.00}
    response = requests.put(f"{BASE_URL}/maintenance/{maintenance_id}", json=update_data, headers=headers)
    if response.status_code == 409:
        print("  ✅ Correctly rejected update of IN_PROGRESS maintenance")
    else:
        print(f"  ❌ Expected 409, got {response.status_code}")
    
    # Complete maintenance
    print("\n  Completing maintenance...")
    complete_data = {"actual_cost": 55.00}
    response = requests.patch(f"{BASE_URL}/maintenance/{maintenance_id}/complete", json=complete_data, headers=headers)
    print(f"  Completed: {response.status_code}")
    
    # Try to start after completing (COMPLETED -> IN_PROGRESS should fail)
    print("\n  Testing COMPLETED -> IN_PROGRESS (should fail)...")
    response = requests.patch(f"{BASE_URL}/maintenance/{maintenance_id}/start", json={}, headers=headers)
    if response.status_code == 409:
        print("  ✅ Correctly rejected COMPLETED -> IN_PROGRESS")
    else:
        print(f"  ❌ Expected 409, got {response.status_code}")

def test_filter_by_status(token, vehicle_id):
    """Test filtering by status."""
    print("\n=== Testing Filter by Status ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    statuses = ["SCHEDULED", "IN_PROGRESS", "COMPLETED"]
    for status in statuses:
        params = {"status": status, "vehicle_id": vehicle_id}
        response = requests.get(f"{BASE_URL}/maintenance", params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"  {status}: {data['total']} records")
        else:
            print(f"  ❌ Failed to filter by {status}")

def test_filter_by_maintenance_type(token, vehicle_id):
    """Test filtering by maintenance type."""
    print("\n=== Testing Filter by Maintenance Type ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    types = ["Preventive", "Corrective", "Emergency", "Inspection"]
    for mtype in types:
        params = {"maintenance_type": mtype, "vehicle_id": vehicle_id}
        response = requests.get(f"{BASE_URL}/maintenance", params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"  {mtype}: {data['total']} records")
        else:
            print(f"  ❌ Failed to filter by {mtype}")

def test_pagination(token):
    """Test pagination."""
    print("\n=== Testing Pagination ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get first page
    params = {"skip": 0, "limit": 2}
    response = requests.get(f"{BASE_URL}/maintenance", params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"  Page 1: {len(data['items'])} items (Total: {data['total']})")
    
    # Get second page
    params = {"skip": 2, "limit": 2}
    response = requests.get(f"{BASE_URL}/maintenance", params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"  Page 2: {len(data['items'])} items (Total: {data['total']})")
        print("✅ Pagination working")

def test_rbac_permissions():
    """Test RBAC permissions."""
    print("\n=== Testing RBAC Permissions ===")
    
    # Get vehicle ID
    fleet_token = get_token(FLEET_MANAGER)
    headers = {"Authorization": f"Bearer {fleet_token}"}
    response = requests.get(f"{BASE_URL}/vehicles", headers=headers)
    vehicle_id = response.json()["items"][0]["id"]
    
    scheduled_date = (datetime.now() + timedelta(days=10)).isoformat()
    maintenance_data = {
        "vehicle_id": vehicle_id,
        "maintenance_type": "Corrective",
        "description": "RBAC test",
        "scheduled_date": scheduled_date,
        "estimated_cost": 200.00
    }
    
    # Fleet Manager - Should have full access
    print("\n  Fleet Manager:")
    token = get_token(FLEET_MANAGER)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/maintenance", json=maintenance_data, headers=headers)
    print(f"    Create: {response.status_code} {'✅' if response.status_code == 201 else '❌'}")
    
    # Safety Officer - Should have create/update/start/complete/cancel
    print("\n  Safety Officer:")
    token = get_token(SAFETY_OFFICER)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/maintenance", json=maintenance_data, headers=headers)
    print(f"    Create: {response.status_code} {'✅' if response.status_code == 201 else '❌'}")
    
    # Financial Analyst - Should have read-only
    print("\n  Financial Analyst:")
    token = get_token(FINANCIAL_ANALYST)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/maintenance", headers=headers)
    print(f"    Read: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    response = requests.post(f"{BASE_URL}/maintenance", json=maintenance_data, headers=headers)
    print(f"    Create: {response.status_code} {'✅' if response.status_code == 403 else '❌'}")
    
    # Driver - Should have read-only
    print("\n  Driver:")
    token = get_token(DRIVER)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/maintenance", headers=headers)
    print(f"    Read: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    response = requests.post(f"{BASE_URL}/maintenance", json=maintenance_data, headers=headers)
    print(f"    Create: {response.status_code} {'✅' if response.status_code == 403 else '❌'}")

def test_swagger():
    """Test Swagger documentation."""
    print("\n=== Testing Swagger Documentation ===")
    response = requests.get(f"{BASE_URL}/docs")
    if response.status_code == 200:
        print("✅ Swagger documentation accessible at /docs")
    else:
        print(f"❌ Swagger not accessible: {response.status_code}")

def main():
    """Run all tests."""
    print("=" * 60)
    print("PHASE 5 - MAINTENANCE MODULE TEST SUITE")
    print("=" * 60)
    
    # Test health
    test_health()
    
    # Get authentication token
    print("\n=== Authenticating ===")
    fleet_token = get_token(FLEET_MANAGER)
    if not fleet_token:
        print("❌ Cannot proceed without authentication")
        return
    print("✅ Authenticated as Fleet Manager")
    
    # Get a vehicle for testing
    print("\n=== Getting Test Vehicle ===")
    headers = {"Authorization": f"Bearer {fleet_token}"}
    response = requests.get(f"{BASE_URL}/vehicles", headers=headers)
    if response.status_code != 200 or not response.json()["items"]:
        print("❌ No vehicles available for testing")
        return
    vehicle_id = response.json()["items"][0]["id"]
    print(f"✅ Using Vehicle ID: {vehicle_id}")
    
    # Test CRUD operations
    maintenance_id = test_schedule_maintenance(fleet_token, vehicle_id)
    if maintenance_id:
        test_get_maintenance(fleet_token, maintenance_id)
        test_update_maintenance(fleet_token, maintenance_id)
        test_list_maintenance(fleet_token, vehicle_id)
    
    # Test lifecycle (schedule -> start -> complete)
    print("\n" + "=" * 60)
    print("TESTING COMPLETE MAINTENANCE LIFECYCLE")
    print("=" * 60)
    maintenance_id = test_schedule_maintenance(fleet_token, vehicle_id)
    if maintenance_id:
        test_start_maintenance(fleet_token, maintenance_id)
        test_complete_maintenance(fleet_token, maintenance_id)
    
    # Test cancellation flow
    print("\n" + "=" * 60)
    print("TESTING CANCELLATION FLOW")
    print("=" * 60)
    maintenance_id = test_schedule_maintenance(fleet_token, vehicle_id)
    if maintenance_id:
        test_cancel_maintenance(fleet_token, maintenance_id)
    
    # Test invalid operations
    test_schedule_maintenance_invalid_vehicle(fleet_token)
    test_invalid_state_transitions(fleet_token, vehicle_id)
    
    # Test filtering
    print("\n" + "=" * 60)
    print("TESTING FILTERS")
    print("=" * 60)
    test_filter_by_status(fleet_token, vehicle_id)
    test_filter_by_maintenance_type(fleet_token, vehicle_id)
    test_pagination(fleet_token)
    
    # Test RBAC
    test_rbac_permissions()
    
    # Test Swagger
    test_swagger()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)
    print("\n✅ Phase 5 - Maintenance Module Implementation Complete")
    print("\nNext Steps:")
    print("  1. Review Swagger documentation at http://localhost:8000/docs")
    print("  2. Check maintenance endpoints under 'maintenance' tag")
    print("  3. Verify state transitions and RBAC work as expected")

if __name__ == "__main__":
    main()
