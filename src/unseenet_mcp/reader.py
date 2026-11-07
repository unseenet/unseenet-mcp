"""The read-only tools, as plain functions over a core ``Session`` (#1, #2).

Nothing here posts, signs or changes anything in the network: it lists groups
and fetches articles. That is why ``ClientRuntime.refresh()`` is not used - it
also sets up an inbox, which is a post. What the client library lacks goes to
unseenet/unseenet, not here.

Every result that holds text from the network is wrapped by
``untrusted.wrapped`` (#4).
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field

from unseenet import known_nodes as kn

from .state import State
from .untrusted import clean, wrapped

log = logging.getLogger(__name__)

# The project's groups for people that "what's new" watches by default: where the
# project talks, asks for help, tests and announces. The councils' own groups
# (talk, claims, log) are found from each council's manifest when asked.
DEFAULT_WATCH = (
    "unseenet@ph5fc5hop5232qsz",
    kn.HELP_GROUP,
    "test.unseenet@ph5fc5hop5232qsz",
    "unseenet.chat@ph5fc5hop5232qsz",
)
# The project's councils (UN-RFC 0054); core 0.8 names them in known_nodes, 0.7 not yet.
NAMES_COUNCIL = getattr(kn, "NAMES_COUNCIL", "unseenet.names@xvchjwehdhfptpza")
LISTS_COUNCIL = getattr(kn, "LISTS_COUNCIL", "unseenet.lists@727td54rrn4glwoh")
COUNCILS = (NAMES_COUNCIL, LISTS_COUNCIL)
COUNCIL_PEOPLE_FIELDS = ("talk",)            # read as posts
COUNCIL_EVENT_FIELDS = ("claims", "log")     # read as events: subjects only
NETWORK_ERRORS = (OSError, ConnectionError, asyncio.TimeoutError, asyncio.IncompleteReadError,
                  RuntimeError, ValueError)
FIRST_RUN_SHOW = 5                           # posts shown per group the very first time


def short(group_id: str) -> str:
    return group_id.split("@", 1)[0]


def message(m, limit: int = 4000) -> dict:
    """One post as the model sees it: who, when, where, and its text cleaned."""
    text = m.body if m.readable else f"[not readable: {m.error or 'encrypted'}]"
    return {
        "group": m.group, "number": m.number, "id": m.message_id,
        "thread_root": m.thread_root, "is_reply": bool(m.references),
        "subject": clean(m.subject, 300), "from_name": clean(m.from_name, 100),
        "author_key": m.author_key, "date": m.date.isoformat() if m.date else None,
        "kind": m.kind, "text": clean(text, limit),
        "hidden_by_report": bool(getattr(m, "reported", None)),
    }


@dataclass
class Reader:
    session: object
    state: State
    watch: tuple[str, ...] = DEFAULT_WATCH
    councils: tuple[str, ...] = COUNCILS
    _ready: bool = field(default=False, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    # --- getting going, without posting anything ---
    async def ready(self) -> None:
        """Find a node the first time (the known-node list), nothing more."""
        async with self._lock:
            if self._ready:
                return
            s = self.session
            if not s.nodes:
                await s.fall_back_to_known_node()
            self._ready = True

    async def fetch(self, group_id: str) -> list:
        """A group's posts as clients show them (ignored and edited ones resolved),
        oldest first by article number."""
        await self.ready()
        msgs = await self.session.fetch_group(group_id)
        try:
            msgs = self.session.visible(msgs)
        except Exception:                      # marks are a nicety, never a failure
            pass
        return sorted((m for m in msgs if not getattr(m, "private_profile", False)),
                      key=lambda m: m.number)

    async def resolve(self, group: str) -> str:
        """A full group ID from what a person types: ``unseenet.help`` or the full ID."""
        group = group.strip()
        if "@" in group:
            return group
        known = [*self.watch, *self.councils, *kn.STARTER_GROUPS]
        for gid in known:
            if short(gid) == group:
                return gid
        await self.ready()
        found = [g.group_id for g in await self.session.list_groups(group)
                 if short(g.group_id) == group]
        if len(found) == 1:
            return found[0]
        if not found:
            raise ValueError(f"no group called {group!r} on the nodes asked")
        raise ValueError(f"{group!r} is ambiguous; give the full ID, one of: {', '.join(found)}")

    # --- the tools ---
    async def list_groups(self, pattern: str = "*") -> dict:
        await self.ready()
        groups = await self.session.list_groups(pattern)
        rows = [{"id": g.group_id, "type": g.type, "description": clean(g.description, 300)}
                for g in groups if not self.session.is_data_group(g.group_id)]
        return wrapped({"pattern": pattern, "count": len(rows), "groups": rows[:500]})

    async def read_group(self, group: str, limit: int = 20) -> dict:
        gid = await self.resolve(group)
        msgs = await self.fetch(gid)
        roots: dict[str, dict] = {}
        for m in msgs:                         # threads, newest activity first
            t = roots.setdefault(m.thread_root, {"root": None, "replies": 0, "last": m.number})
            if m.message_id == m.thread_root:
                t["root"] = m
            else:
                t["replies"] += 1
            t["last"] = max(t["last"], m.number)
        ordered = sorted(roots.values(), key=lambda t: t["last"], reverse=True)[:limit]
        threads = [{"root": message(t["root"], 1500) if t["root"] else None,
                    "replies": t["replies"], "last_number": t["last"]} for t in ordered]
        return wrapped({"group": gid, "posts": len(msgs), "threads": threads})

    async def read_thread(self, group: str, message_id: str) -> dict:
        gid = await self.resolve(group)
        msgs = await self.fetch(gid)
        root = next((m.thread_root for m in msgs if m.message_id == message_id), message_id)
        posts = [message(m) for m in msgs if m.thread_root == root]
        if not posts:
            raise ValueError(f"no post {message_id} in {gid}")
        return wrapped({"group": gid, "thread_root": root, "posts": posts})

    async def search(self, query: str, groups: list[str] | None = None, limit: int = 30) -> dict:
        """Searched here, in what was fetched: a node is never told what you look for."""
        q = query.lower().strip()
        if not q:
            raise ValueError("give something to search for")
        ids = [await self.resolve(g) for g in groups] if groups else list(self.watch)
        hits, errors = [], {}
        for gid in ids:
            try:
                for m in await self.fetch(gid):
                    if q in f"{m.subject}\n{m.from_name}\n{m.body}".lower():
                        hits.append(message(m, 1500))
            except NETWORK_ERRORS as exc:
                errors[gid] = str(exc) or type(exc).__name__
        hits.sort(key=lambda h: h["date"] or "", reverse=True)
        return wrapped({"query": query, "groups": ids, "hits": hits[:limit], "errors": errors})

    async def council_groups(self, council: str) -> dict[str, str]:
        """The groups a council names in its manifest (talk, claims, log, ...)."""
        chain = await self.session.council_chain(council)
        cur = chain.current
        return {k: v for k, v in (cur.data if cur else {}).items()
                if isinstance(v, str) and "@" in v}

    async def council_status(self, council: str | None = None) -> dict:
        ids = [await self.resolve(council)] if council else list(self.councils)
        out = []
        for gid in ids:
            entry: dict = {"council": gid}
            try:
                await self.ready()
                chain = await self.session.council_chain(gid)
                cur = chain.current
                entry["members"] = len(cur.members) if cur else None
                entry["full_members"] = len(cur.full()) if cur else None
                entry["min_level"] = cur.min_level if cur else None
                entry["hearings"] = [{**h, "reason": clean(str(h.get("reason") or ""), 500),
                                      "closes": str(h["closes"]) if h.get("closes") else None,
                                      "applies": str(h["applies"]) if h.get("applies") else None}
                                     for h in await self.session.council_hearings(gid)]
                groups = await self.council_groups(gid)
                if groups.get("log"):
                    entry["log"] = [{"number": m.number, "subject": clean(m.subject, 200),
                                     "date": m.date.isoformat() if m.date else None}
                                    for m in (await self.fetch(groups["log"]))[-10:]]
            except NETWORK_ERRORS as exc:
                entry["error"] = str(exc) or type(exc).__name__
            out.append(entry)
        return wrapped({"councils": out})

    async def network(self) -> dict:
        await self.ready()
        s = self.session
        try:
            announced = await s.refresh_announced_nodes()
        except NETWORK_ERRORS as exc:
            announced, error = s.announced_nodes(), str(exc)
        else:
            error = None
        rows = [{k: clean(str(v), 200) if isinstance(v, str) else v for k, v in a.items()
                 if k in ("name", "address", "version", "first", "last", "key")}
                for a in announced]
        return wrapped({"node_in_use": s.node, "announced_nodes": len(rows), "nodes": rows,
                        "error": error})

    async def whats_new(self, mark_seen: bool = True, per_group: int = 20) -> dict:
        """Everything since the last call: new posts in the watched groups and the
        councils' talk, new claims and log entries, keys posting for the first time,
        hearings that are open. The first call ever only sets a starting point."""
        first = self.state.first_run
        groups: dict[str, str] = {gid: "posts" for gid in self.watch}
        errors: dict[str, str] = {}
        for c in self.councils:
            try:
                await self.ready()
                for k, gid in (await self.council_groups(c)).items():
                    if k in COUNCIL_PEOPLE_FIELDS:
                        groups[gid] = "posts"
                    elif k in COUNCIL_EVENT_FIELDS:
                        groups[gid] = "events"
            except NETWORK_ERRORS as exc:
                errors[c] = str(exc) or type(exc).__name__
        new_posts, events, new_keys = [], [], {}
        highs: dict[str, int] = {}
        for gid, kind in groups.items():
            try:
                msgs = await self.fetch(gid)
            except NETWORK_ERRORS as exc:
                errors[gid] = str(exc) or type(exc).__name__
                continue
            if msgs:
                highs[gid] = msgs[-1].number
            seen = self.state.seen.get(gid)
            fresh = [m for m in msgs if seen is None or m.number > seen]
            if seen is None:
                fresh = fresh[-FIRST_RUN_SHOW:] if kind == "posts" else []
            for m in fresh:
                if m.author_key and m.author_key not in self.state.authors and not first:
                    new_keys.setdefault(m.author_key, {"key": m.author_key,
                                                       "name": clean(m.from_name, 100),
                                                       "first_seen_in": gid, "id": m.message_id})
            if kind == "posts":
                new_posts += [message(m, 1500) for m in fresh[-per_group:]]
            else:
                events += [{"group": gid, "number": m.number, "subject": clean(m.subject, 200),
                            "author_key": m.author_key,
                            "date": m.date.isoformat() if m.date else None}
                           for m in fresh[-per_group:]]
            self.state.authors |= {m.author_key for m in msgs if m.author_key}
        hearings = []
        for c in self.councils:
            try:
                for h in await self.session.council_hearings(c):
                    if h.get("active") or h.get("state") in ("open", "hearing"):
                        hearings.append({"council": c, "id": h["id"], "kind": h.get("kind"),
                                         "state": h.get("state"),
                                         "objections": h.get("objections"),
                                         "closes": str(h["closes"]) if h.get("closes") else None})
            except NETWORK_ERRORS as exc:
                errors.setdefault(c, str(exc) or type(exc).__name__)
        if mark_seen:
            self.state.seen.update(highs)
            self.state.save()
        return wrapped({
            "first_run": first,
            "note": ("First run: this sets the starting point; the newest few posts per "
                     "group are shown, and new keys are counted from now on.") if first else None,
            "groups_watched": sorted(groups),
            "new_posts": new_posts, "council_events": events,
            "new_keys": list(new_keys.values()), "open_hearings": hearings,
            "errors": errors,
        })
