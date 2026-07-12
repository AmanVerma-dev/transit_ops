# Maintenance Module API Reference

Quick reference for the Vehicle Maintenance API endpoints.

## Base URL
```
http://localhost:8000/maintenance
```

## Authentication
All endpoints require authentication. Include JWT token in header:
```
Authorization: Bearer <token>
```

## Endpoints

### 1. Schedule Maintenance
```http
POST /maintenance
```

**Permission:** Fleet Manager, Safety Officer

**Request Body:**
```json
{
  "vehicle_id": 1,
  "maintenance_type": "Preventive",
  "description": "Regular oil change and filter replacement",
  "scheduled_date": "2026-07-20T10:00:00Z",
  "estimated_cost": 150.00,
  "technician_notes": "Check brake pads while servicing"
}
```

**Maintenance Types:**
- `Preventive` - Scheduled preventive maintenance
- `Corrective` - Repair work
- `Emergency` - Urgent repairs
- `Inspection` - Vehicle inspection

**Response:** `201 Created`
```json
{
  "id": 1,
  "vehicle_id": 1,
  "maintenance_type": "Preventive",
  "description": "Regular oil change and filter replacement",
  "scheduled_date": "2026-07-20T10:00:00Z",
  "started_at": null,
  "completed_at": null,
  "estimated_cost": 150.00,
  "actual_cost": null,
  "status": "SCHEDULED",
  "technician_notes": "Check brake pads while servicing",
  "created_by": 1,
  "created_at": "2026-07-12T10:00:00Z",
  "updated_at": "2026-07-12T10:00:00Z"
}
```

**Errors:**
- `404` - Vehicle not found
- `403` - Insufficient permissions
- `422` - Validation error

---

### 2. List Maintenance Records
```http
GET /maintenance
```

**Permission:** All authenticated users

**Query Parameters:**
```
vehicle_id       (optional) - Filter by vehicle ID
status           (optional) - SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
maintenance_type (optional) - Preventive, Corrective, Emergency, Inspection
scheduled_date   (optional) - Exact date (ISO 8601)
start_date       (optional) - Range start date
end_date         (optional) - Range end date
skip             (optional) - Pagination offset (default: 0)
limit            (optional) - Page size (default: 100, max: 100)
```

**Example:**
```http
GET /maintenance?vehicle_id=1&status=SCHEDULED&skip=0&limit=10
```

**Response:** `200 OK`
```json
{
  "total": 25,
  "items": [
    {
      "id": 1,
      "vehicle_id": 1,
      "status": "SCHEDULED",
      ...
    }
  ]
}
```

---

### 3. Get Maintenance Record
```http
GET /maintenance/{id}
```

**Permission:** All authenticated users

**Response:** `200 OK`
```json
{
  "id": 1,
  "vehicle_id": 1,
  "maintenance_type": "Preventive",
  "description": "Regular oil change and filter replacement",
  "scheduled_date": "2026-07-20T10:00:00Z",
  "started_at": null,
  "completed_at": null,
  "estimated_cost": 150.00,
  "actual_cost": null,
  "status": "SCHEDULED",
  "technician_notes": "Check brake pads while servicing",
  "created_by": 1,
  "created_at": "2026-07-12T10:00:00Z",
  "updated_at": "2026-07-12T10:00:00Z"
}
```

**Errors:**
- `404` - Maintenance record not found

---

### 4. Update Maintenance Record
```http
PUT /maintenance/{id}
```

**Permission:** Fleet Manager, Safety Officer

**Important:** Only works on `SCHEDULED` maintenance

**Request Body:** (All fields optional)
```json
{
  "maintenance_type": "Preventive",
  "description": "Updated description",
  "scheduled_date": "2026-07-21T10:00:00Z",
  "estimated_cost": 175.00,
  "actual_cost": null,
  "technician_notes": "Updated notes"
}
```

**Response:** `200 OK`

**Errors:**
- `404` - Maintenance record not found
- `409` - Cannot update (not SCHEDULED)
- `403` - Insufficient permissions
- `422` - Validation error

---

### 5. Start Maintenance
```http
PATCH /maintenance/{id}/start
```

**Permission:** Fleet Manager, Safety Officer

**State Transition:** `SCHEDULED` → `IN_PROGRESS`

**Request Body:**
```json
{
  "technician_notes": "Starting oil change service"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "status": "IN_PROGRESS",
  "started_at": "2026-07-20T10:05:00Z",
  "technician_notes": "Starting oil change service",
  ...
}
```

