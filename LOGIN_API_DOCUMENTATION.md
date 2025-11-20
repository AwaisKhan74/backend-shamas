# Login API Documentation

## Overview

JWT-based authentication API with refresh tokens. Users can login directly with their credentials (work_id or email + password) and receive JWT tokens for authenticated API requests.

**Authentication Method:** JWT (JSON Web Tokens) with refresh tokens  
**Token Lifetime:** Access tokens expire in 1 hour, refresh tokens expire in 7 days  
**Token Rotation:** Enabled - refresh tokens are rotated on each use  
**Token Blacklisting:** Enabled - revoked tokens are blacklisted

## Base URL

```
http://127.0.0.1:8000/api/auth/
```

---

## Authentication Endpoints

### 1. Login

**Endpoint**: `POST /api/auth/login/`

**Description**: Authenticate user and create session.

**Authentication**: Not required (public endpoint)

**Request Body**:
```json
{
  "work_id": "ADMIN001",  // Optional: Use work_id OR email
  "email": "admin@shamsvision.com",  // Optional: Use email OR work_id
  "password": "admin123"  // Required
}
```

**Example Request** (using work_id):
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "work_id": "ADMIN001",
    "password": "admin123"
  }'
```

**Example Request** (using email):
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@shamsvision.com",
    "password": "admin123"
  }'
```

**Success Response** (200 OK):
```json
{
"success": true,
"message": "Login successful",
"access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
"token_type": "Bearer",
"expires_in": 3600,
"user_role": "ADMIN",
"user": {
  "id": 1,
  "work_id": "ADMIN001",
  "username": "admin",
  "email": "admin@shamsvision.com",
  "first_name": "Admin",
  "last_name": "User",
  "full_name": "Admin User",
  "display_name": "Mehroz Daniyal",
  "phone_number": "+966512345678",
  "role": "ADMIN",
  "role_display": "Admin",
  "status": "ONLINE",
  "profile_image": null,
  "has_gps_permission": false,
  "has_camera_permission": false,
  "country": "Saudi Arabia",
  "city": "Makkah",
  "address": "123 Sunset Boulevard",
  "is_active": true,
  "date_joined": "2025-11-03T10:00:00Z",
  "last_login": "2025-11-06T07:30:00Z",
  "created_at": "2025-11-03T10:00:00Z",
  "updated_at": "2025-11-06T07:30:00Z"
}
}
```

**Response Fields:**
- `access_token`: JWT access token (valid for 1 hour) - use in `Authorization: Bearer <token>` header
- `refresh_token`: JWT refresh token (valid for 7 days) - use to get new access tokens
- `token_type`: Always "Bearer"
- `expires_in`: Access token expiration time in seconds (3600 = 1 hour)
- `user_role`: Role code (e.g., `FIELD_AGENT`, `MANAGER`, `ADMIN`)
- `user.display_name`: Public name shown to other users
- `user.status`: Current availability (`ONLINE`, `OFFLINE`, `AWAY`)
- `user.profile_image`: Absolute URL for profile image (if uploaded)
- `user.country`, `user.city`, `user.address`: Location information stored on the user record

**Error Response** (400 Bad Request):
```json
{
  "success": false,
  "errors": {
    "error": "Invalid credentials."
  }
}
```

**Error Response** (400 Bad Request - Missing credentials):
```json
{
  "success": false,
  "errors": {
    "error": "Either work_id or email is required."
  }
}
```

**Error Response** (400 Bad Request - Account disabled):
```json
{
  "success": false,
  "errors": {
    "error": "User account is disabled."
  }
}
```

---

### 2. Profile (View)

**Endpoint**: `GET /api/auth/profile/`

**Description**: Fetch the authenticated user's profile details exactly as entered during account setup (display name, account ID, country, city, address, etc.). Also returns contact details and status, along with the absolute URL of the profile image when available.

**Authentication**: Required (Bearer token)

**Headers**:
```
Authorization: Bearer <access_token>
```

