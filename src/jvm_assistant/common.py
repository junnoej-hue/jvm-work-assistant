from __future__ import annotations
import json
import os
import re
import ssl
import sys
from pathlib import Path
from urllib import request, error

class UserError(Exception):
    """A safe, user-facing error with no credentials or source payload."""

# Supported installation keeps this venv directly inside the source checkout.
# A regular install avoids macOS hidden .pth files breaking editable imports.
ROOT = Path(sys.prefix).resolve().parent

def state_dir() -> Path:
    p = Path(os.environ.get("JVM_ASSISTANT_STATE_DIR", str(Path.home() / "Library/Application Support/JvMWorkAssistant")))
    if p.is_symlink():
        raise UserError("State directory cannot be a symlink")
    p.mkdir(parents=True, exist_ok=True, mode=0o700)
    p.chmod(0o700)
    return p

def load_config() -> dict:
    p = state_dir() / "settings.json"
    if not p.exists():
        return {"webex_rooms": []}
    if p.is_symlink() or p.stat().st_size > 65536:
        raise UserError("Invalid settings file")
    return json.loads(p.read_text())

def save_config(config: dict):
    p = state_dir() / "settings.json"
    tmp = p.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    os.replace(tmp, p)

def bounded_int(value: int, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise UserError(f"Choose a number from {low} to {high}")
    return value

def clean_id(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_=.-]{1,512}", value):
        raise UserError("Invalid service identifier")
    return value

class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise UserError("Unexpected redirect rejected; credentials were not forwarded")

def webex_http(path: str, *, token: str | None = None, form: dict | None = None) -> dict:
    if not path.startswith("/") or path.startswith("//") or "\r" in path or "\n" in path:
        raise UserError("Invalid API path")
    if form is not None and path != "/access_token":
        raise UserError("Only OAuth token exchange can use POST")
    headers = {"Accept": "application/json"}
    data = None
    if form is not None:
        from urllib.parse import urlencode
        data = urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif token:
        headers["Authorization"] = "Bearer " + token
    req = request.Request("https://webexapis.com/v1" + path, data=data, headers=headers, method="POST" if form is not None else "GET")
    opener = request.build_opener(NoRedirect(), request.HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(req, timeout=25) as response:
            raw = response.read(4_000_001)
            if len(raw) > 4_000_000:
                raise UserError("Response too large; narrow the request")
            result = json.loads(raw)
            # Follow only the service-provided next page on the same HTTPS endpoint.
            from urllib.parse import urlparse
            result.pop('_next_path', None)
            for link in response.headers.get('Link','').split(','):
                match = re.search(r'<([^>]+)>;\s*rel="next"', link)
                if not match:
                    continue
                nxt = urlparse(match[1])
                if nxt.scheme != 'https' or nxt.netloc != 'webexapis.com' or nxt.path != '/v1' + path.split('?')[0] or nxt.fragment:
                    raise UserError('Unexpected pagination URL rejected')
                result['_next_path'] = nxt.path[3:] + ('?' + nxt.query if nxt.query else '')
            return result
    except error.HTTPError as exc:
        raise UserError(f"Webex returned HTTP {exc.code}; check authorization or try later") from None
    except (error.URLError, TimeoutError, OSError):
        raise UserError("Webex connection failed; check your network") from None
    except (ValueError, UnicodeError):
        raise UserError("Webex returned an invalid response") from None