**Errors:**
- `404` - Maintenance record not found
- `409` - Invalid state transition (not SCHEDULED)
- `403` - Insufficient permissions

---

### 6. Complete Maintenance
```http
PATCH /maintenance/{id}/complete
```

**Permission:** Fleet Manager, Safety Officer

**State Transition:** `IN_PROGRESS` → `COMPLETED`

**Request Body:**
```json
{
  "actual_cost": 185.50,
  "technician_notes": "Oil change completed. Brake pads at 60% - good condition."
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "status": "COMPLETED",
  "started_at": "2026-07-20T10:05:00Z",
  "completed_at": "2026-07-20T11:30:00Z",
  "estimated_cost": 150.00,
  "actual_cost": 185.50,
  "technician_notes": "Oil change completed. Brake pads at 60% - good condition.",
  ...
}
```

**Errors:**
- `404` - Maintenance record not found
- `409` - Invalid state transition (not IN_PROGRESS)
- `422` - Invalid actual cost (must be >= 0)
- `403` - Insufficient permissions

---

### 7. Cancel Maintenance
```http
PATCH /maintenance/{id}/cancel
```

**Permission:** Fleet Manager, Safety Officer

**State Transition:** `SCHEDULED` → `CANCELLED`

**Request Body:**
```json
{
  "reason": "Vehicle scheduled for emergency trip"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "status": "CANCELLED",
  "technician_notes": "CANCELLED: Vehicle scheduled for emergency trip",
  ...
}
```

**Errors:**
- `404` - Maintenance record not found
- `409` - Invalid state transition (not SCHEDULED)
- `403` - Insufficient permissions

---

### 8. Delete Maintenance Record
```http
DELETE /maintenance/{id}
```

**Permission:** Fleet Manager only

**Response:** `204 No Content`

**Errors:**
- `404` - Maintenance record not found
- `403` - Insufficient permissions

---

## State Diagram

```
┌──────────┐
│SCHEDULED │
└────┬─────┘
     │
     │ start_maintenance()
     ▼
┌────────────┐
│IN_PROGRESS │
└─────┬──────┘
      │
      │ complete_maintenance()
      ▼
┌───────────┐
│ COMPLETED │
└───────────┘

┌──────────┐
│SCHEDULED │
└────┬─────┘
     │
     │ cancel_maintenance()
     ▼
┌───────────┐
│ CANCELLED │
└───────────┘
```

## Valid State Transitions

| From | To | Method |
|------|-----|--------|
| SCHEDULED | IN_PROGRESS | `PATCH /maintenance/{id}/start` |
| IN_PROGRESS | COMPLETED | `PATCH /maintenance/{id}/complete` |
| SCHEDULED | CANCELLED | `PATCH /maintenance/{id}/cancel` |

**All other transitions return `409 Conflict`**

## Role Permissions

| Role | Create | Read | Update | Start/Complete/Cancel | Delete |
|------|--------|------|--------|----------------------|--------|
| Fleet Manager | ✅ | ✅ | ✅ | ✅ | ✅ |
| Safety Officer | ✅ | ✅ | ✅ | ✅ | ❌ |
| Financial Analyst | ❌ | ✅ | ❌ | ❌ | ❌ |
| Driver | ❌ | ✅ | ❌ | ❌ | ❌ |

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (delete successful) |
| 401 | Unauthorized (not logged in) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found (resource doesn't exist) |
| 409 | Conflict (invalid state transition) |
| 422 | Unprocessable Entity (validation error) |

## cURL Examples

### Schedule Maintenance
```bash
curl -X POST http://localhost:8000/maintenance \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "maintenance_type": "Preventive",
    "description": "Regular oil change",
    "scheduled_date": "2026-07-20T10:00:00Z",
    "estimated_cost": 150.00
  }'
```

### Start Maintenance
```bash
curl -X PATCH http://localhost:8000/maintenance/1/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "technician_notes": "Starting service"
  }'
```

### Complete Maintenance
```bash
curl -X PATCH http://localhost:8000/maintenance/1/complete \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "actual_cost": 175.50,
    "technician_notes": "Service completed"
  }'
```

### List Scheduled Maintenance for Vehicle
```bash
curl -X GET "http://localhost:8000/maintenance?vehicle_id=1&status=SCHEDULED" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

**For interactive testing, use Swagger UI:** http://localhost:8000/docs
