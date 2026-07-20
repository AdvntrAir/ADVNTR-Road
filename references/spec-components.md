# ADVNTR Road — Build Spec: Component Library & Template Structure
### Use when: fixing layout bugs, component rendering, template structure
### This is the file for most bug-fix sessions

Every interactive behavior from the React design system is stripped — what
remains is the visual specification only.
 
Define all component CSS in `template/styles/components.css`.
 
### 6.1 Base / Reset
 
```css
/* template/styles/layout.css — @page and base */
 
@page {
    size: letter;                    /* 8.5in × 11in */
    margin: 0.75in 0.875in;
    background: #F9E4C5;            /* Champagne — mandatory */
}
 
@page cover {
    margin: 0;                       /* Full bleed cover */
    background: #1B4436;            /* Brunswick */
}
 
@page back-cover {
    margin: 0;
    background: #1B4436;
}
 
*, *::before, *::after { box-sizing: border-box; }
 
body {
    margin: 0;
    background: var(--surface-page);
    color: var(--text-primary);
    font-family: var(--font-body);
    font-size: var(--text-body);
    line-height: var(--leading-body);
    -webkit-font-smoothing: antialiased;
}
 
h1, h2, h3, h4, h5, h6 {
    margin: 0;
    font-family: var(--font-display);
    color: var(--text-primary);
    line-height: var(--leading-tight);
    font-weight: var(--weight-bold);
}
 
p { margin: 0; line-height: var(--leading-body); }
 
hr {
    border: none;
    border-top: var(--rule-accent);
    margin: var(--space-8) 0;
}
```
 
### 6.2 Section Header
 
```css
.section-header {
    border-top: var(--rule-accent);
    padding-top: var(--space-6);
    margin-bottom: var(--space-8);
    page-break-after: avoid;
    break-after: avoid;
}
 
.section-header__eyebrow {
    font-family: var(--font-mono);
    font-size: var(--text-label);
    letter-spacing: var(--tracking-label);
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: var(--space-3);
}
 
.section-header__title {
    font-family: var(--font-display);
    font-size: var(--text-h2);
    font-weight: var(--weight-bold);
    color: var(--text-primary);
    line-height: var(--leading-tight);
    margin-bottom: var(--space-2);
}
 
.section-header__subhead {
    font-family: var(--font-display);
    font-style: italic;
    font-size: var(--text-lg);
    color: var(--text-secondary);
    line-height: var(--leading-snug);
}
```
 
HTML:
```html
<div class="section-header">
  <div class="section-header__eyebrow">SECTION 03 — WHERE TO CAMP</div>
  <h2 class="section-header__title">Where You Sleep Matters</h2>
  <p class="section-header__subhead">From rain forest riverbanks to coastal bluffs.</p>
</div>
```
 
### 6.3 Pull Quote
 
```css
.pull-quote {
    border-left: var(--rule-accent);
    padding-left: var(--space-5);
    padding-top: var(--space-2);
    padding-bottom: var(--space-2);
    margin: var(--stack-md) 0;
    page-break-inside: avoid;
    break-inside: avoid;
}
 
.pull-quote__text {
    font-family: var(--font-display);
    font-style: italic;
    font-size: var(--text-xl);
    color: var(--text-primary);
    line-height: var(--leading-snug);
}
```
 
HTML:
```html
<blockquote class="pull-quote">
  <p class="pull-quote__text">"Sol Duc earns its reputation, but not without a trade."</p>
</blockquote>
```
 
### 6.4 Campground Card
 
```css
.camp-card {
    background: var(--surface-card);
    border-radius: var(--radius-md);
    border: 1px solid var(--border-card);
    box-shadow: var(--shadow-card);
    padding: var(--pad-card);
    margin-bottom: var(--stack-md);
    page-break-inside: avoid;
    break-inside: avoid;
}
 
.camp-card--featured {
    border-top: 3px solid var(--color-buff);
}
 
.camp-card__region {
    font-family: var(--font-mono);
    font-size: 9.5px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 6px;
}
 
.camp-card__name {
    font-family: var(--font-display);
    font-size: 22px;
    font-weight: var(--weight-bold);
    color: var(--text-primary);
    line-height: 1.2;
    letter-spacing: -0.01em;
    margin-bottom: var(--space-3);
}
 
.camp-card__badges {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: var(--space-3);
}
 
.camp-card__divider {
    border: none;
    border-top: 1px solid var(--border-card);
    margin: var(--space-3) 0;
}
 
.camp-card__description {
    font-family: var(--font-body);
    font-size: 14.5px;
    color: var(--text-primary);
    line-height: 1.7;
    margin-bottom: var(--space-4);
    max-width: var(--measure-prose);
}
 
/* Metadata grid — required fields */
.camp-card__meta {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: var(--gap-sm);
    padding-top: var(--space-3);
    border-top: 1px solid var(--border-card);
}
 
.camp-card__meta-item {}
 
.camp-card__meta-label {
    font-family: var(--font-mono);
    font-size: 9px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    display: block;
    margin-bottom: 3px;
}
 
.camp-card__meta-value {
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: var(--text-primary);
    font-weight: var(--weight-bold);
}
 
/* Tags row */
.camp-card__tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: var(--space-3);
}
```
 
