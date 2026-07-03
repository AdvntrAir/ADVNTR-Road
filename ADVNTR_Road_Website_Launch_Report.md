# ADVNTR Road Website Launch Report

Generated 2026-07-03. Covers the new one-page launch website built at `apps/web/`
alongside the existing, untouched PDF guide pipeline.

## 1. Stack chosen and why

**Astro (static output) + TypeScript + vanilla CSS, deployed to Netlify.**

- The site is content-heavy and editorial, not app-like — Astro's static-first,
  zero-client-JS-by-default model fits, and it ships the smallest possible
  bundle for a Lighthouse-friendly launch.
- No UI framework (React/Vue/etc.) was added. Every interactive need (scroll
  reveal, mobile nav scroll) is a few lines of vanilla JS in `<script>` tags —
  adding a framework would have been dependency weight with no payoff at this
  scope.
- Content collections (`astro:content`) give Field Notes and Intel Packs a
  typed schema now, so they can grow into full articles later without a
  rearchitecture.

## 2. Repo structure summary

Existing repo root (untouched): `build.py`, `template/`, `guides/`, `design_system/`,
`docs/`, `series.yaml`, `requirements.txt`, `output/` (gitignored).

New: `apps/web/` — a self-contained Astro project with its own
`package.json`/`node_modules`, independent of the Python PDF toolchain.

```
apps/web/
├── src/
│   ├── components/     (Header, Footer, Hero, GuideCard, section components...)
│   ├── layouts/         (BaseLayout, LegalLayout)
│   ├── pages/           (index + legal pages + field-notes/intel/guides routes)
│   ├── content/          (field-notes/*.md, intel/*.md — typed collections)
│   ├── data/             (guides.ts, site.ts, image-credits.ts, internal queues)
│   ├── lib/              (rss.ts, content-adapter.ts)
│   └── styles/           (tokens.css, global.css)
├── public/               (images, _redirects, robots.txt, favicons)
├── astro.config.mjs
├── netlify.toml
└── .env.example
```

## 3. Existing PDF workflow protection notes

- No files under `template/`, `guides/`, `build.py`, `design_system/`, `docs/`,
  or `series.yaml` were modified, moved, or deleted.
- `.gitignore` already excluded `output/` and `.venv/`; nothing there was touched.
- One pre-existing stray issue found at session start — `.env.example` had been
  deleted in the working tree (unrelated to this task) — it was restored from
  git history (`git show HEAD:.env.example`) before any other work began.
- Verified live: `.venv/bin/python build.py --guide olympic-np --no-maps` still
  builds `output/olympic-np-2026.pdf` successfully (see §26).

## 4. Claude Code Skills and Tools Used

**Discovered and used:**
- Beehiiv MCP (`dbf14817-...`) — `list_publications`, `get_publication`,
  `list_subscribe_forms`, `list_external_rss_feeds`, `list_site_redirects`,
  `list_posts`. Used for real discovery, not guessed values.
- Google Drive MCP (`b097a13f-...`) — `search_files`, `get_file_metadata`,
  `get_file_permissions`. Used to locate and confirm public sharing on the
  canonical Olympic and Oregon Coast PDFs.
- `frontend-design` skill — invoked for a design critique pass (see §9 and
  the design notes below). Available, installed, and invoked successfully.
- Claude Preview tools (`preview_start`, `preview_screenshot`,
  `preview_eval`, `preview_snapshot`, `preview_resize`, `preview_console_logs`,
  `preview_network`) — used for desktop/mobile visual QA (see §25).
- Astro's built-in `astro check` (via `@astrojs/check` + `typescript`,
  installed as dev dependencies) — used for type/diagnostic checking.

**Available but not used:**
- `ui-ux-pro-max` skill — overlapping with `frontend-design`; only one design
  pass was run to avoid conflicting direction.
- `deploy-to-vercel` / Vercel MCP tools — explicitly out of scope; this is a
  Netlify launch per the brief.
- Canva, DocuSign, and other small-business plugin tools — not relevant to a
  static site build.

**Missing tools that would have helped:**
- No Lighthouse-in-browser MCP tool was available in this environment; performance
  was optimized by construction (static HTML, no client JS frameworks, lazy
  images) but not measured with an actual Lighthouse run. See §25 and §29 for
  the manual-check fallback.
- No direct Netlify MCP/CLI was available to actually create the site or
  verify DNS; deployment steps are documented for Matt to run (§15–16).

**Manual setup Matt should consider:** see §29 (remaining launch blockers) and
§28 (recommended next prompt).

