@echo off
echo Testing Textile Generator API...
echo.

echo [1/5] Health Check...
curl http://localhost:5000/api/health
echo.

echo [2/5] Available Styles...
curl http://localhost:5000/api/styles
echo.

echo [3/5] Generating Pattern...
curl -X POST http://localhost:5000/api/generate -H "Content-Type: application/json" -d "{\"prompt\":\"geometric pattern\",\"style\":\"block_print\"}"
echo.

echo [4/5] Check Status (ID=1)...
timeout /t 5
curl http://localhost:5000/api/status/1
echo.

echo [5/5] Done!
pause