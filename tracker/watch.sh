#!/bin/bash
# Watch every issue/PR and release feed behind the Apple LLM Compatibility Tracker,
# across llama.cpp, Ollama, LM Studio, oMLX, vllm-mlx, mlx-lm and ds4.
# The watchlist itself lives in probe.py, derived from the page's own data.
# CI runs probe.py directly (see .github/workflows/refresh.yml); this script is
# for watching locally.
# Emits ONE line per state change (open->closed, merged, new release). Silent otherwise.

SNAP="${SNAP:-$(cd "$(dirname "$0")" && pwd)/watch-state.txt}"
INTERVAL="${INTERVAL:-43200}"   # twice a day
GH="env -u GITHUB_TOKEN gh"

probe() {
  python3 "$(dirname "$0")/probe.py" 2>/dev/null
}

ONCE="${1:-}"

while true; do
  cur=$(probe)
  if [ -z "$cur" ]; then sleep "$INTERVAL"; continue; fi
  if [ ! -f "$SNAP" ]; then
    printf '%s' "$cur" > "$SNAP"
    echo "Tracker watch armed: $(printf '%s' "$cur" | grep -c .) items baselined."
  else
    while IFS='|' read -r key state label; do
      [ -z "$key" ] && continue
      old=$(grep -F "$key|" "$SNAP" 2>/dev/null | head -1 | cut -d'|' -f2)
      if [ -n "$old" ] && [ "$old" != "$state" ]; then
        if [[ "$key" == *"@release" ]]; then
          echo "ENGINE RELEASE: ${key%@release} shipped $state (was $old) — https://github.com/${key%@release}/releases/latest"
        else
          echo "TRACKER CHANGE: $key  $old -> $state  ($label)  https://github.com/${key%%#*}/issues/${key##*#}"
        fi
      elif [ -z "$old" ]; then
        echo "TRACKER NEW: $key = $state ($label)"
      fi
    done <<< "$cur"
    printf '%s' "$cur" > "$SNAP"
  fi
  python3 "$(dirname "$0")/build.py" >/dev/null 2>&1 || true
  [ "$ONCE" = "--once" ] && exit 0
  sleep "$INTERVAL"
done