**`pbakaus/impeccable` frontend-design skill:** The skill referenced in the
brief (`npx skills add pbakaus/impeccable --skill frontend-design`) was not a
separately installable package in this environment — the `frontend-design`
skill already present in the Claude Code skill list was used instead, and it
covers the same brief (typography, hierarchy, restraint, avoiding generic
AI-landing-page patterns). It was invoked once, mid-build, against the actual
homepage code and screenshots. Concrete changes it drove:
- Removed pill-shaped buttons and pill status badges (the single biggest
  "generic SaaS" tell) in favor of square-cornered buttons and a dot-marker +
  small-caps label pattern for status tags.
- Replaced heavy drop-shadow card elevation with a hairline border + top
  accent rule (`border-top: 2px solid var(--color-brunswick)`), echoing the
  PDF guides' own card language instead of a generic SaaS shadow system.
- Added a signature element: a thin masthead "folio" bar under the header
  (`Pacific Northwest Edition · Vol. 01 · 2026 · Verified Guides`), directly
  reusing the running-header pattern already present in the PDF guide
  template (`visual-opener__data`), so the web site visually cites the print
  product instead of inventing a new, generic pattern.
- Added a Playfair Display drop cap to the manifesto section's lead paragraph
  for a literary/print cue.

## 5. Website files added

See the file tree in §2. Full list (39 source + content files, plus images and
config) is in the repo under `apps/web/`.

## 6. Website files modified

None outside `apps/web/` and the root `.env.example` restoration (§3). No
existing repo file was edited.

## 7. Pages and sections created

One page (`/`) with all required sections: Hero, Manifesto, Free Guides,
Launch Library, Why Different, How It Works, Field Notes preview, The
Trailhead preview, Subscribe, Trust Band, FAQ (with schema). Plus:
`/affiliate-disclosure`, `/accuracy-disclaimer`, `/privacy`, `/terms`,
`/image-credits`, `/field-notes`, `/field-notes/[slug]`, `/intel`,
`/intel/[slug]`, `/guides/[slug]` (6 static guide pages), and `/404`.

## 8. Components created

`Header`, `Footer`, `Hero`, `Manifesto`, `FreeGuides`, `LaunchLibrary`,
`GuideCard`, `WhyDifferent`, `HowItWorks`, `FieldNotesPreview`,
`TrailheadPreview`, `SubscribeSection`, `SubscribeForm`, `TrustBand`, `FAQ`.

## 9. Brand system implementation notes

Colors, type families, and spacing scale ported from
`template/styles/tokens.css` into `apps/web/src/styles/tokens.css` (web-only
subset — print-specific units dropped, rem-based type scale added for
responsive behavior). Google Fonts used for Playfair Display, Inter, Space
Mono, and Titan One (brand mark, currently unused — reserved). Topographic
line motif reused verbatim (`template/assets/topo-lines.svg`) as a background
texture in the hero, footer, Trailhead, and Subscribe sections. See §4 for the
design-critique changes that moved the button/tag/card language away from
generic SaaS defaults.

## 10. SEO implementation notes

Per-page unique title/description, canonical URLs against `https://road.advntr.io`,
Open Graph + Twitter Card meta (using the existing 1200×630 Beehiiv-hosted
ADVNTR Road logo asset as the default share image — no new placeholder image
was invented), `robots.txt`, and an auto-generated sitemap via
`@astrojs/sitemap`. Semantic headings throughout, alt text on all meaningful
images, a skip-to-content link, and visible focus states via `:focus-visible`.

## 11. AEO and schema implementation notes

JSON-LD emitted: `Organization` + `WebSite` (every page, via `BaseLayout`),
`FAQPage` (homepage, generated from the same `faqs` array that renders the
visible FAQ section — no content duplication), `DigitalDocument` (each
`/guides/[slug]` page, with `isAccessibleForFree` reflecting real status),
`Article` (each Field Notes entry).

## 12. Beehiiv MCP discovery results

- Publication: **ADVNTR Road** (`pub_deb2e42d-316d-4040-aad7-01ca6aa0189e`),
  public URL `https://advntr-road.beehiiv.com/`, not private, not white-labeled.
- **No custom subscribe form exists yet** (`list_subscribe_forms` returned 0
  results) and **no external RSS feed is configured** on the Beehiiv side.
- **One published post** exists: "Oregon Coast" (tagged Road Trip / Oregon /
  Pacific Northwest / Oregon Coast) — a guide-announcement post, not an essay
  or an Intel Pack. It doesn't match the Trailhead keyword classifier, so it
  falls into the ambiguous/Field-Notes bucket per the documented rule, but
  the homepage's minimum-RSS-item threshold (3) keeps the curated Field Notes
  placeholders active until more real posts accumulate — see §14.
