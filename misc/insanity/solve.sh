#!/bin/bash

# Test script for all 7 horcrux flags

BASE_URL="http://localhost:3000"
SESSION_ID="test_$(date +%s)"

echo "========================================"
echo "Testing Platform 9¾ - All 7 Flags"
echo "========================================"
echo "Session ID: $SESSION_ID"
echo ""

# Array of all 7 flags
FLAGS=(
    "H7CTF{c4ll_0ut_my_name}"
    "H7CTF{always_check_the_discord_start_messages_of_a_ctf_i_have_seen_it_a_number_of_times}"
    "H7CTF{h1d1ng_fl4gs_1n_d1sc0rd_1s_cr4zy}"
    "H7CTF{never_gonna_give_you_up_never_gonna_let_you_down}"
    "H7CTF{keeping_this_small_to_make_life_easier}"
    "H7CTF{do_you_believe_in_love_at_first_sight}"
    "H7CTF{https://pbs.twimg.com/media/F43XxNAb0AAugH3?format=jpg&name=small}"
)

# Test each flag
for i in "${!FLAGS[@]}"; do
    FLAG="${FLAGS[$i]}"
    NUM=$((i + 1))
    
    echo "Testing Horcrux $NUM..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/validate" \
        -H "Content-Type: application/json" \
        -d "{\"flag\":\"$FLAG\",\"sessionId\":\"$SESSION_ID\"}")
    
    VALID=$(echo "$RESPONSE" | grep -o '"valid":true')
    FOUND=$(echo "$RESPONSE" | grep -o '"found":[0-9]*' | cut -d: -f2)
    
    if [ -n "$VALID" ]; then
        echo "  ✓ Horcrux $NUM validated! ($FOUND/7 total)"
    else
        echo "  ✗ Horcrux $NUM failed!"
    fi
    
    sleep 0.5
done

echo ""
echo "========================================"
echo "Retrieving Final Flag..."
echo "========================================"

FINAL=$(curl -s -X POST "$BASE_URL/api/final" \
    -H "Content-Type: application/json" \
    -d "{\"sessionId\":\"$SESSION_ID\"}")

SUCCESS=$(echo "$FINAL" | grep -o '"success":true')

if [ -n "$SUCCESS" ]; then
    FLAG=$(echo "$FINAL" | grep -o '"flag":"[^"]*"' | cut -d'"' -f4)
    echo ""
    echo "✓ FINAL FLAG RETRIEVED:"
    echo "  $FLAG"
    echo ""
else
    echo ""
    echo "✗ Could not retrieve final flag"
    echo "$FINAL"
    echo ""
fi

echo "========================================"
