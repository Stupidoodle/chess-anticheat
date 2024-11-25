#!/bin/bash

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed. Aborting." >&2; exit 1; }

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.dev.txt

# Install Node.js dependencies
cd client
npm install

# Setup pre-commit hooks
pre-commit install

# Setup development databases
docker-compose -f docker-compose.dev.yml up -d

# Initialize database schemas
alembic upgrade head

# Download and setup Stockfish
mkdir -p engines
cd engines
wget https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar
tar -xf stockfish-ubuntu-x86-64-avx2.tar
chmod +x stockfish/stockfish-ubuntu-x86-64-avx2

echo "Development environment setup complete!"