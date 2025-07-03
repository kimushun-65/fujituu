# User Management API

FastAPI implementation of a user management system with signup, user details, update, and account closure functionality.

## Installation

```bash
pip install -r requirements.txt
```

## Running the API

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### POST /signup
Create a new user account.

**Request Body:**
```json
{
  "user_id": "TaroYamada",
  "password": "PasSwd4TY"
}
```

**Response (200):**
```json
{
  "message": "Account successfully created",
  "user": {
    "user_id": "TaroYamada",
    "nickname": "TaroYamada",
    "comment": "僕は元気です"
  }
}
```

### GET /users/{user_id}
Get user details. Optional Basic Authentication for private data.

**Headers (optional):**
- `Authorization: Basic <base64-encoded-user_id:password>`

**Response (200):**
```json
{
  "message": "User details by user_id",
  "user": {
    "user_id": "TaroYamada",
    "nickname": "TaroYamada",
    "comment": "僕は元気です"
  }
}
```

### PATCH /users/{user_id}
Update user information. Requires Basic Authentication.

**Headers:**
- `Authorization: Basic <base64-encoded-user_id:password>`

**Request Body:**
```json
{
  "nickname": "たろー",
  "comment": "僕は元気です"
}
```

**Response (200):**
```json
{
  "message": "User successfully updated",
  "user": {
    "user_id": "TaroYamada",
    "nickname": "たろー",
    "comment": "僕は元気です"
  }
}
```

### POST /close
Delete user account. Requires Basic Authentication.

**Headers:**
- `Authorization: Basic <base64-encoded-user_id:password>`

**Response (200):**
```json
{
  "message": "Account and user successfully removed"
}
```

## Test Account
A test account "Test-" is mentioned in the specifications but not auto-created. Use the signup endpoint to create test accounts.

## Interactive API Documentation
Visit `http://localhost:8000/docs` for Swagger UI documentation.