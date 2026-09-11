# Lark / Feishu CLI for Claude Code

A Claude Code **marketplace catalog**. It does not copy skill files. The `lark-cli` plugin is loaded from the official [`larksuite/cli`](https://github.com/larksuite/cli) `skills/` tree via `git-subdir`.

This repo is not an official Lark, Feishu, or ByteDance product.

## Install

Requires [Node.js](https://nodejs.org/) and the `lark-cli` binary.

```bash
npx @larksuite/cli@latest install
lark-cli config init --new --brand feishu --lang zh
lark-cli auth login --recommend
```

In Claude Code:

```text
/plugin marketplace add soundadam/claude-plugin-lark-cli
/plugin install lark-cli@soundadam-lark
```

Restart Claude Code after install. Skills stay on upstream `main`; `/plugin marketplace update soundadam-lark` refreshes the catalog, then update the plugin to pull new skill commits.

## What this marketplace points at

Plugin root = [`larksuite/cli/skills`](https://github.com/larksuite/cli/tree/main/skills). Each `lark-*` folder is a sub-skill (`lark-doc`, `lark-drive`, `lark-im`, …). Claude only reads a skill when the task matches it.

## License

Marketplace JSON and docs in this repository are MIT. Skill text is MIT © Lark Technologies Pte. Ltd., served from the upstream repo.

---

# 中文

本仓库只是 Claude Code 的 marketplace 目录，**不拷贝**官方 skill。安装插件时 Claude 会 sparse clone [`larksuite/cli`](https://github.com/larksuite/cli) 的 `skills/`。

先装 CLI 并登录，再：

```text
/plugin marketplace add soundadam/claude-plugin-lark-cli
/plugin install lark-cli@soundadam-lark
```
