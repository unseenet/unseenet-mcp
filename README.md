# unseenet-mcp

An [MCP](https://modelcontextprotocol.io) server for
[Unseenet](https://unseenet.org): lets an LLM client such as Claude
Desktop read groups and threads, search and - only when you allow it -
post, as you.

**Status:** planning. Nothing works yet; see the issues.

## Idea

- It is just another client. Like the TUI and the web client it is built
  only on the public core library of
  [unseenet/unseenet](https://github.com/unseenet/unseenet); the user
  interface happens to be a language model instead of a person.
- This repo is a thin layer that maps `Session` calls to MCP tools.
  What the client library lacks (e.g. search) goes into
  unseenet/unseenet (#139), not here.
- Runs locally, next to your own vault. Never on a node.

## Safety rules

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

## Planned tools

| Tool | Does |
|---|---|
| `list_groups` | your subscribed groups, with unread counts |
| `read_group` | newest threads in a group |
| `read_thread` | a whole thread |
| `search` | search a group or all subscribed groups |
| `post` | post or reply (off by default, confirmed) |

## Part of Unseenet

Unseenet is made in several repositories, each released on its own:

| Repository | What it is |
|---|---|
| [unseenet](https://github.com/unseenet/unseenet) | The protocol (UN-RFCs), the core library, the node and the command-line client |
| [unseenet-tui](https://github.com/unseenet/unseenet-tui) | The terminal client (moving here from unseenet, unseenet#548) |
| [unseenet-gui](https://github.com/unseenet/unseenet-gui) | The graphical client - in a window, booted, or in a browser |
| [unseenet-portable](https://github.com/unseenet/unseenet-portable) | Builds the portable clients, Terminal and Graphical, with Tor inside (unseenet#549) |
| [unseenet-bootable](https://github.com/unseenet/unseenet-bootable) | Builds the bootable images, Terminal and Graphical, and later a node image (unseenet#550) |
| [unseenet-docs](https://github.com/unseenet/unseenet-docs) | The site [unseenet.org](https://unseenet.org), gathering the docs of every repository (unseenet#547) |
| [unseenet-entrance](https://github.com/unseenet/unseenet-entrance) | Web entrances: the graphical client in an ordinary browser |
| [unseenet-gateway](https://github.com/unseenet/unseenet-gateway) | Gateways to other networks: Usenet, Nostr, Matrix |
| [unseenet-bots](https://github.com/unseenet/unseenet-bots) | Bots that keep channels filled with current content |
| [unseenet-helpbot](https://github.com/unseenet/unseenet-helpbot) | The bot that answers questions in `unseenet.help` |
| [unseenet-stats](https://github.com/unseenet/unseenet-stats) | Statistics for the network |
| [unseenet-mcp](https://github.com/unseenet/unseenet-mcp) | An MCP server, so a language model can read and post as you (planning) |
| [unseenet-demo](https://github.com/unseenet/unseenet-demo) | Demo people, feeds and sites, made with the command-line client |

## Licence

Apache-2.0, like the rest of Unseenet.