**Example Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer <access_token>"
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "user_role": "FIELD_AGENT",
"profile": {
  "id": 5,
  "work_id": "FA001",
  "username": "mehroz",
  "email": "mehroz@example.com",
  "first_name": "Mehroz",
  "last_name": "Daniyal",
  "full_name": "Mehroz Daniyal",
  "display_name": "Mehroz Daniyal",
  "phone_number": "+966512345678",
  "role": "FIELD_AGENT",
  "role_display": "Field Agent",
  "status": "ONLINE",
  "country": "Saudi Arabia",
  "city": "Makkah",
  "address": "123 Sunset Boulevard",
  "profile_picture": null,
  "profile_image": "http://127.0.0.1:8000/media/profile_pictures/mehroz.png",
  "has_gps_permission": true,
  "has_camera_permission": true,
  "is_active": true,
  "date_joined": "2025-11-03T10:00:00Z",
  "last_login": "2025-11-06T07:30:00Z",
  "created_at": "2025-11-03T10:00:00Z",
  "updated_at": "2025-11-06T07:30:00Z"
}
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 3. Profile (Update)

**Endpoint**: `PUT /api/auth/profile/update/` (or `PATCH` for partial updates)

**Description**: Update the authenticated user's profile information (display name, country, city, address, availability status) and linked user fields (first name, last name, phone number, profile image).

**Authentication**: Required (Bearer token)

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data  # Required when uploading profile_picture
```

**Request Body Fields** (send only the fields you want to update):
- `display_name` *(string, optional)*
- `status` *(string, optional; one of `ONLINE`, `OFFLINE`, `AWAY`)*
- `country` *(string, optional)*
- `city` *(string, optional)*
- `address` *(string, optional)*
- `first_name` *(string, optional)*
- `last_name` *(string, optional)*
- `phone_number` *(string, optional, unique)*
- `profile_picture` *(image, optional)*

**Example Request** (JSON payload):
```bash
curl -X PATCH http://127.0.0.1:8000/api/auth/profile/update/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Mehroz Daniyal",
    "status": "ONLINE",
    "country": "Saudi Arabia",
    "city": "Makkah",
    "address": "123 Sunset Boulevard",
    "first_name": "Mehroz",
    "last_name": "Daniyal",
    "phone_number": "+966512345678"
  }'
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "user_role": "FIELD_AGENT",
  "profile": {
    "id": 5,
    "work_id": "FA001",
    "username": "mehroz",
    "email": "mehroz@example.com",
    "first_name": "Mehroz",
    "last_name": "Daniyal",
    "full_name": "Mehroz Daniyal",
    "display_name": "Mehroz Daniyal",
    "phone_number": "+966512345678",
    "role": "FIELD_AGENT",
    "role_display": "Field Agent",
    "status": "ONLINE",
    "country": "Saudi Arabia",
    "city": "Makkah",
    "address": "123 Sunset Boulevard",
    "profile_image": "http://127.0.0.1:8000/media/profile_pictures/mehroz.png",
    "has_gps_permission": true,
    "has_camera_permission": true,
    "is_active": true,
    "date_joined": "2025-11-03T10:00:00Z",
    "last_login": "2025-11-06T08:05:00Z",
    "created_at": "2025-11-03T10:00:00Z",
    "updated_at": "2025-11-06T08:05:00Z"
  }
}
```

**Validation Errors** (400 Bad Request):
```json
{
  "success": false,
  "errors": {
    "phone_number": ["A user with this phone number already exists."]
  }
}
```

---

### 4. Delete User (Admin)

**Endpoint**: `DELETE /api/auth/users/{user_id}/delete/`

**Description**: Soft delete a user. Only admins can call this endpoint. The user record remains in the database but is flagged as deleted and `is_active` is set to `False`, preventing future logins.

**Authentication**: Required (Bearer token, admin only)

**Headers**:
```
Authorization: Bearer <admin_access_token>
```

**Example Request**:
```bash
ADMIN_TOKEN="<ADMIN_ACCESS_TOKEN>"
USER_ID=42

curl -X DELETE http://127.0.0.1:8000/api/auth/users/${USER_ID}/delete/ \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "User FA001 soft-deleted successfully."
}
```

**Error Responses**:
- **400 Bad Request** – Admin attempts to delete their own account.
- **403 Forbidden** – Caller is not an admin.
- **404 Not Found** – User already deleted or does not exist.

---

### 5. Update User (Admin)

**Endpoint**: `PATCH /api/auth/users/{user_id}/update/`  
**Alternate Method**: `PUT /api/auth/users/{user_id}/update/`

**Description**: Update another user's details. Only admins can call this endpoint. Supports partial updates (PATCH) or full updates (PUT).

**Authentication**: Required (Bearer token, admin only)

**Headers**:
```
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

