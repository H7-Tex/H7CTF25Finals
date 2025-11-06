#!/bin/bash

# Build and test script for Horcrux Validator

echo "========================================"
echo "Building Platform 9¾ Docker Image"
echo "========================================"

cd "$(dirname "$0")"

# Build the Docker image
docker build -t platform-nine-three-quarters .

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build successful!"
    echo ""
    echo "To run the container:"
    echo "  docker run -p 3000:3000 platform-nine-three-quarters"
    echo ""
    echo "Then access: http://localhost:3000"
    echo ""
    echo "To test with curl:"
    echo '  curl -X POST http://localhost:3000/api/validate -H "Content-Type: application/json" -d '"'"'{"flag":"H7CTF{c4ll_0ut_my_name}","sessionId":"test123"}'"'"''
    echo ""
    echo "Test all flags:"
    echo '  ./test_flags.sh'
    echo ""
else
    echo "✗ Build failed!"
    exit 1
fi
