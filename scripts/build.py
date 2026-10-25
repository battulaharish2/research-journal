"""Build the static profile and conference journals; originals remain untouched."""
import json
import re
from html import escape as e
from pathlib import Path
from shutil import copy2
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
PHOTOS = ROOT.parent / 'Photos'

def page(title, body, prefix='./', gallery=False):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Harish Battula — speech, physiological signals and machine learning. Research, projects and conference journals."><meta name="referrer" content="no-referrer"><title>{e(title)} · Harish Battula</title><link rel="stylesheet" href="{prefix}styles.css">{f'<script defer src="{prefix}gallery.js"></script>' if gallery else ''}</head><body><a class="skip" href="#main">Skip to content</a><header><a class="brand" href="{prefix}index.html">Harish Battula<span>.</span></a><nav aria-label="Main navigation"><a href="{prefix}index.html#research">Research</a><a href="{prefix}index.html#projects">Projects</a><a href="{prefix}index.html#journal">Journal</a><a href="{prefix}index.html#about">About</a></nav></header><main id="main">{body}</main><footer><span>Harish Battula · Research &amp; life along the way.</span><span>Personal website · Photographs from my conference travels.</span></footer></body></html>'''

def build_research():
    title = 'Learning from Heart Sounds'
    summary = 'Interpretable acoustic patterns, measurement uncertainty, and generalization across recording conditions.'
    text = (ROOT / 'content/heart-sounds.html').read_text(encoding='utf-8')
    body = f'''<div class="article-head"><a class="back" href="../index.html#research">← Back to research</a><p class="eyebrow">Ongoing research / Biomedical signal analysis</p><h1>{title}</h1><p class="lead">I am exploring whether heart sounds offer useful clues about cardiovascular health.</p></div><article class="article-copy">{text}</article>'''
    folder = OUT / 'learning-from-heart-sounds'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'index.html').write_text(page(title, body, '../'), encoding='utf-8')
    return f'''<div class="publication"><small>Ongoing research</small><h3><a href="./learning-from-heart-sounds/index.html">{title}</a></h3><p>{summary}</p><a class="text-link" href="./learning-from-heart-sounds/index.html">Read the research note ↗</a></div>'''


