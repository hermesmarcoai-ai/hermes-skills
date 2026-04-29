#!/bin/bash
# shell.sh - Shell predicate evaluator
# Usage: shell.sh "command"

cmd="${1:-}"
[[ -z "$cmd" ]] && echo "shell: no command specified" >&2 && exit 2

bash -c "$cmd"
