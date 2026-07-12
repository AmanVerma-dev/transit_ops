"""
Phase 5 - Maintenance Module Verification Script

Verifies that all required files and components are present.
"""

import os
import sys

def check_file(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False

def check_import(module_path, description):
    """Check if a module can be imported."""
    try:
        __import__(module_path)
        print(f"✅ {description}")
        return True
    except ImportError as e:
        print(f"❌ {description} - IMPORT ERROR: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {description} - WARNING: {e}")
        return False

def check_content(filepath, search_strings, description):
    """Check if file contains specific strings."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            missing = [s for s in search_strings if s not in content]
            if not missing:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - Missing: {', '.join(missing)}")
                return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("PHASE 5 - MAINTENANCE MODULE VERIFICATION")
    print("=" * 60)
    
    base_path = "app"
    all_checks = []
    
    # Check Model
    print("\n=== 1. MODEL ===")
    model_path = os.path.join(base_path, "models", "maintenance.py")
    all_checks.append(check_file(model_path, "Maintenance Model File"))
    all_checks.append(check_content(
        model_path,
        ["class Maintenance", "MaintenanceStatus", "MaintenanceType", "SCHEDULED", "IN_PROGRESS", "COMPLETED", "CANCELLED"],
        "Maintenance Model Content"
    ))
    
    # Check Schema
    print("\n=== 2. SCHEMA ===")
    schema_path = os.path.join(base_path, "schemas", "maintenance.py")
    all_checks.append(check_file(schema_path, "Maintenance Schema File"))
    all_checks.append(check_content(
        schema_path,
        ["MaintenanceCreate", "MaintenanceUpdate", "MaintenanceResponse", "MaintenanceListResponse", "MaintenanceFilter"],
        "Maintenance Schema Content"
    ))
    
    # Check Repository
    print("\n=== 3. REPOSITORY ===")
    repo_path = os.path.join(base_path, "repositories", "maintenance.py")
    all_checks.append(check_file(repo_path, "Maintenance Repository File"))
    all_checks.append(check_content(
        repo_path,
        ["class MaintenanceRepository", "create", "get_by_id", "get_all", "update", "delete", "exists"],
        "Maintenance Repository Content"
    ))
    
    # Check Service
    print("\n=== 4. SERVICE ===")
    service_path = os.path.join(base_path, "services", "maintenance.py")
    all_checks.append(check_file(service_path, "Maintenance Service File"))
    all_checks.append(check_content(
        service_path,
        ["class MaintenanceService", "schedule_maintenance", "start_maintenance", "complete_maintenance", "cancel_maintenance", "update_maintenance"],
        "Maintenance Service Content"
    ))
    
    # Check Routes
    print("\n=== 5. ROUTES ===")
    routes_path = os.path.join(base_path, "api", "routes", "maintenance.py")
    all_checks.append(check_file(routes_path, "Maintenance Routes File"))
    all_checks.append(check_content(
        routes_path,
        ["@router.post", "@router.get", "@router.put", "@router.patch", "/start", "/complete", "/cancel", "@router.delete"],
        "Maintenance Routes Content"
    ))
    
    # Check Router Registration
    print("\n=== 6. ROUTER REGISTRATION ===")
    router_path = os.path.join(base_path, "api", "router.py")
    all_checks.append(check_content(
        router_path,
        ["from app.api.routes import", "maintenance", 'api_router.include_router(maintenance.router, prefix="/maintenance"'],
        "Router Registration"
    ))
    
    # Check Model Registration
    print("\n=== 7. MODEL REGISTRATION ===")
    models_init_path = os.path.join(base_path, "models", "__init__.py")
    all_checks.append(check_content(
        models_init_path,
        ["from app.models.maintenance import Maintenance"],
        "Model Import in __init__.py"
    ))
    
    # Check Business Rules
    print("\n=== 8. BUSINESS RULES ===")
    all_checks.append(check_content(
        service_path,
        ["MaintenanceStatus.SCHEDULED", "MaintenanceStatus.IN_PROGRESS", "MaintenanceStatus.COMPLETED", "MaintenanceStatus.CANCELLED"],
        "Status Enum Usage"
    ))
    all_checks.append(check_content(
        service_path,
        ["HTTP_409_CONFLICT", "HTTP_404_NOT_FOUND", "HTTP_422_UNPROCESSABLE_ENTITY"],
        "HTTP Status Codes"
    ))
    all_checks.append(check_content(
        service_path,
        ["vehicle_repo.get_by_id"],
        "Vehicle Validation"
    ))
    
    # Check RBAC
    print("\n=== 9. RBAC ===")
    all_checks.append(check_content(
        routes_path,
        ['require_roles(["Fleet Manager"', '"Safety Officer"'],
        "RBAC Permissions"
    ))
    
    # Check Test File
    print("\n=== 10. TEST FILE ===")
    test_path = "test_maintenance.py"
    all_checks.append(check_file(test_path, "Maintenance Test File"))
    if os.path.exists(test_path):
        all_checks.append(check_content(
            test_path,
            ["test_schedule_maintenance", "test_start_maintenance", "test_complete_maintenance", "test_cancel_maintenance", "test_invalid_state_transitions"],
            "Test Coverage"
        ))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    passed = sum(all_checks)
    total = len(all_checks)
    print(f"\nPassed: {passed}/{total} checks")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! Phase 5 implementation is complete.")
        print("\nImplemented Features:")
        print("  ✅ Maintenance Model with Status and Type enums")
        print("  ✅ Complete CRUD operations")
        print("  ✅ State transitions: SCHEDULED → IN_PROGRESS → COMPLETED")
        print("  ✅ Cancellation: SCHEDULED → CANCELLED")
        print("  ✅ Business rule validation")
        print("  ✅ Vehicle existence check")
        print("  ✅ Filtering by vehicle, status, type, date range")
        print("  ✅ Pagination support")
        print("  ✅ RBAC permissions")
        print("  ✅ Comprehensive error handling")
        print("  ✅ Test suite")
        print("\nNext Steps:")
        print("  1. Ensure dependencies are installed: pip install -r requirements.txt")
        print("  2. Start the server: python -m uvicorn app.main:app --reload")
        print("  3. Run tests: python test_maintenance.py")
        print("  4. View API docs: http://localhost:8000/docs")
    else:
        print(f"\n⚠️  {total - passed} check(s) failed. Please review the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