def build():
    OUT.mkdir(exist_ok=True)
    for p in (ROOT / 'public').iterdir():
        copy2(p, OUT / p.name)
    posts = json.loads((ROOT / 'content/posts.json').read_text(encoding='utf-8'))
    slugs = set()
    for post in posts:
        slug = post['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs:
            raise ValueError('Post slugs must be unique lowercase URL names.')
        slugs.add(slug)
        source = (PHOTOS / post['folder']).resolve()
        if source.parent != PHOTOS.resolve():
            raise ValueError('Photo folders must be directly inside Photos.')
        files = sorted(source.glob('*.jpg'))
        if not files or post['cover'] not in [p.name for p in files]:
            raise ValueError(f'Missing photos or cover for {slug}.')
        post['count'] = len(files)
        assets = OUT / 'images' / slug
        assets.mkdir(parents=True, exist_ok=True)
        figures = []
        for i, p in enumerate(files):
            name = p.stem + '.webp'
            with Image.open(p) as original:
                image = ImageOps.exif_transpose(original).convert('RGB')
                image.thumbnail((1600, 1600))
                # New pixel image prevents source EXIF/GPS metadata from propagating.
                clean = Image.new('RGB', image.size)
                clean.paste(image)
                clean.save(assets / name, 'WEBP', quality=82, method=4)
                width, height = clean.size
            caption = post.get('captions', {}).get(p.name, f"{post['conference']} and travel collection · photograph {i + 1}.")
            src = f'../images/{slug}/{name}'
            figures.append(f'<figure><button class="photo-button" data-photo="{src}" data-caption="{e(caption, quote=True)}" aria-label="Enlarge: {e(caption, quote=True)}"><img src="{src}" alt="{e(caption, quote=True)}" width="{width}" height="{height}" loading="lazy"></button><figcaption>{e(caption)}</figcaption></figure>')
        post['cover_url'] = f"images/{slug}/{Path(post['cover']).stem}.webp"
        text = ''.join(f'<p>{e(p)}</p>' for p in post['paragraphs'])
        pending = '<p class="pending">A photo journal; personal reflections will be added here.</p>' if post.get('story_pending') else ''
        body = f'''<div class="article-head"><a class="back" href="../index.html#journal">← Back to the journal</a><p class="eyebrow">{e(post['conference'])} / {e(post['location'])}</p><h1>{e(post['title'])}</h1><p class="lead">{e(post['summary'])}</p><span class="eyebrow">{e(post['year'])} · {len(files)} photographs</span></div><article class="article-copy">{text}{pending}</article><section class="gallery" aria-label="Conference and travel photographs">{''.join(figures)}</section><dialog aria-label="Photo viewer"><img alt=""><p></p><div class="controls"><button data-prev aria-label="Previous photograph">← Previous</button><span data-count aria-live="polite"></span><button data-next aria-label="Next photograph">Next →</button><button data-close>Close ×</button></div></dialog>'''
        folder = OUT / slug
        folder.mkdir(exist_ok=True)
        (folder / 'index.html').write_text(page(post['conference'], body, '../', True), encoding='utf-8')
    cards = ''.join(f'''<a class="journal" href="./{p['slug']}/index.html"><img src="./{p['cover_url']}" alt="{e(p['conference'])} research poster photograph" width="800" height="600" loading="lazy"><div class="meta">{e(p['conference'])} · {e(p['year'])} / {p['count']} PHOTOGRAPHS</div><h3>{e(p['title'])}</h3><p>{e(p['summary'])}</p><span class="text-link">Read the journal ↗</span></a>''' for p in posts)
    research = build_research()
    publications = [
        ('EUSIPCO 2026', "Alzheimer’s Dementia Detection from Spontaneous Speech Using Graph Neural Networks"),
        ('INTERSPEECH 2025', 'Heart Rate as a Proxy Measure to Assess Human Confidence in Spoken Speech'),
        ('EUSIPCO 2024', 'Heart Rate from Read-Speech Influenced by Physical Exercise'),
        ('IEEE I&CPS 2023', 'A Comparative Study of Forecasting Problems on Electrical Load Timeseries Data using Deep Learning Techniques')
    ]
    papers = ''.join(f'<div class="publication"><small>{e(venue)}</small><h3>{e(title)}</h3></div>' for venue, title in publications)
    body = f'''<section class="hero"><div><span class="eyebrow">Research / Signal processing / Field notes</span><h1>Signals, stories,<br>and the places<br>between.</h1><p class="lead">I’m Harish. I work with speech, physiological signals and machine learning.</p><p>This is where I share my research, the tools I build, and experiences from conferences and the journeys around them.</p><a class="button" href="#research">Explore my research ↗</a><a class="text-link" href="#journal">Read the journal</a></div><figure><img src="./images/eusipco-2024/20240829_114053.webp" alt="Research poster photograph from EUSIPCO 2024" width="700" height="900" fetchpriority="high"><figcaption>EUSIPCO 2024 · Lyon, France · A moment at the poster.</figcaption></figure></section><section class="section" id="journal"><div class="section-heading"><div><span class="eyebrow">01 / Beyond the paper</span><h2>The conference journal.</h2></div><p>The venue, the poster conversations, the feedback — and a little exploring afterward.</p></div><div class="journals">{cards}</div></section><section class="section" id="research"><div class="research-grid"><div><span class="eyebrow">02 / Research</span><h2>Listening for<br>useful patterns.</h2><p>My work spans speech and physiological sensing, neurological speech analysis and time-series modelling. I’m interested in how signals and learned representations can help us study health.</p><a class="text-link" href="https://scholar.google.com/citations?user=jEgWu88AAAAJ">View Google Scholar ↗</a></div><div>{research}{papers}</div></div></section><section class="section" id="projects"><span class="eyebrow">03 / Open tools</span><h2>Research you can try.</h2><div class="project"><div class="signal" aria-hidden="true">∿</div><div><span class="eyebrow">Interactive signal lab</span><h3>Signal Explorer</h3><p>A first look at speech, audio, ECG, PPG, PCG and EEG. Explore real examples, compare waveforms and spectra, or open your own recording locally in your browser.</p><a class="button" href="https://battulaharish2.github.io/signal-explorer/">Open the demo ↗</a><a class="text-link" href="https://github.com/battulaharish2/signal-explorer">Source on GitHub</a></div></div></section><section class="section" id="about"><div class="about"><span class="eyebrow">04 / A little background</span><h2>Research is also<br>about the conversations.</h2><p>I hold an M.Tech. in Electrical Engineering from NIT Warangal. My research experience includes speech processing, physiological sensing, graph representations of speech and machine learning for healthcare.</p><p>Conferences are an opportunity to explain a paper, work through questions and hear different perspectives. The discussions around my poster — and the input and feedback people shared — were among the most enjoyable parts of these trips.</p><a class="text-link" href="https://www.linkedin.com/in/harish-battula-a441a0126/">LinkedIn ↗</a> &nbsp; <a class="text-link" href="https://github.com/battulaharish2">GitHub ↗</a></div></section>'''
    (OUT / 'index.html').write_text(page('Research & conference journal', body), encoding='utf-8')
    (OUT / '.nojekyll').touch()
    print(f'Built {len(posts)} journals and {sum(p["count"] for p in posts)} photographs in {OUT}')

if __name__ == '__main__':
    build()
