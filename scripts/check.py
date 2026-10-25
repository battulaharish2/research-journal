"""Check rendered links, gallery coverage and stripped photo metadata."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = []
        self.photo_buttons = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ['href', 'src']:
            if a.get(key): self.links.append(a[key])
        if a.get('id'): self.ids.append(a['id'])
        if 'data-photo' in a: self.links.append(a['data-photo']); self.photo_buttons += 1

posts = json.loads((ROOT / 'content/posts.json').read_text(encoding='utf-8'))
total = 0
for page in OUT.rglob('*.html'):
    parser = Links()
    parser.feed(page.read_text(encoding='utf-8'))
    assert len(parser.ids) == len(set(parser.ids)), f'Duplicate IDs in {page}'
    total += parser.photo_buttons
    for href in parser.links:
        url = urlsplit(href)
        if url.scheme or url.netloc: continue
        target = (page.parent / unquote(url.path)).resolve() if url.path else page.resolve()
        assert target.is_relative_to(OUT.resolve()), href
        assert target.exists(), (page, href)
        if url.fragment:
            check = Links(); check.feed(target.read_text(encoding='utf-8'))
            assert url.fragment in check.ids, (page, href)
images = list((OUT / 'images').rglob('*.webp'))
assert total == len(images) == 30
for image in images:
    with Image.open(image) as im:
        assert not im.getexif(), image
        assert max(im.size) <= 1600
assert len(posts) == 2
research_page = OUT / 'learning-from-heart-sounds/index.html'
research = Links(); research.feed(research_page.read_text(encoding='utf-8'))
home = Links(); home.feed((OUT / 'index.html').read_text(encoding='utf-8'))
assert './learning-from-heart-sounds/index.html' in home.links
assert research.photo_buttons == 0
assert 'Ongoing research' in research_page.read_text(encoding='utf-8')
print(f'PASS: {len(list(OUT.rglob("*.html")))} pages; research entry linked; all local links and anchors; 30 gallery photos; no image EXIF; bounded dimensions.')
