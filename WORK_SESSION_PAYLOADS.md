# Work Session API Payloads

This document details the required payloads for check-in, check-out, take break, and resume day APIs.

---

## 1. Start Day (Check-in)

**Endpoint:** `POST /api/operations/sessions/start-day/`

**Required Fields:**
- `latitude` (decimal, required)
- `longitude` (decimal, required)

**Example Payload:**
```json
{
    "latitude": 24.7136,
    "longitude": 46.6753
}
```

**Notes:**
- Both `latitude` and `longitude` are **REQUIRED**
- Latitude must be between -90 and 90
- Longitude must be between -180 and 180
- Only one session per day per user (will error if already started)

---

## 2. Take Break

**Endpoint:** `POST /api/operations/sessions/take-break/`

**Required Fields:**
- None (all fields are optional)

**Optional Fields:**
- `route_id` (integer, optional) - Route ID if you want to associate break with a route

**Example Payload (With Route):**
```json
{
    "route_id": 5
}
```

**Example Payload (Without Route - Recommended):**
```json
{}
```

**Or simply send an empty body.**

**Notes:**
- Route is **OPTIONAL** - breaks are tracked per work session, not per route
- You must have an active session (started the day)
- Cannot take a break if already on a break
- Break time is automatically tracked for 9-hour shift calculation

---

## 3. Resume Day

**Endpoint:** `POST /api/operations/sessions/resume-day/`

**Required Fields:**
- None (no payload required)

**Example Payload:**
```json
{}
```

**Or simply send an empty body.**

**Notes:**
- No payload required
- You must be on a break to resume
- Break duration is automatically calculated when you resume
- Work time tracking continues after resume

---

## 4. Check Out

**Endpoint:** `POST /api/operations/sessions/check-out/`

**Required Fields:**
- None (all fields are optional)

**Optional Fields:**
- `latitude` (decimal, optional) - Check-out GPS latitude
- `longitude` (decimal, optional) - Check-out GPS longitude

**Example Payload (With GPS):**
```json
{
    "latitude": 24.7136,
    "longitude": 46.6753
}
```

**Example Payload (Without GPS):**
```json
{}
```

**Or simply send an empty body.**

**Notes:**
- GPS coordinates are **OPTIONAL**
- If provided, both `latitude` and `longitude` should be provided together
- You must have an active session (started the day)
- Cannot check out if currently on a break (must resume first)
- Cannot check out if already checked out
- Total hours worked and break duration are calculated automatically

---

## Summary Table

| Endpoint | Required Fields | Optional Fields | Empty Body Allowed |
|----------|----------------|-----------------|-------------------|
| **Start Day** | `latitude`, `longitude` | None | ❌ No |
| **Take Break** | None | `route_id` | ✅ Yes |
| **Resume Day** | None | None | ✅ Yes |
| **Check Out** | None | `latitude`, `longitude` | ✅ Yes |

---

## Complete Workflow Example

### 1. Start Day (Check-in)
```bash
POST /api/operations/sessions/start-day/
{
    "latitude": 24.7136,
    "longitude": 46.6753
}
```

### 2. Take Break (Optional - can be called multiple times)
```bash
POST /api/operations/sessions/take-break/
{}
```

### 3. Resume Day
```bash
POST /api/operations/sessions/resume-day/
{}
```

### 4. Check Out
```bash
POST /api/operations/sessions/check-out/
{
    "latitude": 24.7136,
    "longitude": 46.6753
}
```

---

## Response Examples

### Start Day Response
```json
{
    "success": true,
    "session": {
        "id": 1,
        "user": 5,
        "shift_date": "2025-01-20",
        "timestamp": "2025-01-20T09:00:00Z",
        "latitude": "24.713600",
        "longitude": "46.675300",
        "status": "ACTIVE",
        "total_hours_worked": 0.0,
        "total_hours_worked_seconds": 0,
        "break_duration_hours": 0.0,
        "break_duration_seconds": 0,
        "remaining_shift_hours": 9.0,
        "remaining_shift_seconds": 32400
    }
}
```

### Take Break Response
```json
{
    "success": true,
    "message": "Break started successfully",
    "session": {
        "id": 1,
        "status": "ON_BREAK",
        "total_hours_worked": 4.5,
        "break_duration_hours": 0.0,
        "remaining_shift_hours": 4.5
    },
    "break": {
        "id": 1,
        "start_time": "2025-01-20T13:00:00Z",
        "end_time": null,
        "duration": null
    }
}
```

### Resume Day Response
```json
{
    "success": true,
    "message": "Resumed from break. Break duration: 0:30:00",
    "session": {
        "id": 1,
        "status": "ACTIVE",
        "total_hours_worked": 4.5,
        "break_duration_hours": 0.5,
        "break_duration_seconds": 1800,
        "remaining_shift_hours": 4.0
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

### Check Out Response
```json
{
    "success": true,
    "message": "Checked out successfully",
    "session": {
        "id": 1,
        "status": "COMPLETED",
        "check_out_time": "2025-01-20T18:00:00Z",
        "check_out_latitude": "24.713600",
        "check_out_longitude": "46.675300",
        "total_hours_worked": 9.0,
        "total_hours_worked_seconds": 32400,
        "break_duration_hours": 0.5,
        "break_duration_seconds": 1800,
        "remaining_shift_hours": 0.0
    }
}
```

---

## Error Scenarios

### Start Day Errors
- **Already started:** `"You have already started today's session."`
- **Missing coordinates:** `"Both latitude and longitude are required."`
- **Invalid coordinates:** Validation error for out-of-range values

### Take Break Errors
- **No active session:** `"No active session found for today. Please start your day first."`
- **Already on break:** `"You are already on a break. Please resume your work first."`

### Resume Day Errors
- **No break in progress:** `"There is no break in progress to resume."`
- **No active break record:** `"No active break record found."`

### Check Out Errors
- **No session:** `"No session found for today."`
- **On break:** `"Resume your session before checking out."`
- **Already checked out:** `"You have already checked out for today."`

---

## Important Notes

1. **GPS Coordinates:**
   - Use decimal format (e.g., `24.7136` not `24°42'49"N`)
   - Latitude: -90 to 90
   - Longitude: -180 to 180

2. **Break Tracking:**
   - Route is optional for breaks
   - Multiple breaks per day are supported
   - Total break duration is accumulated automatically

3. **9-Hour Shift:**
   - System tracks 9-hour shifts automatically
   - Work hours exclude break time
   - Remaining shift time is calculated in real-time

4. **Session Status:**
   - `ACTIVE`: Working (not on break)
   - `ON_BREAK`: Currently on break
   - `COMPLETED`: Checked out

5. **Time Tracking:**
   - All times are in UTC
   - Break duration is calculated automatically
   - Total hours worked = (checkout - checkin) - break time


