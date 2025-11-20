# Authentication API Summary

## ✅ Current Highlights
- OTP flow fully removed across models, serializers, utilities, and admin.
- JWT authentication with access & refresh tokens via `djangorestframework-simplejwt`.
- Role-based permissions (FIELD_AGENT, MANAGER, ADMIN) enforced for protected endpoints.
- Admin tooling for listing, updating, soft-deleting, and bulk-deleting users.
- User profile information managed directly on the `User` model (no separate profile table).

## 🔗 Endpoints (`/api/auth/`)

| Endpoint | Method(s) | Description | Auth / Role |
|----------|-----------|-------------|-------------|
| `/login/` | POST | Obtain access & refresh tokens using `work_id` or `email` + password | Public |
| `/token/refresh/` | POST | Rotate refresh token & issue new access token | Public (refresh token) |
| `/token/verify/` | POST | Validate a JWT without returning user data | Public |
| `/token/blacklist/` | POST | Blacklist provided refresh token | Authenticated |
| `/profile/` | GET | Fetch authenticated user details | Authenticated |
| `/profile/update/` | PUT / PATCH | Update authenticated user profile fields | Authenticated |
| `/users/` | GET | List non-deleted users | Admin |
| `/users/<id>/update/` | PUT / PATCH | Update another user's details | Admin |
| `/users/<id>/delete/` | DELETE | Soft delete a user | Admin |
| `/users/bulk-delete/` | POST | Soft delete multiple users (payload: `user_ids`) | Admin |

> All admin endpoints automatically respect soft-delete flags and guard against accidental self-deletion where relevant.

## 🔐 Authentication & Permissions
- **Authentication**: Bearer tokens issued via JWT (Simple JWT). Access tokens default to 1 hour; refresh tokens to 7 days with rotation & blacklist enabled.
- **Permissions**: `IsAuthenticated` for user-owned operations, `IsAdmin` (custom) for administrative routes.

## 🧪 Quick Testing Snippets

### Login (obtain tokens)
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your-password"}'
```

### Refresh Access Token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<REFRESH_TOKEN>"}'
```

### Admin Bulk Delete Example
```bash
curl -X POST http://127.0.0.1:8000/api/auth/users/bulk-delete/ \
  -H "Authorization: Bearer <ADMIN_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"user_ids": [5, 6, 7]}'
```

## 📚 Reference
- **Detailed documentation**: `LOGIN_API_DOCUMENTATION.md`
- **JWT configuration**: `JWT_AUTHENTICATION_DOCUMENTATION.md`
- **Overall architecture**: `COMPLETE_DOCUMENTATION.md`

Everything above is deployed and verified via `python manage.py check`. Feel free to extend with additional role-specific routes as needed.
