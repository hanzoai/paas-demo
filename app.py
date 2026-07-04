import os, json, urllib.request, time
from http.server import BaseHTTPRequestHandler, HTTPServer

BASE  = os.environ.get("HANZO_BASE", "https://api.hanzo.ai/v1")
MODEL = os.environ.get("HANZO_MODEL", "deepseek-v3.2")
TOKEN = os.environ.get("HANZO_TOKEN", "")
PORT  = int(os.environ.get("PORT", "8000"))

def ask(prompt):
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 120}).encode()
    req = urllib.request.Request(BASE + "/chat/completions", data=body,
        headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"]["content"].strip(), round((time.time() - t0) * 1000)

PAGE = """<!doctype html><html><head><meta charset=utf-8><title>Hanzo PaaS AI Demo</title>
<style>body{{font-family:system-ui,-apple-system,sans-serif;max-width:720px;margin:56px auto;padding:0 20px}}
.card{{background:#0b0b0c;color:#e8e8ea;padding:26px;border-radius:16px}}
.ans{{background:#111214;border-left:3px solid #6ee7b7;padding:14px 16px;border-radius:8px;white-space:pre-wrap;margin-top:8px}}
.k{{color:#9a9aa2;font-size:13px}} b{{color:#fff}} a{{color:#6ee7b7}}</style></head><body>
<div class=card><h1>&#128640; Deployed on Hanzo native cloud PaaS</h1>
<p class=k>This container was built from a git repo by an in-cluster <b>BuildKit</b> job, pushed to GHCR, reconciled by the operator, and served through the tenant ingress. On every load it calls <b>api.hanzo.ai/v1/chat</b> &mdash; the platform's own AI gateway &mdash; as org <b>maxpower</b>.</p>
<p class=k>model <b>{model}</b> &middot; endpoint {base} &middot; round-trip <b>{ms} ms</b></p>
<p><b>Prompt:</b> {prompt}</p>
<div class=ans>{answer}</div></div></body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/healthz"):
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok"); return
        prompt = "In one upbeat sentence, confirm you are Hanzo AI answering an app deployed on the Hanzo native cloud PaaS."
        try:
            answer, ms = ask(prompt)
        except Exception as e:
            answer, ms = "AI call failed: " + repr(e), 0
        b = PAGE.format(model=MODEL, base=BASE, ms=ms, prompt=prompt, answer=answer).encode()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass

print(f"paas-demo on :{PORT} model={MODEL} base={BASE}", flush=True)
HTTPServer(("0.0.0.0", PORT), H).serve_forever()
