# Notification APIs & Trigger Points

## 📱 Notification APIs Created

I created **6 API endpoints** for managing notifications:

### Base URL: `/api/notifications/`

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | **GET** | `/api/notifications/` | List all notifications (paginated, filterable) |
| 2 | **GET** | `/api/notifications/{id}/` | Get notification details |
| 3 | **POST** | `/api/notifications/{id}/mark_read/` | Mark a notification as read |
| 4 | **POST** | `/api/notifications/mark_all_read/` | Mark all notifications as read |
| 5 | **GET** | `/api/notifications/unread_count/` | Get count of unread notifications |
| 6 | **DELETE** | `/api/notifications/clear_all/` | Delete all read notifications |

**Query Parameters for List API:**
- `is_read` - Filter by read status (`true`/`false`)
- `type` - Filter by notification type (e.g., `LEAVE_APPROVED`, `PENALTY_ISSUED`)
- `page` - Page number for pagination

---

## 🔔 Notification Trigger Points

Notifications are **automatically created** when specific actions occur in other features. Here's where each notification is triggered:

---

### 1. ✅ Leave Management Notifications

#### **LEAVE_APPROVED** Notification
**Triggered When:**
- A leave request status is changed to `APPROVED`
- **API/Feature:** Leave Request Management (`/api/leaves/{id}/status/`)
- **Action:** Manager/Admin approves a leave request
- **Signal:** `post_save` on `LeaveRequest` model when `status` changes to `APPROVED`

**Example:**
```python
# When this happens:
PATCH /api/leaves/1/status/
{
  "status": "APPROVED"
}

# Notification is automatically created for the requester
```

---

#### **LEAVE_REJECTED** Notification
**Triggered When:**
- A leave request status is changed to `REJECTED`
- **API/Feature:** Leave Request Management (`/api/leaves/{id}/status/`)
- **Action:** Manager/Admin rejects a leave request
- **Signal:** `post_save` on `LeaveRequest` model when `status` changes to `REJECTED`

**Example:**
```python
# When this happens:
PATCH /api/leaves/1/status/
{
  "status": "REJECTED"
}

# Notification is automatically created for the requester
```

---

#### **LEAVE_CANCELLED** Notification
**Triggered When:**
- A leave request status is changed to `CANCELLED`
- **API/Feature:** Leave Request Management (`/api/leaves/{id}/cancel/`)
- **Action:** User cancels their own leave request OR Manager/Admin cancels it
- **Signal:** `post_save` on `LeaveRequest` model when `status` changes to `CANCELLED`

**Example:**
```python
# When this happens:
PATCH /api/leaves/1/cancel/
{
  "status": "CANCELLED"
}

# Notification is automatically created for the requester
```

---

### 2. ✅ Penalty Notifications

#### **PENALTY_ISSUED** Notification
**Triggered When:**
- A new penalty is created
- **API/Feature:** Penalty Management (`/api/administration/penalties/`)
- **Action:** Manager/Admin creates a penalty for a field agent
- **Signal:** `post_save` on `Penalty` model when a new penalty is created

**Example:**
```python
# When this happens:
POST /api/administration/penalties/
{
  "user": 5,
  "penalty_type": "FINANCIAL",
  "amount": 100.00,
  "points_deducted": 50,
  "reason": "Skipped store visit"
}

# Notification is automatically created for the penalized user
```

---

### 3. ✅ Rewards/Points Notifications

#### **POINTS_EARNED** Notification
**Triggered When:**
- A `PointsTransaction` is created with positive points
- **API/Feature:** Points System (automatic via signals)
- **Action:** Points are automatically awarded when:
  - Store visit is completed
  - Image quality is approved
  - Perfect visit bonus is earned
- **Signal:** `post_save` on `PointsTransaction` model when `points > 0`

**Example:**
```python
# When this happens automatically:
# Store visit completed → PointsTransaction created with points=100

# Notification is automatically created: "100 Points Earned"
```

---

#### **POINTS_DEDUCTED** Notification
**Triggered When:**
- A `PointsTransaction` is created with negative points
- **API/Feature:** Points System (automatic via signals)
- **Action:** Points are automatically deducted when:
  - Store visit is skipped
  - Image is rejected
  - Penalty is issued
- **Signal:** `post_save` on `PointsTransaction` model when `points < 0`

**Example:**
```python
# When this happens automatically:
# Store visit skipped → PointsTransaction created with points=-50

# Notification is automatically created: "50 Points Deducted"
```

---

### 4. ✅ Route Management Notifications

#### **ROUTE_ASSIGNED** Notification
**Triggered When:**
- A new route is created and assigned to a field agent
- **API/Feature:** Route Management (via admin or API)
- **Action:** Manager/Admin creates a new route with a field agent assigned
- **Signal:** `post_save` on `Route` model when a new route is created with `user` field set

**Example:**
```python
# When this happens:
POST /api/core/routes/  # or via admin
{
  "name": "Route 1",
  "user": 3,  # Field agent ID
  "date": "2025-01-20"
}

# Notification is automatically created: "New Route Assigned"
```

---

#### **ROUTE_APPROVED** Notification
**Triggered When:**
- A route status changes from non-APPROVED to `APPROVED`
- **API/Feature:** Route Management (via admin or API)
- **Action:** Manager approves a pending route
- **Signal:** `post_save` on `Route` model when `status` changes to `APPROVED` and `approved_by` is set