HTML:
```html
<article class="camp-card">
  <div class="camp-card__region">HOH RAIN FOREST, OLYMPIC NP</div>
  <h3 class="camp-card__name">Hoh Rain Forest Campground</h3>
 
  <div class="camp-card__badges">
    <span class="badge badge--consensus">Consensus Pick</span>
    <span class="badge badge--reservable">Reservable</span>
  </div>
 
  <hr class="camp-card__divider">
 
  <p class="camp-card__description">
    The Hoh sits inside one of the wettest temperate rain forests in North America,
    and the campground earns every reputation attached to it. Sites along the river
    hear the Hoh moving at night. Bring rain gear regardless of the forecast —
    this is a place that makes its own weather.
  </p>
 
  <div class="camp-card__meta">
    <div class="camp-card__meta-item">
      <span class="camp-card__meta-label">Reservations</span>
      <span class="camp-card__meta-value">Recreation.gov</span>
    </div>
    <div class="camp-card__meta-item">
      <span class="camp-card__meta-label">Hookups</span>
      <span class="camp-card__meta-value">None</span>
    </div>
    <div class="camp-card__meta-item">
      <span class="camp-card__meta-label">Max Length</span>
      <span class="camp-card__meta-value">21 ft</span>
    </div>
    <div class="camp-card__meta-item">
      <span class="camp-card__meta-label">Pets</span>
      <span class="camp-card__meta-value">Leash only</span>
    </div>
    <div class="camp-card__meta-item">
      <span class="camp-card__meta-label">Verified</span>
      <span class="camp-card__meta-value">June 2026</span>
    </div>
  </div>
 
  <div class="camp-card__tags">
    <span class="tag">🐾 Dog Friendly</span>
    <span class="tag">🏕️ Fills Fast</span>
  </div>
</article>
```
 
### 6.5 Badge — all 7 variants
 
```css
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: var(--font-body);
    font-size: 11px;
    font-weight: var(--weight-semibold);
    line-height: 1;
    padding: 4px 10px;
    border-radius: var(--radius-sm);
    white-space: nowrap;
    letter-spacing: 0.01em;
}
 
/* Moss Green — verified, consensus */
.badge--consensus  { background: var(--tag-consensus-bg); color: var(--tag-consensus-text);
                     border: 1px solid var(--tag-consensus-border); }
.badge--verified   { background: var(--tag-consensus-bg); color: var(--tag-consensus-text);
                     border: 1px solid var(--tag-consensus-border); }
.badge--consensus::before { content: '✓ '; }
.badge--verified::before  { content: '✓ '; }
 
/* Buff — editorial judgment, urgency */
.badge--hidden-gem { background: var(--tag-editorial-bg); color: var(--tag-editorial-text);
                     border: 1px solid var(--tag-editorial-border); }
.badge--heads-up   { background: var(--tag-editorial-bg); color: var(--tag-editorial-text);
                     border: 1px solid var(--tag-editorial-border); }
.badge--reservable { background: var(--tag-editorial-bg); color: var(--tag-editorial-text);
                     border: 1px solid var(--tag-editorial-border); }
.badge--hidden-gem::before { content: '◆ '; }
.badge--heads-up::before   { content: '▲ '; }
.badge--reservable::before { content: '◎ '; }
 
/* No color — factual classification */
.badge--dog-friendly { background: var(--tag-neutral-bg); color: var(--tag-neutral-text);
                       border: 1px solid var(--tag-neutral-border); }
.badge--big-rig      { background: var(--tag-neutral-bg); color: var(--tag-neutral-text);
                       border: 1px solid var(--tag-neutral-border); }
```
 
### 6.6 Tag (inline metadata)
 
```css
.tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: var(--weight-regular);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-secondary);
    padding: 3px 8px;
    border-radius: var(--radius-xs);
    background: var(--surface-gray-subtle);
    border: 1px solid var(--border-card);
    white-space: nowrap;
    line-height: 1.4;
}
```
 
### 6.7 Business Listing Card (compact)
 
```css
.business-card {
    background: var(--surface-card);
    border-radius: var(--radius-md);
    border: 1px solid var(--border-card);
    box-shadow: var(--shadow-xs);
    padding: var(--space-5) var(--pad-card);
    margin-bottom: var(--space-4);
    display: grid;
    grid-template-columns: 1fr auto;
    gap: var(--gap-md);
    page-break-inside: avoid;
    break-inside: avoid;
}
 
.business-card__name {
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: var(--weight-bold);
    color: var(--text-primary);
    margin-bottom: 4px;
}
 
.business-card__type {
    font-family: var(--font-mono);
    font-size: 9.5px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: var(--space-2);
}
 
.business-card__description {
    font-family: var(--font-body);
    font-size: 14px;
    color: var(--text-primary);
    line-height: 1.65;
}
 
.business-card__meta {
    font-family: var(--font-mono);
    font-size: 9.5px;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: var(--text-secondary);
    text-align: right;
    white-space: nowrap;
}
```
 
### 6.8 Guide Hero (cover interior / section openers)
 