**Payload Fields** (all optional; only provided fields are updated):
- `work_id` *(string, unique)*
- `username` *(string, unique)*
- `email` *(string, unique)*
- `first_name`, `last_name`, `display_name`
- `status` *(ONLINE, OFFLINE, AWAY)*
- `role` *(FIELD_AGENT, MANAGER, ADMIN)*
- `phone_number` *(E.164, unique)*
- `country`, `city`, `address`
- `has_gps_permission`, `has_camera_permission` *(boolean)*
- `is_active` *(boolean)*
- `profile_picture` *(multipart upload)*

**Example Request** (PATCH JSON payload):
```bash
ADMIN_TOKEN="<ADMIN_ACCESS_TOKEN>"
USER_ID=42

curl -X PATCH http://127.0.0.1:8000/api/auth/users/${USER_ID}/update/ \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
        "role": "MANAGER",
        "status": "ONLINE",
        "display_name": "Team Lead",
        "has_gps_permission": true
      }'
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "user": {
    "id": 42,
    "work_id": "MN001",
    "username": "manager01",
    "email": "manager@example.com",
    "first_name": "Team",
    "last_name": "Lead",
    "full_name": "Team Lead",
    "display_name": "Team Lead",
    "phone_number": "+15555555555",
    "role": "MANAGER",
    "role_display": "Manager",
    "status": "ONLINE",
    "profile_image": null,
    "has_gps_permission": true,
    "has_camera_permission": false,
    "country": "UAE",
    "city": "Dubai",
    "address": null,
    "is_active": true,
    "date_joined": "2025-11-01T11:00:00Z",
    "last_login": "2025-11-06T06:45:00Z",
    "created_at": "2025-11-01T11:00:00Z",
    "updated_at": "2025-11-10T09:05:00Z"
  }
}
```

**Error Responses**:
- **400 Bad Request** – validation failures (duplicate work_id/email/phone_number, invalid role, etc.).
- **403 Forbidden** – caller is not an admin.
- **404 Not Found** – user is soft-deleted or does not exist.

---

### 6. Bulk Delete Users (Admin)

**Endpoint**: `POST /api/auth/users/bulk-delete/`

**Description**: Soft delete multiple users in a single request. Only admins can call this endpoint. Each user is flagged as deleted and `is_active` is set to `False`.

**Authentication**: Required (Bearer token, admin only)

**Headers**:
```
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

**Payload**:
```json
{
  "user_ids": [5, 6, 7]
}
```

**Example Request**:
```bash
ADMIN_TOKEN="<ADMIN_ACCESS_TOKEN>"

curl -X POST http://127.0.0.1:8000/api/auth/users/bulk-delete/ \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"user_ids": [5, 6, 7]}'
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "deleted_count": 3,
  "deleted_users": [
    {"id": 5, "work_id": "FA001", "username": "agent01"},
    {"id": 6, "work_id": "FA002", "username": "agent02"},
    {"id": 7, "work_id": "MN001", "username": "manager01"}
  ],
  "not_found_ids": []
}
```

**Error Responses**:
- **400 Bad Request** – Invalid or empty `user_ids`, non-integer values, or attempt to delete own account.
- **403 Forbidden** – Caller is not an admin.
- **404 Not Found** – None of the provided IDs match active users.

---

### 7. List Users (Admin)

**Endpoint**: `GET /api/auth/users/`

**Description**: List all non-deleted users. Only admins can access this endpoint. Users who have been soft-deleted (`is_deleted=True`) are excluded automatically.

**Authentication**: Required (Bearer token, admin only)

**Headers**:
```
Authorization: Bearer <admin_access_token>
```

**Example Request**:
```bash
ADMIN_TOKEN="<ADMIN_ACCESS_TOKEN>"

