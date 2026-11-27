"""PyCharm Run entry point for TestPilot AI."""

import argparse
import errno
import logging
import signal
import socket
import threading
import time
import webbrowser
from contextlib import closing
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, build_opener

HOST = "127.0.0.1"
LOG = logging.getLogger("testpilot")


def open_when_ready(url: str, stopped: threading.Event, *, timeout: float = 30) -> None:
    client = build_opener(ProxyHandler({}))
    deadline = time.monotonic() + timeout
    detail = "服务尚未响应"
    while not stopped.is_set():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            LOG.warning("健康检查等待超时 (%s)。请检查 SQLite 和运行日志，服务就绪后访问 %s", detail, url)
            return
        try:
            with client.open(f"{url}/api/health", timeout=min(1, remaining)) as response:
                if response.status == 200:
                    break
        except HTTPError as exc:
            detail = f"HTTP {exc.code}"
            exc.close()
        except (URLError, OSError) as exc:
            detail = str(exc)
        stopped.wait(0.15)
    if stopped.is_set():
        return
    try:
        if webbrowser.open(url, new=2):
            LOG.info("已向默认浏览器发送打开请求 %s", url)
        else:
            LOG.warning("系统未确认浏览器启动，请手动访问 %s", url)
    except (OSError, webbrowser.Error) as exc:
        LOG.warning("打开浏览器失败 (%s)，请手动访问 %s", exc, url)


def main() -> int:
    parser = argparse.ArgumentParser(description="启动 TestPilot AI 本地服务")
    parser.add_argument("--mode", choices=("demo", "dev"), default="demo")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true", help="跳过浏览器启动")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("端口必须在 1 到 65535 之间")

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    try:
        import uvicorn
        from backend.app import create_app
    except ImportError as exc:
        LOG.error("项目依赖加载失败 (%s)。请在 PyCharm 项目解释器中安装 requirements.txt。", exc)
        return 1

    url = f"http://{HOST}:{args.port}"
    stopped = threading.Event()
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as listener:
            # Windows can otherwise allow a second listener to share the address.
            if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            else:
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                listener.bind((HOST, args.port))
            except OSError as exc:
                if exc.errno in (errno.EADDRINUSE, 10048):
                    LOG.error("端口 %d 已被占用。请访问已有服务或停止占用进程后重新运行。", args.port)
                else:
                    LOG.error("无法绑定 %s (%s)。请检查端口占用和本机端口限制。", url, exc)
                return 1

            server = uvicorn.Server(uvicorn.Config(
                create_app(mode=args.mode), host=HOST, port=args.port, workers=1,
                log_level="debug" if args.mode == "dev" else "info",
                proxy_headers=False,
            ))
            LOG.info("启动 %s 模式 %s", args.mode, url)
            if not args.no_browser:
                threading.Thread(
                    target=open_when_ready, args=(url, stopped),
                    name="open-dashboard", daemon=True,
                ).start()
            server.run(sockets=[listener])
            return 0 if server.started else 1
    except KeyboardInterrupt:
        return 0
    except Exception:
        LOG.exception("TestPilot AI 启动或运行失败")
        return 1
    finally:
        stopped.set()


if __name__ == "__main__":
    # Uvicorn replays the stopping signal after it has closed the listener.
    # Treat a Windows console break like Ctrl+C once graceful shutdown is done.
    if hasattr(signal, "SIGBREAK") and signal.getsignal(signal.SIGBREAK) == signal.SIG_DFL:
        signal.signal(signal.SIGBREAK, signal.default_int_handler)
    raise SystemExit(main())