**Example:**
```python
# When this happens:
PATCH /api/core/routes/1/
{
  "status": "APPROVED",
  "approved_by": 2  # Manager ID
}

# Notification is automatically created: "Route Approved"
```

---

### 5. ✅ Quality Check Notifications

#### **IMAGE_APPROVED** Notification
**Triggered When:**
- An image's `quality_status` changes to `APPROVED`
- **API/Feature:** Image Quality Check (via admin or API)
- **Action:** Manager/Admin/QC reviewer approves an image
- **Signal:** `post_save` on `Image` model when `quality_status` changes from non-APPROVED to `APPROVED`

**Example:**
```python
# When this happens:
PATCH /api/operations/images/1/
{
  "quality_status": "APPROVED",
  "quality_checked_by": 2  # Manager ID
}

# Notification is automatically created: "Image Approved"
```

---

#### **IMAGE_REJECTED** Notification
**Triggered When:**
- An image's `quality_status` changes to `REJECTED`
- **API/Feature:** Image Quality Check (via admin or API)
- **Action:** Manager/Admin/QC reviewer rejects an image
- **Signal:** `post_save` on `Image` model when `quality_status` changes from non-REJECTED to `REJECTED`

**Example:**
```python
# When this happens:
PATCH /api/operations/images/1/
{
  "quality_status": "REJECTED",
  "quality_checked_by": 2  # Manager ID
}

# Notification is automatically created: "Image Rejected"
```

---

### 6. ✅ Store Visit Notifications

#### **STORE_VISIT_COMPLETED** Notification
**Triggered When:**
- A store visit status changes to `COMPLETED`
- **API/Feature:** Store Visit Management (`/api/operations/store-visits/{id}/complete/`)
- **Action:** Field agent completes a store visit
- **Signal:** `post_save` on `StoreVisit` model when `status` changes to `COMPLETED`

**Example:**
```python
# When this happens:
POST /api/operations/store-visits/1/complete/
{
  "exit_time": "2025-01-20T15:30:00Z",
  "exit_latitude": 24.7136,
  "exit_longitude": 46.6753
}

# Notification is automatically created: "Store Visit Completed"
```

---

#### **STORE_VISIT_FLAGGED** Notification
**Triggered When:**
- A store visit status changes to `FLAGGED` OR is created with `FLAGGED` status
- **API/Feature:** Store Visit Flagging (`/api/operations/store-visits/{id}/flag-store/`)
- **Action:** Manager/Admin flags a store visit for review OR field agent flags it
- **Signal:** `post_save` on `StoreVisit` model when `status` changes to `FLAGGED` or is created as `FLAGGED`

**Example:**
```python
# When this happens:
POST /api/operations/store-visits/1/flag-store/
{
  "reason": "Quality issues",
  "additional_details": "Images are blurry"
}

# Notification is automatically created: "Store Visit Flagged"
```

---

## 📊 Summary Table

| Notification Type | Trigger Feature | Trigger API/Action | Signal Model |
|------------------|----------------|-------------------|--------------|
| **LEAVE_APPROVED** | Leave Management | `PATCH /api/leaves/{id}/status/` with `status=APPROVED` | `LeaveRequest` |
| **LEAVE_REJECTED** | Leave Management | `PATCH /api/leaves/{id}/status/` with `status=REJECTED` | `LeaveRequest` |
| **LEAVE_CANCELLED** | Leave Management | `PATCH /api/leaves/{id}/cancel/` | `LeaveRequest` |
| **PENALTY_ISSUED** | Penalty Management | `POST /api/administration/penalties/` | `Penalty` |
| **POINTS_EARNED** | Points System | Automatic (store visit completed, image approved) | `PointsTransaction` |
| **POINTS_DEDUCTED** | Points System | Automatic (store visit skipped, image rejected) | `PointsTransaction` |
| **ROUTE_ASSIGNED** | Route Management | `POST /api/core/routes/` (new route created) | `Route` |
| **ROUTE_APPROVED** | Route Management | `PATCH /api/core/routes/{id}/` with `status=APPROVED` | `Route` |
| **IMAGE_APPROVED** | Quality Check | `PATCH /api/operations/images/{id}/` with `quality_status=APPROVED` | `Image` |
| **IMAGE_REJECTED** | Quality Check | `PATCH /api/operations/images/{id}/` with `quality_status=REJECTED` | `Image` |
| **STORE_VISIT_COMPLETED** | Store Visits | `POST /api/operations/store-visits/{id}/complete/` | `StoreVisit` |
| **STORE_VISIT_FLAGGED** | Store Visits | `POST /api/operations/store-visits/{id}/flag-store/` | `StoreVisit` |

---

## 🔧 How It Works

1. **User performs an action** (e.g., approves leave, creates penalty)
2. **Django model is saved** (via API or admin)
3. **Django signal fires** (`post_save` signal)
4. **Signal handler checks** if notification should be created
5. **NotificationService creates notification** if user preferences allow
6. **Notification stored in database** and available via API

---

## ⚙️ User Preferences

Notifications respect user preferences:
- If `push_notifications_enabled = False` → No notifications created
- If `reward_alerts_enabled = False` → No points/rewards notifications
- If `qc_alerts_enabled = False` → No quality check notifications
- If `route_reminders_enabled = False` → No route reminder notifications

---

## 📝 Notes

- All notifications are created **automatically** via Django signals
- No manual API calls needed to create notifications
- Notifications are **user-specific** - each user only sees their own notifications
- Notifications are stored in the database and persist until deleted
- The notification system is **non-blocking** - it doesn't affect the main API response

