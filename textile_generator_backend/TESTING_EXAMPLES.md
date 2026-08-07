# Testing Examples

Quick reference for testing the API with curl commands.

## Setup

Store token in variable for easy access:

```bash
# Register and login
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@textile.local",
    "password": "test123456"
  }'

# Login
TOKEN=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123456"}' \
  | jq -r '.access_token')

echo $TOKEN  # Verify token
```

---

## Health & Info

### Check API Health
```bash
curl http://localhost:5000/api/health | jq
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": false,
  "database": "ok"
}
```

### Get Available Styles
```bash
curl http://localhost:5000/api/styles | jq
```

### API Root
```bash
curl http://localhost:5000 | jq
```

---

## Authentication

### Register User
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "artist",
    "email": "artist@textile.local",
    "password": "securepass123"
  }' | jq
```

### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "artist",
    "password": "securepass123"
  }' | jq
```

### Get Current User
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/me | jq
```

### Error: Invalid Credentials
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "artist",
    "password": "wrong"
  }' | jq
# Returns: {"error": "Invalid username or password"}
```

---

## Generation

### Generate Pattern (No Auth)
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "intricate geometric floral pattern",
    "style": "bandhani"
  }' | jq
```

### Generate with Colors
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "traditional tribal motifs",
    "style": "ikat",
    "color_1": "indigo",
    "color_2": "cream"
  }' | jq
```

### Generate with Seed (Reproducible)
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "paisley pattern with botanical elements",
    "style": "paisley",
    "seed": 42
  }' | jq
```

### Generate with Authentication
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "block print with geometric elements",
    "style": "block_print",
    "color_1": "#8B4513",
    "color_2": "#FFFACD"
  }' | jq
```

### Check Generation Status
```bash
# Check generation 1
curl http://localhost:5000/api/status/1 | jq

# Pretty print
curl http://localhost:5000/api/status/1 | jq '.generation'
```

### Poll Until Complete
```bash
for i in {1..12}; do
  status=$(curl -s http://localhost:5000/api/status/1 | jq -r '.generation.status')
  echo "Attempt $i: $status"
  if [ "$status" = "completed" ]; then
    echo "Generation complete!"
    curl http://localhost:5000/api/status/1 | jq '.generation.image_url'
    break
  fi
  sleep 5
done
```

### Get Generation History (Auth Required)
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/history?limit=5" | jq
```

### Get History with Pagination
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/history?limit=10&offset=0" | jq
```

---

## Images

### Download Generated Image
```bash
# First get image_url from /api/status/<id>
IMAGE_URL=$(curl -s http://localhost:5000/api/status/1 | jq -r '.generation.image_url')

# Download
curl $IMAGE_URL -o pattern.png

# Or direct download if filename is known
curl http://localhost:5000/api/images/textile_1_1702857600.png -o pattern.png
```

### Save to File
```bash
curl http://localhost:5000/api/images/textile_1_1702857600.png \
  -o my_textile_pattern.png

# Verify
file my_textile_pattern.png  # Should show: PNG image data
ls -lh my_textile_pattern.png
```

---

## Error Scenarios

### Missing Required Fields
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "pattern"}' | jq
# Returns: {"error": "Missing prompt and/or style"}
```

### Invalid Style
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "pattern",
    "style": "invalid_style"
  }' | jq
# Returns: {"error": "Invalid style..."}
```

### Non-existent Generation
```bash
curl http://localhost:5000/api/status/99999 | jq
# Returns: {"error": "Generation not found"}
```

### Missing Authorization
```bash
curl http://localhost:5000/api/history | jq
# Returns: {"error": "Missing Authorization Header"}
```

### Invalid Token
```bash
curl -H "Authorization: Bearer invalid_token" \
  http://localhost:5000/api/me | jq
# Returns: {"error": "..."}
```

---

## Batch Generation

