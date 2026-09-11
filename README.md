# Lark / Feishu CLI for Claude Code

A Claude Code **marketplace catalog**. It does not copy skill files. The `lark-cli` plugin is loaded from the official [`larksuite/cli`](https://github.com/larksuite/cli) `skills/` tree via `git-subdir`.

This repo is not an official Lark, Feishu, or ByteDance product.

## Why a plugin (and how invocation actually works)

A plugin is a **package**: one install, one update, one enable/disable. That is the main advantage over `bunx skills add` dumping 20+ folders into `~/.claude/skills`.

It is **not** “manual-only by default.” Claude Code still:

1. Puts each enabled skill’s **name + description** into the session listing (so Claude can auto-match).
2. Loads the full `SKILL.md` **body only when the skill is invoked**.
3. Lets you invoke a plugin skill yourself: `/lark-cli:lark-doc`, `/lark-cli:lark-im`, …

So context savings come from lazy-loading the bodies, not from hiding the catalog. `claude plugin details lark-cli@soundadam-lark` currently estimates **~4,508 always-on tokens** for all 28 descriptions — against ~120k if every body were resident (`lark-sheets` alone is ~13.9k on invoke, `lark-im` ~13k). Official Lark skills do not set `disable-model-invocation`, so Claude can still auto-trigger when a task matches.

`/plugin marketplace add` only registers the catalog. Skills appear after **installing** the plugin and restarting Claude Code.

## Cutting the always-on cost

Claude Code already bounds the listing: `skillListingBudgetFraction` (default `0.01`) reserves 1% of the context window, in characters, for *all* skill descriptions combined, and `skillListingMaxDescChars` (default `1536`) caps each one. Over budget, descriptions are truncated to fit.

Two caveats, both verified against **Claude Code 2.1.212**:

- **`skillOverrides` does not work on plugin skills.** The enforcement path short-circuits on source — `if (e.type !== "prompt" || e.source === "plugin") return "on"` — so `"off"` / `"user-invocable-only"` / `"name-only"` entries in user, project, or local settings are silently ignored for anything installed from a marketplace. Verified side by side: `{"skillOverrides": {"dataviz": "off"}}` removes the bundled `dataviz` skill from the model's listing; the same entry for `lark-doc` does nothing. Only `policySettings` (admin-managed `managed-settings.json`) or `flagSettings` can override a plugin skill.
- **The default `skillListingMaxDescChars` buys nothing here.** The 28 descriptions total 5,340 characters and the longest is 580, so nothing hits the 1,536 cap.

Lowering the cap *does* apply to plugin skills (confirmed: `skillListingMaxDescChars: 40` truncates `lark-sheets` to exactly 40 characters). It is global, though — it hits bundled and plugin skills alike:

| cap | listing chars | saved |
| --- | --- | --- |
| `1536` (default) | 5,340 | 0% |
| `300` | 4,602 | 14% |
| `200` | 3,928 | 26% |
| `150` | 3,242 | 39% |
| `100` | 2,368 | 56% |

Weigh that against routing accuracy. These descriptions carry the disambiguation rules (`BaseApp 不走 lark-apps`, `文件导入/导出转 lark-drive`), and those clauses sit at the end of the string — exactly what truncation removes first. Lower the cap and you are trading routing precision for context; how far you can go is untested here.

The levers that work cleanly:

1. **Fork this marketplace and trim the `skills` array** in `.claude-plugin/marketplace.json` to the skills you actually use. Per-skill always-on costs are in `claude plugin details`.
2. **Disable the plugin when you are not doing Feishu work** — `claude plugin disable lark-cli@soundadam-lark`.

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

**In the Claude desktop app there is no skill browser.** `/skills` is a `local-jsx` terminal dialog, like `/permissions` and `/config`, so the desktop Code tab will not render it. Plugin skills also never appear as bare `/lark-doc` — they are namespaced `/lark-cli:lark-doc`. To confirm the install from the desktop app, type `/lark-cli:` and check that it autocompletes; to audit the full set, run `claude plugin details lark-cli@soundadam-lark` in a terminal, or `claude` interactively and then `/skills`.

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
- **正文**只在被调用时进入上下文；**名称 + description** 会在插件启用期间一直占 listing（整包约 **4,508** always-on token。正文全驻留则是约 120k：光 `lark-sheets` 调用一次就 ~13.9k）。
- 上游 skill 允许模型自动匹配。不想占 listing 时，禁用插件即可。

### 降低 always-on 开销

Claude Code 本身给 listing 上了预算：`skillListingBudgetFraction`（默认 `0.01`，即上下文窗口 1% 的字符数）和 `skillListingMaxDescChars`（默认 `1536`，单条 description 上限），超预算会自动截短。

两个坑，均在 **Claude Code 2.1.212** 上实测确认：

- **`skillOverrides` 对插件 skill 无效。** 执行路径按来源短路——`if (e.type !== "prompt" || e.source === "plugin") return "on"`——所以 user / project / local 设置里的 `"off"` / `"user-invocable-only"` / `"name-only"` 对 marketplace 装的 skill 会被静默忽略。对照实验：`{"skillOverrides": {"dataviz": "off"}}` 能让内置的 `dataviz` 从模型 listing 里消失；同样的写法对 `lark-doc` 毫无作用。只有 `policySettings`（管理员的 `managed-settings.json`）和 `flagSettings` 能覆盖插件 skill。
- **默认的 `skillListingMaxDescChars` 在这里省不到东西。** 28 条 description 合计 5,340 字符，最长的才 580，全都够不着 1,536 的上限。

调低上限对插件 skill **确实生效**（实测 `skillListingMaxDescChars: 40` 把 `lark-sheets` 精确截到 40 字），但它是全局的，内置 skill 一起遭殃：

| 上限 | listing 字符 | 节省 |
| --- | --- | --- |
| `1536`（默认） | 5,340 | 0% |
| `300` | 4,602 | 14% |
| `200` | 3,928 | 26% |
| `150` | 3,242 | 39% |
| `100` | 2,368 | 56% |

代价是路由精度：这些 description 里带着消歧规则（`BaseApp 不走 lark-apps`、`文件导入/导出转 lark-drive`），而这些子句都在字符串末尾——正好是截断最先吃掉的部分。能压到多低，本仓库没有实测。

干净的办法只有两个：

1. **fork 本仓库，把 `.claude-plugin/marketplace.json` 里的 `skills` 数组删到只剩你真用的那几个。** 每个 skill 的 always-on 成本见 `claude plugin details`。
2. **不做飞书的时候禁用整个插件**——`claude plugin disable lark-cli@soundadam-lark`。

### 桌面端看不到 skill 是正常的

Claude 桌面版**没有 skill 浏览界面**。`/skills` 是 `local-jsx` 终端对话框，和 `/permissions`、`/config` 同类，桌面版 Code tab 不渲染。插件 skill 也不会以裸的 `/lark-doc` 出现，一律带命名空间 `/lark-cli:lark-doc`。

想在桌面端确认装好了：输入框打 `/lark-cli:` 看能不能补全。想看全量清单：终端里跑 `claude plugin details lark-cli@soundadam-lark`，或者 `claude` 进交互模式再 `/skills`。

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