```css
.guide-hero {
    background: var(--surface-page);
    padding: var(--space-12) 0 var(--space-8);
    border-bottom: 2px solid var(--color-buff);
    margin-bottom: var(--stack-lg);
}
 
.guide-hero__region {
    font-family: var(--font-mono);
    font-size: var(--text-label);
    letter-spacing: var(--tracking-label);
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: var(--space-3);
}
 
.guide-hero__title {
    font-family: var(--font-display);
    font-size: 42px;
    font-weight: var(--weight-bold);
    color: var(--text-primary);
    line-height: 1.1;
    letter-spacing: -0.02em;
    margin-bottom: var(--space-4);
}
 
.guide-hero__subtitle {
    font-family: var(--font-display);
    font-style: italic;
    font-size: 22px;
    color: var(--text-secondary);
    line-height: var(--leading-snug);
    margin-bottom: var(--space-5);
}
 
.guide-hero__intro {
    font-family: var(--font-body);
    font-size: 16px;
    line-height: 1.7;
    color: var(--text-secondary);
    max-width: 62ch;
    margin-bottom: var(--space-5);
}
 
.guide-hero__stats {
    font-family: var(--font-mono);
    font-size: var(--text-label);
    letter-spacing: var(--tracking-caps);
    text-transform: uppercase;
    color: var(--text-secondary);
}
```
 
### 6.9 Topo Line System
 
Generate `template/assets/topo-lines.svg` using this pattern. The paths are
organic, irregular horizontal curves — not perfect sine waves. Generate a set
of 8–12 paths with varying curvature and spacing.
 
```svg
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 800 600"
     preserveAspectRatio="xMidYMid slice"
     style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;">
  <!-- Each path = one contour line. Organic, irregular, not sine-wave. -->
  <!-- Cover/back cover: stroke="#DDAD8A" opacity="0.18" -->
  <!-- Section dividers: stroke="#1B4436" opacity="0.12" -->
  <path d="M-50,80 C120,65 280,95 450,72 C580,55 700,88 850,70"
        stroke="#DDAD8A" stroke-width="0.8" fill="none" opacity="0.18"/>
  <path d="M-50,140 C100,128 260,158 420,138 C560,122 690,148 850,132"
        stroke="#DDAD8A" stroke-width="0.8" fill="none" opacity="0.18"/>
  <path d="M-50,200 C140,185 300,218 460,200 C600,185 720,210 850,195"
        stroke="#DDAD8A" stroke-width="0.8" fill="none" opacity="0.18"/>
  <path d="M-50,265 C90,252 250,278 430,258 C575,242 700,268 850,255"
        stroke="#DDAD8A" stroke-width="0.8" fill="none" opacity="0.18"/>
  <path d="M-50,330 C110,315 275,342 450,325 C590,310 715,335 850,320"
        stroke="#DDAD8A" stroke-width="0.8" fill="none" opacity="0.18"/>
  <path d="M-50,398 C130,382 290,408 460,390 C600,375 720,402 850,388"
        stroke="#DDAD8A" stroke-width="0.8" fill="none" opacity="0.18"/>
  <path d="M-50,468 C105,452 265,480 445,462 C585,448 710,472 850,458"
        stroke="#DDAD8A" stroke-width="0.8" fill="none" opacity="0.18"/>
  <path d="M-50,538 C120,522 280,548 455,530 C595,515 718,540 850,526"
        stroke="#DDAD8A" stroke-width="0.8" fill="none" opacity="0.18"/>
</svg>
```
 
For section divider use (less opacity, Brunswick):
```html
<div style="position:relative;overflow:hidden;height:60px;margin:var(--stack-lg) 0;">
  <!-- Swap stroke color to #1B4436, opacity to 0.10 -->
</div>
```
 
### 6.10 Page Break Control (WeasyPrint — both properties required on every container)
 
```css
/* template/styles/print.css */
 
/* Force both — WeasyPrint requires both for reliable behavior */
.camp-card,
.business-card,
.gateway-card,
.section-header,
.pull-quote,
.map-container,
.activity-block,
.checklist-group,
.guide-hero,
.topo-divider {
    page-break-inside: avoid;
    break-inside: avoid;
}
 
/* Headers always stay with following content */
.section-header,
h1, h2, h3 {
    page-break-after: avoid;
    break-after: avoid;
}
 
/* Each major section starts on a new page */
.section {
    page-break-before: always;
    break-before: always;
}
 
/* Cover and TOC don't cascade breaks to children */
.page-cover,
.page-toc {
    page-break-before: avoid;
    break-before: avoid;
}
 
/* Map images must not split */
.map-container img,
.map-container svg {
    page-break-inside: avoid;
    break-inside: avoid;
}
```
 
---
 
## 7. TEMPLATE STRUCTURE
 
`template/guide_template.html` — complete Jinja2 template.
 
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  /* Inline all CSS here — WeasyPrint handles linked files but inline is safer */
  {{ font_css }}
 
  /* Paste full contents of: */
  /* tokens.css → typography-embed.css → layout.css → components.css → maps.css → print.css */
</style>
</head>
<body>
 
