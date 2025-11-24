# Endpoints That Return Work Hours and Break Time Details

This document lists all endpoints that return detailed work hours and break time information for users.

---

## Primary Endpoint: Get Current Session

### **GET** `/api/operations/sessions/current/`

**Description:** Get current session with complete work hours and break details.

**Query Parameters:**
- `user_id` (optional) - For managers/admins to view other user's session

**Response Example:**
```json
{
    "success": true,
    "session": {
        "id": 1,
        "user": 5,
        "user_detail": {
            "id": 5,
            "work_id": "FA001",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "role": "FIELD_AGENT"
        },
        "shift_date": "2025-01-20",
        "timestamp": "2025-01-20T09:00:00Z",
        "latitude": "24.713600",
        "longitude": "46.675300",
        "check_out_time": null,
        "check_out_latitude": null,
        "check_out_longitude": null,
        "status": "ACTIVE",
        "current_break_start": null,
        "total_break_duration": "0:30:00",
        
        // WORK HOURS DETAILS
        "total_hours_worked": 4.5,
        "total_hours_worked_seconds": 16200,
        
        // BREAK TIME DETAILS
        "total_break_seconds": 1800,
        "break_duration_hours": 0.5,
        "break_duration_seconds": 1800,
        
        // REMAINING SHIFT TIME
        "remaining_shift_hours": 4.0,
        "remaining_shift_seconds": 14400,
        
        "created_at": "2025-01-20T09:00:00Z",
        "updated_at": "2025-01-20T13:30:00Z"
    },
    "breaks": [
        {
            "id": 1,
            "session": 1,
            "session_id": 1,
            "user": 5,
            "user_detail": {
                "id": 5,
                "work_id": "FA001",
                "first_name": "John",
                "last_name": "Doe"
            },
            "route": null,
            "route_detail": null,
            "start_time": "2025-01-20T13:00:00Z",
            "end_time": "2025-01-20T13:30:00Z",
            "duration": "0:30:00",
            "duration_seconds": 1800,
            "created_at": "2025-01-20T13:00:00Z",
            "updated_at": "2025-01-20T13:30:00Z"
        }
    ]
}
```

**Fields Included:**
- ✅ `total_hours_worked` - Hours worked (excluding breaks)
- ✅ `total_hours_worked_seconds` - Hours worked in seconds
- ✅ `break_duration_hours` - Total break duration in hours
- ✅ `break_duration_seconds` - Total break duration in seconds
- ✅ `total_break_seconds` - Total break duration in seconds (alias)
- ✅ `remaining_shift_hours` - Remaining time in 9-hour shift
- ✅ `remaining_shift_seconds` - Remaining time in seconds
- ✅ `total_break_duration` - Break duration as time delta
- ✅ `current_break_start` - Start time of current break (if on break)
- ✅ `status` - Session status (ACTIVE, ON_BREAK, COMPLETED)
- ✅ Individual break records with start/end times

---

## Action Endpoints That Return Work Hours

All these endpoints return the same work hours and break time details in their responses:

### 1. **POST** `/api/operations/sessions/start-day/`

**Description:** Start work day (check-in). Returns session data with initial work hours.

**Response Includes:**
```json
{
    "success": true,
    "session": {
        "id": 1,
        "total_hours_worked": 0.0,
        "total_hours_worked_seconds": 0,
        "break_duration_hours": 0.0,
        "break_duration_seconds": 0,
        "remaining_shift_hours": 9.0,
        "remaining_shift_seconds": 32400,
        "status": "ACTIVE",
        // ... other fields
    }
}
```

---

### 2. **POST** `/api/operations/sessions/take-break/`

**Description:** Start a break. Returns session data with current work hours (break time not yet added).

**Response Includes:**
```json
{
    "success": true,
    "message": "Break started successfully",
    "session": {
        "id": 1,
        "total_hours_worked": 4.5,
        "total_hours_worked_seconds": 16200,
        "break_duration_hours": 0.0,
        "break_duration_seconds": 0,
        "remaining_shift_hours": 4.5,
        "remaining_shift_seconds": 16200,
        "status": "ON_BREAK",
        "current_break_start": "2025-01-20T13:00:00Z",
        // ... other fields
    },
    "break": {
        "id": 1,
        "start_time": "2025-01-20T13:00:00Z",
        "end_time": null,
        "duration": null
    }
}
```

---

### 3. **POST** `/api/operations/sessions/resume-day/`

**Description:** Resume work after break. Returns session data with updated break duration.

