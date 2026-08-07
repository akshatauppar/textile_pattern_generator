# Textile Pattern Generator - Backend API

A Flask-based REST API for generating seamless textile patterns using Stable Diffusion XL with custom LoRA weights. Supports user authentication, generation history tracking, and multiple textile style presets.

## Features

- **AI-Powered Generation**: Uses Stable Diffusion XL with custom LoRA adapter for textile pattern generation
- **Multiple Styles**: Support for Bandhani, Ikat, Block Print, and Paisley patterns
- **User Authentication**: Optional JWT-based authentication with registration and login
- **Generation History**: Track all generations with metadata and status
- **Guest Mode**: Generate patterns without authentication
- **Background Processing**: Asynchronous pattern generation with status tracking
- **Memory Optimization**: Efficient GPU/CPU memory usage with mixed precision
- **RESTful API**: Clean, documented REST endpoints

## Technology Stack

- **Backend**: Flask 2.3.3
- **Database**: PostgreSQL 12+
- **Authentication**: Flask-JWT-Extended
- **ML**: Stable Diffusion XL, Diffusers, Transformers
- **Storage**: Local file system
- **Python**: 3.9+

## Project Structure

```
textile_generator_backend/
├── app/
│   ├── models/          # SQLAlchemy database models
│   ├── routes/          # Flask blueprints (auth, generation)
│   └── utils/           # Utilities (ML generator)
├── uploads/             # Generated images storage
├── config.py            # Configuration management
├── app.py               # Flask application factory
├── init_db.py           # Database initialization script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- PostgreSQL 12+ (running locally)
- CUDA 11.8+ (for GPU acceleration, recommended)
- ~20GB disk space for models
- ~12GB VRAM for optimal performance

### 1. Clone and Install Dependencies

```bash
cd textile_generator_backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

DB_HOST=localhost
DB_PORT=5432
DB_NAME=textile_generator
DB_USER=textile_user
DB_PASS=textile_pass

MODEL_PATH=../models/textile_lora_final
```

### 3. Setup PostgreSQL Database

```bash
# Create database and user (Linux/Mac)
sudo -u postgres psql

# Or on Windows, use pgAdmin or:
psql -U postgres

# Then run in psql:
CREATE USER textile_user WITH PASSWORD 'textile_pass';
CREATE DATABASE textile_generator OWNER textile_user;
GRANT ALL PRIVILEGES ON DATABASE textile_generator TO textile_user;
```

### 4. Initialize Database

```bash
python init_db.py --init
python init_db.py --seed  # Add sample data
```

### 5. Verify Model Path

Ensure your LoRA model is at the path specified in `.env`:

```bash
ls ../models/textile_lora_final/
# Should contain: adapter_config.json, adapter_model.bin, etc.
```

### 6. Start Development Server

```bash
python app.py
```

Server will run at `http://localhost:5000`

## API Endpoints

### Health & Info

**GET** `/api/health`
- Check API and model status
- Returns: `{ status, model_loaded, database }`

**GET** `/api/styles`
- Get list of supported textile styles
- Returns: `{ styles: [{ id, name, description }, ...] }`

### Authentication (Optional)

**POST** `/api/register`
- Register new user
- Body: `{ username, email, password }`
- Returns: `{ message, user: { id, username, email } }`

**POST** `/api/login`
- Login and get JWT token
- Body: `{ username, password }`
- Returns: `{ access_token, user: { id, username, email } }`

**GET** `/api/me`
- Get current authenticated user
- Headers: `Authorization: Bearer <token>`
- Returns: `{ user: { id, username, email, created_at } }`

### Generation

**POST** `/api/generate`
- Generate a textile pattern
- Headers: `Authorization: Bearer <token>` (optional for guests)
- Body:
  ```json
  {
    "prompt": "floral geometric pattern",
    "style": "bandhani",
    "color_1": "indigo",
    "color_2": "white",
    "seed": 42
  }
  ```
- Returns: `{ generation: { id, status, prompt, style, created_at } }`

**GET** `/api/status/<generation_id>`
- Get status of a generation
- Returns: `{ generation: { id, status, image_url, prompt, ... } }`

**GET** `/api/history?limit=10&offset=0`
- Get user's generation history
- Headers: `Authorization: Bearer <token>` (required)
- Returns: `{ generations: [...] }`

**GET** `/api/images/<filename>`
- Serve generated image (PNG)
- Returns: PNG image file

## Example Usage

### Register and Login

```bash
# Register
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "artist",
    "email": "artist@textile.local",
    "password": "securepass123"
  }'

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "artist",
    "password": "securepass123"
  }'
# Response includes access_token
```

