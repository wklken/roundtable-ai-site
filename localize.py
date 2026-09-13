"""Build complete, shareable translations of the four static website pages."""
import json
from html import escape
from html.parser import HTMLParser
from pathlib import Path

SOURCE = Path(__file__).parent
ROOT = SOURCE / 'docs'
BASE = '/roundtable-ai-site/'
ORIGIN = 'https://wklken.me'
LANGUAGES = {'en': 'English', 'zh-Hans': '简体中文', 'zh-Hant': '繁體中文', 'ja': '日本語', 'ko': '한국어', 'de': 'Deutsch', 'fr': 'Français', 'es': 'Español'}
# Brand names, numbers, speaker initials and symbols do not require translation.
INVARIANT = {2, 12, 22, 25, 28, 33, 39, 41, 44, 47, 51, 103, 108, 143, 147}
LABELS = {
 'en': ['Language', 'Main navigation', 'Little Roundtable home', 'Discussion stages', 'Illustrative decision report', 'Little Roundtable app icon'],
 'zh-Hans': ['语言', '主导航', 'Little Roundtable 首页', '讨论阶段', '决策报告示例', 'Little Roundtable 应用图标'],
 'zh-Hant': ['語言', '主要導覽', 'Little Roundtable 首頁', '討論階段', '決策報告範例', 'Little Roundtable App 圖示'],
 'ja': ['言語', 'メインナビゲーション', 'Little Roundtable ホーム', '議論の段階', '意思決定レポートの例', 'Little Roundtable アプリアイコン'],
 'ko': ['언어', '주 탐색', 'Little Roundtable 홈', '토론 단계', '의사결정 보고서 예시', 'Little Roundtable 앱 아이콘'],
 'de': ['Sprache', 'Hauptnavigation', 'Little Roundtable Startseite', 'Diskussionsphasen', 'Beispielhafter Entscheidungsbericht', 'Little Roundtable App-Symbol'],
 'fr': ['Langue', 'Navigation principale', 'Accueil Little Roundtable', 'Étapes de discussion', 'Exemple de rapport de décision', 'Icône de Little Roundtable'],
 'es': ['Idioma', 'Navegación principal', 'Inicio de Little Roundtable', 'Etapas de la conversación', 'Ejemplo de informe de decisión', 'Icono de Little Roundtable'],
}


def prefix(lang):
 return BASE if lang == 'en' else BASE + lang + '/'


def catalog(lang, english):
 if lang == 'en':
  return {text: text for text in english}
 entries = {}
 for line in (SOURCE / 'locales' / (lang + '.txt')).read_text().splitlines():
  if not line.strip():
   continue
  key, value = line.split('|', 1)
  index = int(key)
  if index in entries or not value.strip():
   raise ValueError(f'{lang}: duplicate or empty translation {index}')
  entries[index] = value
 missing = set(range(len(english))) - entries.keys() - INVARIANT
 extra = entries.keys() - set(range(len(english)))
 if missing or extra:
  raise ValueError(f'{lang}: missing={sorted(missing)}, extra={sorted(extra)}')
 return {text: entries.get(index, text) for index, text in enumerate(english)}


class LocalizedHTML(HTMLParser):
 def __init__(self, lang, route, translations, english):
  super().__init__(convert_charrefs=True)
  self.lang, self.route, self.translations = lang, route, translations
  self.output = []
  self.attr_text = dict(zip(['Main navigation', 'Main', 'Little Roundtable home', 'Discussion stages', 'Illustrative decision report', 'Little Roundtable app icon'], [LABELS[lang][1], LABELS[lang][1], *LABELS[lang][2:]]))
  self.description = translations[english[9]] + ' ' + translations[english[10]]
  self.image_alt = translations[english[13]]

 def handle_decl(self, decl):
  self.output.append('<!' + decl + '>')

 def handle_starttag(self, tag, attrs):
  attrs = dict(attrs)
  if tag == 'html':
   attrs.update(lang=self.lang, **{'data-locale': self.lang, 'data-route': self.route})
  if tag == 'meta' and attrs.get('name') == 'description':
   attrs['content'] = self.description if not self.route else self.translations[{'support/':'Support', 'privacy/':'Privacy policy', 'terms/':'Terms of use'}[self.route]] + ' — Little Roundtable'
  if tag == 'meta' and attrs.get('name') == 'theme-color':
   attrs['content'] = '#fcfaef'
  if tag == 'link' and attrs.get('rel') == 'canonical':
   attrs['href'] = ORIGIN + prefix(self.lang) + self.route
  href = attrs.get('href', '')
  if tag == 'a' and href.startswith(BASE):
   attrs['href'] = prefix(self.lang) + href[len(BASE):]
  for attr in ['aria-label', 'alt', 'title']:
   if attrs.get(attr) in self.attr_text:
    attrs[attr] = self.attr_text[attrs[attr]]
   elif attr == 'alt' and attrs.get(attr, '').startswith('Little Roundtable on Mac:'):
    attrs[attr] = self.image_alt
  self.output.append('<' + tag + ''.join(' ' + key + ('="' + escape(value, quote=True) + '"' if value is not None else '') for key, value in attrs.items()) + '>')

 def handle_endtag(self, tag):
  if tag == 'head':
   if self.route:
    self.output.append('<link rel="canonical" href="' + ORIGIN + prefix(self.lang) + self.route + '">')
   for lang in LANGUAGES:
    self.output.append(f'<link rel="alternate" hreflang="{lang}" href="{ORIGIN}{prefix(lang)}{self.route}">')
   self.output.append(f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{BASE}{self.route}"><link rel="stylesheet" href="{BASE}site.css"><script src="{BASE}language.js" defer></script>')
  if tag == 'nav':
   label = LABELS[self.lang][0]
   self.output.append('<label class="language-picker"><span class="sr-only">' + label + '</span><select id="site-language" aria-label="' + label + '">')
   for lang, name in LANGUAGES.items():
    selected = ' selected' if lang == self.lang else ''
    self.output.append(f'<option value="{lang}" data-url="{prefix(lang)}{self.route}"{selected}>{name}</option>')
   self.output.append('</select></label><noscript><div class="language-links">')
   for lang, name in LANGUAGES.items():
    self.output.append(f'<a lang="{lang}" href="{prefix(lang)}{self.route}">{name}</a> ')
   self.output.append('</div></noscript>')
  self.output.append('</' + tag + '>')

 def handle_data(self, data):
  text = data.strip()
  if not text:
   self.output.append(data)
   return
  if text not in self.translations:
   raise ValueError(f'Uncatalogued text: {text}')
  leading = data[:len(data) - len(data.lstrip())]
  trailing = data[len(data.rstrip()):]
  self.output.append(leading + escape(self.translations[text]) + trailing)

 def handle_comment(self, text):
  self.output.append('<!--' + text + '-->')


def build():
 english = json.loads((SOURCE / 'locales/en.json').read_text())
 # Read all English inputs before writing any localized output.
 pages = {route: (ROOT / route / 'index.html').read_text() for route in ['', 'support/', 'privacy/', 'terms/']}
 for lang in LANGUAGES:
  translations = catalog(lang, english)
  for route, html in pages.items():
   parser = LocalizedHTML(lang, route, translations, english)
   parser.feed(html)
   folder = ROOT / (lang if lang != 'en' else '') / route
   folder.mkdir(parents=True, exist_ok=True)
   (folder / 'index.html').write_text(''.join(parser.output))
 print(f'Built {len(pages) * len(LANGUAGES)} pages in {len(LANGUAGES)} languages; all translation keys present.')

if __name__ == '__main__':
 build()
