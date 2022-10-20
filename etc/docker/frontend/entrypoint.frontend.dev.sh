#!/bin/sh

set -e

cd /app

echo "Installing the dependencies..."
npm install --include=dev

echo "Running the development server..."
exec npm run dev