**Response Includes:**
```json
{
    "success": true,
    "message": "Resumed from break. Break duration: 0:30:00",
    "session": {
        "id": 1,
        "total_hours_worked": 4.5,
        "total_hours_worked_seconds": 16200,
        "break_duration_hours": 0.5,
        "break_duration_seconds": 1800,
        "remaining_shift_hours": 4.0,
        "remaining_shift_seconds": 14400,
        "status": "ACTIVE",
        "current_break_start": null,
        // ... other fields
    },
    "break": {
        "id": 1,
        "start_time": "2025-01-20T13:00:00Z",
        "end_time": "2025-01-20T13:30:00Z",
        "duration": "0:30:00",
        "duration_seconds": 1800
    }
}
```

---

### 4. **POST** `/api/operations/sessions/check-out/`

**Description:** Complete work day (check-out). Returns final session data with total work hours.

**Response Includes:**
```json
{
    "success": true,
    "message": "Checked out successfully",
    "session": {
        "id": 1,
        "check_out_time": "2025-01-20T18:00:00Z",
        "check_out_latitude": "24.713600",
        "check_out_longitude": "46.675300",
        "total_hours_worked": 8.5,
        "total_hours_worked_seconds": 30600,
        "break_duration_hours": 0.5,
        "break_duration_seconds": 1800,
        "remaining_shift_hours": 0.5,
        "remaining_shift_seconds": 1800,
        "status": "COMPLETED",
        // ... other fields
    }
}
```

---

## Summary Table

| Endpoint | Method | Returns Work Hours? | Returns Break Time? | Returns Individual Breaks? |
|----------|--------|---------------------|---------------------|---------------------------|
| **Get Current Session** | GET | ✅ Yes | ✅ Yes | ✅ Yes |
| **Start Day** | POST | ✅ Yes | ✅ Yes | ❌ No |
| **Take Break** | POST | ✅ Yes | ✅ Yes | ✅ Yes (current break) |
| **Resume Day** | POST | ✅ Yes | ✅ Yes | ✅ Yes (completed break) |
| **Check Out** | POST | ✅ Yes | ✅ Yes | ❌ No |

---

## All Work Hours & Break Time Fields

All endpoints that use `CheckInSerializer` return these fields:

### Work Hours Fields:
- `total_hours_worked` (float) - Total hours worked excluding breaks
- `total_hours_worked_seconds` (int) - Total hours worked in seconds

### Break Time Fields:
- `break_duration_hours` (float) - Total break duration in hours
- `break_duration_seconds` (int) - Total break duration in seconds
- `total_break_seconds` (int) - Total break duration in seconds (alias)
- `total_break_duration` (string) - Break duration as time delta (e.g., "0:30:00")
- `current_break_start` (datetime/null) - Start time of current break (if on break)

### Remaining Shift Fields:
- `remaining_shift_hours` (float) - Remaining time in 9-hour shift
- `remaining_shift_seconds` (int) - Remaining time in seconds

### Session Status:
- `status` (string) - Session status: `ACTIVE`, `ON_BREAK`, or `COMPLETED`

### Individual Break Records:
- `breaks` (array) - List of all breaks with:
  - `start_time` - Break start time
  - `end_time` - Break end time
  - `duration` - Break duration
  - `duration_seconds` - Break duration in seconds

---

## Recommended Endpoint for Getting Work Hours

**Use this endpoint to get complete work hours and break details:**

```
GET /api/operations/sessions/current/
```

**Why this endpoint?**
- ✅ Returns complete session data
- ✅ Includes all work hours and break time fields
- ✅ Includes list of all individual breaks
- ✅ Works for field agents (own session) and managers/admins (other users)
- ✅ Real-time calculations
- ✅ Can be called anytime to check current status

**For Managers/Admins:**
```
GET /api/operations/sessions/current/?user_id=5
```

This allows managers/admins to view any user's work hours and break details.

---

## Example Usage

### Field Agent - View Own Work Hours
```bash
GET /api/operations/sessions/current/
Authorization: Bearer {access_token}
```

### Manager/Admin - View User's Work Hours
```bash
GET /api/operations/sessions/current/?user_id=5
Authorization: Bearer {access_token}
```

### Response Interpretation
```json
{
    "session": {
        "total_hours_worked": 4.5,        // User worked 4.5 hours
        "break_duration_hours": 0.5,      // User took 0.5 hours (30 min) break
        "remaining_shift_hours": 4.0,      // 4 hours remaining in 9-hour shift
        "status": "ACTIVE"                 // Currently working (not on break)
    },
    "breaks": [
        {
            "start_time": "2025-01-20T13:00:00Z",
            "end_time": "2025-01-20T13:30:00Z",
            "duration": "0:30:00"           // 30-minute break
        }
    ]
}
```

---

## Notes

1. **Real-Time Calculations:** All work hours are calculated in real-time based on current server time
2. **Multiple Breaks:** System supports multiple breaks per day, all are accumulated
3. **Break Tracking:** Break time is automatically tracked when you resume from break
4. **9-Hour Shift:** System tracks 9-hour shifts, remaining time is calculated automatically
5. **Status Tracking:** `status` field shows if user is working, on break, or completed


