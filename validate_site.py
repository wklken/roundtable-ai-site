"""Validate localized pages as a public website, including links and accessibility references."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from localize import BASE, LANGUAGES

ROOT = Path(__file__).parent / 'docs'

class Page(HTMLParser):
 def __init__(self, path):
  super().__init__()
  self.path, self.links, self.ids, self.refs, self.options = path, [], set(), [], []
  self.lang = None
  self.selected = []
  self.alternates = set()
 def handle_starttag(self, tag, attrs):
  a = dict(attrs)
  if tag == 'html': self.lang = a['lang']
  if 'id' in a:
   assert a['id'] not in self.ids, (self.path, 'duplicate ID', a['id'])
   self.ids.add(a['id'])
  for name in ['aria-controls', 'aria-labelledby']:
   self.refs.extend(a.get(name, '').split())
  for name in ['href', 'src', 'data-url']:
   if a.get(name): self.links.append(a[name])
  if tag == 'option':
   self.options.append(a['value'])
   if 'selected' in a: self.selected.append(a['value'])
  if tag == 'link' and a.get('rel') == 'alternate': self.alternates.add(a['hreflang'])

pages = {}
for path in ROOT.rglob('*.html'):
 page = Page(path)
 page.feed(path.read_text())
 pages[path.resolve()] = page
assert len(pages) == len(LANGUAGES) * 4, len(pages)
for path, page in pages.items():
 relative = path.relative_to(ROOT.resolve())
 expected_lang = relative.parts[0] if relative.parts[0] in LANGUAGES else 'en'
 assert page.lang == expected_lang, (path, page.lang)
 assert page.selected == [expected_lang], path
 assert set(page.options) == set(LANGUAGES), path
 assert page.alternates == set(LANGUAGES) | {'x-default'}, path
 assert set(page.refs) <= page.ids, (path, 'broken ARIA reference')
 for link in page.links:
  parts = urlsplit(link)
  if parts.scheme or parts.netloc: continue
  if parts.path:
   assert parts.path.startswith(BASE), (path, link)
   target = ROOT / unquote(parts.path[len(BASE):])
   if target.is_dir(): target /= 'index.html'
  else: target = path
  assert target.is_file(), (path, link)
  if parts.fragment:
   assert parts.fragment in pages[target.resolve()].ids, (path, link, 'missing anchor')
assert (ROOT/'assets/pilot-discussion.jpg').read_bytes() == (ROOT.parent/'assets/pilot-discussion.jpg').read_bytes()
print(f'PASS: {len(pages)} pages, {len(LANGUAGES)} languages, selected locale, internal links/assets, anchors and ARIA references; screenshot unchanged.')
