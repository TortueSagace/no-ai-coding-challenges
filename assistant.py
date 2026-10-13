"""AI assistant for the challenges that allow one: a small, fast chat model that has read the statement.

The models are served for free by OpenRouter. Each user brings their own key (https://openrouter.ai/keys):
- on Kaggle: Add-ons -> Secrets -> add a secret named OPENROUTER_API_KEY, then tick it for the notebook;
- locally: an OPENROUTER_API_KEY environment variable, or a line OPENROUTER_API_KEY=... in a .env file
  in the notebook's folder or one of its parents.

In the notebook:  ask("question")  |  ask("question", my_solution)  |  reset()
Standard library only. Every notebook loads this file from the repo, so editing MODELS here updates them all.
"""

import inspect
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

KEY_NAME = "OPENROUTER_API_KEY"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Tried in order: a model that is rate-limited, removed or failing falls through to the next one.
# Free, mid-sized and fast, with reasoning switched off: genuinely helpful, but not meant to one-shot the
# problem (`python -m cfnb oneshot <pid>` measures that). Best first; the Gemmas are often rate-limited upstream.
MODELS = [
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
    "apodex/apodex-1.1-mini:free",
    "poolside/laguna-xs-2.1:free",
    "cohere/north-mini-code:free",  # slow and thinks aloud: last resort
]
MAX_TOKENS = 2000

SYSTEM_PROMPT = """You are the assistant of a programmer solving a Codeforces problem in a Python notebook.
They implement `my_solution`, which solves ONE test case: its arguments are already parsed and it returns \
the answer (see the interface below). It does not read input or print anything.
Be concise and accurate. Answer in English (unless asked in another language), in Markdown, with code in \
```python blocks.
Answer exactly what is asked: explain, hint or debug, and write a full solution only if explicitly asked for one.
When code is shown, point to concrete bugs, with a small failing input when you can. If you are unsure, say so.

{context}"""

NO_KEY = (f"🔑 No OpenRouter key found. Get a free one at https://openrouter.ai/keys, then either add a Kaggle "
          f"secret named {KEY_NAME} (Add-ons → Secrets, and tick it for this notebook) or, locally, put "
          f"{KEY_NAME}=... in a .env file. Rerun this cell afterwards (or paste the key when ask() prompts for it).")

_current = None


def find_key():
    """Return (key, where it was found), or (None, None)."""
    key = os.environ.get(KEY_NAME, "").strip()
    if key:
        return key, "environment variable"
    try:
        from kaggle_secrets import UserSecretsClient
        key = (UserSecretsClient().get_secret(KEY_NAME) or "").strip()
        if key:
            return key, "Kaggle secret"
    except Exception:  # not on Kaggle, or the secret is not attached to this notebook
        pass
    for folder in (Path.cwd(), *Path.cwd().parents):
        env = folder / ".env"
        if env.is_file():
            for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
                name, sep, value = line.partition("=")
                if sep and name.strip().removeprefix("export ").strip() == KEY_NAME and value.strip():
                    return value.strip().strip("'\""), ".env file"
    return None, None


class _Output:
    """Live Markdown in a notebook (one display updated as the answer streams), plain text elsewhere."""

    def __init__(self):
        self.text, self.last = "", 0.0
        try:
            from IPython import get_ipython
            from IPython.display import Markdown, display
            if get_ipython() is None:
                raise ImportError
            self.markdown = Markdown
            self.handle = display(Markdown("*…*"), display_id=True)
        except ImportError:
            self.handle = None

    def add(self, piece):
        self.text += piece
        if self.handle is None:
            print(piece, end="", flush=True)
        elif time.time() - self.last > 0.2:
            self.handle.update(self.markdown(self.text))
            self.last = time.time()

    def finish(self, note):
        if self.handle is None:
            print(("\n\n" if self.text else "") + note)
        else:
            self.handle.update(self.markdown(self.text + ("\n\n" if self.text else "") + note))


class _ModelFailed(Exception):
    pass


