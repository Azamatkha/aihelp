"""Backendga ulanishni tekshirish: nima uchun yuborib bo'lmayotganini to'liq ko'rsatadi."""

import socket
import ssl
import sys
import tempfile
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

        url = f"{settings.BACKEND_URL}/health/"
        w(f"\n1) GET {url}")
        try:
            resp = requests.get(url, proxies=sync._proxies(), timeout=15)
            w(self.style.SUCCESS(f"   OK: HTTP {resp.status_code} {resp.text[:200]}"))
        except Exception as e:
            for i, line in enumerate(_cause_chain(e)):
                w(self.style.ERROR(f"   {'  ' * i}{line}"))

        parts = urlsplit(settings.BACKEND_URL)
        host, port = parts.hostname, parts.port or 443
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
            resp = requests.post(
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
