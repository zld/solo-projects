#!/bin/bash
cd "$(dirname "$0")"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Starting frontend server..."
npm run dev
