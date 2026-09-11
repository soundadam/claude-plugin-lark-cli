#!/usr/bin/env bash
# Re-vendor the tracked skills from larksuite/cli and re-apply the
# disable-model-invocation flag that keeps them out of the always-on listing.
#
#   ./scripts/sync-upstream.sh [ref]     # ref defaults to main
#
# Review `git diff` afterwards: upstream owns the skill text, this repo only
# owns the one frontmatter line each file gains below.
set -euo pipefail

UPSTREAM="https://github.com/larksuite/cli.git"
REF="${1:-main}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$REPO_ROOT/plugins/lark-cli/skills"

# lark-shared is vendored but deliberately NOT registered in plugin.json.
# lark-doc's body requires reading ../lark-shared/SKILL.md, so the directory
# must exist on disk; leaving it unregistered keeps it off the skill listing.
SKILLS=(lark-doc lark-wiki lark-shared)

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git clone --depth 1 --branch "$REF" --filter=blob:none --sparse "$UPSTREAM" "$TMP/cli"
git -C "$TMP/cli" sparse-checkout set skills
SHA="$(git -C "$TMP/cli" rev-parse HEAD)"

for s in "${SKILLS[@]}"; do
  src="$TMP/cli/skills/$s"
  [ -d "$src" ] || { echo "upstream is missing skills/$s" >&2; exit 1; }
  rm -rf "${DEST:?}/$s"
  cp -R "$src" "$DEST/$s"
done

python3 - "$DEST" "${SKILLS[@]}" <<'PY'
import re, sys, pathlib
dest, skills = pathlib.Path(sys.argv[1]), sys.argv[2:]
for s in skills:
    p = dest / s / "SKILL.md"
    t = p.read_text(encoding="utf-8")
    if "disable-model-invocation" in t:
        continue
    t, n = re.subn(r"(?m)^(description:.*)$", r"\1\ndisable-model-invocation: true", t, count=1)
    if n != 1:
        sys.exit(f"{s}: could not locate a single-line `description:` in the frontmatter")
    p.write_text(t, encoding="utf-8")
    print(f"  flagged {s}")
PY

printf '%s\n' "$SHA" > "$REPO_ROOT/plugins/lark-cli/UPSTREAM_SHA"
echo "synced ${SKILLS[*]} from $UPSTREAM@$REF ($SHA)"