curl -X GET http://127.0.0.1:8000/api/auth/users/ \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "count": 3,
  "results": [
    {
      "id": 3,
      "work_id": "FA001",
      "username": "mehroz",
      "email": "mehroz@example.com",
      "first_name": "Mehroz",
      "last_name": "Daniyal",
      "full_name": "Mehroz Daniyal",
      "display_name": "Mehroz Daniyal",
      "phone_number": "+966512345678",
      "role": "FIELD_AGENT",
      "role_display": "Field Agent",
      "status": "ONLINE",
      "country": "Saudi Arabia",
      "city": "Makkah",
      "address": "123 Sunset Boulevard",
      "profile_image": null,
      "has_gps_permission": true,
      "has_camera_permission": true,
      "is_active": true,
      "date_joined": "2025-11-03T10:00:00Z",
      "last_login": "2025-11-06T08:05:00Z",
      "created_at": "2025-11-03T10:00:00Z",
      "updated_at": "2025-11-06T08:05:00Z"
    },
    {
      "id": 2,
      "work_id": "MN001",
      "username": "manager01",
      "email": "manager@example.com",
      "first_name": "Team",
      "last_name": "Lead",
      "full_name": "Team Lead",
      "display_name": "Team Lead",
      "phone_number": "+15555555555",
      "role": "MANAGER",
      "role_display": "Manager",
      "status": "OFFLINE",
      "country": "UAE",
      "city": "Dubai",
      "address": null,
      "profile_image": "http://127.0.0.1:8000/media/profile_pictures/manager.png",
      "has_gps_permission": false,
      "has_camera_permission": false,
      "is_active": true,
      "date_joined": "2025-11-01T11:00:00Z",
      "last_login": "2025-11-06T06:45:00Z",
      "created_at": "2025-11-01T11:00:00Z",
      "updated_at": "2025-11-06T06:45:00Z"
    }
  ]
}
```

**Error Response** (403 Forbidden):
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### 6. Refresh Token

**Endpoint**: `POST /api/auth/token/refresh/`

**Description**: Issue a new access token using Simple JWT’s built-in refresh view. When refresh rotation is enabled, a new refresh token is also returned.

**Authentication**: Not required (provide refresh token in body)

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Example Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

**Success Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Note:** Always save the newly returned `refresh` token when `ROTATE_REFRESH_TOKENS` is enabled.

**Error Response** (400 Bad Request - Missing token):
```json
{
  "refresh": [
    "This field is required."
  ]
}
```

**Error Response** (401 Unauthorized - Invalid/expired token):
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 7. Verify Token

**Endpoint**: `POST /api/auth/token/verify/`

**Description**: Validate an access or refresh token. The view returns an empty object when the token is valid and raises an error when it is not.

**Authentication**: Not required (token supplied in body)

**Request Body**:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Example Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

**Success Response** (200 OK):
```json
{}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 8. Logout / Blacklist Refresh Token

**Endpoint**: `POST /api/auth/token/blacklist/`

**Description**: Use Simple JWT’s blacklist view to invalidate a refresh token. Requires the refresh token to be provided in the request body.

**Authentication**: Required (Bearer token)

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Example Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/blacklist/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

**Success Response** (200 OK / 205 Reset Content):
```json
{}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 9. Get Current User

**Endpoint**: `GET /api/auth/me/`

**Description**: Get current authenticated user's profile.

**Authentication**: Required (Bearer token)

**Headers**:
```
Authorization: Bearer <access_token>
```

**Example Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "user": {
    "id": 1,
    "work_id": "ADMIN001",
    "username": "admin",
    "email": "admin@shamsvision.com",
    "first_name": "Admin",
    "last_name": "User",
    "full_name": "Admin User",
    "phone_number": null,
    "role": "ADMIN",
    "role_display": "Admin",
    "profile_picture": null,
    "has_gps_permission": false,
    "has_camera_permission": false,
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T12:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Using JWT Tokens

### Making Authenticated Requests

All authenticated endpoints require the `Authorization` header with the Bearer token:

```
Authorization: Bearer <access_token>
```

**Example:**
```bash
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Token Expiration Handling

When an access token expires (after 1 hour), you'll receive a `401 Unauthorized` response. Use the refresh token to get a new access token:

1. **Detect 401 response** on any authenticated request
2. **Call refresh endpoint** with your refresh token
3. **Update stored tokens** with the new access_token and refresh_token
4. **Retry the original request** with the new access token

