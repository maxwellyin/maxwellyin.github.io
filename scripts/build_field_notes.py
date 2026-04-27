from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent.parent
FIELD_NOTES_DIR = ROOT / "field-notes"
PREVIEWS_DIR = FIELD_NOTES_DIR / "previews"
ARTICLES_DIR = FIELD_NOTES_DIR / "articles"
ASSETS_DIR = FIELD_NOTES_DIR / "assets"
IMAGE_DIR = ASSETS_DIR / "article-images"
CSS_PATH = FIELD_NOTES_DIR / "blog.css"


@dataclass(frozen=True)
class ArticleConfig:
    slug: str
    source_path: str
    preview: str
    title: str
    subtitle: str
    description: str
    summary: str
    published: str
    reading_note: str
    tags: tuple[str, ...]
    drop_headings: tuple[str, ...] = ()


ARTICLES = (
    ArticleConfig(
        slug="trm-recursive-reasoning",
        source_path="/Users/maxwellyin/Library/Mobile Documents/com~apple~CloudDocs/document/job application/产出积累/1.TRM.pdf",
        preview="trm-recursive-reasoning-report.png",
        title="Less Is More: Recursive Reasoning with Tiny Networks",
        subtitle="Reproduction and analysis notes on TRM, HRM simplification, and why deep supervision matters more than architectural ornament.",
        description="Full HTML edition of the TRM reproduction and analysis report by Maxwell J. Yin.",
        summary="A compact recursive architecture can go surprisingly far when training dynamics are explicit. This note reconstructs the Tiny Recursive Model, compares it against HRM, and examines which pieces actually drive reasoning performance.",
        published="April 2026",
        reading_note="Reconstructed from the original PDF and reorganized into a web article.",
        tags=("Recursive Reasoning", "TRM", "HRM", "Reproduction"),
        drop_headings=("Reproduction and Analysis Report",),
    ),
    ArticleConfig(
        slug="glyph-visual-compression",
        source_path="/Users/maxwellyin/Library/Mobile Documents/com~apple~CloudDocs/document/job application/产出积累/2.glyph.pdf",
        preview="glyph-visual-compression-study.png",
        title="A Study of Long-Context Modeling through Visual Compression",
        subtitle="Reproducing Glyph and situating it against DeepSeek-OCR and the broader shift toward denser input representations.",
        description="Full HTML edition of the Glyph visual compression study by Maxwell J. Yin.",
        summary="Instead of endlessly stretching attention, Glyph and related systems redesign the input channel itself. This article follows that thread from DeepSeek-OCR to Glyph and walks through the reproduced experiments.",
        published="April 2026",
        reading_note="Reconstructed from the original PDF and reorganized into a web article.",
        tags=("Long Context", "Glyph", "Visual Compression", "VLM Systems"),
    ),
    ArticleConfig(
        slug="long-context-architecture-analysis",
        source_path="/Users/maxwellyin/Library/Mobile Documents/com~apple~CloudDocs/document/job application/产出积累/3.LongContext_Reasoning_LLM_Architecture_Analysis.pdf",
        preview="long-context-reasoning-architecture-analysis.png",
        title="A Comparative Analysis of Large-Model Architectures for Long Context and Reasoning",
        subtitle="A system-oriented survey of dense transformers, hybrid attention, MoE, token compression, and diffusion LLM tradeoffs.",
        description="Full HTML edition of the long-context and reasoning architecture analysis by Maxwell J. Yin.",
        summary="When long-context reasoning becomes a deployment requirement, architecture choice stops being academic. This note compares the main model families through the lenses of capability, throughput, memory, and serving realism.",
        published="April 2026",
        reading_note="Reconstructed from the original PDF and reorganized into a web article.",
        tags=("Architecture Analysis", "Reasoning", "Inference Systems", "Model Tradeoffs"),
    ),
)


