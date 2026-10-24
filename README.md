# Harish Battula — research & conference journal

Personal research website with two conference stories and 30 photographs. Public site: https://battulaharish2.github.io/research-journal/. Profile and publication titles come from the supplied CV; conference reflections come from the owner's notes. No phone number, private email, employer details or CV download is included.

## Update a story

Edit `content/posts.json`: change the title, summary, paragraphs and captions. Each paragraph is plain text. Add a post by copying an entry, giving it a unique lowercase slug and the name of a folder directly inside `../Photos`. The cover must be an existing JPG filename. Rebuild to update the pages.

The source photos remain untouched. The build makes smaller WebP copies with orientation applied and original EXIF/GPS metadata omitted. Generic captions are used where individual details have not been provided. Review them before publication.

## Build and preview

Requires Python 3 and Pillow (`python -m pip install Pillow`). From this directory:

```text
python scripts/build.py
python scripts/check.py
python -m http.server 4181 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:4181. The `dist` folder is a complete static website for GitHub Pages. Keep paths relative so it also works under a repository subpath. No framework, account system, tracking, external fonts or server-side storage is needed. Photo viewer supports Escape, arrow keys and labelled buttons. Photos also remain visible with JavaScript disabled.

GitHub Actions publishes the checked-in `dist` folder on pushes to main. After editing text or source styles, run the build and checks, then commit both the source changes and regenerated `dist`. The original images are outside this project; a fresh source checkout needs those folders to rebuild. The generated `dist` is self-contained.