**Example Flow:**
```javascript
// 1. Make request
let response = await fetch('/api/auth/me/', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});

// 2. If token expired, refresh
if (response.status === 401) {
  const refreshResponse = await fetch('/api/auth/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken })
  });
  
  const { access, refresh } = await refreshResponse.json();
  
  // 3. Update tokens and retry
  accessToken = access;
  refreshToken = refresh ?? refreshToken; // Persist rotated refresh token if returned
  
  response = await fetch('/api/auth/me/', {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
}
```

### Token Storage Best Practices

**Web Applications:**
- ✅ **Recommended**: HTTP-only cookies (most secure)
- ⚠️ **Acceptable**: In-memory storage (JavaScript variables)
- ❌ **Not Recommended**: localStorage (vulnerable to XSS)

**Mobile Applications:**
- ✅ **iOS**: Keychain Services
- ✅ **Android**: Keystore
- ❌ **Not Recommended**: SharedPreferences/UserDefaults

---

## Token Lifecycle

1. **Login** → Receive `access_token` (1 hour) and `refresh_token` (7 days)
2. **API Requests** → Use `access_token` in `Authorization: Bearer <token>` header
3. **Token Expires** → Use `refresh_token` to get new `access_token` and new `refresh_token`
4. **Logout** → Blacklist `refresh_token` (cannot be used again)
5. **Refresh Token Expires** → User must login again (after 7 days)

---

## Security Notes

- ✅ **Token Rotation**: Refresh tokens are automatically rotated on each use
- ✅ **Token Blacklisting**: Revoked tokens are stored in database and cannot be reused
- ✅ **HTTPS Required**: Always use HTTPS in production
- ✅ **Short-lived Access Tokens**: Access tokens expire in 1 hour
- ⚠️ **Store Securely**: Never commit tokens to version control
- ⚠️ **Handle Expiration**: Implement automatic token refresh logic

---

### 10. Update Profile

**Endpoint**: `PUT /api/auth/me/update/` or `PATCH /api/auth/me/update/`

**Description**: Update current user's profile.

**Authentication**: Required (Bearer token)

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "has_gps_permission": true,
  "has_camera_permission": true
}
```

**Example Request**:
```bash
curl -X PUT http://127.0.0.1:8000/api/auth/me/update/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890"
  }'
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "user": {
    // Updated user data
  }
}
```

---

### 11. Change Password

**Endpoint**: `POST /api/auth/me/change-password/`

**Description**: Change user password.

**Authentication**: Required (Bearer token)

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "old_password": "oldpassword123",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

**Example Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/me/change-password/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "admin123",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
  }'
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Error Response** (400 Bad Request):
```json
{
  "success": false,
  "errors": {
    "old_password": ["Old password is incorrect."]
  }
}
```

---

### 12. Password Reset Request

**Endpoint**: `POST /api/auth/password/reset/request/`

**Description**: Request password reset token.

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "admin@shamsvision.com"  // Optional: Use email OR phone_number
  // OR
  "phone_number": "+1234567890"  // Optional: Use phone_number OR email
}
```

**Example Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/password/reset/request/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@shamsvision.com"
  }'
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Password reset token has been sent to your email/phone",
  "token": "reset_token_here"  // Only in dev mode
}
```

**Note**: In production, the token should be sent via email/SMS, not returned in the response.

---

### 13. Password Reset Confirm

**Endpoint**: `POST /api/auth/password/reset/confirm/`

**Description**: Confirm password reset with token.

**Authentication**: Not required

**Request Body**:
```json
{
  "token": "reset_token_from_email",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

**Example Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/password/reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "reset_token_here",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
  }'
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

**Error Response** (400 Bad Request):
```json
{
  "success": false,
  "error": "Token has expired or already been used"
}
```

---

## Authentication Method