<!-- ═══════════════════════════════════════════════════════════
     COVER PAGE
     ═══════════════════════════════════════════════════════════ -->
<div class="page-cover" style="
  page: cover;
  background: var(--color-brunswick);
  width: 8.5in; height: 11in;
  display: flex; flex-direction: column;
  padding: 0.75in 0.875in;
  position: relative; overflow: hidden;">
 
  <!-- Topo line layer -->
  <div style="position:absolute;top:0;left:0;right:0;bottom:0;z-index:0;">
    {% include 'assets/topo-lines.svg' %}
  </div>
 
  <!-- Content layer -->
  <div style="position:relative;z-index:1;flex:1;display:flex;flex-direction:column;">
 
    <!-- Stacked mark -->
    <div style="margin-bottom: 48px;">
      <!-- Stacked mark SVG from Section 5 -->
      <svg xmlns="http://www.w3.org/2000/svg" width="120" height="90" viewBox="0 0 160 120">
        <text text-anchor="middle" x="80" y="42" font-family="'Titan One',Impact,sans-serif"
              font-size="38" fill="#F9E4C5" letter-spacing="2">ADV</text>
        <text text-anchor="middle" x="80" y="80" font-family="'Titan One',Impact,sans-serif"
              font-size="38" fill="#F9E4C5" letter-spacing="2">NTR</text>
        <text text-anchor="middle" x="80" y="112" font-family="'Titan One',Impact,sans-serif"
              font-size="28" fill="#DDAD8A" letter-spacing="8">ROAD</text>
      </svg>
    </div>
 
    <!-- Guide title -->
    <div style="flex:1;">
      <div style="font-family:var(--font-mono);font-size:10px;letter-spacing:0.15em;
                  text-transform:uppercase;color:rgba(249,228,197,0.55);margin-bottom:16px;">
        {{ guide.region }}
      </div>
      <h1 style="font-family:var(--font-display);font-size:52px;font-weight:700;
                 color:var(--color-champagne);line-height:1.05;letter-spacing:-0.02em;
                 margin-bottom:16px;">
        {{ guide.title }}
      </h1>
      <p style="font-family:var(--font-display);font-style:italic;font-size:22px;
                color:var(--color-buff);line-height:1.4;max-width:44ch;">
        {{ guide.subtitle }}
      </p>
    </div>
 
    <!-- Illustrated map slot -->
    {% if guide.cover_map %}
    <div style="width:100%;height:280px;overflow:hidden;border-radius:4px;margin-bottom:32px;">
      <img src="{{ guide.cover_map }}"
           style="width:100%;height:100%;object-fit:cover;object-position:center;">
    </div>
    {% endif %}
 
    <!-- Edition / footer -->
    <div style="font-family:var(--font-mono);font-size:9px;letter-spacing:0.15em;
                text-transform:uppercase;color:rgba(249,228,197,0.40);
                border-top:1px solid rgba(249,228,197,0.12);padding-top:16px;">
      {{ guide.edition }} · road.advntr.io
    </div>
  </div>
</div>
 
<!-- ═══════════════════════════════════════════════════════════
     TABLE OF CONTENTS
     ═══════════════════════════════════════════════════════════ -->
<div class="page-toc section" style="min-height:100vh;padding:var(--pad-page);">
  <!-- Editorial wordmark light -->
  <div style="margin-bottom:var(--stack-xl);padding-bottom:var(--space-6);
              border-bottom:var(--rule-accent);">
    <svg xmlns="http://www.w3.org/2000/svg" width="220" height="38" viewBox="0 0 280 48">
      <text x="0" y="38" font-family="'Playfair Display',Georgia,serif"
            font-weight="700" font-size="32" fill="#1B4436">ADVNTR</text>
      <text x="194" y="38" font-family="'Playfair Display',Georgia,serif"
            font-style="italic" font-size="32" fill="#DDAD8A">Road</text>
    </svg>
  </div>
 
  <div style="font-family:var(--font-mono);font-size:10px;letter-spacing:0.15em;
              text-transform:uppercase;color:var(--text-secondary);margin-bottom:var(--space-6);">
    Contents
  </div>
 
  {% for section in guide.sections %}
  <div style="display:flex;justify-content:space-between;align-items:baseline;
              padding:var(--space-3) 0;border-bottom:var(--rule-subtle);">
    <span style="font-family:var(--font-display);font-size:16px;color:var(--text-primary);">
      {{ section.title }}
    </span>
    <span style="font-family:var(--font-mono);font-size:10px;letter-spacing:0.10em;
                 color:var(--text-secondary);">
      {{ loop.index + 2 }}
    </span>
  </div>
  {% endfor %}
</div>
 
<!-- ═══════════════════════════════════════════════════════════
     CONTENT SECTIONS (01–08 + ZONES)
     Rendering order: 01 → 02 → 03 → 04a…04e → 05 → 06 → 07 → 08
     Zones are injected between sections 03 and 05 automatically.
     ═══════════════════════════════════════════════════════════ -->
 
