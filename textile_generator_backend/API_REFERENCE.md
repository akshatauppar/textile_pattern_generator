# API Reference - Textile Pattern Generator

## Base URL
```
http://localhost:5000/api
```

## Response Format

All responses are JSON. Successful responses contain the requested data, while errors contain an `error` field:

```json
{
  "error": "Error message"
}
```

## Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required or failed
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `500 Internal Server Error` - Server error

---

## Authentication Endpoints

### POST /register

Register a new user account.

**Request Body:**
```json
{
  "username": "string (3-80 chars, unique)",
  "email": "string (unique, valid email)",
  "password": "string (min 6 chars)"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "artist",
    "email": "artist@textile.local",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Error (409):**
```json
{
  "error": "Username already exists"
}
```

---

### POST /login

Login and receive JWT access token.

**Request Body:**
```json
{
  "username": "string (username or email)",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGc...",
  "user": {
    "id": 1,
    "username": "artist",
    "email": "artist@textile.local",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Error (401):**
```json
{
  "error": "Invalid username or password"
}
```

---

### GET /me

Get current authenticated user details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "artist",
    "email": "artist@textile.local",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Error (401):**
```json
{
  "error": "Missing Authorization Header"
}
```

---

## Generation Endpoints

### POST /generate

Generate a new textile pattern (authenticated or guest).

**Headers (Optional):**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "prompt": "string (required, min 3 chars)",
  "style": "string (required: bandhani|ikat|block_print|paisley)",
  "color_1": "string (optional: color name or hex)",
  "color_2": "string (optional: color name or hex)",
  "seed": "integer (optional: for reproducibility)"
}
```

**Example:**
```json
{
  "prompt": "intricate floral motifs with geometric elements",
  "style": "ikat",
  "color_1": "indigo",
  "color_2": "cream",
  "seed": 42
}
```

**Response (200):**
```json
{
  "generation": {
    "id": 1,
    "user_id": 1,
    "prompt": "intricate floral motifs with geometric elements",
    "style": "ikat",
    "color_1": "indigo",
    "color_2": "cream",
    "seed": 42,
    "status": "processing",
    "created_at": "2024-01-15T10:35:00",
    "completed_at": null
  }
}
```

**Error (400):**
```json
{
  "error": "Invalid style. Must be one of: bandhani, ikat, block_print, paisley"
}
```

**Note:** Generation happens asynchronously. Status will be "processing" initially, then "completed" once done. Check `/status/<id>` for image URL.

---

### GET /status/<generation_id>

Get status and details of a generation (including image URL when complete).

**Parameters:**
- `generation_id` (integer): ID of the generation

**Response (200) - Processing:**
```json
{
  "generation": {
    "id": 1,
    "user_id": 1,
    "prompt": "intricate floral motifs",
    "style": "ikat",
    "status": "processing",
    "created_at": "2024-01-15T10:35:00",
    "completed_at": null
  }
}
```

**Response (200) - Completed:**
```json
{
  "generation": {
    "id": 1,
    "user_id": 1,
    "prompt": "intricate floral motifs",
    "style": "ikat",
    "status": "completed",
    "image_url": "/api/images/textile_1_1705318500.png",
    "created_at": "2024-01-15T10:35:00",
    "completed_at": "2024-01-15T10:40:30"
  }
}
```

**Response (200) - Failed:**
```json
{
  "generation": {
    "id": 1,
    "user_id": 1,
    "status": "failed",
    "error_message": "CUDA out of memory",
    "created_at": "2024-01-15T10:35:00",
    "completed_at": "2024-01-15T10:36:15"
  }
}
```

**Error (404):**
```json
{
  "error": "Generation not found"
}
```

---

### GET /history

Get generation history for authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `limit` (integer, optional): Maximum results (1-100, default: 10)
- `offset` (integer, optional): Results to skip (default: 0)

**Example Request:**
```
GET /history?limit=20&offset=0
```

**Response (200):**
```json
{
  "generations": [
    {
      "id": 5,
      "user_id": 1,
      "prompt": "paisley pattern",
      "style": "paisley",
      "status": "completed",
      "image_url": "/api/images/textile_5_1705318800.png",
      "created_at": "2024-01-15T11:00:00",
      "completed_at": "2024-01-15T11:05:30"
    },
    {
      "id": 4,
      "user_id": 1,
      "prompt": "block print design",
      "style": "block_print",
      "status": "completed",
      "image_url": "/api/images/textile_4_1705318500.png",
      "created_at": "2024-01-15T10:50:00",
      "completed_at": "2024-01-15T10:55:15"
    }
  ]
}
```

**Error (401):**
```json
{
  "error": "Missing Authorization Header"
}
```

---

### GET /images/<filename>

Download a generated textile pattern image.

**Parameters:**
- `filename` (string): Image filename from generation response

**Example Request:**
```
GET /images/textile_1_1705318500.png
```

**Response (200):**
- Binary PNG image file
- MIME type: `image/png`

**Error (404):**
```json
{
  "error": "Image not found"
}
```

**Error (400):**
```json
{
  "error": "Invalid filename"
}
```

---

## Utility Endpoints

### GET /health

Check API health status and model availability.

**Response (200):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database": "ok"
}
```

**Response (200) - Degraded:**
```json
{
  "status": "degraded",
  "model_loaded": false,
  "database": "error: connection refused"
}
```

---

### GET /styles

Get list of supported textile styles.

**Response (200):**
```json
{
  "styles": [
    {
      "id": "bandhani",
      "name": "Bandhani",
      "description": "Traditional tie-dye patterns"
    },
    {
      "id": "ikat",
      "name": "Ikat",
      "description": "Resist-dyed textile patterns"
    },
    {
      "id": "block_print",
      "name": "Block Print",
      "description": "Hand-stamped patterns"
    },
    {
      "id": "paisley",
      "name": "Paisley",
      "description": "Classic paisley motifs"
    }
  ]
}
```

---

## Common Patterns

### Guest Pattern Generation

No authentication required:

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "geometric textile design",
    "style": "block_print"
  }'
