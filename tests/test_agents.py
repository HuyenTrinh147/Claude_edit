"""Agent wiring tests. No real API calls: run_agent is exercised against a local mock of the
Messages API, and the agent flows replace run_agent with a scripted fake that calls the tools."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from anthropic.lib.tools import ToolError

from vedit.agents import editor, scriptwriter
from vedit.agents.base import AgentError, AgentRun, run_agent, web_tools
from vedit.agents.tools import knowledge_tools, plan_tools
from vedit.edl import EditPlan
from vedit.knowledge import KnowledgeBase
from vedit.pipeline import analyze
from vedit.project import Project


def _sse(content: list[dict], stop: str) -> bytes:
    events = [{"type": "message_start", "message": {
        "id": "msg_1", "type": "message", "role": "assistant", "model": "claude-opus-5-5", "content": [],
        "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 10, "output_tokens": 1}}}]
    for i, block in enumerate(content):
        if block["type"] == "text":
            events += [{"type": "content_block_start", "index": i, "content_block": {"type": "text", "text": ""}},
                       {"type": "content_block_delta", "index": i, "delta": {"type": "text_delta", "text": block["text"]}}]
        else:
            events += [{"type": "content_block_start", "index": i, "content_block": {**block, "input": {}}},
                       {"type": "content_block_delta", "index": i,
                        "delta": {"type": "input_json_delta", "partial_json": json.dumps(block["input"])}}]
        events.append({"type": "content_block_stop", "index": i})
    events += [{"type": "message_delta", "delta": {"stop_reason": stop, "stop_sequence": None},
                "usage": {"output_tokens": 5}}, {"type": "message_stop"}]
    return "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in events).encode()


@pytest.fixture
def mock_api(monkeypatch):
    """Local Messages API: replies with the queued responses, records request bodies."""
    state = {"requests": [], "responses": []}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            state["requests"].append(json.loads(self.rfile.read(int(self.headers["content-length"]))))
            body = _sse(*state["responses"].pop(0))
            self.send_response(200)
            self.send_header("content-type", "text/event-stream")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("ANTHROPIC_BASE_URL", f"http://127.0.0.1:{server.server_port}")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    yield state
    server.shutdown()


def test_run_agent_tool_loop(mock_api, settings):
    kb = KnowledgeBase(settings.knowledge_dir)
    kb.save("Hook mở đầu", "scripting", "Câu hỏi gây tò mò.", ["hook"], ["https://example.com"])
    mock_api["responses"] = [
        ([{"type": "text", "text": "Tra kho."},
          {"type": "tool_use", "id": "toolu_1", "name": "kb_search", "input": {"query": "hook"}}], "tool_use"),
        ([{"type": "text", "text": "Xong."}], "end_turn"),
    ]
    run = run_agent(settings, label="T", system="sys", prompt="hi",
                    tools=[*web_tools(), *knowledge_tools(kb, writable=False)], effort="low", quiet=True)
    assert run.text == "Xong." and run.turns == 2 and run.stop_reason == "end_turn"
    first, second = mock_api["requests"]
    assert first["model"] == settings.model
    assert first["thinking"] == {"type": "adaptive"} and first["output_config"] == {"effort": "low"}
    assert first["fallbacks"] == "default" and first["cache_control"] == {"type": "ephemeral"}
    assert [t["name"] for t in first["tools"]] == ["web_search", "web_fetch", "kb_search", "kb_read"]
    result = second["messages"][-1]["content"][0]
    assert result["type"] == "tool_result" and "scripting/hook-mo-dau" in result["content"]


def test_run_agent_refusal(mock_api, settings):
    mock_api["responses"] = [([{"type": "text", "text": ""}], "refusal")]
    with pytest.raises(AgentError, match="từ chối"):
        run_agent(settings, label="T", system="s", prompt="p", tools=[], effort="low", quiet=True)


def scripted(calls: list[tuple[str, dict]], log: list):
    """Fake run_agent: calls the named tools in order, records results / ToolErrors."""
    def fake(settings, *, label, system, prompt, tools, effort, max_iterations=60, quiet=False):
        by_name = {(t if isinstance(t, dict) else t.to_dict())["name"]: t for t in tools}
        json.dumps([t if isinstance(t, dict) else t.to_dict() for t in tools])  # schemas serialise
        for name, args in calls:
            try:
                log.append((name, by_name[name].call(args)))
            except ToolError as e:
                log.append((name, ToolError, str(e.content)))
        return AgentRun(text="ok", stop_reason="end_turn", turns=1)
    return fake


SCRIPT = {
    "title": "T", "title_options": ["a", "b"], "hook": "h", "hook_options": ["x", "y"], "concept": "c",
    "target_audience": "Gen Z", "platform": "tiktok", "duration_target": 5,
    "trend_insights": [{"trend": "POV", "evidence": "https://example.com", "how_to_apply": "mở bằng POV"}],
    "keywords": ["a", "b", "c"], "hashtags": ["#a", "#b", "#c"], "post_caption": "cap",
    "scenes": [{"start": 0, "end": 2, "purpose": "hook", "visual": "cảnh 1", "on_screen_text": "Chỉ 20k?"}],
    "music_direction": "lofi", "cta": "follow",
}
PLAN = {
    "canvas": {"width": 360, "height": 640},
    "clips": [{"source": "main", "start": 0.2, "end": 1.8}, {"source": "main", "start": 4.0, "end": 5.0, "fit": "blur"}],
    "texts": [{"text": "Chỉ 20k?", "start": 0, "end": 1.5, "position": "upper", "size": 40}],
    "export": {"encoder_preset": "ultrafast"},
}


def test_scriptwriter_then_editor_flow(media, settings, monkeypatch):
    project = Project.create(settings, media["land"], "Demo quán cà phê")
    analyze(settings, project, transcript=media["srt"])

    log: list = []
    monkeypatch.setattr(scriptwriter, "run_agent", scripted([
        ("view_frames", {"times": [1.0, 99]}),
        ("save_script", {"title": "thiếu trường"}),
        ("save_script", SCRIPT),
        ("save_edit_plan", {"clips": [{"source": "main", "start": 0, "end": 60}]}),
        ("save_edit_plan", PLAN),
    ], log))
    scriptwriter.run_scriptwriter(settings, project, goal="review quán", duration=5)
    frames = log[0][1]
    assert [b["type"] for b in frames] == ["text", "image", "text"] and "ngoài video" in frames[2]["text"]
    assert log[1][1] is ToolError and "hook_options" in log[1][2]
    assert log[3][1] is ToolError and "vượt quá độ dài nguồn" in log[3][2]
    assert "# T" in (project.script_dir / "script.md").read_text(encoding="utf-8")
    plan = EditPlan.load(project.plan_path)
    assert plan.sources["main"] == str(media["land"].resolve())

    log.clear()
    monkeypatch.setattr(editor, "run_agent", scripted([
        ("render_preview", {}), ("inspect_render", {"times": [0.5], "which": "final"}), ("render_final", {}),
    ], log))
    editor.run_editor(settings, project, quiet=True)
    preview_blocks = log[0][1]
    assert preview_blocks[0]["type"] == "text" and any(b["type"] == "image" for b in preview_blocks)
    assert log[1][1] is ToolError
    assert (project.renders_dir / "final.mp4").exists() and (project.renders_dir / "final.jpg").exists()


def test_scriptwriter_requires_saved_outputs(media, settings, monkeypatch):
    project = Project.create(settings, media["land"])
    analyze(settings, project)
    monkeypatch.setattr(scriptwriter, "run_agent", scripted([("save_script", SCRIPT)], []))
    with pytest.raises(AgentError, match="plan"):
        scriptwriter.run_scriptwriter(settings, project, goal="x")


def test_editor_falls_back_to_deterministic_render(media, settings, monkeypatch):
    project = Project.create(settings, media["land"])
    plan_tools(project)[0].call(PLAN)  # save_edit_plan
    monkeypatch.setattr(editor, "run_agent", scripted([], []))
    editor.run_editor(settings, project, quiet=True)
    assert (project.renders_dir / "final.mp4").exists()