### Generate Multiple Patterns
```bash
for i in {1..3}; do
  PROMPT="Pattern $i with unique design"
  curl -s -X POST http://localhost:5000/api/generate \
    -H "Content-Type: application/json" \
    -d "{
      \"prompt\": \"$PROMPT\",
      \"style\": \"block_print\",
      \"seed\": $((1000 + i))
    }" | jq '.generation.id'
done
```

### Check All Statuses
```bash
for id in {1..3}; do
  echo "Generation $id:"
  curl -s http://localhost:5000/api/status/$id | jq '.generation | {id, status, created_at}'
done
```

---

## Performance Testing

### Measure Response Time
```bash
time curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "test pattern",
    "style": "bandhani"
  }' > /dev/null
```

### Load Testing (simple)
```bash
for i in {1..10}; do
  curl -s -X POST http://localhost:5000/api/generate \
    -H "Content-Type: application/json" \
    -d "{
      \"prompt\": \"pattern $i\",
      \"style\": \"block_print\"
    }" &
done
wait
```

### Monitor Database
```bash
# Check number of generations
curl -s http://localhost:5000/api/history \
  -H "Authorization: Bearer $TOKEN" | jq '.generations | length'

# Check generation statuses
curl -s http://localhost:5000/api/history \
  -H "Authorization: Bearer $TOKEN" | jq '.generations[] | {id, status}'
```

---

## Data Inspection

### Extract JSON Values
```bash
# Get generation ID
curl -s -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "style": "bandhani"}' | jq '.generation.id'

# Get image URL
curl -s http://localhost:5000/api/status/1 | jq '.generation.image_url'

# Get all completed generations
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/history | jq '.generations[] | select(.status == "completed")'
```

---

## Useful Aliases

Add to ~/.bashrc or ~/.zshrc:

```bash
# API shortcuts
alias textile-health="curl -s http://localhost:5000/api/health | jq"
alias textile-styles="curl -s http://localhost:5000/api/styles | jq"
alias textile-history="curl -s -H 'Authorization: Bearer $TOKEN' http://localhost:5000/api/history | jq"

# Generate and save
textile-gen() {
  local prompt=$1
  local style=$2
  curl -s -X POST http://localhost:5000/api/generate \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$prompt\", \"style\": \"$style\"}" | jq '.generation'
}

# Check status
textile-status() {
  local id=$1
  curl -s http://localhost:5000/api/status/$id | jq '.generation'
}
```

Usage:
```bash
textile-health
textile-styles
textile-gen "floral pattern" "bandhani"
textile-status 1
```

---

## Using with Postman

### Import Collection

Create `textile-api.postman_collection.json`:

```json
{
  "info": {
    "name": "Textile Pattern Generator",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{token}}",
        "type": "string"
      }
    ]
  },
  "item": [
    {
      "name": "Health",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/api/health"
      }
    },
    {
      "name": "Register",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/api/register",
        "body": {
          "mode": "raw",
          "raw": "{\"username\": \"user\", \"email\": \"user@test.com\", \"password\": \"pass123\"}"
        }
      }
    },
    {
      "name": "Generate",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/api/generate",
        "body": {
          "mode": "raw",
          "raw": "{\"prompt\": \"pattern\", \"style\": \"bandhani\"}"
        }
      }
    }
  ]
}
```

Import into Postman and set variable `token` from login response.

---

## Debugging

### Enable Verbose Output
```bash
# Show all headers
curl -v http://localhost:5000/api/health

# Show request/response
curl -v -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@test.com", "password": "pass"}'
```

### Save Response to File
```bash
curl http://localhost:5000/api/status/1 > response.json
cat response.json | jq
```

### Check HTTP Status Code
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health
# Returns: 200
```

---

## References

- [curl documentation](https://curl.se/)
- [jq manual](https://stedolan.github.io/jq/manual/)
- [HTTP status codes](https://httpwg.org/specs/rfc7231.html#status.codes)
