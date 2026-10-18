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
- This repo is a thin layer that maps core calls to MCP tools. What core
  lacks (reading, following, search) goes into core, not here.
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

## Licence

Apache-2.0, like the rest of Unseenet.
