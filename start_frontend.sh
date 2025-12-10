#!/bin/bash

echo "Starting LCR Module A Frontend..."
echo ""

cd frontend || exit 1

if [ ! -d "node_modules" ]; then
    echo "ERROR: Node modules not found!"
    echo "Please run setup first:"
    echo "  cd frontend"
    echo "  npm install"
    exit 1
fi

echo "Starting Vite development server..."
echo "Frontend will open at http://localhost:3000"
echo "Press Ctrl+C to stop"
echo ""

npm run dev
