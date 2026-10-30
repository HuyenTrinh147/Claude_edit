"""Shared agent loop: Claude + the SDK's streaming tool runner, server-side web tools,
prompt caching, refusal fallbacks and console progress output."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any, Iterable

import anthropic

from ..config import Settings

WEB_SEARCH = {"type": "web_search_20260209", "name": "web_search"}
WEB_FETCH = {"type": "web_fetch_20260209", "name": "web_fetch"}


def web_tools(max_searches: int = 15, max_fetches: int = 15) -> list[dict]:
    return [{**WEB_SEARCH, "max_uses": max_searches}, {**WEB_FETCH, "max_uses": max_fetches}]


class AgentError(RuntimeError):
    pass


class Console:
    """Prefixed, flush-immediately console output for one agent."""

    def __init__(self, label: str, quiet: bool = False):
        self.label = label
        self.quiet = quiet
        self._mid_line = False

    def _end_line(self) -> None:
        if self._mid_line:
            sys.stdout.write("\n")
            self._mid_line = False

    def info(self, msg: str) -> None:
        if self.quiet:
            return
        self._end_line()
        print(f"[{self.label}] {msg}", flush=True)

    def stream(self, text: str) -> None:
        if self.quiet or not text:
            return
        sys.stdout.write(text)
        sys.stdout.flush()
        self._mid_line = not text.endswith("\n")

    def done(self) -> None:
        self._end_line()


def _short(value: Any, limit: int = 110) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


@dataclass
class AgentRun:
    text: str
    stop_reason: str | None
    turns: int
    usage: dict[str, int] = field(default_factory=dict)


def run_agent(
    settings: Settings,
    *,
    label: str,
    system: str,
    prompt: str | list[dict],
    tools: Iterable[Any],
    effort: str,
    max_iterations: int = 60,
    quiet: bool = False,
) -> AgentRun:
    """Run one agent until Claude stops calling tools. Client tools run locally via the
    SDK tool runner; web_search / web_fetch run on Anthropic's servers."""
    console = Console(label, quiet)
    client = anthropic.Anthropic()
    params: dict[str, Any] = dict(
        model=settings.model,
        max_tokens=settings.max_tokens,
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
        tools=list(tools),
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        cache_control={"type": "ephemeral"},  # cache the growing conversation between turns
        max_iterations=max_iterations,
        stream=True,
    )
    if settings.use_fallbacks:
        # On a safety refusal the API re-runs the turn on a fallback model chosen by refusal category.
        params.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")

    usage = {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    final_text: list[str] = []
    stop_reason = None
    turns = 0
    console.info(f"model={settings.model} effort={effort}")
    try:
        runner = client.beta.messages.tool_runner(**params)
        for stream in runner:
            for event in stream:
                if event.type == "content_block_delta" and event.delta.type == "text_delta":
                    console.stream(event.delta.text)
                elif event.type == "content_block_stop":
                    block = event.content_block
                    if block.type == "tool_use":
                        console.info(f"🔧 {block.name} {_short(block.input)}")
                    elif block.type == "server_tool_use":
                        args = block.input if isinstance(block.input, dict) else {}
                        console.info(f"🌐 {block.name}: {_short(args.get('query') or args.get('url') or block.input)}")
                    elif block.type == "fallback":
                        console.info(f"↪ chuyển sang model dự phòng: {block.to.model}")
            message = stream.get_final_message()
            turns += 1
            stop_reason = message.stop_reason
            for key in usage:
                usage[key] += getattr(message.usage, key, 0) or 0
            final_text = [b.text for b in message.content if b.type == "text"]
    except anthropic.AuthenticationError as e:
        raise AgentError("ANTHROPIC_API_KEY không hợp lệ (kiểm tra .env)") from e
    except TypeError as e:  # raised by the SDK when no credential source resolves at all
        if "authentication" not in str(e):
            raise
        raise AgentError("Chưa có ANTHROPIC_API_KEY — sao chép .env.example thành .env và điền key") from e
    except anthropic.RateLimitError as e:
        raise AgentError("Bị giới hạn tốc độ API (429) — thử lại sau ít phút") from e
    except anthropic.APIConnectionError as e:
        raise AgentError(f"Không kết nối được Claude API: {e}") from e
    except anthropic.APIStatusError as e:
        raise AgentError(f"Claude API lỗi {e.status_code}: {e.message}") from e
    finally:
        console.done()

    if stop_reason == "refusal":
        raise AgentError("Claude từ chối yêu cầu này (stop_reason=refusal)")
    if stop_reason == "max_tokens":
        console.info("⚠ phản hồi bị cắt do chạm max_tokens (tăng VEDIT_MAX_TOKENS)")
    if stop_reason in ("tool_use", "pause_turn"):
        console.info(f"⚠ dừng vì chạm giới hạn {max_iterations} vòng lặp")
    console.info(f"xong sau {turns} lượt — tokens in={usage['input_tokens']:,} "
                 f"(cache đọc {usage['cache_read_input_tokens']:,}) out={usage['output_tokens']:,}")
    return AgentRun(text="\n".join(final_text).strip(), stop_reason=stop_reason, turns=turns, usage=usage)
