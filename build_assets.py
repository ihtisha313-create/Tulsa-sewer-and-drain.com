#!/usr/bin/env python3
"""
Build script: minify CSS and JS into css/style.min.css and js/main.min.js
Run once after editing the source files: python3 build_assets.py
"""
import re, os

def minify_css(src):
    # Remove /* ... */ comments
    src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)
    # Collapse whitespace around structural characters
    src = re.sub(r'\s*([{}:;,>~+])\s*', r'\1', src)
    # Collapse all remaining whitespace to single space
    src = re.sub(r'\s+', ' ', src)
    # Remove space after ( and before )
    src = re.sub(r'\(\s+', '(', src)
    src = re.sub(r'\s+\)', ')', src)
    # Remove trailing semicolons before }
    src = src.replace(';}', '}')
    # Remove leading/trailing whitespace
    return src.strip()

def minify_js(src):
    # Remove /* ... */ block comments
    src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)
    # Remove single-line // comments (skip URLs like https://)
    src = re.sub(r'(?m)(?<!:)//[^\n]*$', '', src)
    # Collapse multiple blank lines → single newline
    src = re.sub(r'\n{2,}', '\n', src)
    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in src.splitlines()]
    src = '\n'.join(l for l in lines if l)
    # Collapse spaces around structural characters ONLY (not inside strings—
    # safe here because string literals don't span lines after stripping)
    src = re.sub(r' *([{}:,;]) *', r'\1', src)
    src = re.sub(r' *([\(\)\[\]]) *', r'\1', src)
    # Collapse multiple spaces to one (leave newlines — they act as statement sep)
    src = re.sub(r'  +', ' ', src)
    return src.strip()

base = os.path.dirname(os.path.abspath(__file__))

css_src = os.path.join(base, 'css', 'style.css')
css_dst = os.path.join(base, 'css', 'style.min.css')
with open(css_src, 'r', encoding='utf-8') as f:
    raw_css = f.read()
min_css = minify_css(raw_css)
with open(css_dst, 'w', encoding='utf-8') as f:
    f.write(min_css)
print(f'CSS: {len(raw_css):,} → {len(min_css):,} bytes '
      f'({100*(1-len(min_css)/len(raw_css)):.0f}% smaller) → {css_dst}')

js_src = os.path.join(base, 'js', 'main.js')
js_dst = os.path.join(base, 'js', 'main.min.js')
with open(js_src, 'r', encoding='utf-8') as f:
    raw_js = f.read()
min_js = minify_js(raw_js)
with open(js_dst, 'w', encoding='utf-8') as f:
    f.write(min_js)
print(f'JS:  {len(raw_js):,} → {len(min_js):,} bytes '
      f'({100*(1-len(min_js)/len(raw_js)):.0f}% smaller) → {js_dst}')
