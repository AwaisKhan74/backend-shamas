# JWT Authentication Documentation

## Overview

The application now uses **JWT (JSON Web Tokens)** with refresh tokens for authentication, following industry best practices. This provides a stateless, scalable authentication mechanism that works well for mobile apps and single-page applications (SPAs).

## Features

✅ **JWT Access Tokens** - Short-lived tokens (1 hour) for API requests  
✅ **Refresh Tokens** - Long-lived tokens (7 days) for obtaining new access tokens  
✅ **Token Rotation** - Refresh tokens are rotated on each use  
✅ **Token Blacklisting** - Revoked tokens are blacklisted for security  
✅ **Automatic Token Management** - Old tokens are automatically blacklisted after rotation  

## Configuration

### JWT Settings (`settings.py`)

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),    # 7 days
    'ROTATE_REFRESH_TOKENS': True,  # Rotate refresh tokens
    'BLACKLIST_AFTER_ROTATION': True,  # Blacklist old tokens
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
```

### Key Settings Explained

- **ACCESS_TOKEN_LIFETIME**: How long access tokens remain valid (1 hour)
- **REFRESH_TOKEN_LIFETIME**: How long refresh tokens remain valid (7 days)
- **ROTATE_REFRESH_TOKENS**: When enabled, a new refresh token is issued each time you refresh
- **BLACKLIST_AFTER_ROTATION**: Old refresh tokens are blacklisted after rotation (security best practice)
- **UPDATE_LAST_LOGIN**: Automatically updates user's last_login field

## API Endpoints

### 1. Login

**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**OR**

```json
{
  "work_id": "EMP001",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "work_id": "EMP001",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "FIELD_AGENT",
    ...
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "password": ["This field is required."]
  }
}
```

---

### 2. Refresh Token

**Endpoint:** `POST /api/auth/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Note:** Simple JWT rotates refresh tokens when `ROTATE_REFRESH_TOKENS` is enabled. Persist the new `refresh` value.

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 3. Verify Token

**Endpoint:** `POST /api/auth/token/verify/`

**Request Body:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 4. Logout / Blacklist Token

**Endpoint:** `POST /api/auth/token/blacklist/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK / 205 Reset Content):**
```json
{}
```

**Note:** Blacklisting removes the refresh token from circulation so it cannot be used again.

---

### 5. Get Current User

**Endpoint:** `GET /api/auth/me/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "work_id": "EMP001",
    "email": "user@example.com",
    ...
  }
}
```

---

## Client Implementation Guide

### 1. Login Flow

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const loginData = await loginResponse.json();

// Store tokens securely
localStorage.setItem('access_token', loginData.access_token);
localStorage.setItem('refresh_token', loginData.refresh_token);
```

### 2. Making Authenticated Requests

```javascript
// Get access token from storage
const accessToken = localStorage.getItem('access_token');

// Make authenticated request
const response = await fetch('http://localhost:8000/api/auth/me/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  }
});
```

### 3. Handling Token Expiration

```javascript
async function makeAuthenticatedRequest(url, options = {}) {
  let accessToken = localStorage.getItem('access_token');
  
  // Make request with access token
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${accessToken}`,
    }
  });
  
  // If token expired (401), refresh it
  if (response.status === 401) {
    const newTokens = await refreshAccessToken();
    accessToken = newTokens.access;
    
    // Retry request with new token
    response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${accessToken}`,
      }
    });
  }
  
  return response;
}

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('http://localhost:8000/api/auth/token/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh: refreshToken
    })
  });
  
  const data = await response.json();
  
  if (response.ok && data.access) {
    // Update stored tokens
    localStorage.setItem('access_token', data.access);
    if (data.refresh) {
      localStorage.setItem('refresh_token', data.refresh); // Rotated token
    }
    return data;
  } else {
    // Refresh token expired, redirect to login
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
    throw new Error('Session expired');
  }
}
```

### 4. Logout Flow

```javascript
async function logout() {
  const accessToken = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');
  
  await fetch('http://localhost:8000/api/auth/token/blacklist/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh: refreshToken
    })
  });
  
  // Clear tokens
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  
  // Redirect to login
  window.location.href = '/login';
}
```

## Security Best Practices

### ✅ Implemented

1. **Token Rotation**: Refresh tokens are rotated on each use
2. **Token Blacklisting**: Revoked tokens are stored in database and cannot be reused
3. **Short-lived Access Tokens**: Access tokens expire in 1 hour
4. **HTTPS Only**: Tokens should only be transmitted over HTTPS in production
5. **Secure Storage**: 
   - **Web**: Store in memory or secure HTTP-only cookies
   - **Mobile**: Use secure storage (Keychain on iOS, Keystore on Android)

### ⚠️ Client-Side Recommendations

1. **Never store tokens in localStorage** (if possible) - Use HTTP-only cookies or secure storage
2. **Implement token refresh logic** - Automatically refresh tokens before they expire
3. **Clear tokens on logout** - Always clear tokens from storage on logout
4. **Handle token expiration** - Redirect to login if refresh token expires
5. **Use HTTPS** - Always use HTTPS in production

## Token Structure

### Access Token Payload

```json
{
  "token_type": "access",
  "exp": 1234567890,  // Expiration timestamp
  "iat": 1234564290,  // Issued at timestamp
  "jti": "abc123...",  // JWT ID (for blacklisting)
  "user_id": 1
}
```

### Refresh Token Payload

```json
{
  "token_type": "refresh",
  "exp": 1234567890,  // Expiration timestamp
  "iat": 1234564290,  // Issued at timestamp
  "jti": "xyz789...",  // JWT ID (for blacklisting)
  "user_id": 1
}
```

## Database Tables

### OutstandingToken

Stores all issued refresh tokens for tracking and blacklisting.

### BlacklistedToken

Stores blacklisted tokens that can no longer be used.

## Testing

### Using cURL

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

**Get Current User:**
```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

**Refresh Token:**
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

**Logout / Blacklist:**
```bash
curl -X POST http://localhost:8000/api/auth/token/blacklist/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

## Migration from Session Authentication

The application previously used session-based authentication. The migration to JWT:

1. ✅ Removed session login (`login(request, user)`)
2. ✅ Added JWT token generation on login
3. ✅ Updated logout to blacklist tokens instead of destroying session
4. ✅ Added refresh token endpoint
5. ✅ Added token verification endpoint

**Note:** Session authentication is still enabled for Django admin panel compatibility.

## Troubleshooting

### Token Expired Error

**Error:** `"Invalid or expired refresh token"`

**Solution:** User needs to login again. Refresh token has expired (7 days).

### Token Blacklisted Error

**Error:** `"Token is blacklisted"`

**Solution:** Token was revoked (logout). User needs to login again.

### Missing Authorization Header

**Error:** `"Authentication credentials were not provided."`

**Solution:** Include `Authorization: Bearer <access_token>` header in request.

## Summary

✅ JWT authentication with refresh tokens  
✅ Token rotation and blacklisting  
✅ Secure token management  
✅ Mobile and SPA friendly  
✅ Scalable and stateless  

The implementation follows industry best practices for JWT authentication and provides a secure, scalable authentication mechanism for your application.

