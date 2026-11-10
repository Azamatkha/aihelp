"""Backendga ulanishni tekshirish: nima uchun yuborib bo'lmayotganini to'liq ko'rsatadi."""

import socket
import ssl
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from support import sync


def _cause_chain(exc: BaseException) -> list[str]:
    """Exception va uning ichidagi barcha sabablari (requests xatoni 3-4 qavat o'raydi)."""
    out, seen = [], set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        out.append(f"{type(exc).__module__}.{type(exc).__name__}: {exc}")
        exc = exc.__cause__ or exc.__context__
    return out


def _server_certificate(host: str, port: int) -> dict:
    """Server bergan sertifikat (tekshirmasdan) — kim imzolagani va AIA manzili."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with socket.create_connection((host, port), timeout=15) as raw:
        with ctx.wrap_socket(raw, server_hostname=host) as tls:
            der = tls.getpeercert(binary_form=True)
    pem = ssl.DER_cert_to_PEM_cert(der)
    with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as f:
        f.write(pem)
    try:
        return ssl._ssl._test_decode_cert(f.name)  # stdlib; sertifikatni dict ga ochadi
    finally:
        Path(f.name).unlink(missing_ok=True)


def _windows_proxy() -> dict:
    """Brauzer (Edge/Chrome) ishlatadigan Windows proxy sozlamalari — registrdan."""
    try:
        import winreg
    except ImportError:
        return {}
    out = {}
    path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            for name in ("ProxyEnable", "ProxyServer", "ProxyOverride", "AutoConfigURL", "AutoDetect"):
                try:
                    out[name] = winreg.QueryValueEx(key, name)[0]
                except OSError:
                    pass
    except OSError as e:
        out["xato"] = str(e)
    return out


def _tcp_checks(host: str, port: int) -> list[str]:
    """DNS natijasi va har bir IP ga to'g'ridan-to'g'ri TCP ulanish (proxy'siz)."""
    lines = []
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError as e:
        return [f"DNS xato: {type(e).__name__}: {e}"]
    for family, _, _, _, addr in dict.fromkeys((i[0], i[1], i[2], i[3], i[4]) for i in infos):
        started = time.monotonic()
        try:
            with socket.socket(family, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect(addr)
            lines.append(f"{addr[0]} -> OK ({time.monotonic() - started:.1f} s)")
        except OSError as e:
            lines.append(f"{addr[0]} -> {type(e).__name__}: {e} ({time.monotonic() - started:.1f} s)")
    return lines


def _name(parts) -> str:
    return ", ".join(f"{k}={v}" for rdn in parts for k, v in rdn)


class Command(BaseCommand):
    help = "turon-ai backendga ulanishni tekshiradi va xato sababini to'liq chiqaradi"

    def handle(self, *args, **options):
        if not settings.BACKEND_URL:
            raise CommandError(".env da BACKEND_URL yo'q")
        w = self.stdout.write
        w(f"Python:     {sys.executable}")
        w(f"truststore: {'yoqilgan' if 'truststore' in sys.modules else 'YO`Q (pip install -r requirements.txt)'}")
        w(f"Manzil:     {settings.BACKEND_URL}")
        w(f"Proxy:      {settings.BACKEND_PROXY or 'yo`q'}")

        parts = urlsplit(settings.BACKEND_URL)
        host, port = parts.hostname, parts.port or 443

        # Brauzer ochyapti-yu Python ochmasa — odatda brauzer proxy/PAC orqali chiqadi
        w("\n0) Tarmoq")
        w(f"   Windows proxy (brauzerniki): {_windows_proxy() or '—'}")
        w(f"   Python ko'radigan proxy:     {urllib.request.getproxies() or '—'}")
        w(f"   DNS + TCP {host}:{port} (proxy'siz):")
        for line in _tcp_checks(host, port):
            w(f"     {line}")

        # syncbackend bilan bir xil: "none" — muhitdagi HTTP(S)_PROXY ham e'tiborsiz
        http = requests.Session()
        http.headers["User-Agent"] = sync.USER_AGENT  # nginx python-requests'ni 403 qiladi
        if settings.BACKEND_PROXY.lower() == "none":
            http.trust_env = False

        url = f"{settings.BACKEND_URL}/health/"
        w(f"\n1) GET {url}")
        try:
            resp = http.get(url, proxies=sync._proxies(), timeout=15)
            w(self.style.SUCCESS(f"   OK: HTTP {resp.status_code} {resp.text[:200]}"))
        except Exception as e:
            for i, line in enumerate(_cause_chain(e)):
                w(self.style.ERROR(f"   {'  ' * i}{line}"))

        w(f"\n2) Server sertifikati ({host}:{port}, tekshirmasdan)")
        try:
            cert = _server_certificate(host, port)
            w(f"   Kimga:        {_name(cert.get('subject', ()))}")
            w(f"   Kim imzolagan: {_name(cert.get('issuer', ()))}")
            w(f"   Amal qiladi:  {cert.get('notBefore')} — {cert.get('notAfter')}")
            w(f"   Domenlar:     {', '.join(v for _, v in cert.get('subjectAltName', ()))}")
            w(f"   CA Issuers:   {', '.join(cert.get('caIssuers', ())) or '—'}")
        except Exception as e:
            w(self.style.ERROR(f"   Olib bo'lmadi: {type(e).__name__}: {e}"))

        if not settings.BACKEND_API_KEY:
            return
        w("\n3) POST /v1/telegram-bot/sync (bo'sh so'rov, kalitni tekshirish)")
        try:
            resp = http.post(
                f"{settings.BACKEND_URL}/v1/telegram-bot/sync",
                json={"users": [], "messages": []},
                headers={"X-Bot-Key": settings.BACKEND_API_KEY},
                proxies=sync._proxies(),
                timeout=15,
            )
            style = self.style.SUCCESS if resp.status_code == 200 else self.style.ERROR
            w(style(f"   HTTP {resp.status_code}: {resp.text[:300]}"))
        except Exception as e:
            for i, line in enumerate(_cause_chain(e)):
                w(self.style.ERROR(f"   {'  ' * i}{line}"))
