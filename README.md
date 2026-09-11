# Lark / Feishu CLI for Claude Code

A Claude Code **marketplace catalog**. It does not copy skill files. The `lark-cli` plugin is loaded from the official [`larksuite/cli`](https://github.com/larksuite/cli) `skills/` tree via `git-subdir`.

This repo is not an official Lark, Feishu, or ByteDance product.

## Why a plugin (and how invocation actually works)

A plugin is a **package**: one install, one update, one enable/disable. That is the main advantage over `bunx skills add` dumping 20+ folders into `~/.claude/skills`.

It is **not** “manual-only by default.” Claude Code still:

1. Puts each enabled skill’s **name + description** into the session listing (so Claude can auto-match).
2. Loads the full `SKILL.md` **body only when the skill is invoked**.
3. Lets you invoke a plugin skill yourself: `/lark-cli:lark-doc`, `/lark-cli:lark-im`, …

So context savings come from lazy-loading the bodies, not from hiding the catalog. `claude plugin details lark-cli@soundadam-lark` currently estimates **~3,025 always-on tokens** for all 28 descriptions, versus ~900 more when `/lark-cli:lark-doc` actually fires. Official Lark skills do not set `disable-model-invocation`, so Claude can still auto-trigger when a task matches. To drop the listing cost entirely, disable or uninstall the plugin (`claude plugin disable lark-cli@soundadam-lark`) when you are not using Feishu.

`/plugin marketplace add` only registers the catalog. Skills appear after **installing** the plugin and restarting Claude Code.

## Install

Requires [Bun](https://bun.sh/) and the `lark-cli` binary on `PATH`. Bun blocks the package `postinstall` (it calls `node`), and the default shim is `#!/usr/bin/env node`, so point the bin at the downloaded native binary:

```bash
bun add -g @larksuite/cli
bun "$HOME/.bun/install/global/node_modules/@larksuite/cli/scripts/install.js"
ln -sfn "$HOME/.bun/install/global/node_modules/@larksuite/cli/bin/lark-cli" "$HOME/.bun/bin/lark-cli"
lark-cli config init --new --brand feishu --lang zh
lark-cli auth login --recommend
```

Do not use the official `install` wizard (`bunx @larksuite/cli@latest install`): it still shells out to `npm install -g` and `npx skills add`. The plugin below replaces that skills step. Re-run the `bun …/install.js` and `ln -sfn` lines after `bun add -g` upgrades, because Bun restores the Node shim.

In Claude Code:

```text
/plugin marketplace add soundadam/claude-plugin-lark-cli
/plugin install lark-cli@soundadam-lark
```

Or from a terminal:

```bash
claude plugin install lark-cli@soundadam-lark
```

Restart Claude Code after install. Confirm with `/lark-cli:lark-doc` or `claude plugin details lark-cli@soundadam-lark`.

Skills stay on upstream `main`; `/plugin marketplace update soundadam-lark` refreshes the catalog, then update the plugin to pull new skill commits.

## What this marketplace points at

Plugin root = [`larksuite/cli/skills`](https://github.com/larksuite/cli/tree/main/skills). Each `lark-*` folder is a sub-skill (`lark-doc`, `lark-drive`, `lark-im`, …). The listing is always present while the plugin is enabled; Claude only reads a skill body when you or Claude invoke it.

## License

Marketplace JSON and docs in this repository are MIT. Skill text is MIT © Lark Technologies Pte. Ltd., served from the upstream repo.

---

# 中文

本仓库只是 Claude Code 的 marketplace 目录，**不拷贝**官方 skill。安装插件时 Claude 会 sparse clone [`larksuite/cli`](https://github.com/larksuite/cli) 的 `skills/`。

## Plugin 的实际优势

Plugin 是**打包与开关**，不是“只能手动、绝不自动”。

- 一次安装 / 更新 / 禁用整组 skill，不用往 `~/.claude/skills` 里摊 20+ 份文件。
- 你可以手动打 `/lark-cli:lark-doc` 这类命令。
- **正文**只在被调用时进入上下文；**名称 + description** 会在插件启用期间一直占 listing（目前整包约 3k always-on token；`/lark-cli:lark-doc` 再加约 900）。
- 上游 skill 允许模型自动匹配。不想占 listing 时，禁用插件即可。

`/plugin marketplace add` 只是登记目录。必须再执行 `/plugin install lark-cli@soundadam-lark`（或 `claude plugin install lark-cli@soundadam-lark`），重启后才能在 `/` 菜单里看到 skill。

先装 CLI 并登录：

```bash
bun add -g @larksuite/cli
bun "$HOME/.bun/install/global/node_modules/@larksuite/cli/scripts/install.js"
ln -sfn "$HOME/.bun/install/global/node_modules/@larksuite/cli/bin/lark-cli" "$HOME/.bun/bin/lark-cli"
lark-cli config init --new --brand feishu --lang zh
lark-cli auth login --recommend
```

不要跑官方的 `… install` 向导：它会调用 `npm` / `npx skills add`。然后再：

```text
/plugin marketplace add soundadam/claude-plugin-lark-cli
/plugin install lark-cli@soundadam-lark
```
