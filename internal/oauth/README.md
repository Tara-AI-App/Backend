# OAuth Module

This module handles OAuth integration with GitHub and Google Drive for user authentication and token management.

## Features

- GitHub OAuth integration
- Token storage and management
- User authentication via OAuth

## API Endpoints

### GitHub OAuth
- `GET /api/v1/oauth/github/auth-url` - Get GitHub OAuth authorization URL
- `POST /api/v1/oauth/github/callback` - Exchange GitHub code for access token
- `POST /api/v1/oauth/github/save-token` - Save GitHub token for user
- `GET /api/v1/oauth/github/token` - Get user's GitHub token (requires auth)

## Configuration

Add the following environment variables to your `.env` file:

```env
# GitHub OAuth Configuration
GH_CLIENT_ID=your_github_client_id
GH_CLIENT_SECRET=your_github_client_secret
GH_REDIRECT_URI=http://localhost:3000/oauth/github/callback
```

## Usage Examples

### 1. Get GitHub OAuth URL

```bash
curl -X GET "http://localhost:8000/api/v1/oauth/github/auth-url?state=random_state_string"
```

Response:
```json
{
  "auth_url": "https://github.com/login/oauth/authorize?client_id=...&redirect_uri=...&scope=user:email,repo&state=random_state_string"
}
```

### 2. Exchange Code for Token

```bash
curl -X POST "http://localhost:8000/api/v1/oauth/github/callback" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "github_authorization_code",
    "state": "optional_state"
  }'
```

Response:
```json
{
  "access_token": "gho_abc123...",
  "token_type": "bearer",
  "scope": "user:email,repo",
  "user_info": {
    "id": 12345,
    "login": "username",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

### 3. Save Token for User

```bash
curl -X POST "http://localhost:8000/api/v1/oauth/github/save-token?user_id=user-uuid" \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "gho_abc123...",
    "token_type": "bearer",
    "scope": "user:email,repo",
    "user_info": {...}
  }'
```

Response:
```json
{
  "id": "token-uuid",
  "user_id": "user-uuid",
  "provider": "github",
  "token_type": "Bearer",
  "expires_at": "2025-01-27T10:00:00Z",
  "created_at": "2025-01-27T10:00:00Z"
}
```

### 4. Get User's GitHub Token (Authenticated)

```bash
curl -X GET "http://localhost:8000/api/v1/oauth/github/token" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```


## Frontend Integration

### React/Next.js Example

```javascript
// 1. Redirect user to GitHub OAuth
const handleGitHubLogin = () => {
  const response = await fetch('/api/v1/oauth/github/auth-url');
  const { auth_url } = await response.json();
  window.location.href = auth_url;
};

// 2. Exchange code for token
const handleOAuthCallback = async (code) => {
  const tokenResponse = await fetch('/api/v1/oauth/github/callback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code })
  });
  
  const githubData = await tokenResponse.json();
  return githubData; // Contains access_token and user_info
};

// 3. Save token for user
const saveToken = async (userId, githubData) => {
  const saveResponse = await fetch(`/api/v1/oauth/github/save-token?user_id=${userId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(githubData)
  });
  
  const tokenData = await saveResponse.json();
  return tokenData; // Token saved in database
};
```

## Database Schema

The OAuth tokens are stored in the `user_oauth_tokens` table:

- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key to users table)
- `provider` (VARCHAR(50)) - "github", "google_drive", etc.
- `access_token` (TEXT) - The OAuth access token
- `refresh_token` (TEXT, Optional) - Refresh token if available
- `token_type` (VARCHAR(50)) - Usually "Bearer"
- `expires_at` (DATETIME, Optional) - Token expiration
- `created_at` (DATETIME) - Creation timestamp

## Security Notes

- Access tokens are stored in the database and should be encrypted in production
- The OAuth flow uses state parameters for CSRF protection
- All endpoints except auth URL generation require JWT authentication
