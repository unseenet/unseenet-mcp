<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/unseenet/unseenet/main/assets/logo-dark.svg">
    <img src="https://raw.githubusercontent.com/unseenet/unseenet/main/assets/logo-light.svg" alt="Unseenet" width="360">
  </picture>
</p>

<h1 align="center">unseenet-mcp</h1>

<p align="center"><b>Unseenet for language models.</b><br>
An MCP server: an LLM client reads groups and threads, searches and - only when you allow it - posts, as you.</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="Apache-2.0"></a>
</p>

> **Pre-alpha.** Nothing is stable yet, and Unseenet has not had a security
> review. Do not rely on it to protect anyone yet.

## What it is

An [MCP](https://modelcontextprotocol.io) server for
[Unseenet](https://unseenet.org): lets an LLM client such as Claude
Desktop read groups and threads, search and - only when you allow it -
post, as you.

**Status:** planning. Nothing works yet; see the issues.

- It is just another client. Like the TUI and the web client it is built
  only on the public core library of
  [unseenet/unseenet](https://github.com/unseenet/unseenet); the user
  interface happens to be a language model instead of a person.
- This repo is a thin layer that maps `Session` calls to MCP tools.
  What the client library lacks (e.g. search) goes into
  unseenet/unseenet (#139), not here.
- Runs locally, next to your own vault. Never on a node.

## How it works

### Safety rules

- **Read-only by default.** Posting is a separate tool that must be
  switched on, and every post is confirmed by you.
- **No key material.** No tool exports keys, opens the vault for writing
  or changes identities.
- **Network content is untrusted.** Posts are returned to the model as
  quoted data, marked as such - a post can contain text written to
  steer the model (prompt injection).
- **Content leaves Tor if your model is in the cloud.** Unseenet carries
  everything over onion services, but what the MCP server hands to a
  cloud LLM goes to that provider. That is your choice to make; use a
  local model if it matters.

### Planned tools

| Tool | Does |
|---|---|
| `list_groups` | your subscribed groups, with unread counts |
| `read_group` | newest threads in a group |
| `read_thread` | a whole thread |
| `search` | search a group or all subscribed groups |
| `post` | post or reply (off by default, confirmed) |

## Versions and releases

Not released yet: it is being planned. When it is, it follows the
[Unseenet conventions](https://github.com/unseenet/.github/blob/main/CONVENTIONS.md#versions).

## Part of Unseenet

| Repository | What it is |
|---|---|
| [unseenet](https://github.com/unseenet/unseenet) | The protocol (UN-RFCs), the core library, the node and the command-line client |
| [unseenet-tui](https://github.com/unseenet/unseenet-tui) | The terminal client |
| [unseenet-gui](https://github.com/unseenet/unseenet-gui) | The graphical client - in a window, booted, or in a browser |
| [unseenet-portable](https://github.com/unseenet/unseenet-portable) | Builds the portable clients, Terminal and Graphical, with Tor inside |
| [unseenet-bootable](https://github.com/unseenet/unseenet-bootable) | Builds the bootable images, Terminal and Graphical |
| [unseenet-docs](https://github.com/unseenet/unseenet-docs) | The site [unseenet.org](https://unseenet.org) |
| [unseenet-entrance](https://github.com/unseenet/unseenet-entrance) | Web entrances: the graphical client in an ordinary browser |
| [unseenet-gateway](https://github.com/unseenet/unseenet-gateway) | Gateways to other networks: Usenet, Nostr, Matrix |
| [unseenet-bots](https://github.com/unseenet/unseenet-bots) | Bots that keep channels filled with current content |
| [unseenet-helpbot](https://github.com/unseenet/unseenet-helpbot) | The bot that answers questions in `unseenet.help` |
| [unseenet-watchman](https://github.com/unseenet/unseenet-watchman) | Automatic spam reports and content labels that readers may choose to follow |
| [unseenet-stats](https://github.com/unseenet/unseenet-stats) | Statistics for the network |
| [unseenet-mcp](https://github.com/unseenet/unseenet-mcp) | An MCP server, so a language model can read and post as you (planning) |
| [unseenet-demo](https://github.com/unseenet/unseenet-demo) | Demo people, feeds and sites, made with the command-line client |

## License

[Apache License 2.0](LICENSE). The Unseenet logo: CC BY 4.0.