The API uses **Session Authentication** (Django's default).

### How It Works

1. **Login**: User sends credentials → Server validates → Creates session → Returns user data
2. **Subsequent Requests**: Client includes session cookie → Server validates session → Returns data
3. **Logout**: Client sends logout request → Server destroys session

### Using Session Cookies

After login, the server sets a session cookie. Include this cookie in subsequent requests:

**JavaScript (Fetch)**:
```javascript
fetch('http://127.0.0.1:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',  // Important: Include cookies
  body: JSON.stringify({
    work_id: 'ADMIN001',
    password: 'admin123'
  })
})
.then(response => response.json())
.then(data => {
  console.log(data);
  // Session cookie is automatically stored
});
```

**JavaScript (Axios)**:
```javascript
axios.post('http://127.0.0.1:8000/api/auth/login/', {
  work_id: 'ADMIN001',
  password: 'admin123'
}, {
  withCredentials: true  // Important: Include cookies
})
.then(response => {
  console.log(response.data);
});
```

**cURL** (Save cookies):
```bash
# Login and save cookies
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "work_id": "ADMIN001",
    "password": "admin123"
  }'

# Use cookies in subsequent requests
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

---

## Error Handling

All endpoints return consistent error format:

```json
{
  "success": false,
  "errors": {
    "field_name": ["Error message"],
    "error": "General error message"
  }
}
```

**Common HTTP Status Codes**:
- `200 OK`: Success
- `400 Bad Request`: Validation error or invalid credentials
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Testing the API

### Using cURL

```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "work_id": "ADMIN001",
    "password": "admin123"
  }'

# 2. Get current user
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Content-Type: application/json" \
  -b cookies.txt

# 3. Update profile
curl -X PUT http://127.0.0.1:8000/api/auth/me/update/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "first_name": "John",
    "last_name": "Doe"
  }'

# 4. Refresh token (replace <REFRESH_TOKEN>)
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<REFRESH_TOKEN>"
  }'

# 5. Logout / blacklist refresh token (replace <ACCESS_TOKEN> and <REFRESH_TOKEN>)
curl -X POST http://127.0.0.1:8000/api/auth/token/blacklist/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<REFRESH_TOKEN>"
  }'
```

### Using Python Requests

```python
import requests

BASE_URL = 'http://127.0.0.1:8000/api/auth'

# Create session
session = requests.Session()

# 1. Login
response = session.post(f'{BASE_URL}/login/', json={
    'work_id': 'ADMIN001',
    'password': 'admin123'
})
login_data = response.json()
print(login_data)

# Attach access token to the session for authenticated requests
session.headers.update({
    'Authorization': f"Bearer {login_data['access_token']}",
    'Content-Type': 'application/json'
})

# 2. Get current user
response = session.get(f'{BASE_URL}/me/')
print(response.json())

# 3. Update profile
response = session.put(f'{BASE_URL}/me/update/', json={
    'first_name': 'John',
    'last_name': 'Doe'
})
print(response.json())

# 4. Refresh token
refresh_response = requests.post(f'{BASE_URL}/token/refresh/', json={
    'refresh': login_data['refresh_token']
})
print(refresh_response.json())

# 5. Logout / blacklist refresh token
logout_response = session.post(f'{BASE_URL}/token/blacklist/', json={
    'refresh': login_data['refresh_token']
})
print(logout_response.status_code)
```

---

## Security Notes

1. **HTTPS**: Always use HTTPS in production
2. **CSRF Protection**: Django's CSRF protection is enabled (required for POST/PUT/DELETE)
3. **Session Security**: Sessions are secure by default
4. **Password Validation**: Uses Django's password validators
5. **Account Status**: Checks `is_active` flag before login

---

## Next Steps

1. ✅ Login API created
2. ⏳ Add JWT authentication (optional, for mobile apps)
3. ⏳ Add rate limiting
4. ⏳ Add API documentation (Swagger/OpenAPI)
5. ⏳ Add logging and monitoring

---

## Summary

- **Login**: `POST /api/auth/login/` - Login with work_id/email + password
- **Refresh Token**: `POST /api/auth/token/refresh/` - Get new access/refresh tokens
- **Logout / Blacklist**: `POST /api/auth/token/blacklist/` - Invalidate refresh token
- **Current User**: `GET /api/auth/me/` - Get current user profile
- **Update Profile**: `PUT /api/auth/me/update/` - Update user profile
- **Change Password**: `POST /api/auth/me/change-password/` - Change password
- **Password Reset**: `POST /api/auth/password/reset/request/` - Request reset
- **Confirm Reset**: `POST /api/auth/password/reset/confirm/` - Confirm reset

All endpoints are ready to use! 🚀


