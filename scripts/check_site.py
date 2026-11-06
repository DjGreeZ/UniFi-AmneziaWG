"""Validate generated HTML, internal links, translations and search metadata."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, urljoin, unquote
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
CONFIG = json.loads((ROOT / 'site/pages.json').read_text(encoding='utf-8'))
BASE = CONFIG['base_url']
PREFIX = urlparse(BASE).path
ERRORS = []

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.links, self.images = path, set(), [], []
        self.canonical, self.alternates, self.metadata = [], {}, {}
        self.h1, self.lang, self.title, self.schemas = 0, '', '', []
        self.in_title, self.in_schema, self.buffer = False, False, ''
        raw = path.read_text(encoding='utf-8')
        if re.search(r'\{\{[a-z_]+\}\}', raw):
            ERRORS.append(f'{path}: unresolved template placeholder')
        self.feed(raw)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:
                ERRORS.append(f'{self.path}: duplicate id {a["id"]}')
            self.ids.add(a['id'])
        if tag == 'html': self.lang = a.get('lang', '')
        if tag == 'h1': self.h1 += 1
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        if tag in ('script', 'img') and a.get('src'): self.links.append(a['src'])
        if tag == 'img':
            self.images.append(a)
            if not a.get('alt'): ERRORS.append(f'{self.path}: image has no alt text')
        if tag == 'link':
            if a.get('rel') == 'canonical': self.canonical.append(a.get('href'))
            if a.get('rel') == 'alternate': self.alternates[a.get('hreflang')] = a.get('href')
            if a.get('rel') in ('stylesheet', 'icon'): self.links.append(a['href'])
        if tag == 'meta': self.metadata[a.get('name', a.get('property'))] = a.get('content', '')
        if tag == 'title': self.in_title = True
        if tag == 'script' and a.get('type') == 'application/ld+json': self.in_schema, self.buffer = True, ''

    def handle_data(self, data):
        if self.in_title: self.title += data
        if self.in_schema: self.buffer += data

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag == 'script' and self.in_schema:
            try: self.schemas.append(json.loads(self.buffer))
            except ValueError: ERRORS.append(f'{self.path}: invalid JSON-LD')
            self.in_schema = False

pages = {path.resolve(): Page(path) for path in DOCS.rglob('*.html')}
canonicals, titles = set(), set()
for path, page in pages.items():
    is_404 = path.name == '404.html'
    relative = path.relative_to(DOCS).as_posix()
    page_url = BASE + (relative[:-10] if relative.endswith('index.html') else relative)
    if page.h1 != 1: ERRORS.append(f'{relative}: expected one h1')
    if page.lang not in ('ru', 'en'): ERRORS.append(f'{relative}: invalid language')
    if not page.title: ERRORS.append(f'{relative}: missing title')
    if not is_404:
        if page.canonical != [page_url]: ERRORS.append(f'{relative}: incorrect canonical {page.canonical}')
        if page_url in canonicals: ERRORS.append(f'{relative}: duplicate canonical')
        canonicals.add(page_url)
        if page.title in titles: ERRORS.append(f'{relative}: duplicate title')
        titles.add(page.title)
        if not page.metadata.get('description'): ERRORS.append(f'{relative}: missing description')
        if not page.schemas: ERRORS.append(f'{relative}: missing structured data')
        if set(page.alternates) != {'ru', 'en', 'x-default'}: ERRORS.append(f'{relative}: missing language alternates')
        if page.alternates.get(page.lang) != page_url: ERRORS.append(f'{relative}: missing self hreflang')
        if page.metadata.get('og:url') != page_url: ERRORS.append(f'{relative}: incorrect og:url')
        page.links.extend(page.alternates.values())
        page.links.append(page.metadata.get('og:image', ''))
    for link in page.links:
        absolute = urlparse(urljoin(page_url, link))
        if absolute.netloc != urlparse(BASE).netloc: continue
        if not absolute.path.startswith(PREFIX):
            ERRORS.append(f'{relative}: link escapes project Pages prefix: {link}')
            continue
        target = DOCS / unquote(absolute.path[len(PREFIX):])
        if absolute.path.endswith('/'): target /= 'index.html'
        if not target.is_file():
            ERRORS.append(f'{relative}: missing target {link}')
        elif absolute.fragment and target.suffix == '.html':
            other = pages.get(target.resolve())
            if not other or unquote(absolute.fragment) not in other.ids:
                ERRORS.append(f'{relative}: missing anchor {link}')
        if link in page.alternates.values() and target.resolve() in pages:
            if pages[target.resolve()].alternates != page.alternates:
                ERRORS.append(f'{relative}: nonreciprocal hreflang {link}')

sitemap = ET.parse(DOCS / 'sitemap.xml')
locations = {node.text for node in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
if locations != canonicals: ERRORS.append('Sitemap does not match canonical pages')
if len(canonicals) != len(CONFIG['pages']) * 2: ERRORS.append('Unexpected number of pages')
if not (DOCS / '.nojekyll').is_file(): ERRORS.append('Missing .nojekyll')
if ERRORS:
    print('\n'.join(ERRORS))
    sys.exit(1)
print(f'PASS: {len(canonicals)} pages; links, anchors, assets, canonical URLs, reciprocal hreflang, JSON-LD and sitemap.')
