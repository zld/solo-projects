#!/bin/bash
cd "$(dirname "$0")"

echo "Starting Inventory System..."
echo ""

echo "[1/2] Starting backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
python main.py &
BACKEND_PID=$!

sleep 3

echo ""
echo "[2/2] Starting frontend..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run dev &
FRONTEND_PID=$!

echo ""
echo "System started!"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
