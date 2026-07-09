#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" = "" ]; then
  echo "Usage: bash scaffold.sh output/<project-name>"
  exit 1
fi

TARGET="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_DIR="$SKILL_DIR/templates"

mkdir -p "$TARGET/assets/jimeng" "$TARGET/assets/html" "$TARGET/assets/recordings" "$TARGET/assets/original" "$TARGET/assets/audio" "$TARGET/subtitles"

[ -f "$TARGET/article.md" ] || touch "$TARGET/article.md"
for f in video-plan.md narration.md shot-list.md asset-manifest.md edit-guide.md; do
  if [ ! -f "$TARGET/$f" ]; then
    cp "$TEMPLATE_DIR/$f" "$TARGET/$f"
  fi
done

if [ ! -f "$TARGET/assets/html/html-diagram-template.html" ]; then
  cp "$TEMPLATE_DIR/html-diagram-template.html" "$TARGET/assets/html/html-diagram-template.html"
fi

echo "Created Jimeng video project at: $TARGET"
