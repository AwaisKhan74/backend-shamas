# How Break and Work Hours Tracking Works

## Overview

The system tracks break hours and worked hours **automatically on the server-side** using timestamps. The payload can be empty because **the server records all time information automatically**.

---

## How It Works: Server-Side Automatic Tracking

### 1. **Take Break** - What Happens Behind the Scenes

When you call `POST /api/operations/sessions/take-break/` with an empty payload `{}`:

**Server automatically:**
1. Records the **current server time** as break start time: `start_time = timezone.now()`
2. Updates session status to `ON_BREAK`
3. Stores `current_break_start` in the `CheckIn` model
4. Creates a `Break` record with the start time

**Code Implementation:**
```python
# In views.py - take_break action
start_time = timezone.now()  # Server records current time
session.start_break(start_time=start_time)  # Updates session

# Creates Break record
break_entry = Break.objects.create(
    user=user,
    session=session,
    route=route,  # Optional
    start_time=start_time,  # Server timestamp
)
```

**Database Fields Updated:**
- `CheckIn.current_break_start` = `2025-01-20 13:00:00` (server time)
- `CheckIn.status` = `ON_BREAK`
- `Break.start_time` = `2025-01-20 13:00:00` (server time)

---

### 2. **Resume Day** - Break Duration Calculation

When you call `POST /api/operations/sessions/resume-day/` with an empty payload `{}`:

**Server automatically:**
1. Records the **current server time** as break end time: `end_time = timezone.now()`
2. Calculates break duration: `duration = end_time - start_time`
3. Adds duration to `total_break_duration` in `CheckIn` model
4. Clears `current_break_start`
5. Updates session status to `ACTIVE`

**Code Implementation:**
```python
# In views.py - resume_day action
end_time = timezone.now()  # Server records current time
active_break.end_time = end_time
active_break.calculate_duration()  # Calculates: end_time - start_time
active_break.save()

# Updates CheckIn model
break_duration = session.resume_from_break(end_time=end_time)
# This adds the break duration to total_break_duration
```

**Break Duration Calculation:**
```python
# In models.py - resume_from_break method
def resume_from_break(self, end_time=None):
    if not self.current_break_start:
        raise ValueError("No active break to resume from.")
    end_time = end_time or timezone.now()
    duration = end_time - self.current_break_start  # Calculate duration
    self.total_break_duration += duration  # Add to total
    self.current_break_start = None
    self.status = self.Status.ACTIVE
    self.save()
    return duration
```

**Example:**
- Break started: `2025-01-20 13:00:00`
- Break ended: `2025-01-20 13:30:00`
- Break duration: `0:30:00` (30 minutes)
- `total_break_duration` = `0:30:00`

---

### 3. **Work Hours Calculation** - Automatic Real-Time Tracking

Work hours are calculated **automatically** using this formula:

```
Total Work Hours = (Check-out Time - Check-in Time) - Total Break Duration
```

**Code Implementation:**
```python
# In models.py - total_hours_worked property
@property
def total_hours_worked(self):
    if not self.check_out_time:
        # If not checked out, calculate from start to now (minus breaks)
        now = timezone.now()
        if self.current_break_start:
            # If on break, don't count break time
            total_time = (self.current_break_start - self.timestamp) - self.total_break_duration
        else:
            total_time = (now - self.timestamp) - self.total_break_duration
    else:
        # If checked out, calculate from start to checkout (minus breaks)
        total_time = (self.check_out_time - self.timestamp) - self.total_break_duration
    
    return total_time.total_seconds() / 3600.0  # Convert to hours
```

---

## Complete Example: How Hours Are Tracked

### Scenario: User works 9 hours with 1 break

**1. Check-in at 9:00 AM**
```
POST /api/operations/sessions/start-day/
{
    "latitude": 24.7136,
    "longitude": 46.6753
}

Server records:
- timestamp = 2025-01-20 09:00:00
- status = ACTIVE
```

**2. Work until 1:00 PM (4 hours worked)**
```
Current state:
- timestamp = 09:00:00
- current_time = 13:00:00
- total_break_duration = 0:00:00
- total_hours_worked = (13:00 - 09:00) - 0:00 = 4.0 hours
```