```

### Authenticated Pattern Generation

Include JWT token:

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "prompt": "floral bandhani pattern",
    "style": "bandhani",
    "color_1": "indigo",
    "color_2": "white"
  }'
```

### Poll for Completion

Check status every 5 seconds:

```bash
for i in {1..60}; do
  STATUS=$(curl -s http://localhost:5000/api/status/1 | jq -r '.generation.status')
  if [ "$STATUS" = "completed" ]; then
    echo "Generation complete!"
    break
  fi
  echo "Status: $STATUS"
  sleep 5
done
```

### Download Image

Once generation is complete:

```bash
curl -X GET http://localhost:5000/api/images/textile_1_1705318500.png \
  -o my_pattern.png
```

---

## Error Handling

### Common Error Responses

**Invalid JSON:**
```json
{
  "error": "Missing required fields"
}
```

**Unauthorized:**
```json
{
  "error": "Missing Authorization Header"
}
```

**Not Found:**
```json
{
  "error": "Not found"
}
```

**Server Error:**
```json
{
  "error": "Internal server error"
}
```

### Retry Strategy

For transient errors (500, 503):
- Retry with exponential backoff
- Max 3 attempts
- Wait 1s, 2s, 4s between attempts

---

## Rate Limiting

Currently no rate limiting is enforced. Future versions may implement:
- Request rate limiting per user
- Generation queue management
- Token bucket algorithm

---

## CORS

API allows requests from any origin by default in development mode. Restrict this in production by modifying [app.py](app.py):

```python
CORS(app, resources={
    r"/api/*": {"origins": ["https://yourdomain.com"]}
})
```

---

## Version History

- **v1.0.0** (2024-01-15): Initial release
  - User authentication
  - Pattern generation
  - Image serving
  - Generation history
