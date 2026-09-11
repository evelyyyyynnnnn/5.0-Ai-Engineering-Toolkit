"""An answerer backed by a real language model.

Everything else in this harness is a deterministic stub, and the results file
says so: `any_language_model_run: false`. The stubs exist to show that the
grader separates careful behaviour from reckless behaviour, which has to be
established before a model's score means anything. That work is done. This is
the part that was missing.

It speaks the OpenAI chat protocol, so it works against Ollama on localhost
(no key, no network beyond the machine) or any hosted endpoint. Nothing here
parses, repairs or second-guesses the model's reply: the reply is handed to the
same lexical grader every stub is graded by. A wrapper that tidied the answer
before grading would be measuring the wrapper.

    ollama pull qwen2.5-coder:7b
    python run_llm_demo.py
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

SYSTEM = (
    "You answer questions about company filings, using ONLY the documents "
    "given to you.\n"
    "If the documents state the figure, reply with the value exactly as it is "
    "written, followed by the document's id in square brackets, e.g. "
    "1,284,500 [A]\n"
    "If the documents do not state it, reply exactly: "
    "That figure is not stated in the provided documents.\n"
    "Never estimate, convert, or infer a number that is not written in a "
    "document. Reply with one short line and nothing else."
)


def render_prompt(q) -> str:
    """The documents and the question, as the model sees them."""
    parts = []
    for doc_id, text in q.sources.items():
        parts.append(f"--- DOCUMENT {doc_id} ---\n{text.strip()}")
    parts.append(f"--- QUESTION ---\n{q.text}")
    return "\n\n".join(parts)


class LLMAnswerer:
    """Callable over a Question, exactly like every stub answerer."""

    is_language_model = True

    def __init__(self, model: str = "qwen2.5-coder:7b",
                 base_url: str | None = None,
                 api_key_env: str = "OPENAI_API_KEY",
                 timeout: int = 120):
        self.model = model
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL")
                         or "http://localhost:11434/v1").rstrip("/")
        # Ollama ignores the key but the header must be present.
        self.api_key = os.environ.get(api_key_env) or "ollama"
        self.timeout = timeout
        self.name = f"llm:{model}"
        self.calls: list = []

    def complete(self, prompt: str) -> str:  # pragma: no cover - needs a server
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": prompt}],
            "temperature": 0,
        }).encode()
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=body,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.api_key}"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            payload = json.loads(resp.read())
        return payload["choices"][0]["message"]["content"].strip()

    def __call__(self, q) -> str:
        import time

        prompt = render_prompt(q)
        t0 = time.time()
        try:
            reply = self.complete(prompt)
            error = None
        except (urllib.error.URLError, OSError, KeyError, ValueError) as exc:
            # A failed call is recorded as a failed call. Substituting a
            # refusal would score the model for behaviour it never produced.
            reply, error = "", f"{type(exc).__name__}: {exc}"
        self.calls.append({"qid": q.qid, "latency_s": round(time.time() - t0, 2),
                           "reply_chars": len(reply), "error": error})
        return reply


class ScriptedAnswerer:
    """A stand-in for LLMAnswerer whose replies are fixed in advance.

    Lets the wiring be tested -- prompt shape, error handling, the fact that
    replies reach the grader unaltered -- without a model server. It is not a
    model and never appears in a results file.
    """

    is_language_model = False

    def __init__(self, replies: dict, name: str = "scripted"):
        self.replies = replies
        self.name = name
        self.prompts: list = []

    def __call__(self, q) -> str:
        self.prompts.append(render_prompt(q))
        return self.replies.get(q.qid, "")