**3. Take break at 1:00 PM**
```
POST /api/operations/sessions/take-break/
{}

Server automatically:
- current_break_start = 2025-01-20 13:00:00 (server time)
- status = ON_BREAK
- Break.start_time = 2025-01-20 13:00:00
```

**4. Resume at 1:30 PM (30-minute break)**
```
POST /api/operations/sessions/resume-day/
{}

Server automatically:
- end_time = 2025-01-20 13:30:00 (server time)
- break_duration = 13:30 - 13:00 = 0:30:00 (30 minutes)
- total_break_duration = 0:30:00
- current_break_start = null
- status = ACTIVE
```

**5. Work until 6:00 PM**
```
Current state:
- timestamp = 09:00:00
- current_time = 18:00:00
- total_break_duration = 0:30:00
- total_hours_worked = (18:00 - 09:00) - 0:30 = 8.5 hours
```

**6. Check-out at 6:00 PM**
```
POST /api/operations/sessions/check-out/
{
    "latitude": 24.7136,
    "longitude": 46.6753
}

Server automatically:
- check_out_time = 2025-01-20 18:00:00
- total_hours_worked = (18:00 - 09:00) - 0:30 = 8.5 hours
- break_duration_hours = 0.5 hours
- remaining_shift_hours = 9.0 - 8.5 = 0.5 hours
```

---

## Database Fields That Track Time

### CheckIn Model Fields:
- `timestamp` - Check-in time (set on start-day)
- `current_break_start` - Start time of current break (set on take-break, cleared on resume)
- `total_break_duration` - Cumulative break time (updated on resume)
- `check_out_time` - Check-out time (set on check-out)

### Break Model Fields:
- `start_time` - Break start time (set on take-break)
- `end_time` - Break end time (set on resume)
- `duration` - Break duration (calculated on resume)

---

## Why Payload Can Be Empty

The payload is empty because:

1. **Server Records Time Automatically**
   - Server uses `timezone.now()` to get current time
   - No need for client to send time (prevents time manipulation)

2. **Accurate Time Tracking**
   - Server time is always accurate (UTC)
   - No timezone issues
   - No clock synchronization problems

3. **Security**
   - Client cannot manipulate break/work hours
   - All time calculations done server-side

4. **Simplicity**
   - Client just needs to call the endpoint
   - No need to calculate or send time data

---

## How to View Tracked Hours

### Get Current Session
```
GET /api/operations/sessions/current/
```

**Response includes:**
```json
{
    "success": true,
    "session": {
        "id": 1,
        "timestamp": "2025-01-20T09:00:00Z",
        "check_out_time": null,
        "status": "ACTIVE",
        "current_break_start": null,
        "total_break_duration": "0:30:00",
        "total_break_seconds": 1800,
        "total_hours_worked": 4.5,
        "total_hours_worked_seconds": 16200,
        "break_duration_hours": 0.5,
        "break_duration_seconds": 1800,
        "remaining_shift_hours": 4.0,
        "remaining_shift_seconds": 14400
    },
    "breaks": [
        {
            "id": 1,
            "start_time": "2025-01-20T13:00:00Z",
            "end_time": "2025-01-20T13:30:00Z",
            "duration": "0:30:00",
            "duration_seconds": 1800
        }
    ]
}
```

---

## Multiple Breaks Support

The system supports **multiple breaks per day**. Each break is tracked separately:

**Example:**
- Break 1: 1:00 PM - 1:30 PM (30 minutes)
- Break 2: 3:00 PM - 3:15 PM (15 minutes)
- Total break duration: 45 minutes

**How it works:**
1. Each `take-break` creates a new `Break` record
2. Each `resume-day` calculates that break's duration
3. All break durations are added to `total_break_duration`
4. Work hours = (total time) - (total_break_duration)

---

## Summary

✅ **Break tracking is automatic** - Server records start/end times
✅ **Work hours are calculated automatically** - Formula: (total time) - (break time)
✅ **No payload needed** - Server handles all time tracking
✅ **Real-time updates** - Hours calculated on-the-fly
✅ **Accurate and secure** - Server-side time prevents manipulation
✅ **Multiple breaks supported** - All breaks are accumulated

The system is designed to be **simple for the client** (just call endpoints) while being **robust and accurate on the server** (automatic time tracking).


