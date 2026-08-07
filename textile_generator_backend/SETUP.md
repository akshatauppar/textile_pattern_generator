# Installation and Setup Guide

## Quick Start (5 minutes)

### 1. Prerequisites Check

Verify you have:
- Python 3.9+ installed
- PostgreSQL running locally
- ~20GB free disk space
- (Optional) CUDA 11.8+ for GPU support

```bash
python --version          # Should be 3.9+
psql --version           # Should show PostgreSQL version
nvidia-smi               # Check GPU (optional)
```

### 2. Clone Repository

```bash
cd textile_generator_backend
```

### 3. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Setup PostgreSQL

```bash
# Open PostgreSQL terminal
psql -U postgres

# Create user and database
CREATE USER textile_user WITH PASSWORD 'textile_pass';
CREATE DATABASE textile_generator OWNER textile_user;
GRANT ALL PRIVILEGES ON DATABASE textile_generator TO textile_user;
\q
```

### 6. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings (or use defaults)
```

### 7. Initialize Database

```bash
python init_db.py --init
python init_db.py --seed
```

### 8. Start Server

```bash
python app.py
```

Visit `http://localhost:5000` - you should see:
```json
{
  "message": "Textile Pattern Generator API",
  "version": "1.0.0",
  "status": "running"
}
```

---

## Detailed Setup Guide

### Windows Setup

**Install Python:**
1. Download from python.org
2. Run installer
3. Check "Add Python to PATH"

**Install PostgreSQL:**
1. Download from postgresql.org
2. Run installer, note the password
3. Accept default port 5432

**Setup Project:**
```bash
# Clone/extract project
cd textile_generator_backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL user/database
# Open pgAdmin or use Command Prompt as administrator
psql -U postgres

# Enter PostgreSQL commands (see step 5 above)
```

### Linux/Mac Setup

**Install Dependencies:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.9 python3.9-venv postgresql postgresql-contrib

# Mac (using Homebrew)
brew install python@3.9 postgresql
brew services start postgresql
```

**Setup Project:**
```bash
cd textile_generator_backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL user/database
sudo -u postgres psql

# Enter PostgreSQL commands (see step 5 above)
```

---

## GPU Setup (Optional but Recommended)

### NVIDIA GPU

**Install CUDA Toolkit:**
1. Download from nvidia.com/cuda-downloads
2. Follow installation guide for your OS
3. Verify: `nvcc --version` and `nvidia-smi`

**Install cuDNN:**
1. Download from nvidia.com/cudnn
2. Extract to CUDA installation directory

**Verify PyTorch GPU:**
```bash
python -c "import torch; print(torch.cuda.is_available())"  # Should print True
```

### CPU-Only Setup

If you don't have a GPU, the code will automatically use CPU:
- Slower generation (30-120 seconds per image)
- Lower memory requirements
- No changes needed - it works automatically

---

## Model Files

The model downloads automatically on first use (~7GB):

```bash
# On first generation request, you'll see:
# - Model downloading from HuggingFace
# - Saving to ~/.cache/huggingface/hub/
# - Takes 5-10 minutes
```

**To Pre-download Model:**
```python
from app.utils.generator import TextileGenerator

gen = TextileGenerator()
gen.load_model()  # Downloads model
print("Model loaded!")
```

---

## Database Management

### Reset Database

```bash
# Drop all tables and recreate (loses all data!)
python init_db.py --reset
```

### Only Initialize (keep existing data)

```bash
python init_db.py --init
```

### Add Sample Data

```bash
python init_db.py --seed
```

### Backup Database

```bash
# Backup
pg_dump -U textile_user textile_generator > backup.sql

# Restore
psql -U textile_user textile_generator < backup.sql
```

---

## Troubleshooting

### "pip: command not found"
- Add Python to PATH
- Use `python -m pip` instead of `pip`

### "ModuleNotFoundError: No module named 'flask'"
- Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- Run `pip install -r requirements.txt`

### "psycopg2: connection refused"
- PostgreSQL not running: `sudo systemctl start postgresql` (Linux) or open pgAdmin (Windows/Mac)
- Wrong credentials in `.env`
- User/database not created

### "CUDA out of memory"
- Reduce `num_inference_steps` in generation request (default 30)
- Use CPU: set `device = "cpu"` in generator.py
- Disable xformers optimization

### "ModuleNotFoundError: No module named 'torch'"
- Run `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118`
- For CPU-only: `pip install torch torchvision torchaudio`

### Port 5000 already in use
- Change port in `app.py`: `app.run(port=5001)`
- Or kill process using port: `lsof -ti:5000 | xargs kill -9` (Linux/Mac)

### "No such file or directory: 'models/textile_lora_final'"
- Model path not found in `.env`
- Ensure `MODEL_PATH` points to correct directory
- If using pre-trained model, download it first

---

## First Test Request

Once server is running:

```bash
# Test API is working
curl http://localhost:5000

# Register user
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@textile.local",
    "password": "testpass123"
  }'

# Generate pattern (as guest - no auth needed)
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "simple geometric pattern",
    "style": "block_print",
    "seed": 42
  }'

# Check generation status
curl http://localhost:5000/api/status/1
```

---

## Environment Configuration

### Development (.env)

```env
FLASK_ENV=development
SECRET_KEY=dev-secret-only-for-dev
JWT_SECRET_KEY=dev-jwt-secret-only-for-dev

DB_HOST=localhost
DB_PORT=5432
DB_NAME=textile_generator
DB_USER=textile_user
DB_PASS=textile_pass

MODEL_PATH=../models/textile_lora_final
```

### Production (.env)

```env
FLASK_ENV=production
SECRET_KEY=<use-strong-random-key>
JWT_SECRET_KEY=<use-strong-random-key>

DB_HOST=<production-db-host>
DB_PORT=5432
DB_NAME=textile_generator
DB_USER=<strong-username>
DB_PASS=<strong-password>

MODEL_PATH=/opt/models/textile_lora_final
```

Generate strong keys:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Performance Tips

### Development
- Use default settings for testing
- First generation may be slow (model loading)

### Production
- Set `num_inference_steps` to 20 for faster generation
- Use GPU for best performance
- Consider caching frequently used prompts
- Implement rate limiting
- Use CDN for image serving

### Memory Optimization
- Keep text encoders on CPU (done by default)
- Enable attention slicing (done by default)
- Use float16 on GPU (done by default)

---

## Next Steps

1. **Generate Patterns**: POST `/api/generate`
2. **Check Status**: GET `/api/status/<id>`
3. **Download Images**: GET `/api/images/<filename>`
4. **View History**: GET `/api/history`
5. **Deploy**: See production deployment guide

See [API_REFERENCE.md](API_REFERENCE.md) for complete endpoint documentation.
