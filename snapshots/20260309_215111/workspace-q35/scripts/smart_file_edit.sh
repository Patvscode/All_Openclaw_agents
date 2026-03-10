#!/usr/bin/env bash
# smart_file_edit.sh — Helps Jess handle files that are too large for her context window
#
# Problem: Jess has 32K context. A 24K HTML file uses ~12K tokens just to read.
# After system prompt + task + response, she overflows.
#
# Solution: Before reading/writing large files, check if they fit.
# If too big, automatically split into smaller files or use chunked editing.
#
# Usage:
#   smart_file_edit.sh check <file>           — report if file fits in context
#   smart_file_edit.sh split-js <file>         — extract inline JS to external file
#   smart_file_edit.sh split-css <file>        — extract inline CSS to external file  
#   smart_file_edit.sh chunk-read <file> <n>   — read file in N-line chunks
#   smart_file_edit.sh append <file> <content> — safely append without reading whole file

set -euo pipefail

CTX_TOKENS=32768
RESERVED_TOKENS=10000  # system prompt + task + response headroom
MAX_FILE_TOKENS=$((CTX_TOKENS - RESERVED_TOKENS))  # ~16K tokens available for file content
CHARS_PER_TOKEN=3  # rough estimate
MAX_FILE_CHARS=$((MAX_FILE_TOKENS * CHARS_PER_TOKEN))  # ~64K chars

cmd="${1:-help}"
shift || true

case "$cmd" in
  check)
    file="$1"
    if [ ! -f "$file" ]; then
      echo "ERROR: File not found: $file"
      exit 1
    fi
    size=$(wc -c < "$file")
    lines=$(wc -l < "$file")
    est_tokens=$((size / CHARS_PER_TOKEN))
    
    echo "File: $file"
    echo "Size: ${size} bytes (~${est_tokens} tokens)"
    echo "Lines: ${lines}"
    echo "Context budget: ~${MAX_FILE_TOKENS} tokens for file content"
    echo ""
    
    # For read+modify, you need tokens for: read + new content + response overhead
    # Rule of thumb: if file is > 8K tokens, don't try to read+rewrite
    read_modify_limit=$((CTX_TOKENS / 4))  # ~8K tokens
    
    if [ "$est_tokens" -gt "$MAX_FILE_TOKENS" ]; then
      echo "🚫 TOO LARGE to even read!"
    elif [ "$est_tokens" -gt "$read_modify_limit" ]; then
      echo "⚠️  TOO LARGE to read+modify in one pass!"
      echo "Options:"
      echo "  1. Split inline JS/CSS to external files: smart_file_edit.sh split-js $file"
      echo "  2. Read in chunks: smart_file_edit.sh chunk-read $file 100"
      echo "  3. Append without reading: smart_file_edit.sh append $file 'content'"
      echo "  4. Use 'edit' tool with small targeted replacements"
      exit 2
    else
      echo "✅ File fits in context. Safe to read+modify."
      exit 0
    fi
    ;;

  split-js)
    file="$1"
    dir=$(dirname "$file")
    base=$(basename "$file" .html)
    jsfile="$dir/${base}-scripts.js"
    
    # Extract everything between <script> and </script>
    python3 -c "
import re
with open('$file') as f:
    html = f.read()

# Find the main script block
match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if not match:
    print('No inline script found')
    exit(1)

js_content = match.group(1)

# Write JS to external file
with open('$jsfile', 'w') as f:
    f.write(js_content.strip() + '\n')

# Replace inline script with external reference
new_html = html.replace(match.group(0), '<script src=\"${base}-scripts.js\"></script>')
with open('$file', 'w') as f:
    f.write(new_html)

print(f'Extracted {len(js_content)} chars of JS to $jsfile')
print(f'HTML reduced from {len(html)} to {len(new_html)} chars')
"
    ;;

  split-css)
    file="$1"
    dir=$(dirname "$file")
    base=$(basename "$file" .html)
    cssfile="$dir/${base}-styles.css"
    
    python3 -c "
import re
with open('$file') as f:
    html = f.read()

match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
if not match:
    print('No inline style found')
    exit(1)

css_content = match.group(1)
with open('$cssfile', 'w') as f:
    f.write(css_content.strip() + '\n')

new_html = html.replace(match.group(0), '<link rel=\"stylesheet\" href=\"${base}-styles.css\">')
with open('$file', 'w') as f:
    f.write(new_html)

print(f'Extracted {len(css_content)} chars of CSS to $cssfile')
"
    ;;

  chunk-read)
    file="$1"
    chunk_size="${2:-100}"
    total=$(wc -l < "$file")
    chunks=$(( (total + chunk_size - 1) / chunk_size ))
    echo "File: $file ($total lines, $chunks chunks of $chunk_size lines)"
    echo "Use: sed -n '<start>,<end>p' $file"
    echo ""
    for i in $(seq 1 $chunks); do
      start=$(( (i-1) * chunk_size + 1 ))
      end=$(( i * chunk_size ))
      [ "$end" -gt "$total" ] && end=$total
      echo "  Chunk $i: lines $start-$end  →  sed -n '${start},${end}p' $file"
    done
    ;;

  append)
    file="$1"
    shift
    content="$*"
    echo "$content" >> "$file"
    echo "Appended $(echo "$content" | wc -c) bytes to $file"
    ;;

  help|*)
    echo "smart_file_edit.sh — Handle files larger than context window"
    echo ""
    echo "Commands:"
    echo "  check <file>              Check if file fits in 32K context"
    echo "  split-js <file>           Extract inline <script> to external .js"
    echo "  split-css <file>          Extract inline <style> to external .css"  
    echo "  chunk-read <file> [lines] Show how to read file in chunks"
    echo "  append <file> <content>   Append without reading whole file"
    ;;
esac
