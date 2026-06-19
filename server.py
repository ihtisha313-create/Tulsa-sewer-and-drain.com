#!/usr/bin/env python3
"""
Tulsa Sewer & Drain — performance-optimised static server
  - Gzip compression (HTML / CSS / JS / JSON / SVG)
  - Aggressive Cache-Control (1-year for assets, no-cache for HTML)
  - Inline critical CSS (eliminates render-blocking stylesheet)
  - Minified CSS/JS served transparently (/css/style.css → style.min.css)
  - RFC 8288 Link headers + text/markdown content-negotiation for AI agents
"""
import os, re, html as _html, gzip as _gzip, io, mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 5000

LINK_HEADER = ', '.join([
    '</.well-known/api-catalog>; rel="api-catalog"',
    '</.well-known/agent-skills/index.json>; rel="https://agentskills.io/index"',
])

# Extensions that gzip helps
GZIP_TYPES = frozenset({
    'text/html', 'text/css', 'application/javascript',
    'text/javascript', 'application/json', 'image/svg+xml',
    'text/plain', 'text/markdown', 'text/xml',
})

# Cache-Control by extension
def cache_for(path):
    ext = os.path.splitext(path.split('?')[0])[1].lower()
    # Images & fonts never change — cache forever
    if ext in ('.webp','.jpg','.jpeg','.png','.gif',
               '.ico','.woff','.woff2','.ttf'):
        return 'public, max-age=31536000, immutable'
    # SVG may be updated — 1 week
    if ext == '.svg':
        return 'public, max-age=604800'
    # CSS/JS — 1 day (allows quick updates without stale cache pain)
    if ext in ('.css', '.js'):
        return 'public, max-age=86400'
    # HTML — always revalidate
    return 'no-cache, must-revalidate'

# Transparent redirect: /css/style.css → serve minified CSS
# (JS served as-is; gzip alone gives ~70% compression on 13 KB)
MINIFY_MAP = {
    '/css/style.css': 'css/style.min.css',
}

