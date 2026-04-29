#!/bin/bash
# time.sh - Time predicate evaluator
# Usage: time.sh "MIN HR DOM MON DOW"

spec="${1:-}"
[[ -z "$spec" ]] && echo "time: no spec specified" >&2 && exit 2

read -r min hour dom mon dow <<< "$spec"

now_min=$(date '+%M')
now_hour=$(date '+%H')
now_dom=$(date '+%d')
now_mon=$(date '+%m')
now_dow=$(date '+%w')

check_range() {
    local val=$1 range=$2
    [[ "$range" == "*" ]] && return 0
    [[ "$range" == *"-"* ]] || { [[ "$val" == "$range" ]]; return $?; }
    local start end
    start=${range%-*}
    end=${range#*-}
    [[ $val -ge $start && $val -le $end ]]
}

check_range "$now_min" "$min" || exit 1
check_range "$now_hour" "$hour" || exit 1
check_range "$now_dom" "$dom" || exit 1
check_range "$now_mon" "$mon" || exit 1
check_range "$now_dow" "$dow" || exit 1
exit 0
