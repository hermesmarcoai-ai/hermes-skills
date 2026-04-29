#!/bin/bash
# cron-wrapper.sh - Conditional cron job execution wrapper
# Evaluates predicates before running the actual job

set -euo pipefail

VERSION="1.0.0"

# Defaults
VERBOSE=false
DRY_RUN=false
LOG_FILE=""
STATE_DIR="/var/run/cond-cron"
PREDICATES=()
COMMAND=()

# Price cache (60 second TTL)
declare -A PRICE_CACHE
CACHE_TTL=60
CACHE_TIMESTAMP=0

usage() {
    cat <<EOF
cron-wrapper.sh v${VERSION} - Conditional cron job execution

Usage: cron-wrapper.sh [OPTIONS] -- PREDICATES -- COMMAND [ARG...]

Options:
  -v           Verbose output
  -n           Dry-run mode (don't execute job)
  -l LOG       Log file path
  -s DIR       State directory (default: /var/run/cond-cron)

Predicates:
  shell:"CMD"       Run if CMD exits 0
  time:"MIN HR DOM MON DOW"  Run only during specified time(s)
  state:"KEY OP VAL"  Check state file (KEY == VAL or KEY != VAL)
  price:"SYM OP N"   Run if price comparison is true

Multiple predicates: ALL must pass (AND logic)

Examples:
  cron-wrapper.sh -- shell:"test -f /tmp/ready" -- ./job.sh
  cron-wrapper.sh -v -- price:"BTC > 50000" -- ./trade.sh
  cron-wrapper.sh -n -- shell:"true" -- time:"9-17 * * *" -- echo "would run"

Exit codes:
  0 - Job executed successfully
  1 - Condition failed (job skipped)
  2 - Syntax error
  3 - Command not found
EOF
    exit 2
}

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg"
    [[ -n "$LOG_FILE" ]] && echo "$msg" >> "$LOG_FILE" || true
}

err() {
    log "ERROR: $*"
}

# Parse arguments
while getopts "vnl:s:h" opt; do
    case $opt in
        v) VERBOSE=true ;;
        n) DRY_RUN=true; VERBOSE=true ;;
        l) LOG_FILE="$OPTARG" ;;
        s) STATE_DIR="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done
shift $((OPTIND - 1))

# Skip -- separator
[[ "${1:-}" == "--" ]] && shift

