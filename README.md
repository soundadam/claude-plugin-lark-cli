# Lark / Feishu CLI for Claude Code

A Claude Code plugin that exposes exactly two Lark/Feishu skills — **`/lark-cli:lark-doc`** and **`/lark-cli:lark-wiki`** — and costs **zero always-on context** until you type one.

This repo is not an official Lark, Feishu, or ByteDance product. Skill text is vendored from [`larksuite/cli`](https://github.com/larksuite/cli); see [Staying in sync](#staying-in-sync).

## The point: explicit invocation only

By default an enabled skill puts its **name + description** into every turn's skill listing, so Claude can auto-match it. For the full 28-skill Lark set that was **~4,508 always-on tokens** — paid on every request, whether or not you touched Feishu that day.

Each vendored `SKILL.md` here sets one line of frontmatter:

```yaml
disable-model-invocation: true
```

That removes the skill from the model's listing entirely while keeping the slash command. Verified on **Claude Code 2.1.212** — asked "list every skill you have containing 'lark'", the model answers `NONE`, and `/lark-cli:lark-doc` still loads the body normally.

| | always-on | how it fires |
| --- | --- | --- |
| Upstream 28-skill catalog | ~4,508 tok | auto-match, or `/lark-cli:<name>` |
| **This plugin** | **0 tok** | `/lark-cli:lark-doc`, `/lark-cli:lark-wiki` |

The trade is deliberate: Claude will no longer reach for these on its own. You ask for them by name.

### Why the skills are vendored rather than pulled with `git-subdir`

`disable-model-invocation` lives in `SKILL.md`, which upstream owns. Pointing the plugin at `larksuite/cli` with `git-subdir` gives no place to add it.

The obvious alternative does not work. **`skillOverrides` is ignored for plugin skills** — the enforcement path short-circuits on source:

```js
if (e.type !== "prompt" || e.source === "plugin") return "on";
```

So `"off"` / `"user-invocable-only"` / `"name-only"` in user, project, or local settings silently do nothing to anything installed from a marketplace. Verified side by side on 2.1.212: `{"skillOverrides": {"dataviz": "off"}}` removes the bundled `dataviz` skill from the model's listing; the identical entry for `lark-doc` has no effect. The `/skills` panel writes to `localSettings`, so it is affected too. Only `policySettings` (admin-managed `managed-settings.json`) or `flagSettings` can override a plugin skill.

`disable-model-invocation` works because it is checked *before* that short-circuit.

## Install

Requires [Bun](https://bun.sh/) and the `lark-cli` binary on `PATH`. Bun blocks the package `postinstall` (it calls `node`), and the default shim is `#!/usr/bin/env node`, so point the bin at the downloaded native binary:

```bash
bun add -g @larksuite/cli
bun "$HOME/.bun/install/global/node_modules/@larksuite/cli/scripts/install.js"
ln -sfn "$HOME/.bun/install/global/node_modules/@larksuite/cli/bin/lark-cli" "$HOME/.bun/bin/lark-cli"
lark-cli config init --new --brand feishu --lang zh
lark-cli auth login --recommend
```

Do not use the official `install` wizard (`bunx @larksuite/cli@latest install`): it still shells out to `npm install -g` and `npx skills add`, which dumps all 28 skills into `~/.claude/skills`.

In Claude Code:

```text
/plugin marketplace add soundadam/claude-plugin-lark-cli
/plugin install lark-cli@soundadam-lark
```

Or from a terminal:

```bash
claude plugin install lark-cli@soundadam-lark
```

Restart Claude Code, then type `/lark-cli:lark-doc`.

### Confirming it worked

**The Claude desktop app has no skill browser.** `/skills` is a `local-jsx` terminal dialog, like `/permissions` and `/config`, so the desktop Code tab will not render it. Plugin skills also never appear as bare `/lark-doc` — they are namespaced `/lark-cli:lark-doc`.

- From the desktop app: type `/lark-cli:` and check that it autocompletes.
- From a terminal: `claude plugin details lark-cli@soundadam-lark`, or `claude` interactively and then `/skills`.

Note that `claude plugin details` reports a static estimate from the raw descriptions and is **not** aware of `disable-model-invocation` — it will still print a non-zero always-on figure. The listing itself is what counts; check that by asking Claude directly whether it has a skill named `lark-doc`.

## What is in here

```
plugins/lark-cli/
  .claude-plugin/plugin.json     registers lark-doc and lark-wiki
  UPSTREAM_SHA                   larksuite/cli commit the skills came from
  skills/
    lark-doc/                    registered
    lark-wiki/                   registered
    lark-shared/                 NOT registered — present on disk only
```

`lark-shared` is vendored but deliberately left out of `plugin.json`. `lark-doc`'s body opens with *"MUST 先用 Read 工具读取 `../lark-shared/SKILL.md`"* — auth, identity, and permission rules live there — so the directory has to exist as a sibling. Not registering it means it never reaches the skill listing. It carries the frontmatter flag anyway, as a belt-and-braces measure in case a future version auto-discovers everything under `skills/`.

That relative read is subject to normal file permissions: the first time a skill reads its sibling you will get a permission prompt, since the plugin cache lives outside your working directory. This is upstream behaviour, not something this repo introduces.

## Staying in sync

```bash
./scripts/sync-upstream.sh          # tracks main
./scripts/sync-upstream.sh v1.0.95  # or a tag
```

The script sparse-clones `larksuite/cli`, replaces the three vendored directories, re-applies `disable-model-invocation: true`, and records the upstream commit in `plugins/lark-cli/UPSTREAM_SHA`. It is idempotent — re-running on an unchanged upstream produces no diff. Review `git diff` before committing: upstream owns the skill text, this repo owns one frontmatter line per file.

To track a different skill, add it to `SKILLS` in the script and to `skills` in `plugin.json`.

## Adding more skills back

Each skill's always-on cost, if you ever want to register one without the flag, from `claude plugin details` on the full 28-skill catalog:

| skill | always-on | on invoke |
| --- | --- | --- |
| `lark-doc` | ~170 | ~1.2k |
| `lark-wiki` | ~240 | ~4.3k |
| `lark-shared` | ~170 | ~1.3k |
| `lark-sheets` | ~310 | ~13.9k |
| `lark-im` | ~180 | ~13k |
| `lark-drive` | ~320 | ~8.7k |
| `lark-base` | ~190 | ~8.3k |

## License

Marketplace JSON, scripts, and docs in this repository are MIT. Vendored skill text under `plugins/lark-cli/skills/` is MIT © Lark Technologies Pte. Ltd., modified only by the addition of `disable-model-invocation: true` to each `SKILL.md` frontmatter. See [`NOTICE`](NOTICE).

---

# 中文

一个 Claude Code 插件，只暴露两个飞书 skill——**`/lark-cli:lark-doc`** 和 **`/lark-cli:lark-wiki`**——在你手动敲之前，**always-on 开销为零**。

本仓库不是 Lark / 飞书 / 字节跳动的官方产品。skill 文本 vendor 自 [`larksuite/cli`](https://github.com/larksuite/cli)，同步方式见下文。

## 核心：只有显式触发才进上下文

默认情况下，启用的 skill 会把**名称 + description** 塞进每一轮的 skill listing 供模型自动匹配。上游整套 28 个 skill 是 **~4,508 always-on token**——不管你今天碰没碰飞书，每个请求都在付。

本仓库 vendor 的每个 `SKILL.md` 都加了一行 frontmatter：

```yaml
disable-model-invocation: true
```

它把 skill 从模型的 listing 里彻底摘掉，同时保留斜杠命令。在 **Claude Code 2.1.212** 上实测：问模型"列出你拥有的所有含 'lark' 的 skill"，回答是 `NONE`；而 `/lark-cli:lark-doc` 依然能正常载入正文。

| | always-on | 触发方式 |
| --- | --- | --- |
| 上游 28 skill 全量 | ~4,508 tok | 自动匹配，或 `/lark-cli:<name>` |
| **本插件** | **0 tok** | `/lark-cli:lark-doc`、`/lark-cli:lark-wiki` |

代价是明确的：Claude 不会再主动调用它们，得你点名。

### 为什么 vendor 而不用 `git-subdir`

`disable-model-invocation` 写在 `SKILL.md` 里，而这个文件归上游所有。用 `git-subdir` 直连 `larksuite/cli` 就没地方加这一行。

看似更自然的办法行不通。**`skillOverrides` 对插件 skill 无效**——执行路径按来源短路：

```js
if (e.type !== "prompt" || e.source === "plugin") return "on";
```

所以 user / project / local 设置里的 `"off"` / `"user-invocable-only"` / `"name-only"`，对 marketplace 装的 skill 会被静默忽略。2.1.212 上的对照实验：`{"skillOverrides": {"dataviz": "off"}}` 能让内置的 `dataviz` 从模型 listing 消失；一模一样的写法对 `lark-doc` 毫无作用。`/skills` 面板改的是 `localSettings`，同样中招。只有 `policySettings`（管理员的 `managed-settings.json`）和 `flagSettings` 能覆盖插件 skill。

`disable-model-invocation` 之所以有效，是因为它的判断排在那个短路**之前**。

## 安装

先装 CLI 并登录（Bun 会拦掉 `postinstall`，默认 shim 又是 `#!/usr/bin/env node`，所以要把 bin 指向真正的原生二进制）：

```bash
bun add -g @larksuite/cli
bun "$HOME/.bun/install/global/node_modules/@larksuite/cli/scripts/install.js"
ln -sfn "$HOME/.bun/install/global/node_modules/@larksuite/cli/bin/lark-cli" "$HOME/.bun/bin/lark-cli"
lark-cli config init --new --brand feishu --lang zh
lark-cli auth login --recommend
```

不要跑官方的 `install` 向导（`bunx @larksuite/cli@latest install`）：它会调用 `npm install -g` 和 `npx skills add`，把 28 个 skill 全摊进 `~/.claude/skills`。

然后：

```text
/plugin marketplace add soundadam/claude-plugin-lark-cli
/plugin install lark-cli@soundadam-lark
```

重启 Claude Code，之后打 `/lark-cli:lark-doc`。

### 怎么确认装好了

**Claude 桌面版没有 skill 浏览界面。** `/skills` 是 `local-jsx` 终端对话框，和 `/permissions`、`/config` 同类，桌面版 Code tab 不渲染它。插件 skill 也不会以裸的 `/lark-doc` 出现，一律带命名空间 `/lark-cli:lark-doc`。

- 桌面端：输入框打 `/lark-cli:`，看能不能补全。
- 终端：`claude plugin details lark-cli@soundadam-lark`，或 `claude` 进交互模式再 `/skills`。

注意 `claude plugin details` 给的是基于原始 description 的静态估算，**不认** `disable-model-invocation`，所以它仍会打印一个非零的 always-on 数字。真正算数的是 listing——直接问 Claude 有没有叫 `lark-doc` 的 skill 即可。

## 仓库结构

```
plugins/lark-cli/
  .claude-plugin/plugin.json     注册 lark-doc 和 lark-wiki
  UPSTREAM_SHA                   skill 来自 larksuite/cli 的哪个 commit
  skills/
    lark-doc/                    已注册
    lark-wiki/                   已注册
    lark-shared/                 未注册 —— 只是放在磁盘上
```

`lark-shared` 被 vendor 了，但故意不写进 `plugin.json`。`lark-doc` 的正文开头就是 *"MUST 先用 Read 工具读取 `../lark-shared/SKILL.md`"*——认证、身份、权限规则都在里面——所以这个目录必须作为 sibling 存在。不注册它，它就永远进不了 skill listing。它自己也带了那行 frontmatter，纯属兜底，防止将来某个版本自动发现 `skills/` 下的全部目录。

那条相对读取受常规文件权限约束：skill 第一次读 sibling 时会弹权限提示，因为插件 cache 在工作目录之外。这是上游本来的行为，不是本仓库引入的。

## 同步上游

```bash
./scripts/sync-upstream.sh          # 跟 main
./scripts/sync-upstream.sh v1.0.95  # 或指定 tag
```

脚本会 sparse-clone `larksuite/cli`、替换那三个 vendor 目录、重新打上 `disable-model-invocation: true`，并把上游 commit 记进 `plugins/lark-cli/UPSTREAM_SHA`。它是幂等的——上游没变时重跑不产生 diff。提交前看一眼 `git diff`：skill 正文归上游，本仓库只拥有每个文件多出来的那一行。

想追踪别的 skill，把它加进脚本里的 `SKILLS` 和 `plugin.json` 的 `skills`。

## License

本仓库的 marketplace JSON、脚本和文档为 MIT。`plugins/lark-cli/skills/` 下 vendor 的 skill 文本为 MIT © Lark Technologies Pte. Ltd.，唯一修改是给每个 `SKILL.md` 的 frontmatter 加了 `disable-model-invocation: true`。详见 [`NOTICE`](NOTICE)。
