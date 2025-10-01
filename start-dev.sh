#!/bin/bash

# Algorand Prediction Market - Development Startup Script
# This script starts both the smart contract backend and frontend

set -e

echo "🚀 Starting Algorand Prediction Market Development Environment"
echo "============================================================"

# Check if AlgoKit is installed
if ! command -v algokit &> /dev/null; then
    echo "❌ AlgoKit is not installed. Please install it first:"
    echo "   pip install algokit"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

# Set up cleanup trap
trap cleanup SIGINT SIGTERM

echo "1️⃣ Starting Algorand LocalNet..."
# Start LocalNet in background
algokit localnet start &
LOCALNET_PID=$!

# Wait for LocalNet to be ready
sleep 10

echo "2️⃣ Deploying Smart Contract..."
cd projects/algorand-prediction-market

# Install Python dependencies if needed
if [ ! -d ".venv" ]; then
    echo "   Installing Python dependencies..."
    poetry install
fi

# Deploy the contract
echo "   Deploying prediction market contract..."
poetry run algokit project deploy localnet || {
    echo "❌ Failed to deploy smart contract"
    kill $LOCALNET_PID 2>/dev/null || true
    exit 1
}

# Get the deployed app ID (this would be dynamic in a real setup)
echo "   ✅ Smart contract deployed successfully"

cd ../../

echo "3️⃣ Starting Frontend..."
cd frontend

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "   Installing Node.js dependencies..."
    npm install
fi

# Start the frontend development server
echo "   Starting Next.js development server..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Development environment is ready!"
echo "============================================================"
echo "📱 Frontend:      http://localhost:3000"
echo "🔗 LocalNet:      http://localhost:4001"
echo "📊 Indexer:       http://localhost:8980"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop
wait