# Collect predicates until we hit --
while [[ $# -gt 0 ]] && [[ "$1" != "--" ]]; do
    PREDICATES+=("$1")
    shift
done

# Skip second --
[[ "${1:-}" == "--" ]] && shift

# Remaining is command
COMMAND=("$@")

if [[ ${#PREDICATES[@]} -eq 0 ]]; then
    err "No predicates specified"
    usage
fi

if [[ ${#COMMAND[@]} -eq 0 ]]; then
    err "No command specified"
    usage
fi

# ─── Predicate Evaluators ────────────────────────────────────────────────────

resolve_shell() {
    local cmd="$1"
    cmd="${cmd#shell:}"
    cmd="${cmd#\"}"
    cmd="${cmd%\"}"
    if [[ "$cmd" == *'"'* ]]; then
        # Already quoted, strip the outer shell: quotes
        :
    fi
    if $VERBOSE; then
        log "SHELL: evaluating: $cmd"
    fi
    # Use explicit exit status capture to avoid set -e interference
    bash -c "$cmd" "$cmd"
    return $?
}

resolve_time() {
    local spec="$1"
    spec="${spec#time:}"
    spec="${spec#\"}"
    spec="${spec%\"}"

    if $VERBOSE; then
        log "TIME: checking against spec: $spec"
    fi

    # Parse cron spec: MIN HR DOM MON DOW
    read -r min hour dom mon dow <<< "$spec"

    # Get current values
    local now_min now_hour now_dom now_mon now_dow
    now_min=$(date '+%M')
    now_hour=$(date '+%H')
    now_dom=$(date '+%d')
    now_mon=$(date '+%m')
    now_dow=$(date '+%w')

    # Handle ranges like 9-17
    check_range() {
        local val=$1
        local range=$2
        if [[ "$range" == *"-"* ]]; then
            local start end
            start=${range%-*}
            end=${range#*-}
            [[ $val -ge $start && $val -le $end ]]
        else
            [[ "$val" == "$range" ]]
        fi
    }

    # Validate each field
    [[ "$min" != "*" ]] && check_range "$now_min" "$min" || [[ "$min" == "*" ]] || return 1
    [[ "$hour" != "*" ]] && check_range "$now_hour" "$hour" || [[ "$hour" == "*" ]] || return 1
    [[ "$dom" != "*" ]] && check_range "$now_dom" "$dom" || [[ "$dom" == "*" ]] || return 1
    [[ "$mon" != "*" ]] && check_range "$now_mon" "$mon" || [[ "$mon" == "*" ]] || return 1
    [[ "$dow" != "*" ]] && check_range "$now_dow" "$dow" || [[ "$dow" == "*" ]] || return 1

    return 0
}

resolve_state() {
    local expr="$1"
    expr="${expr#state:}"
    expr="${expr#\"}"
    expr="${expr%\"}"

    if $VERBOSE; then
        log "STATE: checking: $expr"
    fi

    # Parse: KEY OP VAL
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
        err "State predicate requires == or != operator"
        return 2
    fi

    key="${key#"${key%%[![:space:]]*}"}"
    key="${key%"${key##*[![:space:]]}"}"
    val="${val#"${val%%[![:space:]]*}"}"
    val="${val%"${val##*[![:space:]]}"}"

    local state_file="${STATE_DIR}/${key}"
    if [[ ! -f "$state_file" ]]; then
        if [[ "$op" == "!=" ]]; then
            return 0
        fi
        return 1
    fi

    local actual
    actual=$(cat "$state_file" | tr -d '\n')
    actual="${actual#"${actual%%[![:space:]]*}"}"
    actual="${actual%"${actual##*[![:space:]]}"}"

    if $VERBOSE; then
        log "STATE: $key = '$actual' (expected $op '$val')"
    fi

    [[ "$op" == "==" && "$actual" == "$val" ]] && return 0
    [[ "$op" == "!=" && "$actual" != "$val" ]] && return 0
    return 1
}

get_cached_price() {
    local symbol=$1
    local now=$(date +%s)

    if [[ -n "${PRICE_CACHE[$symbol]:-}" ]]; then
        local age=$((now - CACHE_TIMESTAMP))
        if [[ $age -lt $CACHE_TTL ]]; then
            echo "${PRICE_CACHE[$symbol]}"
            return 0
        fi
    fi
    return 1
}

set_cached_price() {
    local symbol=$1
    local price=$2
    PRICE_CACHE[$symbol]=$price
    CACHE_TIMESTAMP=$(date +%s)
}

fetch_price() {
    local symbol=$1

    # Try cache first
    if get_cached_price "$symbol"; then
        return 0
    fi

    # CoinGecko API (free, no key)
    local price
    price=$(curl -s --max-time 10 "https://api.coingecko.com/api/v3/simple/price?ids=${symbol,,}&vs_currencies=usd" 2>/dev/null | \
        python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('${symbol,,}',{}).get('usd','ERROR'))" 2>/dev/null) || true

    if [[ "$price" == "ERROR" ]] || [[ -z "$price" ]]; then
        # Fallback to Binance
        price=$(curl -s --max-time 10 "https://api.binance.com/api/v3/ticker/price?symbol=${symbol^^}USDT" 2>/dev/null | \
            python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('price','ERROR'))" 2>/dev/null) || true
    fi

    if [[ "$price" == "ERROR" ]] || [[ -z "$price" ]]; then
        err "Failed to fetch price for $symbol"
        return 1
    fi

    set_cached_price "$symbol" "$price"
    echo "$price"
}

resolve_price() {
    local expr="$1"
    expr="${expr#price:}"
    expr="${expr#\"}"
    expr="${expr%\"}"

    if $VERBOSE; then
        log "PRICE: checking: $expr"
    fi

    # Parse: SYMBOL OP VALUE [&& SYMBOL OP VALUE]...
    local parts
    IFS='&&' read -ra parts <<< "$expr"

    for part in "${parts[@]}"; do
        part="${part#"${part%%[![:space:]]*}"}"
        part="${part%"${part##*[![:space:]]}"}"

        local symbol op threshold
        if [[ "$part" =~ ^([A-Za-z]+)\ ([<>]=?)\ ([0-9.]+)$ ]]; then
            symbol="${BASH_REMATCH[1]}"
            op="${BASH_REMATCH[2]}"
            threshold="${BASH_REMATCH[3]}"
        else
            err "Invalid price expression: $part"
            return 2
        fi

        local current_price
        current_price=$(fetch_price "$symbol") || return 1

        if $VERBOSE; then
            log "PRICE: $symbol = $current_price (check: $op $threshold)"
        fi

        case $op in
            ">")  [[ $(echo "$current_price > $threshold" | bc -l) == 1 ]] || return 1 ;;
            "<")  [[ $(echo "$current_price < $threshold" | bc -l) == 1 ]] || return 1 ;;
            ">=") [[ $(echo "$current_price >= $threshold" | bc -l) == 1 ]] || return 1 ;;
            "<=") [[ $(echo "$current_price <= $threshold" | bc -l) == 1 ]] || return 1 ;;
            "==") [[ $(echo "$current_price == $threshold" | bc -l) == 1 ]] || return 1 ;;
            "!=") [[ $(echo "$current_price != $threshold" | bc -l) == 1 ]] || return 1 ;;
        esac
    done

    return 0
}

evaluate_predicate() {
    local pred="$1"
    local type="${pred%%:*}"
    local value="${pred#*:}"

    case $type in
        shell) resolve_shell "$pred" ;;
        time)  resolve_time "$pred" ;;
        state) resolve_state "$pred" ;;
        price) resolve_price "$pred" ;;
        *)
            err "Unknown predicate type: $type"
            return 2
            ;;
    esac
}

# ─── Main Logic ───────────────────────────────────────────────────────────────

log "=== Cron Wrapper Started ==="
[[ "$DRY_RUN" == true ]] && log "DRY RUN MODE"

# Evaluate all predicates
echo "DEBUG: PREDICATES=${#PREDICATES[@]}, COMMAND=${#COMMAND[@]}" >&2
for pred in "${PREDICATES[@]}"; do
    echo "DEBUG LOOP: pred=$pred" >&2
    if $VERBOSE; then
        log "Evaluating predicate: $pred"
    fi

    if ! evaluate_predicate "$pred"; then
        log "Condition failed: $pred — skipping job"
        if [[ -n "$LOG_FILE" ]]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] SKIPPED: ${COMMAND[*]} (condition failed)" >> "$LOG_FILE"
        fi
        exit 1
    fi

    if $VERBOSE; then
        log "Predicate passed: $pred"
    fi
done

log "All conditions passed — executing: ${COMMAND[*]}"

if [[ "$DRY_RUN" == true ]]; then
    log "DRY RUN: would execute: ${COMMAND[*]}"
    exit 0
fi

# Execute the command
"${COMMAND[@]}"
exit_code=$?

if [[ $exit_code -eq 0 ]]; then
    log "Job completed successfully"
else
    log "Job failed with exit code: $exit_code"
fi

exit $exit_code
