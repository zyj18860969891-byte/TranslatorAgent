#!/bin/bash
set -e
cd backend_api
echo "Installing dependencies..."
npm install
echo "Starting application..."
node index.js