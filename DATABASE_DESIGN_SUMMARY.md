# Database Design Summary - Shams Vision

## Overview

The Shams Vision database is designed to manage field agent operations, route tracking, store visits, rewards/penalties, and administrative functions. The system uses **PostgreSQL** with Django ORM and follows a modular app-based architecture.

---

## Core Architecture

### **User-Centric Design**
- All operations revolve around the `User` model with three roles: **FIELD_AGENT**, **MANAGER**, **ADMIN**
- Role-based access control (RBAC) throughout the system
- Soft delete support (`is_deleted` flag) for data retention

### **Geographical Hierarchy**
```
District → Store → Route → StoreVisit
```
- **Districts**: Geographical regions with priority levels (HIGH, MEDIUM, LOW)
- **Stores**: Physical locations belonging to districts
- **Routes**: Daily assignments linking field agents to stores via districts

---

## Main Database Tables

### 1. **User Management** (`users` app)

#### `User` (Custom AbstractUser)
- **Key Fields**: `work_id` (unique), `role`, `phone_number`, `email`
- **Roles**: FIELD_AGENT, MANAGER, ADMIN
- **Permissions**: GPS/Camera permissions, notification preferences, preferred language
- **Relationships**: 
  - One-to-One with `Counter` (field agent profile)
  - One-to-Many with `CheckIn`, `Route`, `LeaveRequest`, `Penalty`, `Notification`

#### `Counter`
- **Purpose**: Extended profile for field agents
- **Relationship**: One-to-One with `User` (FIELD_AGENT only)
- **Fields**: `employee_id`, uses `user.is_active` for status

---

### 2. **Core Operations** (`core` app)

#### `District`
- **Purpose**: Geographical districts for organizing stores
- **Key Fields**: `name`, `code`, `priority` (HIGH/MEDIUM/LOW), `status`
- **Relationships**: 
  - One-to-Many with `Store` (CASCADE)
  - One-to-Many with `Route` (CASCADE)

#### `Store`
- **Purpose**: Physical store locations
- **Key Fields**: `name`, `address`, `latitude`, `longitude`, `priority`, `status`
- **Relationships**: 
  - Many-to-One with `District` (CASCADE)
  - Many-to-Many with `Route` via `RouteStore`
  - One-to-Many with `StoreVisit`, `Penalty`

#### `Route`
- **Purpose**: Daily work assignments for field agents
- **Key Fields**: `name`, `date`, `status` (PENDING/APPROVED/STARTED/COMPLETED), `district`
- **Relationships**: 
  - Many-to-One with `User` (FIELD_AGENT), `District` (CASCADE)
  - Many-to-Many with `Store` via `RouteStore`
  - One-to-Many with `StoreVisit`

#### `RouteStore`
- **Purpose**: Junction table linking routes to stores with order/priority
- **Key Fields**: `order`, `status` (PENDING/VISITED/SKIPPED)
- **Relationships**: Many-to-One with `Route`, `Store`

#### `FileManager`
- **Purpose**: File uploads (supports S3 and local storage)
- **Key Fields**: `file`, `purpose`, `bucket`, `object_key`, `content_type`, `checksum`
- **Relationships**: Many-to-One with `User`, `Route` (optional)

---

### 3. **Work Sessions** (`operations` app)

#### `CheckIn`
- **Purpose**: Daily work session tracking (9-hour shift)
- **Key Fields**: 
  - `timestamp` (check-in time), `check_out_time`
  - `latitude`, `longitude` (GPS coordinates)
  - `status` (ACTIVE/ON_BREAK/COMPLETED)
  - `current_break_start`, `total_break_duration`
- **Calculated Properties**:
  - `total_hours_worked` = (checkout - checkin) - break_time
  - `remaining_shift_hours` = 9.0 - hours_worked
- **Relationships**: 
  - Many-to-One with `User` (FIELD_AGENT)
  - One-to-Many with `Break`
- **Constraints**: Unique per user per day

#### `Break`
- **Purpose**: Individual break records during work sessions
- **Key Fields**: `start_time`, `end_time`, `duration`
- **Relationships**: 
  - Many-to-One with `User`, `CheckIn` (session), `Route` (optional)
- **Note**: Route is optional - breaks tracked per session, not per route

#### `StoreVisit`
- **Purpose**: Individual store visit tracking
- **Key Fields**: 
  - `entry_time`, `exit_time`, `entry_latitude`, `entry_longitude`
  - `status` (PENDING/COMPLETED/SKIPPED/FLAGGED)
  - `ai_ml_check_status`, `ai_ml_feedback`
- **Relationships**: 
  - Many-to-One with `User`, `Route`, `Store`, `approved_by`
  - One-to-One with `PermissionForm`
  - One-to-Many with `Image`, `FlaggedStore`

#### `Image`
- **Purpose**: Images captured during store visits
- **Key Fields**: `image`, `quality_status` (PENDING/APPROVED/REJECTED)
- **Relationships**: Many-to-One with `StoreVisit`, `quality_checked_by`
- **Note**: Quality status triggers automatic points calculation

