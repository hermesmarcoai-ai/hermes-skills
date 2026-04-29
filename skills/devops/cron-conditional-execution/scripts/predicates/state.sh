#!/bin/bash
# state.sh - State predicate evaluator
# Usage: state.sh "KEY OP VAL"
# OP is == or !=

STATE_DIR="${STATE_DIR:-/var/run/cond-cron}"

expr="${1:-}"
[[ -z "$expr" ]] && echo "state: no expression specified" >&2 && exit 2

if [[ "$expr" == *"=="* ]]; then
    key="${expr%%==*}"
    val="${expr#*==}"
    op="=="
elif [[ "$expr" == *"!="* ]]; then
    key="${expr%%!=*}"
    val="${expr#*!=}"
    op="!="
else
    echo "state: operator required (== or !=)" >&2
    exit 2
fi

key=$(echo "$key" | xargs)
val=$(echo "$val" | xargs)

state_file="${STATE_DIR}/${key}"
[[ ! -f "$state_file" ]] && [[ "$op" == "!=" ]] && exit 0
[[ ! -f "$state_file" ]] && exit 1

actual=$(cat "$state_file" | tr -d '\n' | xargs)

[[ "$op" == "==" && "$actual" == "$val" ]] && exit 0
[[ "$op" == "!=" && "$actual" != "$val" ]] && exit 0
exit 1