BLOG_CSS = """
:root {
  --bg: #f4f6fb;
  --surface: rgba(255, 255, 255, 0.92);
  --surface-strong: #ffffff;
  --text: #152031;
  --muted: #5f6b7d;
  --accent: #0f766e;
  --accent-dark: #115e59;
  --accent-soft: #ecfeff;
  --border: rgba(148, 163, 184, 0.22);
  --shadow: 0 28px 70px rgba(15, 23, 42, 0.12);
  --max: 1180px;
  --copy: 760px;
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at top left, rgba(15, 118, 110, 0.13), transparent 24%),
    radial-gradient(circle at top right, rgba(15, 23, 42, 0.11), transparent 18%),
    linear-gradient(180deg, #fbfcfe 0%, var(--bg) 100%);
  line-height: 1.72;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  color: var(--accent-dark);
  text-decoration: underline;
}

header {
  color: white;
  background: linear-gradient(125deg, rgba(15, 23, 42, 0.97) 0%, rgba(17, 94, 89, 0.94) 48%, rgba(15, 118, 110, 0.88) 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.header-inner,
.page-shell,
.footer-inner {
  max-width: calc(var(--max) + 32px);
  margin: 0 auto;
  padding-left: 16px;
  padding-right: 16px;
}

.header-inner {
  padding-top: 38px;
  padding-bottom: 38px;
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.brand {
  color: white;
  font-weight: 760;
  letter-spacing: 0.2px;
}

.nav-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.nav-links a {
  color: #d7f7f3;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  padding: 7px 13px;
  font-weight: 600;
  font-size: 0.95rem;
}

.nav-links a:hover,
.nav-links a.active {
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(255, 255, 255, 0.26);
  text-decoration: none;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  padding: 7px 12px;
  margin-bottom: 16px;
  background: rgba(255, 255, 255, 0.1);
  color: #d4fff9;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-title {
  margin: 0;
  max-width: 900px;
  font-size: clamp(2.7rem, 5.8vw, 5rem);
  line-height: 0.98;
  letter-spacing: -0.05em;
}

.hero-subtitle {
  max-width: 760px;
  margin: 16px 0 0;
  color: rgba(229, 255, 251, 0.86);
  font-size: 1.07rem;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 22px;
}

.hero-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 0 13px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  color: #e8fffc;
  font-size: 0.9rem;
  font-weight: 600;
}

.page-shell {
  padding-top: 30px;
  padding-bottom: 56px;
}

.intro-card,
.article-card,
.index-card,
.meta-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 28px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(12px);
}

.index-layout {
  display: grid;
  gap: 22px;
}

.intro-card {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 22px;
  padding: 26px 28px;
}

.intro-card p,
.meta-card p,
.article-lead {
  color: var(--muted);
}

.status-box {
  padding: 20px;
  border-radius: 22px;
  border: 1px solid rgba(15, 118, 110, 0.16);
  background: linear-gradient(180deg, #f8fffe 0%, var(--accent-soft) 100%);
}

.status-box h2,
.article-card h2,
.index-card h2,
.meta-card h2 {
  margin: 0 0 10px;
  letter-spacing: -0.03em;
}

.index-grid {
  display: grid;
  gap: 22px;
}

.index-card {
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(240px, 320px) 1fr;
}

.index-cover {
  min-height: 280px;
  background: linear-gradient(135deg, #dbeafe 0%, #f8fafc 100%);
  border-right: 1px solid var(--border);
}

.index-cover img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  object-position: center top;
}

.index-body {
  padding: 26px 28px;
}

.meta-line {
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 800;
  font-size: 0.82rem;
  margin-bottom: 10px;
}

.card-title {
  margin: 0 0 14px;
  font-size: clamp(1.8rem, 3vw, 2.45rem);
  line-height: 1.08;
  letter-spacing: -0.04em;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  margin: 18px 0 20px;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 11px;
  border-radius: 999px;
  background: #ebfffd;
  color: #115e59;
  border: 1px solid rgba(15, 118, 110, 0.14);
  font-size: 0.85rem;
  font-weight: 700;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid var(--border);
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  padding: 0 16px;
  border-radius: 999px;
  font-weight: 700;
  transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.button:hover {
  text-decoration: none;
  transform: translateY(-1px);
}

.button.primary {
  background: var(--accent);
  color: white;
}

.button.primary:hover {
  background: var(--accent-dark);
  color: white;
}

.button.secondary {
  background: white;
  color: var(--accent);
  border: 1px solid rgba(15, 118, 110, 0.18);
}

.button.secondary:hover {
  background: var(--accent-soft);
}

.article-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 24px;
  align-items: start;
}

.article-card {
  padding: 28px 30px;
}

.article-card h2 {
  margin-top: 34px;
  margin-bottom: 12px;
  font-size: 1.82rem;
  line-height: 1.15;
}

.article-card h3 {
  margin-top: 26px;
  margin-bottom: 10px;
  font-size: 1.25rem;
  line-height: 1.2;
  color: #0f172a;
}

.article-card p {
  max-width: var(--copy);
  margin: 0 0 16px;
  font-size: 1.03rem;
}

.article-card p.compact {
  font-size: 0.97rem;
}

.article-card figure {
  margin: 28px 0;
}

.article-card img {
  width: 100%;
  max-width: 100%;
  display: block;
  border-radius: 20px;
  border: 1px solid var(--border);
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.1);
  background: white;
}

.article-card figcaption {
  margin-top: 10px;
  color: var(--muted);
  font-size: 0.9rem;
}

.article-card .lede {
  font-size: 1.08rem;
  color: #314155;
}

.article-card .small-note {
  color: var(--muted);
  font-size: 0.94rem;
}

.meta-card {
  position: sticky;
  top: 18px;
  padding: 22px 20px;
}

.toc {
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
}

.toc li + li {
  margin-top: 10px;
}

.toc a {
  color: var(--text);
  font-weight: 600;
}

.toc a:hover {
  color: var(--accent);
}

.toc .toc-sub {
  padding-left: 14px;
  font-size: 0.95rem;
}

.footer-inner {
  padding-bottom: 32px;
  text-align: center;
  color: #5d6878;
  font-size: 0.94rem;
}

#fun-stuff {
  color: #5d6878;
  opacity: 0.72;
}

#fun-stuff:hover {
  color: var(--accent);
  opacity: 1;
}

@media (max-width: 980px) {
  .article-layout {
    grid-template-columns: 1fr;
  }

  .meta-card {
    position: static;
  }

  .intro-card,
  .index-card {
    grid-template-columns: 1fr;
  }

  .index-cover {
    min-height: 220px;
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }
}

@media (max-width: 720px) {
  .header-inner {
    padding-top: 34px;
    padding-bottom: 34px;
  }

  .top-nav {
    align-items: flex-start;
    flex-direction: column;
  }

  .article-card,
  .index-body,
  .intro-card,
  .meta-card {
    padding-left: 22px;
    padding-right: 22px;
  }
}
""".strip()