# ── Critical above-the-fold CSS (injected inline, ~4 KB) ─────────────────────
CRITICAL_CSS = (
    "*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}"
    "html{scroll-behavior:smooth}html,body{overflow-x:hidden}"
    "body{font-family:'Source Sans 3','Source Sans Pro',-apple-system,BlinkMacSystemFont,"
    "'Segoe UI',Roboto,sans-serif;color:#2d3748;line-height:1.65;font-size:17px;"
    "background:#fff;-webkit-font-smoothing:antialiased}"
    "img{max-width:100%;height:auto;display:block}"
    "a{color:#b85200;text-decoration:none}"
    "h1,h2,h3,h4,h5,h6{font-family:'Oswald',sans-serif;font-weight:600;color:#1a3a5c;"
    "line-height:1.2;margin-bottom:.6em;letter-spacing:-.01em}"
    "h1{font-size:clamp(1.7rem,4vw,2.6rem)}"
    "h2{font-size:clamp(1.5rem,3.2vw,2rem);margin-top:1.5em}"
    "h3{font-size:clamp(1.15rem,2.5vw,1.45rem)}"
    "p{margin-bottom:1.1em}"
    ":root{--primary:#1a3a5c;--primary-dark:#0f2338;--primary-light:#2c5282;"
    "--accent:#e8640a;--accent-dark:#c45208;--accent-light:#f6ad55;"
    "--text:#2d3748;--text-light:#718096;--light-bg:#f4f7fa;--white:#fff;"
    "--border:#e2e8f0;--shadow:0 4px 6px rgba(0,0,0,.08);"
    "--shadow-lg:0 10px 25px rgba(0,0,0,.12);--radius:8px;--header-height:70px}"
    ".emergency-banner{background:#e8640a;color:#fff;text-align:center;"
    "padding:10px 20px;font-weight:600;font-size:.95rem}"
    ".emergency-banner a{color:#fff;text-decoration:underline}"
    ".top-bar{background:#0f2338;color:#fff;font-size:.9rem;padding:8px 0}"
    ".top-bar-inner{display:flex;justify-content:space-between;align-items:center;"
    "flex-wrap:wrap;gap:8px}"
    ".top-bar a{color:#fff;font-weight:600}"
    ".top-bar-left span{margin-right:18px}"
    ".container{max-width:1200px;margin:0 auto;padding:0 24px}"
    ".container-narrow{max-width:900px;margin:0 auto;padding:0 24px}"
    ".site-header{background:#fff;box-shadow:0 2px 12px rgba(0,0,0,.1);"
    "position:sticky;top:0;z-index:500;height:70px;display:flex;align-items:center}"
    ".header-inner{display:flex;justify-content:space-between;align-items:center;"
    "padding:0 24px;width:100%;max-width:1200px;margin:0 auto;gap:16px}"
    ".logo{display:flex;align-items:center;gap:10px;text-decoration:none;flex-shrink:0}"
    ".logo svg{width:44px;height:44px}"
    ".logo-text{font-family:'Oswald',sans-serif;font-weight:700;font-size:1.2rem;"
    "color:#1a3a5c;line-height:1.15}"
    ".logo-text small{display:block;font-size:.62rem;color:#e8640a;"
    "text-transform:uppercase;letter-spacing:.1em;margin-top:2px;font-weight:600}"
    ".main-nav{display:flex;align-items:center}"
    ".main-nav>ul{list-style:none;display:flex;gap:2px;margin:0;align-items:center}"
    ".main-nav>ul>li>a{color:#1a3a5c;font-weight:600;padding:8px 11px;"
    "border-radius:8px;font-size:.875rem;white-space:nowrap;display:flex;"
    "align-items:center;min-height:44px}"
    ".header-cta{background:#e8640a!important;color:#fff!important;"
    "padding:10px 20px!important;border-radius:8px;font-weight:700;white-space:nowrap}"
    ".mobile-toggle{display:none;background:none;border:2px solid #e2e8f0;"
    "cursor:pointer;width:46px;height:46px;border-radius:8px;color:#1a3a5c;"
    "flex-direction:column;align-items:center;justify-content:center;gap:5px;flex-shrink:0}"
    ".mobile-toggle span{display:block;width:22px;height:2.5px;"
    "background:currentColor;border-radius:2px}"
    ".hero{background:linear-gradient(135deg,#0f2338 0%,#1a3a5c 50%,#2c5282 100%);"
    "color:#fff;padding:70px 0 80px;position:relative;overflow:hidden}"
    ".hero::before{content:'';position:absolute;top:0;right:0;width:55%;height:100%;"
    "background:radial-gradient(circle at 70% 30%,rgba(232,100,10,.18) 0%,transparent 65%);"
    "pointer-events:none}"
    ".hero-grid{display:grid;grid-template-columns:1fr 400px;gap:48px;align-items:center}"
    ".hero h1{color:#fff;font-size:clamp(1.75rem,3.8vw,3rem);margin-bottom:16px;line-height:1.12}"
    ".hero p.lead{font-size:1.15rem;opacity:.94;margin-bottom:26px}"
    ".hero-badge{display:inline-block;background:rgba(232,100,10,.22);border:1px solid #e8640a;"
    "color:#f6ad55;padding:6px 16px;border-radius:30px;font-size:.83rem;font-weight:700;"
    "text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px}"
    ".hero-features{list-style:none;margin:22px 0 30px;padding:0}"
    ".hero-features li{padding-left:34px;position:relative;margin-bottom:10px;font-size:1.04rem}"
    ".hero-features li::before{content:'✓';position:absolute;left:0;top:2px;"
    "width:22px;height:22px;background:#e8640a;color:#fff;border-radius:50%;"
    "display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.82rem}"
    ".hero-cta-row{display:flex;gap:14px;flex-wrap:wrap}"
    ".btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;"
    "padding:13px 26px;border-radius:8px;font-weight:700;text-decoration:none;"
    "transition:all .2s;cursor:pointer;border:none;font-family:inherit;"
    "font-size:1rem;text-align:center;min-height:48px;line-height:1.3}"
    ".btn-primary{background:#e8640a;color:#fff}"
    ".btn-secondary{background:rgba(255,255,255,.15);color:#fff;"
    "border:2px solid rgba(255,255,255,.8)}"
    ".btn-large{padding:16px 32px;font-size:1.05rem}"
    ".btn-block{display:flex;width:100%}"
    ".quote-card{background:#fff;color:#2d3748;padding:28px;border-radius:12px;"
    "box-shadow:0 16px 40px rgba(0,0,0,.2)}"
    ".quote-card h3{color:#1a3a5c;margin-bottom:4px;font-size:1.35rem;margin-top:0}"
    ".quote-card .form-sub{color:#718096;font-size:.92rem;margin-bottom:16px}"
    ".quote-card .form-field{margin-bottom:12px}"
    ".quote-card input,.quote-card select,.quote-card textarea{"
    "width:100%;padding:12px 14px;border:1.5px solid #e2e8f0;border-radius:8px;"
    "font-family:inherit;font-size:1rem;background:#fff;-webkit-appearance:none}"
    ".trust-strip{background:#1a3a5c;color:#fff;padding:32px 0}"
    ".trust-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:28px;text-align:center}"
    ".trust-item{display:flex;flex-direction:column;align-items:center;gap:10px}"
    ".trust-item svg{width:40px;height:40px;fill:#f6ad55}"
    ".trust-item strong{font-family:'Oswald',sans-serif;font-size:1.25rem}"
    ".trust-item span{font-size:.88rem;opacity:.85}"
    ".skip-to-content{position:absolute;top:-100%;left:0;background:#e8640a;color:#fff;"
    "padding:10px 20px;font-weight:700;z-index:9999;text-decoration:none;"
    "border-radius:0 0 4px 0}"
    ".skip-to-content:focus{top:0}"
    ".sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;"
    "overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}"
    ".mobile-call-btn{display:none;position:fixed;bottom:0;left:0;right:0;"
    "background:#e8640a;color:#fff;text-align:center;padding:16px 20px;"
    "font-weight:700;font-size:1.05rem;z-index:400;"
    "box-shadow:0 -4px 16px rgba(0,0,0,.25)}"
    "@media(max-width:992px){.hero-grid{grid-template-columns:1fr}.hero-image{display:none}}"
    "@media(max-width:768px){"
    "body{font-size:16px;padding-bottom:72px}"
    ".site-header{height:62px}:root{--header-height:62px}"
    ".header-inner{padding:0 16px}"
    ".mobile-toggle{display:flex}"
    ".main-nav{position:fixed;top:0;right:0;bottom:0;width:min(320px,88vw);"
    "background:#fff;z-index:600;flex-direction:column;"
    "transform:translateX(100%);transition:transform .3s cubic-bezier(.4,0,.2,1);"
    "box-shadow:-8px 0 32px rgba(0,0,0,.18);overflow-y:auto}"
    ".mobile-call-btn{display:block}"
    ".hero{padding:38px 0 46px}"
    ".hero-grid{grid-template-columns:1fr}"
    ".hero h1{font-size:clamp(1.6rem,6vw,1.95rem)}"
    ".hero-cta-row{flex-direction:column}"
    ".hero-cta-row .btn{width:100%}"
    ".trust-grid{grid-template-columns:repeat(2,1fr)}"
    ".top-bar-left{display:none}.top-bar-inner{justify-content:center}}"
)