### Generate Pattern (with authentication)

```bash
TOKEN="your_access_token_here"

curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "intricate floral motifs with geometric elements",
    "style": "ikat",
    "color_1": "#4B0082",
    "color_2": "#FFD700",
    "seed": 12345
  }'
```

### Generate Pattern (as guest)

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "traditional block print patterns",
    "style": "block_print"
  }'
```

### Check Generation Status

```bash
curl http://localhost:5000/api/status/1
```

### Get Generation History

```bash
TOKEN="your_access_token_here"

curl -X GET http://localhost:5000/api/history?limit=20 \
  -H "Authorization: Bearer $TOKEN"
```

### Download Generated Image

```bash
curl http://localhost:5000/api/images/textile_1_1702857600.png -o pattern.png
```

## Database Schema

### Users Table
- `id` (serial, primary key)
- `username` (varchar, unique)
- `email` (varchar, unique)
- `password_hash` (varchar)
- `created_at` (timestamp)

### Generations Table
- `id` (serial, primary key)
- `user_id` (integer, foreign key, nullable)
- `prompt` (text)
- `style` (varchar)
- `color_1` (varchar, optional)
- `color_2` (varchar, optional)
- `seed` (integer, optional)
- `image_path` (varchar)
- `status` (varchar: pending, processing, completed, failed)
- `error_message` (text, optional)
- `created_at` (timestamp)
- `completed_at` (timestamp, optional)

## Textile Styles

### Bandhani
Traditional tie-dye patterns with circular motifs and symmetrical designs. Perfect for creating intricate geometric patterns.

### Ikat
Resist-dyed textile patterns with abstract geometric designs and characteristic blurred edges.

### Block Print
Hand-stamped patterns with repetitive motifs and artisanal texture. Great for traditional-looking designs.

### Paisley
Classic paisley patterns featuring ornate teardrop shapes and flowing designs.

## Configuration

### Environment Variables

- `FLASK_ENV`: Environment (development, production, testing)
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS`: Database credentials
- `MODEL_PATH`: Path to LoRA model directory
- `FLASK_HOST`, `FLASK_PORT`: Server binding

### Runtime Configuration

Edit [config.py](config.py) to customize:
- Default inference steps
- Guidance scale
- Image dimensions
- SDXL model ID
- JWT token expiry

## Troubleshooting

### Database Connection Error

```
psycopg2.OperationalError: could not connect to server
```

**Solution**: Ensure PostgreSQL is running and credentials in `.env` are correct.

```bash
# Check PostgreSQL status
sudo systemctl status postgresql  # Linux
brew services list | grep postgres  # Mac
# Or start PostgreSQL if not running
```

### CUDA Out of Memory

Model requires ~12GB VRAM. If you get OOM errors:

1. Reduce `num_inference_steps` (default 30)
2. Reduce `IMAGE_SIZE` (default 1024)
3. Enable memory optimization in generator.py
4. Use CPU-only mode (slower but works)

### Model Download Issues

Model (~7GB) is downloaded on first use. Ensure:
- Internet connection is stable
- Sufficient disk space
- HuggingFace is accessible

First generation may take 5-10 minutes.

### JWT Token Expired

Token expires after 24 hours (configurable). Get a new token by logging in again.

## Performance Optimization

### GPU Usage
- U-Net and VAE kept on GPU
- Text encoders on CPU to save VRAM
- Mixed precision (float16 on GPU, float32 on CPU)
- Attention slicing enabled

### Generation Time
- First generation: 5-10 minutes (model loading + download)
- Subsequent: 30-60 seconds at 30 inference steps

### Scaling Considerations
- Currently single-threaded model loading
- Can run multiple Flask workers with shared generator instance
- Consider message queue (Celery) for production

## Development

### Run Tests

```bash
python -m pytest tests/
```

### Reset Database

```bash
python init_db.py --reset
```

### Check Logs

Enable debug logging:

```python
# In app.py or config.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Production Deployment

### Pre-deployment Checklist

- [ ] Change all secret keys in `.env`
- [ ] Set `FLASK_ENV=production`
- [ ] Use strong database password
- [ ] Enable HTTPS/SSL
- [ ] Set up proper logging
- [ ] Configure CORS appropriately
- [ ] Use production WSGI server (Gunicorn, uWSGI)

### Deploy with Gunicorn

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

### Docker Deployment (Optional)

Create `Dockerfile` and `docker-compose.yml` for containerization.

## License

This project is provided as-is for local development use.

## Support

For issues or questions, refer to:
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Diffusers Documentation](https://huggingface.co/docs/diffusers)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