class Assistant:
    def __init__(self, context, questions):
        self.context, self.questions_left = context, questions
        self.key, self.key_source = find_key()
        self.reset()

    def reset(self):
        """Forget the conversation (the question budget is kept)."""
        self.history = [{"role": "system", "content": SYSTEM_PROMPT.format(context=self.context)}]

    def ask(self, question, *code):
        """Ask a question; pass functions (e.g. my_solution) or code strings to show them to the assistant."""
        if not self.key:
            try:
                from getpass import getpass
                self.key, self.key_source = getpass("OpenRouter API key: ").strip(), "prompt"
            except Exception:
                pass
            if not self.key:
                print(NO_KEY)
                return
        if self.questions_left <= 0:
            print("No questions left for this challenge: the rest is up to you! 💪")
            return
        content = question
        for c in code:
            src = c if isinstance(c, str) else _source(c)
            content += f"\n\nMy code:\n```python\n{src.rstrip()}\n```"
        messages = self.history + [{"role": "user", "content": content}]

        out, errors = _Output(), []
        for model in MODELS:
            try:
                for piece in self._stream(model, messages):
                    out.add(piece)
                if not out.text.strip():
                    raise _ModelFailed("empty answer")
            except urllib.error.HTTPError as e:
                message = _error_message(e)
                if e.code == 401:
                    out.finish(f"🔑 OpenRouter rejected the key ({message}). Check {KEY_NAME}.")
                    return
                if e.code == 429 and "per-day" in message:
                    out.finish(f"⏳ Daily limit of free requests reached on your OpenRouter account ({message}).")
                    return
                errors.append(f"{model}: {e.code} {message}")
                continue
            except (_ModelFailed, urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
                if out.text:  # the answer broke off midway: don't restart it with another model
                    out.finish(f"⚠️ The answer was interrupted ({e}). This question was not counted; ask again.")
                    return
                errors.append(f"{model}: {e}")
                continue
            self.history = messages + [{"role": "assistant", "content": out.text}]
            self.questions_left -= 1
            left = f"{self.questions_left} question{'s' if self.questions_left != 1 else ''} left"
            out.finish(f"<sub>{model.removesuffix(':free')} · {left}</sub>")
            return
        out.finish("⏳ Every model is busy or unavailable right now (free models are often rate-limited). "
                   "Wait a minute and ask again; this question was not counted.\n\n"
                   + "\n".join(f"- `{e}`" for e in errors))

    def _stream(self, model, messages):
        body = {"model": model, "messages": messages, "stream": True, "max_tokens": MAX_TOKENS,
                "reasoning": {"enabled": False}}
        request = urllib.request.Request(API_URL, data=json.dumps(body).encode(), headers={
            "Authorization": f"Bearer {self.key}", "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/TortueSagace/no-ai-coding-challenges",
            "X-Title": "No-AI Coding Challenges"})
        with urllib.request.urlopen(request, timeout=60) as response:
            for raw in response:  # server-sent events: "data: {json}" lines, ": comments", "data: [DONE]"
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    return
                chunk = json.loads(data)
                if "error" in chunk:
                    raise _ModelFailed(chunk["error"].get("message", "provider error"))
                choices = chunk.get("choices") or [{}]
                piece = (choices[0].get("delta") or {}).get("content")
                if piece:
                    yield piece


def _source(obj):
    try:
        return inspect.getsource(obj)
    except (TypeError, OSError):
        return repr(obj)


def _error_message(error):
    try:
        info = json.loads(error.read())["error"]
        raw = (info.get("metadata") or {}).get("raw")
        return str(raw or info.get("message"))[:200]
    except Exception:
        return error.reason


def start(context_path, questions=10):
    """Set up the assistant for one challenge; context_path is the chaN_context.md file of the repo."""
    global _current
    _current = Assistant(Path(context_path).read_text(encoding="utf-8"), questions)
    if _current.key:
        print(f"🤖 Assistant ready ({questions} questions, OpenRouter key from {_current.key_source}).")
        print('Ask with ask("..."). To show your code too: ask("...", my_solution).')
    else:
        print(NO_KEY)


def ask(question, *code):
    if _current is None:
        print("Run the assistant setup cell first.")
        return
    _current.ask(question, *code)


def reset():
    if _current is not None:
        _current.reset()