# Simple literal string replacement — no regex, no backtracking risk
_BLOCKING_LINK = b'<link rel="stylesheet" href="/css/style.css">'
_ASYNC_BLOCK = (
    b'<style>' + CRITICAL_CSS.encode() + b'</style>'
    b'<link rel="stylesheet" href="/css/style.css" media="print" '
    b'onload="this.media=\'all\';this.onload=null">'
    b'<noscript><link rel="stylesheet" href="/css/style.css"></noscript>'
)


def inject_critical(html_bytes: bytes) -> bytes:
    """Replace the blocking stylesheet link with inline critical CSS + async load."""
    # Try the exact string first (fast path for 99% of pages)
    if _BLOCKING_LINK in html_bytes:
        return html_bytes.replace(_BLOCKING_LINK, _ASYNC_BLOCK, 1)
    # Fallback: case-insensitive scan for any style.css <link>
    lower = html_bytes.lower()
    start = lower.find(b'<link')
    while start != -1:
        end = lower.find(b'>', start)
        if end == -1:
            break
        tag = lower[start:end+1]
        if b'stylesheet' in tag and b'style.css' in tag:
            return html_bytes[:start] + _ASYNC_BLOCK + html_bytes[end+1:]
        start = lower.find(b'<link', start + 1)
    return html_bytes


def gzip_bytes(data: bytes) -> bytes:
    buf = io.BytesIO()
    with _gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=6) as gz:
        gz.write(data)
    return buf.getvalue()


# ── HTML → Markdown (AI agent content-negotiation) ────────────────────────────
from html.parser import HTMLParser

