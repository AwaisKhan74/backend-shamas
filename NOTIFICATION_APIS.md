# Notification APIs Documentation

## Overview

The notification system automatically creates notifications for various events in the application. All notifications are stored in the database and can be accessed via REST APIs.

## Notification Types Implemented

### 1. Leave Management
- **LEAVE_APPROVED** - When a leave request is approved
- **LEAVE_REJECTED** - When a leave request is rejected
- **LEAVE_CANCELLED** - When a leave request is cancelled

### 2. Penalties
- **PENALTY_ISSUED** - When a penalty is issued to a field agent

### 3. Rewards/Points
- **POINTS_EARNED** - When points are earned by a field agent
- **POINTS_DEDUCTED** - When points are deducted from a field agent

### 4. Route Management
- **ROUTE_ASSIGNED** - When a new route is assigned to a field agent
- **ROUTE_APPROVED** - When a route is approved by a manager

### 5. Quality Checks
- **IMAGE_APPROVED** - When an image is approved by quality check
- **IMAGE_REJECTED** - When an image is rejected by quality check

### 6. Store Visits
- **STORE_VISIT_COMPLETED** - When a store visit is completed
- **STORE_VISIT_FLAGGED** - When a store visit is flagged for review

---

## API Endpoints

### Base URL
All notification endpoints are under `/api/notifications/`

### Authentication
All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

### 1. List Notifications
**GET** `/api/notifications/`

Get a paginated list of all notifications for the authenticated user.

**Query Parameters:**
- `is_read` (optional): Filter by read status (`true` or `false`)
- `type` (optional): Filter by notification type (e.g., `LEAVE_APPROVED`, `PENALTY_ISSUED`)
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/notifications/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "notification_type": "LEAVE_APPROVED",
      "notification_type_display": "Leave Approved",
      "title": "Leave Request Approved",
      "message": "Your leave request from 2025-01-15 to 2025-01-20 has been approved.",
      "is_read": false,
      "priority": "MEDIUM",
      "created_at": "2025-01-10T10:30:00Z"
    }
  ]
}
```

---

### 2. Get Notification Details
**GET** `/api/notifications/{id}/`

Get detailed information about a specific notification.

**Response:**
```json
{
  "id": 1,
  "notification_type": "LEAVE_APPROVED",
  "notification_type_display": "Leave Approved",
  "title": "Leave Request Approved",
  "message": "Your leave request from 2025-01-15 to 2025-01-20 has been approved.",
  "priority": "MEDIUM",
  "priority_display": "Medium",
  "is_read": false,
  "read_at": null,
  "created_at": "2025-01-10T10:30:00Z",
  "metadata": {
    "leave_type": "SICK",
    "start_date": "2025-01-15",
    "end_date": "2025-01-20"
  }
}
```

---

### 3. Mark Notification as Read
**POST** `/api/notifications/{id}/mark_read/`

Mark a specific notification as read.

**Response:**
```json
{
  "success": true,
  "message": "Notification marked as read.",
  "notification": {
    "id": 1,
    "notification_type": "LEAVE_APPROVED",
    "notification_type_display": "Leave Approved",
    "title": "Leave Request Approved",
    "message": "Your leave request from 2025-01-15 to 2025-01-20 has been approved.",
    "priority": "MEDIUM",
    "priority_display": "Medium",
    "is_read": true,
    "read_at": "2025-01-10T11:00:00Z",
    "created_at": "2025-01-10T10:30:00Z",
    "metadata": {}
  }
}
```

---

### 4. Mark All Notifications as Read
**POST** `/api/notifications/mark_all_read/`

Mark all unread notifications for the authenticated user as read.

**Response:**
```json
{
  "success": true,
  "message": "15 notifications marked as read.",
  "count": 15
}
```

---

### 5. Get Unread Count
**GET** `/api/notifications/unread_count/`

Get the count of unread notifications for the authenticated user.

**Response:**
```json
{
  "unread_count": 5
}
```

---

### 6. Clear All Read Notifications
**DELETE** `/api/notifications/clear_all/`

Delete all read notifications for the authenticated user.

**Response:**
```json
{
  "success": true,
  "message": "10 notifications deleted.",
  "count": 10
}
```

---

## Automatic Notification Triggers

Notifications are automatically created when the following events occur:

### Leave Management
- When a leave request status changes to `APPROVED`, `REJECTED`, or `CANCELLED`
- Triggered by: `LeaveRequest.status` field update

### Penalties
- When a new penalty is created
- Triggered by: `Penalty` model creation

### Points/Rewards
- When a `PointsTransaction` is created (points earned or deducted)
- Triggered by: `PointsTransaction` model creation

### Route Management
- When a new route is assigned to a field agent
- When a route status changes to `APPROVED`
- Triggered by: `Route` model creation or status update

### Quality Checks
- When an image quality status changes to `APPROVED` or `REJECTED`
- Triggered by: `Image.quality_status` field update

### Store Visits
- When a store visit status changes to `COMPLETED`
- When a store visit status changes to `FLAGGED`
- Triggered by: `StoreVisit.status` field update

---

## User Notification Preferences

Notifications respect user preferences set in the `User` model:

- `push_notifications_enabled` - Master switch for all notifications
- `route_reminders_enabled` - For route-related reminders
- `reward_alerts_enabled` - For points and rewards notifications
- `qc_alerts_enabled` - For quality check notifications

If a user has disabled notifications for a specific type, notifications of that type will not be created.

---

## Notification Priority Levels

- **LOW** - Low priority notifications
- **MEDIUM** - Standard priority (default)
- **HIGH** - High priority notifications (e.g., penalties, rejections)
- **URGENT** - Urgent notifications

---

## Example Usage

### Get all unread notifications
```bash
curl -X GET "http://localhost:8000/api/notifications/?is_read=false" \
  -H "Authorization: Bearer <access_token>"
```

### Get only leave-related notifications
```bash
curl -X GET "http://localhost:8000/api/notifications/?type=LEAVE_APPROVED" \
  -H "Authorization: Bearer <access_token>"
```

### Mark a notification as read
```bash
curl -X POST "http://localhost:8000/api/notifications/1/mark_read/" \
  -H "Authorization: Bearer <access_token>"
```

### Get unread count
```bash
curl -X GET "http://localhost:8000/api/notifications/unread_count/" \
  -H "Authorization: Bearer <access_token>"
```

---

## Database Model

The `Notification` model includes:
- `user` - ForeignKey to User (recipient)
- `notification_type` - Type of notification
- `title` - Notification title
- `message` - Notification message
- `priority` - Priority level
- `is_read` - Read status
- `read_at` - Timestamp when read
- `created_at` - Creation timestamp
- `metadata` - JSON field for additional data
- `related_object` - GenericForeignKey to any related model

---

## Notes

1. All notifications are user-specific - users can only see their own notifications
2. Notifications are automatically created via Django signals
3. Notifications respect user preferences for notification types
4. The system uses pagination for listing notifications (default: 20 per page)
5. Notifications are never automatically deleted (only manually via clear_all endpoint)

