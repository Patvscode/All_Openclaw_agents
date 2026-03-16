#!/usr/bin/env bash
# safe_write.sh — Check file size before and after operations
# Usage: safe_write.sh <filepath>
# Reports file size and token estimate, warns if dangerous

file="$1"
if [ -z "$file" ]; then
    echo "Usage: safe_write.sh <filepath>"
    exit 1
fi

if [ -f "$file" ]; then
    size=$(wc -c < "$file")
    tokens=$((size / 3))
    echo "📄 $file: ${size} bytes (~${tokens} tokens)"
    if [ "$tokens" -gt 8000 ]; then
        echo "🚫 DO NOT READ THIS FILE — it will overflow your context"
        echo "   Use 'edit' tool for targeted changes, or write to a new file"
        exit 2
    elif [ "$tokens" -gt 5000 ]; then
        echo "⚠️  LARGE — read-only, do not try to rewrite"
        exit 1  
    else
        echo "✅ Safe to read and modify"
        exit 0
    fi
else
    echo "📄 $file: does not exist yet (safe to create)"
    exit 0
fi
