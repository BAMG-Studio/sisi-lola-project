#!/bin/bash

# Sisi Lola Modal Service Performance Test
# Tests DialoGPT inference endpoint

set -e

ENDPOINT="https://bamg-studio--sisi-lola-inference-modelinference-generate-text.modal.run"
HEALTH_ENDPOINT="https://bamg-studio--sisi-lola-inference-modelinference-health.modal.run"

echo "========================================"
echo "SISI LOLA MODAL SERVICE PERFORMANCE TEST"
echo "========================================"
echo ""

# Test 1: Health Check
echo "[TEST 1] Health Check..."
START=$(date +%s%N)
HEALTH_RESPONSE=$(curl -s $HEALTH_ENDPOINT)
END=$(date +%s%N)
HEALTH_TIME=$(( ($END - $START) / 1000000 ))
echo "Response: $HEALTH_RESPONSE"
echo "Time: ${HEALTH_TIME}ms"
echo ""

# Test 2: First Request (Cold Start / Warm-up)
echo "[TEST 2] First Generation Request (Warm-up)..."
START=$(date +%s%N)
RESPONSE1=$(curl -s -X POST $ENDPOINT \\
  -H 'Content-Type: application/json' \\
  -d '{"message": "Hello! How are you doing today?", "max_tokens": 30}' \\
  --max-time 60)
END=$(date +%s%N)
TIME1=$(( ($END - $START) / 1000000 ))
echo "Response: $RESPONSE1"
echo "Time: ${TIME1}ms"
echo ""

# Test 3: Second Request (Warmed up)
echo "[TEST 3] Second Generation Request (Warmed)..."
sleep 1
START=$(date +%s%N)
RESPONSE2=$(curl -s -X POST $ENDPOINT \\
  -H 'Content-Type: application/json' \\
  -d '{"message": "Tell me a joke", "max_tokens": 50}' \\
  --max-time 30)
END=$(date +%s%N)
TIME2=$(( ($END - $START) / 1000000 ))
echo "Response: $RESPONSE2"
echo "Time: ${TIME2}ms"
echo ""

# Test 4: Third Request
echo "[TEST 4] Third Generation Request..."
sleep 1
START=$(date +%s%N)
RESPONSE3=$(curl -s -X POST $ENDPOINT \\
  -H 'Content-Type: application/json' \\
  -d '{"message": "What can you help me with?", "max_tokens": 40}' \\
  --max-time 30)
END=$(date +%s%N)
TIME3=$(( ($END - $START) / 1000000 ))
echo "Response: $RESPONSE3"
echo "Time: ${TIME3}ms"
echo ""

# Test 5: Longer Response
echo "[TEST 5] Longer Response Test..."
sleep 1
START=$(date +%s%N)
RESPONSE4=$(curl -s -X POST $ENDPOINT \\
  -H 'Content-Type: application/json' \\
  -d '{"message": "Tell me a story about Nigeria", "max_tokens": 100}' \\
  --max-time 45)
END=$(date +%s%N)
TIME4=$(( ($END - $START) / 1000000 ))
echo "Response: $RESPONSE4"
echo "Time: ${TIME4}ms"
echo ""

# Summary
echo "========================================"
echo "PERFORMANCE SUMMARY"
echo "========================================"
echo "Health Check: ${HEALTH_TIME}ms"
echo "Request 1 (warm-up): ${TIME1}ms"
echo "Request 2 (warmed): ${TIME2}ms"
echo "Request 3: ${TIME3}ms"
echo "Request 4 (longer): ${TIME4}ms"
echo ""

# Calculate average (excluding first request)
if [ $TIME2 -gt 0 ] && [ $TIME3 -gt 0 ]; then
    AVG=$(( ($TIME2 + $TIME3 + $TIME4) / 3 ))
    echo "Average Response Time (warmed): ${AVG}ms"
fi

echo ""
echo "Test completed successfully!"
