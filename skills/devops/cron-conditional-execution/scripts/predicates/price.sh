#!/bin/bash
# price.sh - Price predicate evaluator
# Usage: price.sh "SYMBOL OP THRESHOLD [&& SYMBOL OP THRESHOLD]..."

# Cache for 60 seconds
CACHE_FILE="${XDG_CACHE_HOME:-$HOME/.cache}/cond-cron-price-cache.json"
CACHE_TTL=60

get_cached_price() {
    local symbol=$1
    local now
    now=$(date +%s)

    [[ -f "$CACHE_FILE" ]] || return 1

    local entry
    entry=$(python3 -c "
import sys, json, time
try:
    with open('$CACHE_FILE') as f:
        cache = json.load(f)
    entry = cache.get('$symbol', {})
    if entry and (time.time() - entry.get('ts', 0)) < $CACHE_TTL:
        print(entry.get('price', ''))
except:
    pass
" 2>/dev/null) || return 1

    [[ -n "$entry" ]] && echo "$entry" && return 0
    return 1
}

set_cached_price() {
    local symbol=$1
    local price=$2
    local now
    now=$(date +%s)

    python3 -c "
import sys, json, time, os
cache_file = '$CACHE_FILE'
cache = {}
if os.path.exists(cache_file):
    try:
        with open(cache_file) as f:
            cache = json.load(f)
    except:
        pass
cache['$symbol'] = {'price': '$price', 'ts': time.time()}
with open(cache_file, 'w') as f:
    json.dump(cache, f)
" 2>/dev/null || true
}

fetch_price() {
    local symbol=$1

    get_cached_price "$symbol" && return 0

    local price

    # Try CoinGecko
    price=$(curl -s --max-time 10 "https://api.coingecko.com/api/v3/simple/price?ids=${symbol,,}&vs_currencies=usd" 2>/dev/null | \
        python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('${symbol,,}',{}).get('usd',''))" 2>/dev/null) || true

    if [[ -z "$price" ]]; then
        # Fallback to Binance
        price=$(curl -s --max-time 10 "https://api.binance.com/api/v3/ticker/price?symbol=${symbol^^}USDT" 2>/dev/null | \
            python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('price',''))" 2>/dev/null) || true
    fi

    [[ -z "$price" ]] && return 1
    set_cached_price "$symbol" "$price"
    echo "$price"
}

expr="${1:-}"
[[ -z "$expr" ]] && echo "price: no expression specified" >&2 && exit 2

IFS='&&' read -ra parts <<< "$expr"

for part in "${parts[@]}"; do
    part=$(echo "$part" | xargs)
    [[ "$part" =~ ^([A-Za-z]+)\ ([<>]=?)\ ([0-9.]+)$ ]] || { echo "price: invalid expression: $part" >&2; exit 2; }

    symbol="${BASH_REMATCH[1]}"
    op="${BASH_REMATCH[2]}"
    threshold="${BASH_REMATCH[3]}"

    price=$(fetch_price "$symbol") || { echo "price: failed to fetch $symbol" >&2; exit 1; }

    result=$(echo "$price $op $threshold" | bc -l 2>/dev/null) || { echo "price: comparison failed" >&2; exit 2; }
    [[ "$result" == "1" ]] || exit 1
done

exit 0
