    # Quick Reference Card

## 🚀 Start Server (30 seconds)

```bash
cd textile_generator_backend
python app.py
# Visit: http://localhost:5000
```

---

## 🔑 Key Commands

### Setup
```bash
python init_db.py --init     # Initialize database
python init_db.py --seed     # Add sample data
python init_db.py --reset    # Reset everything
```

### Run
```bash
python app.py                # Development
gunicorn wsgi:app            # Production
docker-compose up -d         # Docker
```

### Configure
```bash
cp .env.example .env         # Create config
# Edit .env with your settings
```

---

## 📡 API Cheat Sheet

### Health
```bash
curl http://localhost:5000/api/health
```

### Register
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user","email":"user@test.com","password":"pass123"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123"}'
# Copy the access_token
```

### Generate (No Auth)
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"floral pattern","style":"bandhani"}'
```

### Generate (With Auth)
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt":"pattern","style":"ikat","color_1":"indigo","seed":42}'
```

### Check Status
```bash
curl http://localhost:5000/api/status/1
```

### Get History
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/history?limit=10
```

### Download Image
```bash
curl http://localhost:5000/api/images/textile_1_*.png -o pattern.png
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `app.py` | Flask entry point |
| `.env` | Configuration |
| `config.py` | Settings |
| `init_db.py` | Database setup |
| `app/models/__init__.py` | Database models |
| `app/routes/auth.py` | Auth endpoints |
| `app/routes/generation.py` | Generation endpoints |
| `app/utils/generator.py` | ML model |

---

## 🎨 Textile Styles

```
bandhani     → Tie-dye patterns
ikat         → Resist-dyed patterns
block_print  → Hand-stamped designs
paisley      → Ornate teardrop shapes
```

---

## ⚙️ Configuration Quick Reference

```env
FLASK_ENV=development
DB_HOST=localhost
DB_PORT=5432
DB_NAME=textile_generator
DB_USER=textile_user
DB_PASS=textile_pass
MODEL_PATH=../models/textile_lora_final
```

---

## 🐛 Common Errors & Fixes

| Error | Fix |
|-------|-----|
| PostgreSQL connection failed | Start PostgreSQL, check credentials |
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| CUDA out of memory | Use CPU, reduce steps, or optimize |
| Port 5000 in use | Change port or kill process: `lsof -ti:5000 \| xargs kill -9` |
| Model not found | Check MODEL_PATH in .env |
| JWT token invalid | Re-login to get new token |

---

## 📊 Performance Tips

### Faster Generation
- Reduce `num_inference_steps` from 30 to 20
- Use smaller `image_size` (default 1024)
- Pre-load model at startup

### More VRAM
- Enable xformers optimization
- Use attention slicing
- Keep text encoders on CPU (default)

### Production Scale
- Use Gunicorn with 4+ workers
- Setup load balancer (Nginx)
- Implement caching
- Monitor GPU usage

---

## 🔒 Security Checklist

- [ ] Change SECRET_KEY in .env
- [ ] Change JWT_SECRET_KEY in .env
- [ ] Change DB password in .env
- [ ] Use HTTPS in production
- [ ] Setup CORS restrictions
- [ ] Enable rate limiting
- [ ] Regular backups
- [ ] Monitor logs

---

## 📚 Documentation Map

```
README.md           → Setup & overview
API_REFERENCE.md    → All endpoints
SETUP.md           → Installation help
DEPLOYMENT.md      → Production guide
OVERVIEW.md        → Architecture
TESTING_EXAMPLES.md → 50+ examples
GETTING_STARTED.md → Quick start
```

---

## 🚢 Deployment Quick

### Local
```bash
python app.py
```

### Gunicorn
```bash
gunicorn -w 4 wsgi:app
```

### Docker
```bash
docker-compose up -d
```

### AWS
```bash
eb init -p python-3.9 textile
eb create textile-api-env
```

### Render.com
Push to GitHub → Connect Render

---

## 📱 API Endpoints (9 total)

```
POST   /api/register           Register user
POST   /api/login              Get token
GET    /api/me                 Current user

POST   /api/generate           Create pattern
GET    /api/status/<id>        Check progress
GET    /api/history            User's patterns
GET    /api/images/<filename>  Download image

GET    /api/health             Status
GET    /api/styles             Style list
```

---

## 🎯 Quick Workflow

### 1. Setup (5 mins)
```bash
bash quickstart.sh  # or quickstart.bat on Windows
python app.py
```

### 2. Register (optional)
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"me","email":"me@test.com","password":"pass123"}'
```

### 3. Generate
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"beautiful pattern","style":"bandhani"}'
```

### 4. Check Status
```bash
curl http://localhost:5000/api/status/1
# Wait for status: "completed"
```

### 5. Download
```bash
curl http://localhost:5000/api/images/textile_1_*.png > pattern.png
```

---

## 💾 Database Commands

### PostgreSQL Client
```bash
psql -U textile_user -d textile_generator
SELECT COUNT(*) FROM users;
SELECT * FROM generations ORDER BY created_at DESC;
```

### Backup
```bash
pg_dump -U textile_user textile_generator > backup.sql
```

### Restore
```bash
psql -U textile_user textile_generator < backup.sql
```

---

## 🆚 Comparison: Local vs Production

| Aspect | Local | Production |
|--------|-------|------------|
| Server | Flask dev | Gunicorn |
| Workers | 1 | 4+ |
| Debug | On | Off |
| Database | SQLite ok | PostgreSQL required |
| SSL | No | Yes |
| Monitoring | Manual | Automated |
| Backups | None | Daily |

---

## 📈 Expected Performance

| Phase | Duration |
|-------|----------|
| First setup | 5-10 mins |
| First generation | 5-10 mins (model download) |
| Subsequent | 30-60 secs |
| Database query | <100ms |
| Image download | 1-5 secs |

---

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Guide](https://docs.sqlalchemy.org/)
- [Diffusers Library](https://huggingface.co/docs/diffusers)
- [PyTorch Basics](https://pytorch.org/tutorials/)
- [PostgreSQL Manual](https://www.postgresql.org/docs/)

---

## 📞 Quick Help

### Check if running
```bash
curl http://localhost:5000
# Should return {"message": "Textile Pattern Generator API", ...}
```

### View logs
```bash
# Development
tail -f app.log

# Docker
docker-compose logs -f api

# Systemd
journalctl -u textile-api -f
```

### Reset everything
```bash
python init_db.py --reset
rm -rf uploads/*
python app.py
```

---

## 🎉 You're All Set!

**Next step:** Run `python app.py` and visit `http://localhost:5000`

**Questions?** Check:
- README.md for features
- API_REFERENCE.md for endpoints
- SETUP.md for help
- TESTING_EXAMPLES.md for examples

**Ready to deploy?** See DEPLOYMENT.md

---

Last Updated: December 2024
