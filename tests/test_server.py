"""The MCP layer: the tools there are, all read-only, and the server's own key."""

from __future__ import annotations

import stat

from unseenet_mcp import server


async def test_every_tool_is_read_only():
    async def factory():                       # never called: listing needs no session
        raise AssertionError
    tools = await server.build(factory).list_tools()
    names = {t.name for t in tools}
    assert names == {"whats_new", "list_groups", "read_group", "read_thread", "search",
                     "council_status", "network"}
    assert all(t.annotations.read_only_hint for t in tools)
    assert not any("post" in n or "send" in n for n in names)


def test_own_key_is_made_once_and_private(tmp_path):
    a = server.load_key(tmp_path / "key")
    b = server.load_key(tmp_path / "key")
    assert a.key_text == b.key_text
    assert stat.S_IMODE((tmp_path / "key").stat().st_mode) == 0o600