- No site redirects were configured on the Beehiiv side (`list_site_redirects`
  returned 0).

## 13. Beehiiv integration notes

`SubscribeForm.astro` implements the exact fallback order from the brief:
form action → embed URL → publication subscribe page → placeholder. Because
no form or embed exists yet (§12), it currently renders as a styled
link-out button to `https://advntr-road.beehiiv.com/subscribe`, opening in a
new tab. Set `PUBLIC_BEEHIIV_FORM_ACTION` or `PUBLIC_BEEHIIV_EMBED_URL` in
Netlify's environment once Matt creates a subscribe form in Beehiiv, and the
component automatically switches to an inline form/embed — no code change
needed. No Beehiiv API key is used or required anywhere in the site.

## 14. Beehiiv RSS integration notes

`src/lib/rss.ts` fetches `https://rss.beehiiv.com/feeds/CYY7cCTNl3.xml` at
**build time** (not client-side), parses it with `fast-xml-parser`, and
classifies each post as `trailhead` (title/category contains "national park
intel", "park intel", "weekly intel", or "trailhead") or `field-notes`
(everything else, including ambiguous posts — documented in code). A failed
fetch returns `[]` and never throws, so the static build always succeeds.

`src/lib/content-adapter.ts` is the source-agnostic layer the homepage
actually calls: `getFieldNotesPreview()` and `getLatestTrailhead()`. Today,
with only 1 ambiguous RSS post live, both sections render from local fallback
content (`src/content/field-notes/*.md` and `src/content/intel/*.md`) —
this is by design (a `MIN_RSS_ITEMS = 3` threshold prevents one stray post
from displacing five curated placeholders). **Current state: both homepage
sections are showing local fallback content, clearly labeled as such in the
rendered UI.** Swapping to live RSS requires no code change — it happens
automatically once enough matching posts are published.

## 15. Netlify deployment instructions

1. In Netlify: **New site from Git**, pick this repo.
2. Set **Base directory** to `apps/web` (the `netlify.toml` inside that
   folder assumes this; alternatively point Netlify at the repo root and
   uncomment `base = "apps/web"` in `apps/web/netlify.toml`).
3. Build command: `npm run build`. Publish directory: `dist`.
4. Node version: 22 (set via `netlify.toml` → `[build.environment]`).
5. Environment variables to set in Netlify (all safe to expose, `PUBLIC_`
   prefix, no secrets): `PUBLIC_BEEHIIV_FORM_ACTION`,
   `PUBLIC_BEEHIIV_EMBED_URL`, `PUBLIC_BEEHIIV_PUBLICATION_URL` (default
   `https://advntr-road.beehiiv.com`), `PUBLIC_BEEHIIV_RSS_URL` (default
   `https://rss.beehiiv.com/feeds/CYY7cCTNl3.xml`). See `apps/web/.env.example`.
6. Deploy. No paid services or credentials are required for the build to
   succeed — confirmed locally with `npm run build` using only the `.env.example`
   defaults.

## 16. road.advntr.io subdomain setup instructions

1. In Netlify → **Domain management** → **Add a domain** → enter
   `road.advntr.io`.
2. At your DNS provider for `advntr.io`, add a **CNAME** record:
   `road` → `<your-site-name>.netlify.app` (Netlify shows the exact target
   after you add the domain). If the DNS provider doesn't support CNAME
   flattening at the subdomain level, Netlify's own instructions on the
   domain page will show the correct alternative record.
3. Wait for DNS propagation (usually minutes, can take longer), then confirm
   HTTPS is issued (Netlify auto-provisions via Let's Encrypt once DNS
   resolves).
4. After propagation, verify: `https://road.advntr.io` loads over HTTPS,
   redirects `http://` → `https://` automatically, and `astro.config.mjs`'s
   `site: 'https://road.advntr.io'` matches — so canonical URLs, the
   sitemap, and Open Graph tags are already correct for this domain with no
   further code changes.

## 17. Redirect and QR infrastructure notes

`apps/web/public/_redirects` implements `/r/[slug]` as 302s (per spec — these
are living pointers, not permanent moves):

- `/r/olympic-np-free-guide` → the confirmed public Google Drive PDF link
- `/r/oregon-coast-free-guide` → the confirmed public Google Drive PDF link
- `/r/guide-library`, `/r/subscribe`, `/r/latest-trailhead`,
  `/r/latest-field-note` → homepage anchors (no dedicated archive pages are
  live yet for the last two — update these two lines once `/intel` and
  `/field-notes` have enough real content to be the better destination)

Every future guide QR should encode `https://road.advntr.io/r/[slug]` and get
a new line added to this file — no rebuild of an already-printed guide is
ever required to change where its QR code points.

## 18. Legal page status

`/affiliate-disclosure`, `/accuracy-disclaimer`, `/privacy`, `/terms`,
`/image-credits` all exist, styled consistently via `LegalLayout.astro`, each
flagged at the top as **"Launch Draft — Matt Review Required"**. None should
be treated as final legal advice.

## 19. Field Notes content model status

`src/content.config.ts` defines a typed `field-notes` collection
(title, excerpt, publishedDate, status, contentAngle). Seeded with the 5
placeholder titles from the brief, each marked `status: "placeholder"` and
flagged as such on its own page. Ready to become real MDX/Markdown essays by
editing the same files — no schema change needed.

## 20. Existing asset usage

Reused directly from the repo: all four built guides' cover photos
(`guides/*/assets/cover-photo.*`), the three brand logo variants
(`template/assets/logos/`), and the topographic line motif
(`template/assets/topo-lines.svg`). Reused from Beehiiv: the existing
1200×630 ADVNTR Road logo thumbnail as the default social share image
(no new OG image was generated).

## 21. Placeholder assets still needed

- **Mount Rainier cover photo** (`guides/mount-rainier-np/assets/cover-photo.png`)
  has no attribution record in the PDF pipeline's own `image-attributions.json`
  — flagged on `/image-credits` under "Needs verification." Do not reuse it
  beyond this placeholder card until Matt confirms its source/license.
- No dedicated OG/social image exists at `road.advntr.io` scale yet; the
  Beehiiv-hosted logo thumbnail is used as an interim, real (not invented)
  substitute.

## 22. Live guide CTA status

- **Olympic National Park**: live, confirmed public Google Drive PDF link
  (`.../file/d/18W4_o3vpQpiyCQppZNtpNOsyRAmkHpHl/view`), routed through
  `/r/olympic-np-free-guide`.
- **Oregon Coast**: live, confirmed public Google Drive PDF link
  (`.../file/d/17r07KEwe7wf_ljZXj1uAa_aJw38HeZnJ/view`), routed through
  `/r/oregon-coast-free-guide`.
- Both confirmed "anyone with the link, viewer" via Drive MCP on 2026-07-03,
  and both are the canonical copies inside the "3. Stage 3 - Claude Code -
  Guides" Drive folder (not an older/duplicate copy elsewhere in Drive).

## 23. Gumroad placeholder status

Gumroad is not configured. Every non-free guide card's CTA
(`North Cascades`, `Olympic Peninsula Loop`, `Mount Rainier`,
`Columbia River Gorge`) points to `#subscribe` instead of a purchase link, and
is visually disabled/secondary rather than styled as a live "Buy" button. No
Gumroad product IDs or links are referenced anywhere in the code.

## 24. Build results

`npm run build` — **success**, 21 pages generated, 0 errors. `npx astro check`
— **0 errors, 0 warnings** (only pre-existing `zod` deprecation hints from
Astro's content-collections type re-export, not actionable). No ESLint is
configured in this project (none existed to extend, and adding one wasn't
necessary for this scope) — `astro check` is the type/diagnostic gate in use.

## 25. Design verification results

Verified via Claude Preview tools against the live dev server:
- **Desktop (1440×900)**: hero, manifesto, free guides, launch library,
  Trailhead, subscribe, trust band, FAQ, and footer all screenshot-verified
  after the design-critique pass.
- **Mobile (375×812)**: hero and header verified; header nav is a
  horizontally scrollable row (with a right-edge fade mask hinting
  scrollability) rather than a hamburger menu, by deliberate choice for a
  one-page site with anchor navigation.
- **Console**: no runtime errors (only Vite HMR debug logs during dev).
- **Accessibility**: skip link, `:focus-visible` outlines, semantic
  landmarks/headings, alt text on all content images, `prefers-reduced-motion`
  respected for both the CSS reveal transitions and `scroll-behavior`.
- **Lighthouse**: no in-environment Lighthouse tool was available (§4);
  manual check recommended post-deploy via Chrome DevTools or
  `netlify.com`'s built-in Lighthouse panel. The build is static HTML/CSS
  with minimal JS by construction, which should score well by default.

## 26. PDF workflow validation results

Ran `.venv/bin/python build.py --guide olympic-np --no-maps` after all web
changes were made — **succeeded**, wrote `output/olympic-np.html` and
`output/olympic-np-2026.pdf` via WeasyPrint, no errors. `git status` confirms
no existing repo files outside `apps/web/` were touched.

## 27. Remaining launch blockers

- Netlify site itself has not been created (no Netlify MCP/CLI access in
  this environment) — §15 has the exact steps for Matt.
- `road.advntr.io` DNS has not been configured — §16.
- No Beehiiv subscribe form/embed exists yet — site currently link-outs to
  the publication's subscribe page (§13); safe, but an inline embed would
  convert better.
- Contact email (`hello@advntr.io`) is a placeholder — confirm or replace.
- Gumroad is not configured — all paid guide CTAs are intentionally inert.

## 28. Recommended next prompt for Matt

> "Create the Netlify site for apps/web, set the environment variables from
> apps/web/.env.example, and once it's live, help me set up road.advntr.io
> as the custom domain and verify DNS."

## 29. Recommended commit message

```
Add ADVNTR Road launch website (apps/web) alongside the PDF pipeline

One-page Astro site: hero, manifesto, free/launch guide libraries,
Field Notes and Trailhead previews (Beehiiv-RSS-first with local
fallback), subscribe, trust band, FAQ w/ schema, legal pages, and
scaffolded field-notes/intel/guides routes. Netlify + QR redirect
config included. PDF pipeline untouched and re-verified working.
```

## 30. National Park Intel content model status

`intel` content collection defined in `src/content.config.ts` with every
field from the spec (`coverageWindowStart/End`, `publishedDate`,
`trailheadSummary`, `topStories[]` with `storyRank`/`parkOrRegion`/`topic`/
scores/`explorerImpact`/`adventureRoadAngle`, `affectedGuides`,
`recommendedContentAngles`, `sourceUrls`, `optionalJson`, `beehiivUrl`,
`status`). Seeded with one representative issue
(`src/content/intel/2026-06-29-weekly-intel.md`) covering the sample stories
from the brief (Olympic crowd timing, North Cascades logistics, Mount Rainier
verification, Utah desert fire/smoke).

## 31. The Trailhead homepage section status

Live on the homepage (`TrailheadPreview.astro`), currently rendering the
local fallback issue (§14) with coverage window, one-paragraph summary, top 3
ranked stories, affected guides, and a subscribe CTA — clearly labeled as
fallback content in the rendered markup.

## 32. Guide Update Queue status

Internal-only data file at `apps/web/src/data/guide-update-queue.ts` — **not
rendered on any public route.** Seeded with the exact 6 signals from the
brief (Olympic Hoh/Rialto, North Cascades Stehekin/Cascade River Road, Mount
Rainier 2026 verification, Utah desert fire/smoke, Zion/Grand Canyon summer
safety, Canyonlands Needles closure).

## 33. Intel to Field Notes backlog status

Internal-only data file at `apps/web/src/data/content-angle-backlog.ts` —
seeded with all 5 backlog titles from the brief, each with a one-line angle
and source issue reference, status `idea` (not auto-published).

## 34. Weekly Intel workflow recommendation

1. Monday 6am Central scheduled Intel Pack runs (existing process, unchanged).
2. Matt reviews for tone, accuracy, and source quality.
3. Publish the edited version as a Beehiiv issue, tagged with a title/category
   containing "Trailhead" or "Park Intel" so the site's RSS classifier
   (§14) correctly buckets it away from Field Notes.
4. Netlify rebuilds automatically on the next deploy (or trigger manually) —
   the homepage pulls Beehiiv RSS at build time, no code change needed.
5. Convert any `recommendedContentAngles` into a new file in
   `src/content/field-notes/`.
6. Convert any guide-impacting findings into a new entry in
   `src/data/guide-update-queue.ts`.

---

## Final Launch Checklist

- [ ] Netlify deploy successful
- [ ] road.advntr.io DNS configured
- [ ] Beehiiv form tested
- [ ] Beehiiv RSS tested
- [ ] Olympic CTA tested
- [ ] Oregon Coast CTA tested
- [ ] All legal placeholder pages reviewed
- [ ] Image credits reviewed
- [ ] Mobile layout checked
- [ ] Lighthouse checked
- [ ] QR redirects tested
- [x] PDF workflow not broken — verified via local build, §26
- [x] The Trailhead section renders — verified, §31
- [x] Intel Pack fallback content works — verified, §14/§31
- [x] Beehiiv RSS classification works or limitation is documented — documented, §12/§14
- [x] Guide Update Queue created — §32
- [x] Intel-generated Field Notes backlog created — §33
