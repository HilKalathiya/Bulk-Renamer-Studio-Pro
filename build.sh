#!/bin/bash
echo "Building High-Performance Go Engine..."

cd core_engine
go mod init renamer_engine 2>/dev/null || true
# Build for the current OS
go build -o renamer_engine.exe renamer.go # Will output .exe on Windows
go build -o renamer_engine renamer.go     # Will output binary on Linux/Mac

echo "Build Complete. Engine ready."