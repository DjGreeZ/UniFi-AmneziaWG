"""Build the public GitHub Pages site using only Python's standard library."""
from pathlib import Path
from html import escape
import json
import re
import shutil
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE, OUT = ROOT / 'site', ROOT / 'docs'
CONFIG = json.loads((SOURCE / 'pages.json').read_text(encoding='utf-8'))
VERIFY = json.loads((SOURCE / 'verification.json').read_text(encoding='utf-8'))
BASE = CONFIG['base_url']
PREFIX = urlparse(BASE).path
REPO = 'https://github.com/DjGreeZ/UniFi-AmneziaWG'
VERSION = CONFIG['version']
AWG_VERSION = CONFIG['awg_config_version']
PAGES = CONFIG['pages']

def url(lang, key='home'):
    return BASE + ('en/' if lang == 'en' else '') + (key + '/' if key != 'home' else '')

def local(lang, key='home'):
    return urlparse(url(lang, key)).path

def render(lang, key, page):
    ru = lang == 'ru'
    canonical = url(lang, key)
    heading = escape(page['heading']).replace('\n', '<br>')
    nav = ''.join(f'<a href="{local(lang, k)}"' + (' aria-current="page"' if k == key else '') + f'>{escape(v[lang]["label"])}</a>' for k, v in PAGES.items())
    other = 'en' if ru else 'ru'
    language = f'<a class="language" href="{local(other, key)}" lang="{other}" hreflang="{other}" aria-label="' + ('Read this page in English' if ru else 'Читать страницу по-русски') + '">' + ('EN' if ru else 'RU') + '</a>'
    source = (SOURCE / 'content' / lang / (key + '.html')).read_text(encoding='utf-8')
    content = source.replace('{{base}}', PREFIX).replace('{{langbase}}', local(lang)).replace('{{version}}', VERSION).replace('{{awg_version}}', AWG_VERSION)
    project_id = BASE + '#project'
    schema = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'SoftwareSourceCode', '@id': project_id, 'name': 'UniFi-AmneziaWG',
         'description': PAGES['home'][lang]['description'], 'version': VERSION,
         'codeRepository': REPO, 'url': BASE, 'runtimePlatform': 'UniFi OS on ARM64 Linux',
         'programmingLanguage': ['Python', 'JavaScript', 'Shell'],
         'author': {'@type': 'Person', 'name': 'Roman Tselischev', 'alternateName': 'DjGreeZ', 'url': 'https://github.com/DjGreeZ'},
         'isBasedOn': {'@type': 'SoftwareApplication', 'name': 'AmneziaWG', 'url': 'https://github.com/amnezia-vpn/amneziawg-go'}},
        {'@type': 'WebPage', '@id': canonical + '#webpage', 'url': canonical, 'name': page['title'],
         'description': page['description'], 'inLanguage': lang, 'dateModified': CONFIG['updated'],
         'about': {'@id': project_id}}
    ]}
    if key != 'home':
        schema['@graph'].append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'UniFi-AmneziaWG', 'item': url(lang)},
            {'@type': 'ListItem', 'position': 2, 'name': page['label'], 'item': canonical}]})
    tags = ''.join(f'<meta name="{name}" content="{escape(VERIFY.get(key, ""), quote=True)}">\n' for key, name in [('google', 'google-site-verification'), ('yandex', 'yandex-verification')] if VERIFY.get(key))
    alternates = ''.join(f'<link rel="alternate" hreflang="{code}" href="{url(code, key)}">\n' for code in ['ru', 'en'])
    release = f'{REPO}/releases/tag/v{VERSION}'
    if key == 'home':
        main = f'''<main id="main"><section class="hero wrap">
          <div class="hero-copy"><p class="eyebrow"><span class="status-dot"></span> {'НЕЗАВИСИМЫЙ ПРОЕКТ ДЛЯ UNIFI' if ru else 'INDEPENDENT PROJECT FOR UNIFI'}</p>
          <h1>{heading}</h1><p class="hero-lead">{escape(page['lead'])}</p>
          <div class="actions"><a class="button primary" href="{local(lang, 'installation')}">{'Установить' if ru else 'Get started'} <span aria-hidden="true">↗</span></a><a class="button secondary" href="{REPO}">{'Код на GitHub' if ru else 'View on GitHub'} <span aria-hidden="true">↗</span></a></div>
          <p class="hero-note"><a href="{release}">v{VERSION}</a> · {'Тестовая версия' if ru else 'Experimental release'} · AWG {AWG_VERSION} · ARM64 · IPv4</p></div>
          <div class="hero-diagram" aria-label="{'Схема подключения' if ru else 'Connection overview'}"><div class="diagram-caption">{'МАРШРУТ ВАШЕГО ТРАФИКА' if ru else 'YOUR TRAFFIC, ROUTED'}</div>
          <div class="diagram-node"><span class="node-number">01</span><div><strong>UniFi</strong><small>{'Устройства и политики' if ru else 'Devices & routing policies'}</small></div><span class="node-icon" aria-hidden="true">↗</span></div>
          <div class="diagram-line"><span>LOCAL WIREGUARD</span></div>
          <div class="diagram-node active"><span class="node-number">02</span><div><strong>AmneziaWG</strong><small>{'Подключение на вашем шлюзе' if ru else 'Connection on your gateway'}</small></div><span class="node-icon" aria-hidden="true">⤴</span></div>
          <div class="diagram-line"><span>{'ОСНОВНОЙ / РЕЗЕРВ' if ru else 'PRIMARY / BACKUP'}</span></div>
          <div class="diagram-end"><span class="status-dot"></span> {'Ваш VPN-сервер' if ru else 'Your VPN server'}</div>
          <a class="diagram-link" href="{local(lang, 'architecture')}">{'Разобраться в устройстве' if ru else 'Explore the architecture'} <span aria-hidden="true">→</span></a></div>
        </section><div class="wrap home-content">{content}</div></main>'''
    else:
        toc = ''.join(f'<a href="#{ident}">{re.sub("<[^>]+>", "", text)}</a>' for ident, text in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', content))
        main = f'''<main id="main" class="wrap docs-layout"><aside class="docs-sidebar"><p class="eyebrow">{'ДОКУМЕНТАЦИЯ' if ru else 'DOCUMENTATION'}</p><nav aria-label="{'Разделы документации' if ru else 'Documentation sections'}">{nav}</nav><div class="sidebar-version">v{VERSION}<br><span>{'По исходникам релиза' if ru else 'Based on release source'}</span></div></aside><article class="article"><header class="article-header"><p class="eyebrow">UNIFI-AMNEZIAWG / {escape(page['label'].upper())}</p><h1>{heading}</h1><p class="lead">{escape(page['lead'])}</p><p class="updated">{'Проверено по исходникам' if ru else 'Source reviewed'} · <time datetime="{CONFIG['updated']}">{CONFIG['updated']}</time></p></header><nav class="toc" aria-label="{'На этой странице' if ru else 'On this page'}">{toc}</nav><div class="prose">{content}</div></article></main>'''
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(page['title'])}</title><meta name="description" content="{escape(page['description'], quote=True)}">
<meta name="theme-color" content="#f5f6f2"><link rel="canonical" href="{canonical}">
{alternates}<link rel="alternate" hreflang="x-default" href="{url('ru', key)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="UniFi-AmneziaWG"><meta property="og:locale" content="{'ru_RU' if ru else 'en_US'}">
<meta property="og:title" content="{escape(page['title'], quote=True)}"><meta property="og:description" content="{escape(page['description'], quote=True)}"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}assets/social.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="AmneziaWG for UniFi — native routing, failover, traffic statistics">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE}assets/social.png">
<link rel="icon" type="image/svg+xml" href="{PREFIX}assets/favicon.svg"><link rel="stylesheet" href="{PREFIX}assets/site.css">
{tags}<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')}</script><script src="{PREFIX}assets/site.js" defer></script>
</head><body><a class="skip-link" href="#main">{'К содержимому' if ru else 'Skip to content'}</a>
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="{local(lang)}" aria-label="UniFi-AmneziaWG {'главная' if ru else 'home'}"><span class="brand-mark" aria-hidden="true">a<span>↗</span></span><span>UniFi<span class="brand-slash">/</span>AmneziaWG</span></a><nav class="main-nav" aria-label="{'Основная навигация' if ru else 'Main navigation'}">{nav}</nav><div class="header-actions">{language}<a class="github-link" href="{REPO}" aria-label="GitHub repository">GitHub <span aria-hidden="true">↗</span></a></div></div></header>
<div class="protocol-notice"><div class="wrap"><strong>{'Требуется конфиг' if ru else 'Requires an'} AmneziaWG {AWG_VERSION} { 'в формате .conf.' if ru else '.conf configuration.'}</strong><span>{'Версия интеграции:' if ru else 'Integration version:'} {VERSION}.</span><a href="{local(lang, 'installation')}#config">{'Как получить конфиг' if ru else 'Get a configuration'} →</a></div></div>
{main}
<footer class="site-footer wrap"><div><a class="footer-brand" href="{local(lang)}">UniFi / AmneziaWG</a><p>{'Независимая интеграция. Не связана с Ubiquiti.' if ru else 'Independent integration. Not affiliated with Ubiquiti.'}</p><p>Developed by <a href="https://github.com/DjGreeZ">Roman Tselischev · DjGreeZ</a></p></div><nav aria-label="{'Дополнительные ссылки' if ru else 'More links'}"><a href="{release}">{'Релиз' if ru else 'Release'} v{VERSION}</a><a href="{REPO}/issues">{'Сообщить о проблеме' if ru else 'Report an issue'}</a><a href="{local(lang, 'citation')}">{'Как сослаться' if ru else 'How to cite'}</a></nav></footer>
</body></html>'''

def main():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(SOURCE / 'assets', OUT / 'assets', dirs_exist_ok=True)
    urls = []
    for lang in ['ru', 'en']:
        for key, translations in PAGES.items():
            path = OUT / ('en' if lang == 'en' else '') / (key if key != 'home' else '')
            path.mkdir(parents=True, exist_ok=True)
            (path / 'index.html').write_text(render(lang, key, translations[lang]), encoding='utf-8', newline='\n')
            urls.append(url(lang, key))
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += ''.join(f'  <url><loc>{escape(u)}</loc><lastmod>{CONFIG["updated"]}</lastmod></url>\n' for u in urls) + '</urlset>\n'
    (OUT / 'sitemap.xml').write_text(sitemap, encoding='utf-8', newline='\n')
    (OUT / '.nojekyll').write_text('', encoding='utf-8')
    (OUT / '404.html').write_text(f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>404 — UniFi-AmneziaWG</title><link rel="stylesheet" href="{PREFIX}assets/site.css"></head><body><main class="wrap not-found"><p class="eyebrow">404 / UNIFI-AMNEZIAWG</p><h1>Страница не найдена.<br>Page not found.</h1><p><a href="{PREFIX}">На главную</a> · <a href="{PREFIX}en/">English homepage</a></p></main></body></html>', encoding='utf-8', newline='\n')
    print(f'Built {len(urls)} pages + 404, sitemap and assets in {OUT}')

if __name__ == '__main__':
    main()
