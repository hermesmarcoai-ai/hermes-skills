#!/bin/bash
# test-condition.sh - Test predicates without running the full wrapper
# Returns 0 if condition passes, 1 if fails

set -uo pipefail

VERBOSE=true
STATE_DIR="${STATE_DIR:-/var/run/cond-cron}"

usage() {
    cat <<EOF
test-condition.sh - Validate cron predicates

Usage: test-condition.sh TYPE "EXPRESSION"

Types:
  shell   Test a shell command (exit 0 = pass)
  time    Test a time specification
  state   Test a state predicate
  price   Test a price predicate

Examples:
  test-condition.sh shell "test -f /tmp/exists"
  test-condition.sh time "9-17 * * *"
  test-condition.sh state "maintenance_mode != on"
  test-condition.sh price "BTC > 50000"

Exit codes:
  0 - Condition passes
  1 - Condition fails
  2 - Syntax error
EOF
    exit 2
}

[[ $# -lt 2 ]] && usage

TYPE="$1"
EXPR="$2"

# Load price functions from wrapper
get_cached_price() { return 1; }
set_cached_price() { :; }
fetch_price() {
    local symbol=$1
    local price
    price=$(curl -s --max-time 10 "https://api.coingecko.com/api/v3/simple/price?ids=${symbol,,}&vs_currencies=usd" 2>/dev/null | \
        python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('${symbol,,}',{}).get('usd','ERROR'))" 2>/dev/null) || true
    if [[ "$price" == "ERROR" ]] || [[ -z "$price" ]]; then
        price=$(curl -s --max-time 10 "https://api.binance.com/api/v3/ticker/price?symbol=${symbol^^}USDT" 2>/dev/null | \
            python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('price','ERROR'))" 2>/dev/null) || true
    fi
    [[ "$price" == "ERROR" ]] || [[ -z "$price" ]] && return 1
    echo "$price"
    return 0
}

test_shell() {
    local cmd="$EXPR"
    echo "[shell] Running: $cmd"
    if bash -c "$cmd" 2>/dev/null; then
        echo "[shell] PASS (exit 0)"
        return 0
    else
        echo "[shell] FAIL (exit non-zero)"
        return 1
    fi
}

test_time() {
    local spec="$EXPR"
    echo "[time] Checking: $spec"

    read -r min hour dom mon dow <<< "$spec"

    now_min=$(date '+%M')
    now_hour=$(date '+%H')
    now_dom=$(date '+%d')
    now_mon=$(date '+%m')
    now_dow=$(date '+%w')

    echo "[time] Current time: ${now_hour}:${now_min} (DOW=${now_dow})"

    check_range() {
        local val=$1 range=$2
        if [[ "$range" == *"-"* ]]; then
            local start end
            start=${range%-*}
            end=${range#*-}
            [[ $val -ge $start && $val -le $end ]]
        else
            [[ "$val" == "$range" ]]
        fi
    }

    [[ "$min" != "*" ]] && ! check_range "$now_min" "$min" && echo "[time] FAIL: minute $now_min not in $min" && return 1
    [[ "$hour" != "*" ]] && ! check_range "$now_hour" "$hour" && echo "[time] FAIL: hour $now_hour not in $hour" && return 1
    [[ "$dom" != "*" ]] && ! check_range "$now_dom" "$dom" && echo "[time] FAIL: dom $now_dom not in $dom" && return 1
    [[ "$mon" != "*" ]] && ! check_range "$now_mon" "$mon" && echo "[time] FAIL: mon $now_mon not in $mon" && return 1
    [[ "$dow" != "*" ]] && ! check_range "$now_dow" "$dow" && echo "[time] FAIL: dow $now_dow not in $dow" && return 1

    echo "[time] PASS"
    return 0
}

test_state() {
    local expr="$EXPR"
    echo "[state] Checking: $expr"

    local key op val
    if [[ "$expr" == *"=="* ]]; then
        key="${expr%%==*}"
        val="${expr#*==}"
        op="=="
    elif [[ "$expr" == *"!="* ]]; then
        key="${expr%%!=*}"
        val="${expr#*!=}"
        op="!="
    else
        echo "[state] ERROR: Need == or != operator"
        return 2
    fi

    key="${key#"${key%%[![:space:]]*}"}"
    key="${key%"${key##*[![:space:]]}"}"
    val="${val#"${val%%[![:space:]]*}"}"
    val="${val%"${val##*[![:space:]]}"}"

    local state_file="${STATE_DIR}/${key}"
    if [[ ! -f "$state_file" ]]; then
        if [[ "$op" == "!=" ]]; then
            echo "[state] PASS (file missing, treating as !=)"
            return 0
        fi
        echo "[state] FAIL: state file '$state_file' not found"
        return 1
    fi

    local actual
    actual=$(cat "$state_file" | tr -d '\n')
    actual="${actual#"${actual%%[![:space:]]*}"}"
    actual="${actual%"${actual##*[![:space:]]}"}"

    echo "[state] $key = '$actual' (expected $op '$val')"

    [[ "$op" == "==" && "$actual" == "$val" ]] && echo "[state] PASS" && return 0
    [[ "$op" == "!=" && "$actual" != "$val" ]] && echo "[state] PASS" && return 0

    echo "[state] FAIL"
    return 1
}

test_price() {
    local expr="$EXPR"
    echo "[price] Checking: $expr"

    local parts
    IFS='&&' read -ra parts <<< "$expr"

    for part in "${parts[@]}"; do
        part="${part#"${part%%[![:space:]]*}"}"
        part="${part%"${part##*[![:space:]]}"}"

        if [[ "$part" =~ ^([A-Za-z]+)\ ([<>]=?)\ ([0-9.]+)$ ]]; then
            local symbol="${BASH_REMATCH[1]}"
            local op="${BASH_REMATCH[2]}"
            local threshold="${BASH_REMATCH[3]}"
        else
            echo "[price] ERROR: Invalid expression: $part"
            return 2
        fi

        echo -n "[price] Fetching $symbol... "
        local price
        price=$(fetch_price "$symbol") || { echo "FAILED"; return 1; }
        echo "\$${price}"

        local result
        result=$(echo "$price $op $threshold" | bc -l)
        echo "[price] $price $op $threshold = $result"

        [[ "$result" == "1" ]] || { echo "[price] FAIL"; return 1; }
    done

    echo "[price] PASS"
    return 0
}

case "$TYPE" in
    shell) test_shell ;;
    time)  test_time ;;
    state) test_state ;;
    price) test_price ;;
    *)     echo "Unknown type: $TYPE" >&2; exit 2 ;;
esac
