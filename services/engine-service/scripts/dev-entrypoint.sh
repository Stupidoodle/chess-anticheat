#!/bin/bash

# Verify Stockfish installation
echo "Verifying Stockfish installation..."
if ! command -v stockfish &> /dev/null; then
    echo "Error: Stockfish not found"
    exit 1
fi

# Test Stockfish
echo "Testing Stockfish..."
stockfish quit

# Set up engine configuration
echo "Configuring Stockfish..."
stockfish << EOF
setoption name Threads value $ENGINE_THREADS
setoption name Hash value $MAX_HASH_SIZE
quit
EOF

# Start development server
echo "Starting development server..."
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload --log-level debug