#### `PermissionForm`
- **Purpose**: Optional permission forms for store visits
- **Key Fields**: 
  - `representative_name`, `representative_designation`, `representative_contact`
  - `permission_received`, `signature` (FileManager FK)
  - `is_flagged`
- **Relationships**: One-to-One with `StoreVisit`

#### `FlaggedStore`
- **Purpose**: Track flagged stores with reasons
- **Key Fields**: `reason`, `additional_details`, `is_resolved`, `resolution_notes`
- **Relationships**: One-to-One with `StoreVisit`, Many-to-One with `flagged_by`, `resolved_by`

---

### 4. **Leave Management** (`leaves` app)

#### `LeaveRequest`
- **Purpose**: Employee leave requests
- **Key Fields**: 
  - `leave_type` (SICK/CASUAL), `start_date`, `end_date`
  - `status` (PENDING/APPROVED/REJECTED/CANCELLED)
  - `document` (FileManager FK)
- **Relationships**: 
  - Many-to-One with `requested_by` (FIELD_AGENT), `approver` (MANAGER/ADMIN)
- **Note**: Status changes trigger notifications

---

### 5. **Rewards & Points** (`finance` app)

#### `Reward`
- **Purpose**: Reward type definitions
- **Key Fields**: `name`, `points_required`, `value`, `is_active`
- **Relationships**: One-to-Many with `UserReward`

#### `UserReward`
- **Purpose**: Rewards awarded to users
- **Key Fields**: `amount`, `status` (EARNED/WITHDRAWN/EXPIRED), `activity_type`, `points_earned`
- **Relationships**: 
  - Many-to-One with `User` (FIELD_AGENT), `Reward`, `store_visit`

#### `UserPoints`
- **Purpose**: User points balance tracking
- **Key Fields**: `total_points`, `available_points`, `lifetime_points`
- **Relationships**: One-to-One with `User` (FIELD_AGENT)
- **Methods**: `add_points()`, `deduct_points()`

#### `PointsTransaction`
- **Purpose**: Log all points changes
- **Key Fields**: 
  - `transaction_type` (EARNED/DEDUCTED/REDEEMED)
  - `points`, `activity_type`, `description`
- **Relationships**: 
  - Many-to-One with `User`, `store_visit`, `store`, `route`
- **Note**: All points changes are logged here

---

### 6. **Penalties** (`administration` app)

#### `Penalty`
- **Purpose**: Penalties issued to field agents
- **Key Fields**: 
  - `amount`, `reason`, `penalty_type` (FINANCIAL/WARNING)
  - `points_deducted`, `issued_at`
- **Relationships**: 
  - Many-to-One with `user`, `store`, `route`, `store_visit`, `issued_by` (MANAGER/ADMIN)
- **Note**: Penalty creation triggers notifications

#### `DailySummary`
- **Purpose**: Daily performance summaries for field agents
- **Key Fields**: `date`, `total_visits`, `completed_visits`, `skipped_visits`
- **Relationships**: Many-to-One with `user` (FIELD_AGENT)

---

### 7. **Notifications** (`notifications` app)

#### `Notification`
- **Purpose**: In-app notifications with polymorphic relationships
- **Key Fields**: 
  - `notification_type`, `title`, `message`, `priority`
  - `is_read`, `read_at`, `metadata` (JSON)
- **Relationships**: 
  - Many-to-One with `User`
  - Generic ForeignKey to any model (polymorphic)
- **Types**: LEAVE_APPROVED, ROUTE_ASSIGNED, PENALTY_ISSUED, POINTS_EARNED, etc.
- **Note**: Created automatically via Django signals

---

## Key Relationships Diagram

```
User (FIELD_AGENT)
├── Counter (One-to-One)
├── CheckIn (One-to-Many) → Break (One-to-Many)
├── Route (One-to-Many) → RouteStore → Store
│                         └── StoreVisit → Image, PermissionForm, FlaggedStore
├── LeaveRequest (One-to-Many)
├── Penalty (One-to-Many)
├── UserPoints (One-to-One)
├── UserReward (One-to-Many)
├── PointsTransaction (One-to-Many)
└── Notification (One-to-Many)

District
├── Store (One-to-Many)
└── Route (One-to-Many)

Store
├── RouteStore (Many-to-Many via RouteStore)
├── StoreVisit (One-to-Many)
└── Penalty (One-to-Many)
```

---

## How the System Works

### 1. **Daily Workflow**

#### Morning: Check-in
1. Field agent calls `POST /api/operations/sessions/start-day/` with GPS
2. System creates `CheckIn` record with `timestamp` and GPS coordinates
3. Session status = `ACTIVE`

#### During Day: Route Execution
1. Manager assigns `Route` to field agent with stores via `RouteStore`
2. Field agent visits stores, creating `StoreVisit` records
3. Each visit can have multiple `Image` records
4. Optional `PermissionForm` can be submitted
5. Store can be flagged via `FlaggedStore` if issues occur

