#!/usr/bin/env python3
"""Validate the marketplace manifest and the vendored skill tree.

The invariant worth protecting: every registered skill must carry
`disable-model-invocation: true`, or the plugin silently goes back to costing
always-on context on every turn.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "plugins" / "lark-cli"
FLAG = "disable-model-invocation: true"

errors: list[str] = []


def check(condition: object, message: str) -> None:
    if not condition:
        errors.append(message)


market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
check(market["name"] == "soundadam-lark", "marketplace name changed")
check(len(market["plugins"]) == 1, "expected exactly one plugin")

entry = market["plugins"][0]
check(entry["name"] == "lark-cli", "plugin name changed")
check(entry["strict"] is False, "plugin should stay non-strict")
check(
    entry["source"] == "./plugins/lark-cli",
    f"plugin source should be the vendored dir, got {entry['source']!r}",
)
check(
    "bun add -g @larksuite/cli" in entry["description"],
    "description must keep the bun install hint",
)
check("npx " not in entry["description"], "description must not suggest npx")

manifest = json.loads((PLUGIN_DIR / ".claude-plugin" / "plugin.json").read_text())
registered = manifest["skills"]
check(
    registered == ["./skills/lark-doc", "./skills/lark-wiki"],
    f"unexpected registered skills: {registered}",
)

# Every registered skill must exist and be hidden from the model's listing.
for rel in registered:
    skill_md = (PLUGIN_DIR / rel / "SKILL.md").resolve()
    if not skill_md.is_file():
        errors.append(f"missing {skill_md.relative_to(ROOT)}")
        continue
    text = skill_md.read_text(encoding="utf-8")
    frontmatter = text.split("---")[1] if text.startswith("---") else ""
    check(
        FLAG in frontmatter,
        f"{rel} is registered without `{FLAG}` — it would cost always-on context",
    )

# lark-shared backs lark-doc's `Read ../lark-shared/SKILL.md` prerequisite.
shared = PLUGIN_DIR / "skills" / "lark-shared" / "SKILL.md"
check(shared.is_file(), "lark-shared must stay on disk as a sibling of lark-doc")
check(
    "./skills/lark-shared" not in registered,
    "lark-shared must NOT be registered, or it rejoins the skill listing",
)

sha = (PLUGIN_DIR / "UPSTREAM_SHA").read_text().strip()
check(re.fullmatch(r"[0-9a-f]{40}", sha) is not None, f"bad UPSTREAM_SHA: {sha!r}")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

print(f"ok — {len(registered)} registered skills, all hidden from the listing")
print(f"ok — lark-shared vendored but unregistered")
print(f"ok — upstream {sha}")