def sanitize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = text.replace("￼", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def slugify(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return value or "section"


def estimate_read_minutes(words: int) -> int:
    return max(1, round(words / 220))


def render_shared_head(title: str, description: str) -> str:
    return f"""<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="icon" type="image/png" href="/favicon.png" />
  <link rel="apple-touch-icon" href="/favicon.png" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}" />
  <meta name="robots" content="noindex, nofollow, noarchive" />
  <link rel="stylesheet" href="/field-notes/blog.css" />
</head>"""


def render_shell_nav() -> str:
    return '<nav class="top-nav" aria-label="Primary navigation" data-site-shell="subpage-nav"></nav>'


def line_role(max_size: float) -> str:
    if max_size >= 24:
        return "title"
    if max_size >= 17:
        return "section"
    if max_size >= 14:
        return "subsection"
    return "body"


def image_relative_path(article_slug: str, file_name: str) -> str:
    return f"/field-notes/assets/article-images/{article_slug}/{file_name}"


def article_relative_path(article_slug: str) -> str:
    return f"/field-notes/articles/{article_slug}/"


def export_image(block: dict, article_slug: str, page_num: int, image_num: int) -> str:
    article_image_dir = IMAGE_DIR / article_slug
    article_image_dir.mkdir(parents=True, exist_ok=True)
    ext = block.get("ext") or "png"
    file_name = f"page-{page_num:02d}-image-{image_num:02d}.{ext}"
    target = article_image_dir / file_name
    target.write_bytes(block["image"])
    return image_relative_path(article_slug, file_name)


def extract_items(config: ArticleConfig) -> tuple[list[dict], int]:
    path = Path(config.source_path)
    doc = fitz.open(path)
    items: list[dict] = []
    word_count = 0

    for page_index, page in enumerate(doc):
      data = page.get_text("dict")
      page_items = []
      image_index = 0

      for block in data["blocks"]:
          if block["type"] == 0:
              for line in block["lines"]:
                  spans = line["spans"]
                  text = sanitize_text("".join(span["text"] for span in spans))
                  if not text:
                      continue
                  max_size = max(span["size"] for span in spans)
                  role = line_role(max_size)
                  page_items.append(
                      {
                          "kind": "line",
                          "page": page_index + 1,
                          "y": line["bbox"][1],
                          "text": text,
                          "role": role,
                          "size": max_size,
                      }
                  )
          elif block["type"] == 1:
              image_index += 1
              exported = export_image(block, config.slug, page_index + 1, image_index)
              page_items.append(
                  {
                      "kind": "image",
                      "page": page_index + 1,
                      "y": block["bbox"][1],
                      "src": exported,
                      "caption": f"Figure extracted from page {page_index + 1} of the original PDF.",
                  }
              )

      page_items.sort(key=lambda item: (item["y"], 0 if item["kind"] == "line" else 1))
      paragraph_lines: list[str] = []

      def flush_paragraph() -> None:
          nonlocal word_count
          if not paragraph_lines:
              return
          text = sanitize_text(" ".join(paragraph_lines))
          paragraph_lines.clear()
          if not text:
              return
          word_count += len(text.split())
          items.append(
              {
                  "kind": "paragraph",
                  "text": text,
                  "compact": len(text.split()) < 11,
              }
          )

      for item in page_items:
          if item["kind"] == "image":
              flush_paragraph()
              items.append(item)
              continue

          if item["role"] == "body":
              paragraph_lines.append(item["text"])
              continue

          flush_paragraph()
          if item["role"] == "title":
              continue
          items.append({"kind": item["role"], "text": item["text"]})

      flush_paragraph()

    return items, word_count


def dedupe_headings(items: list[dict], config: ArticleConfig) -> list[dict]:
    cleaned: list[dict] = []
    previous_text = ""
    index = 0
    while index < len(items):
        item = items[index]
        text = item.get("text", "")
        if item["kind"] in {"section", "subsection"} and text in config.drop_headings:
            index += 1
            continue
        if item["kind"] in {"section", "subsection"}:
            merged_text = text
            lookahead = index + 1
            while lookahead < len(items) and items[lookahead]["kind"] == item["kind"]:
                merged_text = f"{merged_text} {items[lookahead].get('text', '')}".strip()
                lookahead += 1
            item = dict(item)
            item["text"] = sanitize_text(merged_text)
            text = item["text"]
            index = lookahead
        else:
            index += 1
        if item["kind"] in {"section", "subsection"} and text == previous_text:
            continue
        cleaned.append(item)
        if text:
            previous_text = text
    return cleaned


def build_toc(items: list[dict]) -> list[tuple[str, str, str]]:
    toc = []
    used: dict[str, int] = {}
    for item in items:
        if item["kind"] not in {"section", "subsection"}:
            continue
        base = slugify(item["text"])
        count = used.get(base, 0) + 1
        used[base] = count
        anchor = base if count == 1 else f"{base}-{count}"
        item["anchor"] = anchor
        toc.append((item["kind"], item["text"], anchor))
    return toc


def render_article_html(config: ArticleConfig, items: list[dict], word_count: int) -> str:
    toc = build_toc(items)
    tag_html = "".join(f'<span class="tag">{html.escape(tag)}</span>' for tag in config.tags)
    article_html = []

    article_html.append("<article class=\"article-card\">")
    article_html.append(f"<p class=\"lede\">{html.escape(config.summary)}</p>")
    article_html.append(f"<p class=\"small-note\">{html.escape(config.reading_note)}</p>")

    for item in items:
        if item["kind"] == "section":
            article_html.append(
                f'<h2 id="{html.escape(item["anchor"])}">{html.escape(item["text"])}</h2>'
            )
        elif item["kind"] == "subsection":
            article_html.append(
                f'<h3 id="{html.escape(item["anchor"])}">{html.escape(item["text"])}</h3>'
            )
        elif item["kind"] == "paragraph":
            cls = "compact" if item.get("compact") else ""
            article_html.append(f'<p class="{cls}">{html.escape(item["text"])}</p>' if cls else f'<p>{html.escape(item["text"])}</p>')
        elif item["kind"] == "image":
            article_html.append(
                "<figure>"
                f'<img src="{html.escape(item["src"])}" alt="{html.escape(item["caption"])}" loading="lazy" />'
                f"<figcaption>{html.escape(item['caption'])}</figcaption>"
                "</figure>"
            )

    article_html.append("</article>")

    toc_html = "".join(
        f'<li class="{"toc-sub" if kind == "subsection" else ""}"><a href="#{html.escape(anchor)}">{html.escape(text)}</a></li>'
        for kind, text, anchor in toc
    )
    read_minutes = estimate_read_minutes(word_count)

    return f"""<!DOCTYPE html>
<html lang="en">
{render_shared_head(f"{config.title} - Field Notes - Maxwell J. Yin", config.description)}
<body data-page="field-notes">
  <header>
    <div class="header-inner">
      {render_shell_nav()}
      <div class="eyebrow">Hidden Blog · Full HTML Edition</div>
      <h1 class="hero-title">{html.escape(config.title)}</h1>
      <p class="hero-subtitle">{html.escape(config.subtitle)}</p>
      <div class="hero-meta">
        <span>{html.escape(config.published)}</span>
        <span>{read_minutes} min read</span>
        <span>{word_count} words</span>
      </div>
    </div>
  </header>

  <main class="page-shell">
    <div class="article-layout">
      <div>
        <div class="tag-row">{tag_html}</div>
        <div class="actions">
          <a class="button primary" href="/field-notes/">Back to Field Notes</a>
        </div>
        {''.join(article_html)}
      </div>

      <aside class="meta-card">
        <h2>On This Page</h2>
        <p>{html.escape(config.summary)}</p>
        <ul class="toc">{toc_html}</ul>
      </aside>
    </div>
  </main>

  <footer class="footer-inner" data-site-shell="footer"></footer>
  <script src="/assets/site-shell.js"></script>
</body>
</html>
"""


def render_index_html(cards: list[dict]) -> str:
    card_html = []
    for card in cards:
        tag_html = "".join(f'<span class="tag">{html.escape(tag)}</span>' for tag in card["tags"])
        card_html.append(
            f"""
      <article class="index-card">
        <div class="index-cover">
          <img src="{html.escape(card['preview'])}" alt="{html.escape(card['title'])} cover preview" />
        </div>
        <div class="index-body">
          <div class="meta-line">{html.escape(card['published'])} · {card['read_minutes']} min read</div>
          <h2 class="card-title">{html.escape(card['title'])}</h2>
          <p>{html.escape(card['summary'])}</p>
          <div class="tag-row">{tag_html}</div>
          <div class="actions">
            <a class="button primary" href="{html.escape(card['article_href'])}">Read HTML Article</a>
          </div>
        </div>
      </article>
"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
{render_shared_head("Field Notes - Maxwell J. Yin", "An unlisted page for long-form technical notes, PDF-to-HTML reconstructions, and architecture analysis by Maxwell J. Yin.")}
<body data-page="field-notes">
  <header>
    <div class="header-inner">
      {render_shell_nav()}
      <div class="eyebrow">Unlisted Technical Writing</div>
      <h1 class="hero-title">Field Notes</h1>
      <p class="hero-subtitle">
        A quiet corner for longer-form research reproductions, model teardowns, and architecture notes.
        This page stays off the main site and now hosts full HTML versions instead of PDF-only summaries.
      </p>
    </div>
  </header>

  <main class="page-shell">
    <section class="index-layout">
      <div class="intro-card">
        <div>
          <p>
            This section is intentionally unlisted. It is where I keep longer technical writing that is still useful to publish
            but not yet ready to surface on the homepage or primary navigation.
          </p>
          <p>
            The current set contains three PDF-origin articles that have been reconstructed into HTML, with inline figures
            and section navigation. The original PDFs are no longer served by the site.
          </p>
        </div>
        <aside class="status-box">
          <h2>Current Rules</h2>
          <ul>
            <li>No homepage button or visible site entry point.</li>
            <li>`noindex`, `nofollow`, and `noarchive` remain enabled.</li>
            <li>Only the HTML editions are published on the site.</li>
          </ul>
        </aside>
      </div>

      <div class="index-grid">
        {''.join(card_html)}
      </div>
    </section>
  </main>

  <footer class="footer-inner" data-site-shell="footer"></footer>
  <script src="/assets/site-shell.js"></script>
</body>
</html>
"""


def ensure_dirs() -> None:
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    ensure_dirs()
    CSS_PATH.write_text(BLOG_CSS + "\n", encoding="utf-8")

    cards = []
    for config in ARTICLES:
        items, word_count = extract_items(config)
        items = dedupe_headings(items, config)
        article_dir = ARTICLES_DIR / config.slug
        article_dir.mkdir(parents=True, exist_ok=True)
        article_path = article_dir / "index.html"
        article_path.write_text(render_article_html(config, items, word_count), encoding="utf-8")

        cards.append(
            {
                "title": config.title,
                "summary": config.summary,
                "published": config.published,
                "read_minutes": estimate_read_minutes(word_count),
                "tags": config.tags,
                "preview": f"/field-notes/previews/{config.preview}",
                "article_href": article_relative_path(config.slug),
            }
        )

    index_path = FIELD_NOTES_DIR / "index.html"
    index_path.write_text(render_index_html(cards), encoding="utf-8")


if __name__ == "__main__":
    main()