#### Breaks
1. Field agent calls `POST /api/operations/sessions/take-break/`
2. System records `current_break_start` in `CheckIn`
3. Creates `Break` record with `start_time`
4. Session status = `ON_BREAK`
5. On resume, calculates duration and adds to `total_break_duration`

#### Evening: Check-out
1. Field agent calls `POST /api/operations/sessions/check-out/` with GPS
2. System calculates:
   - `total_hours_worked` = (checkout - checkin) - break_time
   - `remaining_shift_hours` = 9.0 - hours_worked
3. Session status = `COMPLETED`

---

### 2. **Points & Rewards System**

#### Automatic Points Calculation
- **Store Visit Completed**: Points awarded via `PointsCalculationService`
- **Image Quality Approved**: Bonus points added
- **Image Quality Rejected**: Points deducted
- **Store Visit Missed**: Points deducted

#### Points Flow
1. `StoreVisit` or `Image` saved → Django signal triggered
2. `PointsCalculationService` calculates points
3. `UserPoints` balance updated
4. `PointsTransaction` record created (audit trail)
5. `UserReward` created if reward threshold met
6. Notification sent to user

#### Points Structure
- **UserPoints**: Current balance (total, available, lifetime)
- **PointsTransaction**: All changes logged (EARNED/DEDUCTED/REDEEMED)
- **UserReward**: Rewards earned based on points

---

### 3. **Leave Management**

1. Field agent creates `LeaveRequest` with dates and type
2. Status = `PENDING`
3. Manager/Admin approves/rejects via `PATCH /api/leaves/{id}/status/`
4. Status updated, `approver` and `approved_at` set
5. Notification sent to field agent

---

### 4. **Penalty System**

1. Manager/Admin creates `Penalty` for violations
2. Links to `user`, `store`, `route`, `store_visit` (optional)
3. `points_deducted` automatically deducted from `UserPoints`
4. `PointsTransaction` created (DEDUCTED type)
5. Notification sent to field agent

---

### 5. **Notification System**

#### Automatic Notifications (via Django Signals)
- **Leave Status Change**: When `LeaveRequest.status` changes
- **Route Assigned/Approved**: When `Route` created or status changes
- **Penalty Issued**: When `Penalty` created
- **Points Earned/Deducted**: When `PointsTransaction` created
- **Image Quality Check**: When `Image.quality_status` changes
- **Store Visit Status**: When `StoreVisit.status` changes to COMPLETED/FLAGGED

#### Notification Features
- Polymorphic relationships (can link to any model)
- User preferences respected (`push_notifications_enabled`, etc.)
- Priority levels (LOW, MEDIUM, HIGH, URGENT)
- Read/unread tracking

---

## Database Design Principles

### 1. **Data Integrity**
- Foreign keys with appropriate `on_delete` strategies
- Unique constraints (e.g., one check-in per user per day)
- Validation at model level (GPS coordinates, phone numbers)

### 2. **Performance**
- Database indexes on frequently queried fields
- `select_related()` and `prefetch_related()` for efficient queries
- Soft deletes for data retention without breaking relationships

### 3. **Audit Trail**
- `created_at`, `updated_at` timestamps on all models
- `PointsTransaction` logs all points changes
- `Notification` tracks all system events

### 4. **Flexibility**
- Generic ForeignKey in `Notification` for polymorphic relationships
- JSON fields (`metadata`) for extensible data
- Status fields with choices for workflow management

### 5. **Scalability**
- Modular app structure
- Separation of concerns (operations, finance, administration)
- Efficient query patterns

---

## Key Features

### ✅ **9-Hour Shift Tracking**
- Automatic calculation of work hours
- Break time tracking and accumulation
- Real-time remaining shift time

### ✅ **Points & Rewards**
- Automatic points calculation on store visits
- Quality-based bonus/deduction
- Reward redemption system

### ✅ **Geographical Organization**
- District-based store organization
- Route assignment by district
- Priority-based operations

### ✅ **Comprehensive Tracking**
- GPS coordinates for check-in/out and store visits
- Image capture with quality checks
- Permission forms for compliance

### ✅ **Role-Based Access**
- Three-tier role system (FIELD_AGENT, MANAGER, ADMIN)
- Permission-based API access
- Data filtering by role

### ✅ **Notification System**
- Real-time notifications for all key events
- User preference management
- Polymorphic relationships for flexibility

---

## Summary

The Shams Vision database is a **comprehensive field agent management system** that:
- Tracks daily work sessions with 9-hour shift monitoring
- Manages routes and store visits with GPS tracking
- Automatically calculates and awards points/rewards
- Handles leave requests and penalties
- Provides real-time notifications
- Maintains complete audit trails

The design emphasizes **data integrity**, **performance**, and **scalability** while supporting complex workflows through well-defined relationships and automated processes.