{# ── MACRO: map block ─────────────────────────────────────── #}
{% macro render_map(map_key) %}
{% if map_key and guide.maps is defined and guide.maps[map_key] is defined %}
{% set m = guide.maps[map_key] %}
{% if m.image_uri %}
<div class="map-container"
     style="position:relative;width:100%;margin:var(--stack-md) 0;
            border-radius:var(--radius-md);overflow:hidden;
            page-break-inside:avoid;break-inside:avoid;">
  <img src="{{ m.image_uri }}"
       style="display:block;width:100%;height:auto;">
  {% if m.overlay_svg %}
  <svg style="position:absolute;top:0;left:0;width:100%;height:100%;"
       viewBox="0 0 {{ m.size.split('x')[0] }} {{ m.size.split('x')[1] }}"
       xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
    {{ m.overlay_svg | safe }}
  </svg>
  {% endif %}
</div>
{% endif %}
{% endif %}
{% endmacro %}
 
{# ── MACRO: campground card ───────────────────────────────── #}
{% macro render_camp_card(camp) %}
<article class="camp-card {% if camp.featured %}camp-card--featured{% endif %}"
         style="page-break-inside:avoid;break-inside:avoid;">
  <div class="camp-card__region">{{ camp.region }}</div>
  <h3 class="camp-card__name">{{ camp.name }}</h3>
 
  {% if camp.badges %}
  <div class="camp-card__badges">
    {% for badge in camp.badges %}
    <span class="badge badge--{{ badge }}">{{ badge | replace('-',' ') | title }}</span>
    {% endfor %}
  </div>
  {% endif %}
 
  <hr class="camp-card__divider">
 
  {% if camp.editorial %}
  <p class="camp-card__description">{{ camp.editorial }}</p>
  {% endif %}
 
  <div class="camp-card__meta">
    <div class="camp-card__meta-item">
      <span class="camp-card__meta-label">Reservations</span>
      <span class="camp-card__meta-value">{{ camp.reservations.method }}</span>
    </div>
    <div class="camp-card__meta-item">
      <span class="camp-card__meta-label">Hookups</span>
      <span class="camp-card__meta-value">{{ camp.hookups | title }}</span>
    </div>
    <div class="camp-card__meta-item">
      <span class="camp-card__meta-label">Max Length</span>
      <span class="camp-card__meta-value">{{ camp.max_length }}</span>
    </div>
    <div class="camp-card__meta-item">
      <span class="camp-card__meta-label">Pets</span>
      <span class="camp-card__meta-value">
        {{ 'Yes' if camp.pets.allowed else 'No' }}
      </span>
    </div>
    <div class="camp-card__meta-item">
      <span class="camp-card__meta-label">Verified</span>
      <span class="camp-card__meta-value">{{ camp.verified_date }}</span>
    </div>
  </div>
</article>
{% endmacro %}
 
{# ── SECTIONS 01–03 ────────────────────────────────────────── #}
{% for section in guide.sections %}
{% if section.id in ['orientation', 'before-you-arrive', 'where-to-sleep'] %}
<div class="section" id="section-{{ section.id }}"
     style="page-break-before:always;break-before:always;">
 
  <div class="section-header"
       style="page-break-after:avoid;break-after:avoid;">
    <div class="section-header__eyebrow">
      SECTION {{ '%02d'|format(loop.index) }} — {{ section.eyebrow|upper }}
    </div>
    <h2 class="section-header__title">{{ section.title }}</h2>
    {% if section.subhead %}
    <p class="section-header__subhead">{{ section.subhead }}</p>
    {% endif %}
  </div>
 
  {% if section.prose_html %}
  <div class="section-prose"
       style="max-width:var(--measure-prose);margin-bottom:var(--stack-lg);">
    {{ section.prose_html | safe }}
  </div>
  {% endif %}
 
  {{ render_map(section.map_key) }}
 
  {# Gateway town cards — Section 02, conditional #}
  {% if section.show_gateway_towns and guide.gateway_towns %}
  {% for town in guide.gateway_towns %}
  <div class="gateway-card"
       style="background:var(--surface-card);border-radius:var(--radius-md);
              border:1px solid var(--border-card);box-shadow:var(--shadow-card);
              padding:var(--pad-card);margin-bottom:var(--stack-md);
              page-break-inside:avoid;break-inside:avoid;">
    <div style="font-family:var(--font-mono);font-size:9.5px;letter-spacing:0.15em;
                text-transform:uppercase;color:var(--text-secondary);margin-bottom:6px;">
      {{ town.role | upper }}
    </div>
    <h3 style="font-family:var(--font-display);font-size:20px;font-weight:700;
               color:var(--text-primary);margin-bottom:var(--space-3);">
      {{ town.name }}
    </h3>
    {% if town.editorial %}
    <p style="font-family:var(--font-body);font-size:14.5px;
              color:var(--text-primary);line-height:1.7;
              margin-bottom:var(--space-4);">
      {{ town.editorial }}
    </p>
    {% endif %}
    {% if town.services %}
    <div style="font-family:var(--font-mono);font-size:9.5px;letter-spacing:0.12em;
                text-transform:uppercase;color:var(--text-secondary);">
      {{ town.services | join(' · ') | upper }}
    </div>
    {% endif %}
  </div>
  {% endfor %}
  {% endif %}
 
  {# Campground cards — Section 03 #}
  {% if section.show_campgrounds and guide.campgrounds %}
  {% for camp in guide.campgrounds %}
  {{ render_camp_card(camp) }}
  {% endfor %}
  {% endif %}
 
</div>
{% endif %}
{% endfor %}
 
{# ── SECTION 04 — EXPERIENCE ZONES (one sub-section per zone) ── #}
{% if guide.zones %}
{% for zone in guide.zones %}
<div class="section" id="section-zone-{{ zone.id }}"
     style="page-break-before:always;break-before:always;">
 
  <div class="section-header"
       style="page-break-after:avoid;break-after:avoid;">
    <div class="section-header__eyebrow">
      SECTION 04{{ 'abcde'[loop.index0] | upper }} — {{ zone.eyebrow | upper }}
    </div>
    <h2 class="section-header__title">{{ zone.title }}</h2>
    {% if zone.subhead %}
    <p class="section-header__subhead">{{ zone.subhead }}</p>
    {% endif %}
  </div>
 
  {# Highlights sidebar — conditional on zone.highlights #}
  {% if zone.highlights %}
  <div class="zone-highlights"
       style="background:var(--surface-buff-subtle);
              border-left:3px solid var(--color-buff);
              border-radius:0 var(--radius-md) var(--radius-md) 0;
              padding:var(--space-5) var(--pad-card);
              margin-bottom:var(--stack-md);
              page-break-inside:avoid;break-inside:avoid;">
    <div style="font-family:var(--font-mono);font-size:9.5px;letter-spacing:0.15em;
                text-transform:uppercase;color:var(--text-secondary);
                margin-bottom:var(--space-4);">
      Highlights
    </div>
    {% for h in zone.highlights %}
    <div style="margin-bottom:var(--space-3);
                page-break-inside:avoid;break-inside:avoid;">
      <div style="font-family:var(--font-display);font-size:15px;font-weight:700;
                  color:var(--text-primary);margin-bottom:2px;">
        {{ h.label }}
      </div>
      {% if h.note %}
      <div style="font-family:var(--font-body);font-size:14px;
                  color:var(--text-secondary);line-height:1.5;">
        {{ h.note }}
      </div>
      {% endif %}
      {% if h.tags %}
      <div style="margin-top:4px;">
        {% for tag in h.tags %}
        <span class="badge badge--{{ tag }}" style="font-size:10px;">
          {{ tag | replace('-',' ') | title }}
        </span>
        {% endfor %}
      </div>
      {% endif %}
    </div>
    {% endfor %}
  </div>
  {% endif %}
 
  {% if zone.prose_html %}
  <div class="section-prose"
       style="max-width:var(--measure-prose);margin-bottom:var(--stack-lg);">
    {{ zone.prose_html | safe }}
  </div>
  {% endif %}
 
  {{ render_map(zone.map_key) }}
 
</div>
{% endfor %}
{% endif %}
 
{# ── SECTIONS 05–08 ────────────────────────────────────────── #}
{% for section in guide.sections %}
{% if section.id in ['what-to-do','eat-resupply','field-notes','before-you-leave'] %}
 
{# Calculate display number: zones push these sections forward #}
{% set base_num = loop.index %}
{% set zone_count = guide.zones | length if guide.zones else 0 %}
 
<div class="section" id="section-{{ section.id }}"
     style="page-break-before:always;break-before:always;">
 
  <div class="section-header"
       style="page-break-after:avoid;break-after:avoid;">
    <div class="section-header__eyebrow">
      SECTION {{ '%02d'|format(base_num + zone_count) }} — {{ section.eyebrow|upper }}
    </div>
    <h2 class="section-header__title">{{ section.title }}</h2>
    {% if section.subhead %}
    <p class="section-header__subhead">{{ section.subhead }}</p>
    {% endif %}
  </div>
 
  {% if section.prose_html %}
  <div class="section-prose"
       style="max-width:var(--measure-prose);margin-bottom:var(--stack-lg);">
    {{ section.prose_html | safe }}
  </div>
  {% endif %}
 
  {{ render_map(section.map_key if section.map_key is defined else '') }}
 
  {# Business cards — Section 06, conditional #}
  {% if section.show_businesses and guide.businesses %}
  {% for biz in guide.businesses %}
  <div class="business-card"
       style="page-break-inside:avoid;break-inside:avoid;">
    <div>
      <div class="business-card__name">{{ biz.name }}</div>
      <div class="business-card__type">{{ biz.type }}</div>
      {% if biz.editorial %}
      <p class="business-card__description">{{ biz.editorial }}</p>
      {% endif %}
    </div>
    <div class="business-card__meta">
      {% if biz.phone %}<div>{{ biz.phone }}</div>{% endif %}
      {% if biz.website %}
      <div style="margin-top:4px;">
        <a href="{{ biz.website }}"
           style="font-family:var(--font-mono);font-size:9px;
                  color:var(--text-secondary);text-decoration:none;">
          Website ↗
        </a>
      </div>
      {% endif %}
    </div>
  </div>
  {% endfor %}
  {% endif %}
 
  {# Fees block — Section 07, conditional #}
  {% if section.show_fees and guide.fees %}
  {% set f = guide.fees %}
  <div class="fees-block"
       style="background:var(--surface-card);border-radius:var(--radius-md);
              border:1px solid var(--border-card);padding:var(--pad-card);
              margin-bottom:var(--stack-md);
              page-break-inside:avoid;break-inside:avoid;">
    <div style="font-family:var(--font-mono);font-size:9.5px;letter-spacing:0.15em;
                text-transform:uppercase;color:var(--text-secondary);
                margin-bottom:var(--space-4);">
      Entrance Fees · {{ guide.verified }}
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--gap-md);">
      {% if f.entrance_vehicle %}
      <div>
        <div style="font-family:var(--font-mono);font-size:9px;letter-spacing:0.12em;
                    text-transform:uppercase;color:var(--text-muted);margin-bottom:3px;">
          Vehicle (7-day)
        </div>
        <div style="font-family:var(--font-mono);font-size:14px;font-weight:700;
                    color:var(--text-primary);">
          {{ f.entrance_vehicle }}
        </div>
      </div>
      {% endif %}
      {% if f.entrance_person %}
      <div>
        <div style="font-family:var(--font-mono);font-size:9px;letter-spacing:0.12em;
                    text-transform:uppercase;color:var(--text-muted);margin-bottom:3px;">
          Per person (walk-in)
        </div>
        <div style="font-family:var(--font-mono);font-size:14px;font-weight:700;
                    color:var(--text-primary);">
          {{ f.entrance_person }}
        </div>
      </div>
      {% endif %}
      {% if f.camping_range %}
      <div>
        <div style="font-family:var(--font-mono);font-size:9px;letter-spacing:0.12em;
                    text-transform:uppercase;color:var(--text-muted);margin-bottom:3px;">
          Camping
        </div>
        <div style="font-family:var(--font-mono);font-size:14px;font-weight:700;
                    color:var(--text-primary);">
          {{ f.camping_range }}
        </div>
      </div>
      {% endif %}
      {% if f.america_beautiful %}
      <div style="grid-column:1/-1;">
        <span class="badge badge--verified">America the Beautiful Pass Accepted</span>
      </div>
      {% endif %}
    </div>
    {% if f.free_days %}
    <div style="margin-top:var(--space-4);font-family:var(--font-body);font-size:14px;
                color:var(--text-secondary);line-height:1.6;">
      <strong>Free entrance days:</strong> {{ f.free_days }}
    </div>
    {% endif %}
  </div>
  {% endif %}
 
  {# Permits block — Section 07, conditional #}
  {% if section.show_permits and guide.permits %}
  {% set p = guide.permits %}
  <div class="permits-block"
       style="background:var(--surface-card);border-radius:var(--radius-md);
              border:1px solid var(--border-card);padding:var(--pad-card);
              margin-bottom:var(--stack-md);
              page-break-inside:avoid;break-inside:avoid;">
    <div style="font-family:var(--font-mono);font-size:9.5px;letter-spacing:0.15em;
                text-transform:uppercase;color:var(--text-secondary);
                margin-bottom:var(--space-4);">
      Permits
    </div>
    {% if p.backcountry_required %}
    <p style="font-family:var(--font-body);font-size:14.5px;
              color:var(--text-primary);line-height:1.7;margin-bottom:var(--space-3);">
      Backcountry permit required for all overnight wilderness camping.
      Book via <strong>{{ p.platform }}</strong>{% if p.window %} — windows open {{ p.window }}{% endif %}.
      {% if p.walkup %} Walk-up permits: {{ p.walkup }}.{% endif %}
    </p>
    {% endif %}
    {% if p.bear_canister_required %}
    <p style="font-family:var(--font-body);font-size:14.5px;
              color:var(--text-primary);line-height:1.7;margin-bottom:var(--space-3);">
      Bear canister required on select routes.
      {% if p.bear_canister_rental and p.bear_canister_rental.available %}
      Available for rent at {{ p.bear_canister_rental.location }}.
      {% endif %}
    </p>
    {% endif %}
    {% if p.other %}
    {% for permit in p.other %}
    <div style="margin-top:var(--space-3);padding-top:var(--space-3);
                border-top:1px solid var(--border-card);">
      <div style="font-family:var(--font-mono);font-size:9px;letter-spacing:0.12em;
                  text-transform:uppercase;color:var(--text-muted);margin-bottom:4px;">
        {{ permit.name }}
      </div>
      <div style="font-family:var(--font-body);font-size:14px;
                  color:var(--text-primary);line-height:1.6;">
        {{ permit.note }} {% if permit.cost %}— {{ permit.cost }}{% endif %}
      </div>
    </div>
    {% endfor %}
    {% endif %}
  </div>
  {% endif %}
 
  {# Planning checklist — Section 08, conditional #}
  {% if section.show_checklist and guide.checklist %}
  <div class="checklist-group"
       style="background:var(--surface-card);border-radius:var(--radius-md);
              border:1px solid var(--border-card);padding:var(--pad-card);
              margin-bottom:var(--stack-md);
              page-break-inside:avoid;break-inside:avoid;">
    <div style="font-family:var(--font-mono);font-size:9.5px;letter-spacing:0.15em;
                text-transform:uppercase;color:var(--text-secondary);
                margin-bottom:var(--space-5);">
      Pre-Trip Checklist
    </div>
    {% for item in guide.checklist %}
    <div style="display:flex;gap:var(--space-4);align-items:flex-start;
                margin-bottom:var(--space-4);
                page-break-inside:avoid;break-inside:avoid;">
      <div style="width:18px;height:18px;min-width:18px;
                  border:1.5px solid var(--color-buff);
                  border-radius:var(--radius-xs);margin-top:1px;">
      </div>
      <div style="font-family:var(--font-body);font-size:15px;
                  color:var(--text-primary);line-height:1.6;">
        {{ item }}
      </div>
    </div>
    {% endfor %}
  </div>
  {% endif %}
 
  {# Resource links — Section 08, conditional #}
  {% if section.show_resources and guide.resources %}
  <div style="margin-top:var(--stack-md);">
    <div style="font-family:var(--font-mono);font-size:9.5px;letter-spacing:0.15em;
                text-transform:uppercase;color:var(--text-secondary);
                margin-bottom:var(--space-5);">
      Key Resources
    </div>
    {% for r in guide.resources %}
    <div style="margin-bottom:var(--space-5);padding-bottom:var(--space-5);
                border-bottom:1px solid var(--border-subtle);
                page-break-inside:avoid;break-inside:avoid;">
      <div style="font-family:var(--font-display);font-size:16px;font-weight:700;
                  color:var(--text-primary);margin-bottom:2px;">
        {{ r.name }}
      </div>
      <div style="font-family:var(--font-mono);font-size:10px;letter-spacing:0.10em;
                  color:var(--color-moss-green);text-transform:lowercase;
                  margin-bottom:var(--space-2);">
        {{ r.url }}
      </div>
      <div style="font-family:var(--font-body);font-size:14px;
                  color:var(--text-secondary);line-height:1.6;">
        {{ r.use }}{% if r.when %} — {{ r.when }}{% endif %}
      </div>
    </div>
    {% endfor %}
  </div>
  {% endif %}
 
</div>
{% endif %}
{% endfor %}
 
<!-- ═══════════════════════════════════════════════════════════
     BACK COVER
     ═══════════════════════════════════════════════════════════ -->
<div class="page-back-cover" style="
  page: back-cover;
  background: var(--color-brunswick);
  width:8.5in; height:11in;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  position:relative; overflow:hidden;">
 
  <div style="position:absolute;top:0;left:0;right:0;bottom:0;z-index:0;">
    {% include 'assets/topo-lines.svg' %}
  </div>
 
  <div style="position:relative;z-index:1;text-align:center;padding:0 0.875in;width:100%;">
 
    <!-- Stacked mark -->
    <svg xmlns="http://www.w3.org/2000/svg" width="160" height="120" viewBox="0 0 160 120"
         style="margin-bottom:40px;">
      <text text-anchor="middle" x="80" y="42" font-family="'Titan One',Impact,sans-serif"
            font-size="38" fill="#F9E4C5" letter-spacing="2">ADV</text>
      <text text-anchor="middle" x="80" y="80" font-family="'Titan One',Impact,sans-serif"
            font-size="38" fill="#F9E4C5" letter-spacing="2">NTR</text>
      <text text-anchor="middle" x="80" y="112" font-family="'Titan One',Impact,sans-serif"
            font-size="28" fill="#DDAD8A" letter-spacing="8">ROAD</text>
    </svg>
 
    <!-- Series block — conditional on series.yaml -->
    {% if series %}
    <div style="margin-bottom:48px;text-align:left;">
      <div style="font-family:var(--font-mono);font-size:9px;letter-spacing:0.15em;
                  text-transform:uppercase;color:rgba(249,228,197,0.40);
                  margin-bottom:16px;">
        More from ADVNTR Road
      </div>
      {% for guide_ref in series %}
      <div style="margin-bottom:14px;page-break-inside:avoid;break-inside:avoid;">
        <div style="font-family:var(--font-display);font-size:14px;font-weight:700;
                    color:rgba(249,228,197,0.80);line-height:1.3;">
          {{ guide_ref.title }}
        </div>
        {% if guide_ref.teaser %}
        <div style="font-family:var(--font-body);font-size:12px;
                    color:rgba(249,228,197,0.45);line-height:1.5;margin-top:2px;">
          {{ guide_ref.teaser }}
        </div>
        {% endif %}
      </div>
      {% endfor %}
    </div>
    {% endif %}
 
    <div style="font-family:var(--font-mono);font-size:10px;letter-spacing:0.15em;
                text-transform:uppercase;color:rgba(249,228,197,0.40);
                border-top:1px solid rgba(249,228,197,0.12);padding-top:16px;">
      ROAD.ADVNTR.IO · {{ guide.edition }}
    </div>
  </div>
</div>
 
</body>
</html>
```
 
---
 
## 8. CONTENT SCHEMA
 
`guides/[guide-id]/content.yaml` — universal destination-agnostic schema.
