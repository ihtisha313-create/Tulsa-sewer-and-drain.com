#!/usr/bin/env python3
"""
Tulsa Sewer & Drain — static file server with agent-discovery enhancements:
  - RFC 8288 Link response headers on every request
  - Content-Type: text/markdown negotiation (Accept: text/markdown)
"""
import os
import re
import html
from http.server import HTTPServer, SimpleHTTPRequestHandler
from html.parser import HTMLParser

PORT = 5000

LINK_HEADER = ', '.join([
    '</.well-known/api-catalog>; rel="api-catalog"',
    '</.well-known/agent-skills/index.json>; rel="https://agentskills.io/index"',
])


class _TextExtractor(HTMLParser):
    """Minimal HTML → Markdown converter for agent content negotiation."""
    SKIP = {'script', 'style', 'noscript', 'head', 'nav', 'footer',
            'header', 'aside', '.emergency-banner', '.top-bar', '.mobile-call-btn'}

    def __init__(self):
        super().__init__()
        self._stack = []
        self._skip_depth = 0
        self.chunks = []
        self._in_heading = None
        self._in_li = False
        self._in_strong = False

    def _skip_tag(self, tag):
        return tag in {'script', 'style', 'noscript', 'nav', 'footer',
                       'header', 'aside'}

    def handle_starttag(self, tag, attrs):
        self._stack.append(tag)
        if self._skip_depth or self._skip_tag(tag):
            self._skip_depth += 1
            return
        attrs_d = dict(attrs)
        cls = attrs_d.get('class', '')
        skip_classes = {'emergency-banner', 'top-bar', 'mobile-call-btn',
                        'site-header', 'site-footer', 'breadcrumb', 'sidebar-sticky'}
        if any(c in cls for c in skip_classes):
            self._skip_depth += 1
            return
        if tag in ('h1', 'h2', 'h3', 'h4'):
            level = int(tag[1])
            self._in_heading = '#' * level
            self.chunks.append('\n')
        elif tag == 'li':
            self._in_li = True
            self.chunks.append('\n- ')
        elif tag in ('strong', 'b'):
            self._in_strong = True
            self.chunks.append('**')
        elif tag in ('em', 'i'):
            self.chunks.append('_')
        elif tag == 'a':
            href = attrs_d.get('href', '')
            if href and not href.startswith('#'):
                self.chunks.append('[')
        elif tag == 'br':
            self.chunks.append('\n')
        elif tag in ('p', 'div', 'section', 'article', 'main'):
            self.chunks.append('\n')

    def handle_endtag(self, tag):
        if self._skip_depth:
            self._skip_depth -= 1
            if self._stack:
                self._stack.pop()
            return
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()
        if tag in ('h1', 'h2', 'h3', 'h4'):
            if self._in_heading:
                self.chunks.insert(
                    -1 if self.chunks else 0,
                    self._in_heading + ' '
                )
                self._in_heading = None
            self.chunks.append('\n')
        elif tag in ('strong', 'b'):
            self._in_strong = False
            self.chunks.append('**')
        elif tag in ('em', 'i'):
            self.chunks.append('_')
        elif tag == 'a':
            pass
        elif tag in ('p', 'li'):
            self._in_li = False
            self.chunks.append('\n')

    def handle_data(self, data):
        if self._skip_depth:
            return
        text = data.strip()
        if text:
            self.chunks.append(text + ' ')

    def get_markdown(self):
        md = ''.join(self.chunks)
        md = re.sub(r'\n{3,}', '\n\n', md)
        return md.strip()


def html_to_markdown(html_bytes: bytes, title: str = '') -> bytes:
    parser = _TextExtractor()
    try:
        parser.feed(html_bytes.decode('utf-8', errors='replace'))
    except Exception:
        pass
    md = parser.get_markdown()
    if title:
        md = f'# {title}\n\n' + md
    return md.encode('utf-8')


def _extract_title(html_bytes: bytes) -> str:
    m = re.search(rb'<title[^>]*>(.*?)</title>', html_bytes, re.I | re.S)
    if m:
        return html.unescape(m.group(1).decode('utf-8', errors='replace')).strip()
    return ''


class AgentReadyHandler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def end_headers(self):
        self.send_header('Link', LINK_HEADER)
        super().end_headers()

    def do_GET(self):
        accept = self.headers.get('Accept', '')
        if 'text/markdown' in accept:
            self._serve_markdown()
        else:
            super().do_GET()

    def do_HEAD(self):
        accept = self.headers.get('Accept', '')
        if 'text/markdown' in accept:
            self._serve_markdown(head_only=True)
        else:
            super().do_HEAD()

    def _resolve_path(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            for index in ('index.html', 'index.htm'):
                candidate = os.path.join(path, index)
                if os.path.exists(candidate):
                    return candidate
        if os.path.isfile(path):
            return path
        return None

    def _serve_markdown(self, head_only=False):
        fpath = self._resolve_path()
        if fpath is None or not fpath.endswith('.html'):
            super().do_GET()
            return
        try:
            with open(fpath, 'rb') as f:
                raw = f.read()
        except OSError:
            self.send_error(404)
            return
        title = _extract_title(raw)
        md = html_to_markdown(raw, title)
        self.send_response(200)
        self.send_header('Content-Type', 'text/markdown; charset=utf-8')
        self.send_header('Content-Length', str(len(md)))
        self.send_header('Vary', 'Accept')
        self.end_headers()
        if not head_only:
            self.wfile.write(md)

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    httpd = HTTPServer(('0.0.0.0', PORT), AgentReadyHandler)
    print(f'Tulsa Sewer & Drain serving on port {PORT}')
    httpd.serve_forever()
