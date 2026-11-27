"""Local-only Ollama transport and installed GGUF identity checks."""
import ipaddress
import json
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def local_base(url):
    parsed = urlsplit(url)
    if (parsed.scheme != "http" or parsed.username is not None or parsed.password is not None
            or parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
        raise ValueError("仅支持本机回环 HTTP Ollama 服务")
    host = "127.0.0.1" if parsed.hostname == "localhost" else parsed.hostname
    if not host or not ipaddress.ip_address(host).is_loopback:
        raise ValueError("模型服务必须使用本机回环地址")
    return "http://" + (f"[{host}]" if ":" in host else host) + f":{parsed.port or 11434}"


def request_json(base, path, payload, timeout):
    data = None if payload is None else json.dumps(payload).encode("utf8")
    request = Request(base + path, data=data, headers={"Content-Type": "application/json"})
    try:
        with build_opener(NoRedirect(), ProxyHandler({})).open(request, timeout=timeout) as response:
            raw = response.read(512 * 1024 + 1)
    except HTTPError as exc:
        with exc:
            detail = exc.read(2048).decode("utf8", "replace")
        try:
            detail = json.loads(detail)["error"]
        except (ValueError, KeyError, TypeError):
            detail = ""
        raise ValueError(f"Ollama HTTP {exc.code} {str(detail)[:300]}") from None
    if len(raw) > 512 * 1024:
        raise ValueError("本机模型响应超过 512 KiB")
    return json.loads(raw)


def choose_model(base, requested, *, preferred=(), query=None):
    query = query or request_json
    entries = query(base, "/api/tags", None, 5)["models"]
    available = {m["name"]: m for m in entries if m.get("digest") and "cloud" not in m["name"].lower()}
    choices = (requested, requested + ":latest") if requested else (*preferred, *sorted(available))
    for name in dict.fromkeys(choices):
        if name not in available:
            continue
        info = query(base, "/api/show", {"model": name, "verbose": False}, 12)
        if (info.get("remote_model") or info.get("remote_host")
                or info.get("details", {}).get("format") != "gguf"
                or not info.get("model_info", {}).get("general.architecture")):
            continue
        return name, available[name]["digest"]
    raise ValueError("未找到已安装、可验证的本地 GGUF 模型")