class _MD(HTMLParser):
    SKIP = frozenset({'script','style','noscript','nav','footer','header','aside'})
    SKIP_CLS = frozenset({'emergency-banner','top-bar','mobile-call-btn',
                          'site-header','site-footer','breadcrumb','sidebar-sticky'})
    def __init__(self):
        super().__init__()
        self._depth = 0; self.out = []; self._h = None
    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        cls = ad.get('class','')
        if self._depth or tag in self.SKIP or any(c in cls for c in self.SKIP_CLS):
            self._depth += 1; return
        if tag in ('h1','h2','h3','h4'):
            self._h = '#'*int(tag[1]); self.out.append('\n')
        elif tag == 'li': self.out.append('\n- ')
        elif tag in ('strong','b'): self.out.append('**')
        elif tag in ('em','i'): self.out.append('_')
        elif tag == 'br': self.out.append('\n')
        elif tag in ('p','div','section','article','main'): self.out.append('\n')
    def handle_endtag(self, tag):
        if self._depth: self._depth -= 1; return
        if tag in ('h1','h2','h3','h4'):
            if self._h: self.out.insert(-1 if self.out else 0, self._h+' '); self._h=None
            self.out.append('\n')
        elif tag in ('strong','b'): self.out.append('**')
        elif tag in ('em','i'): self.out.append('_')
        elif tag in ('p','li'): self.out.append('\n')
    def handle_data(self, data):
        if not self._depth:
            t = data.strip()
            if t: self.out.append(t+' ')
    def result(self):
        md = ''.join(self.out)
        return re.sub(r'\n{3,}', '\n\n', md).strip()

def to_markdown(raw: bytes, title: str='') -> bytes:
    p = _MD()
    try: p.feed(raw.decode('utf-8', errors='replace'))
    except Exception: pass
    md = (f'# {title}\n\n' if title else '') + p.result()
    return md.encode('utf-8')

def get_title(raw: bytes) -> str:
    m = re.search(rb'<title[^>]*>(.*?)</title>', raw, re.I|re.S)
    return _html.unescape(m.group(1).decode('utf-8','replace')).strip() if m else ''


# ── Request handler ────────────────────────────────────────────────────────────
class Handler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def do_GET(self):
        try:
            self._handle()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            try:
                self.send_error(500)
            except Exception:
                pass

    def do_HEAD(self):
        try:
            self._handle(head_only=True)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            try:
                self.send_error(500)
            except Exception:
                pass

    def _handle(self, head_only=False):
        url_path = self.path.split('?')[0]

        # Markdown negotiation for AI agents
        if 'text/markdown' in self.headers.get('Accept',''):
            return self._serve_markdown(head_only)

        # Transparent minified-file redirect
        rel_min = MINIFY_MAP.get(url_path)
        if rel_min:
            abs_min = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), rel_min)
            if os.path.isfile(abs_min):
                return self._emit_file(abs_min, url_path, head_only)

        # Normal file
        fpath = self._fspath()
        if fpath is None:
            self.send_error(404)
            return
        self._emit_file(fpath, url_path, head_only)

    def _fspath(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            for idx in ('index.html', 'index.htm'):
                c = os.path.join(path, idx)
                if os.path.exists(c):
                    return c
            return None
        return path if os.path.isfile(path) else None

    def _emit_file(self, fpath, url_path, head_only=False):
        try:
            with open(fpath, 'rb') as f:
                body = f.read()
        except OSError:
            self.send_error(404)
            return

        ext = os.path.splitext(fpath)[1].lower()
        ct  = mimetypes.guess_type(fpath)[0] or 'application/octet-stream'
        if ext == '.html':
            ct = 'text/html; charset=utf-8'
            body = inject_critical(body)
        elif ext in ('.css', '.js') and 'charset' not in ct:
            ct += '; charset=utf-8'

        self._write_response(body, ct, cache_for(url_path), head_only)

    def _write_response(self, body, ct, cache, head_only=False):
        gz = ('gzip' in self.headers.get('Accept-Encoding','') and
              ct.split(';')[0].strip() in GZIP_TYPES)
        if gz:
            body = gzip_bytes(body)

        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', cache)
        self.send_header('Vary', 'Accept-Encoding')
        self.send_header('Link', LINK_HEADER)
        if gz:
            self.send_header('Content-Encoding', 'gzip')
        self.end_headers()
        if not head_only:
            self.wfile.write(body)
            self.wfile.flush()

    def _serve_markdown(self, head_only=False):
        fpath = self._fspath()
        if not fpath or not fpath.endswith('.html'):
            return self._emit_file(fpath or '', self.path.split('?')[0], head_only)
        try:
            raw = open(fpath, 'rb').read()
        except OSError:
            self.send_error(404); return
        md = to_markdown(raw, get_title(raw))
        self._write_response(md, 'text/markdown; charset=utf-8',
                             'no-cache, must-revalidate', head_only)

    def log_message(self, fmt, *args):
        pass  # silence per-request noise


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    httpd = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Tulsa Sewer & Drain serving on port {PORT}')
    httpd.serve_forever()
