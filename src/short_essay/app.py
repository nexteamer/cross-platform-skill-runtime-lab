from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template_string, request

from short_essay.db import connect, get_run
from short_essay.workflow import run_short_essay

PAGE = """
<!doctype html>
<title>Short-essay lab</title>
<form method="post" action="/">
  <textarea name="text" rows="8" cols="60">{{ text }}</textarea>
  <p><button type="submit">Run</button></p>
</form>
{% if result %}
<pre>{{ result }}</pre>
<p>run {{ run_id }} status {{ status }}</p>
{% endif %}
"""


def create_app(data_root: Path) -> Flask:
    app = Flask(__name__)
    app.config["DATA_ROOT"] = Path(data_root)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/")
    def index():
        return render_template_string(PAGE, text="", result=None)

    @app.post("/")
    def index_post():
        payload = run_short_essay(request.form.get("text") or "", data_root=app.config["DATA_ROOT"])
        return render_template_string(
            PAGE,
            text=request.form.get("text") or "",
            result=payload["result"],
            run_id=payload["run_id"],
            status=payload["status"],
        )

    @app.post("/api/runs")
    def api_create():
        body = request.get_json(force=True, silent=True) or {}
        payload = run_short_essay(str(body.get("text") or ""), data_root=app.config["DATA_ROOT"])
        return jsonify(payload)

    @app.get("/api/runs/<run_id>")
    def api_get(run_id: str):
        state = get_run(connect(app.config["DATA_ROOT"] / "short-essay.sqlite"), run_id)
        if state is None:
            return jsonify({"error": "missing"}), 404
        return jsonify(state)

    return app
