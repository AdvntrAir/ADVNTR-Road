# ADVNTR Road Destination Research File

Fill in as much verified research as possible. Leave fields blank or mark `UNKNOWN` rather
than inventing data — campground fees, closures, and reservation details must be verifiable
before publication. This file is the single source Codex/Claude uses to generate
`guides/[destination-id]/content.yaml` and the `prose/` files.

---

## 1. Guide Metadata

- **Destination name:** (e.g. "North Cascades National Park")
- **Guide slug:** (lowercase-hyphenated, e.g. `north-cascades`. Becomes `guides/[slug]/`.)
- **Subtitle:** One line, the cover tagline (e.g. "The American Alps. Dramatic peaks, remote backcountry.")
- **Region:** (e.g. "Pacific Northwest - Washington State")
- **Edition:** (e.g. "2026 Field Edition")
- **Published date:** (e.g. "June 2026")
- **Verified date:** (e.g. "June 2026" — the date all fees/closures/reservations were checked)
- **URL:** (e.g. "road.advntr.io/north-cascades")
- **Cover word(s):** The 1-2 word display type on the cover, as separate lines for the line
  break (e.g. "North" / "Cascades"). **Required** — without this the build falls back to the
  first word of the destination name, which usually looks wrong.
- **Cover footer tagline:** Short 3-part phrase under the cover subtitle (e.g.
  "No timed entry / offline first / big-rig routing matters"). Optional — omit the line
  entirely if nothing fits.
- **Cover photo:** The single strongest, most recognizable photo of the destination — this
  is a full-bleed photo cover, not an illustration. Same licensing rules as every other photo
  (see Image Sourcing below). If nothing suitable is found yet, leave it blank; the guide
  still builds without it.
- **Stats (4 short caps-case facts for the cover):**
  - County/region, state
  - Acreage (e.g. "~236,000 ACRES")
  - One distinguishing fact (glaciers, ecosystems, lake count, etc.)
  - "UPDATED [Month Year]"
- **Map bounds (decimal lat/lng, north/south/east/west):** Needed for the live map fetches.

## 2. Experience Zones

List 1-5 distinct destination areas (e.g. for Mount Rainier: Paradise, Sunrise, Carbon
River/Mowich Lake closure). For each zone:

- Zone name
- One-line identity (what makes this zone distinct)
- Highlights (3-6 bullet points: trail name, distance, why it matters)
- Known closures, construction, or access restrictions for this edition's season
- Big-rig accessibility notes

## 3. Section Research (Sections 01-08)

Mirror the fixed 8-section structure. For each, give the raw research; prose gets written
from this, not the other way around.

- **01 — Orientation:** What two-sentence reality defines visiting this year? Road corridors,
  closures, headline 2026 reality.
- **02 — Before You Arrive:** Gateway towns (name, role, distance to park, key services,
  RV/big-rig notes), approach roads, tunnel/bridge clearances, fuel notes.
- **03 — Where To Sleep:** Campground-by-campground rig-size guidance (see Section 5 below for
  the structured data), plus a rig-size stratification summary.
- **04a-04e — Experience Zones:** One file per zone from Section 2 above. Only create as many
  `04x` files as you have zones — omit unused letters entirely, don't leave them blank.
- **05 — What To Do:** Activities by traveler type (RV/van, tent, day-trip/lodge), a
  rig-size-vs-corridor table if useful, "top experiences" list.
- **06 — Eat + Resupply:** Gateway town resupply notes, plus the structured Businesses list
  (Section 6 below).
- **07 — Field Notes:** Fees, permits, cell service reality, seasonal windows, current-year
  closures/headaches.
- **08 — Before You Leave Home:** A practical checklist (each line will render as a checkbox)
  and key external resources (NPS page, Recreation.gov, relevant DOT/closure tracker, offline
  map tool).

## 4. Campground Data

One block per campground. Do not invent missing fields — mark `UNKNOWN` and flag for
verification before publishing.

```
- Name:
- Region/corridor label (e.g. "PARADISE CORRIDOR, MOUNT RAINIER NP"):
- Featured? (true for the 1-2 campgrounds most travelers should default to):
- Lat/Lng:
- Reservation method (Recreation.gov / First-come / Closed / Direct booking):
- Reservation URL (if applicable):
- Hookups (none / partial / full hookups):
- Max vehicle length:
- Dump station / water fill status (note clearly if closed for the edition's season):
- Pets allowed + restrictions:
- Badges (choose from: consensus, reservable, heads-up, big-rig, dog-friendly, hidden-gem):
- Short tags (2-3 words each, e.g. "No Dump 2026", "Dry Camping"):
- Editorial note (2-4 sentences, the actual advice):
- Verified date:
- Website (NPS page or official source):
- Photo: see "Image Sourcing" below. Leave blank if none found — do not use a
  copyrighted/unlicensed photo.
```

## 5. Gateway Towns & Businesses

For each gateway town: role, distance to park, key services, RV/big-rig notes, and any
specific businesses worth recommending. For each business:

```
- Name:
- Type (Restaurant/Brewery, Gear, etc.):
- Town/Location:
- Phone:
- Website:
- Hours:
- Price range ($ / $$ / $$$):
- Editorial note (1-2 sentences, why it's worth the stop):
- Verified date:
```

## 6. Map Markers

For each map panel needed (orientation, gateway towns, campground reference, zone-specific,
closure reference): center lat/lng, zoom, and a marker list (label, lat/lng, type: trailhead /
gateway / campground / closure).

## 7. Image Sourcing

Every photo in the guide must be legally usable in a commercial product. In practice this
means:

- **Public domain or CC-licensed only.** Wikimedia Commons categories for NPS-administered
  sites (search `Category:[Site Name]`) are the most reliable source — most NPS employee
  photos are public domain. Always verify the license on the individual file page before
  using it, not just the category.
- **Private businesses (RV parks, restaurants, gear shops) almost never have a usable public
  photo.** Don't substitute a copyrighted photo from their own website. Leave the card
  text-only, or get explicit permission from the business and note that in
  `image-attributions.json`.
- Record every image's title, credit, license, and source URL in
  `guides/[slug]/assets/image-attributions.json` — this is required for every image added,
  no exceptions.

## 8. Research Quality Flags

List anything you're unsure about, couldn't verify, or that's likely to change before
publication (pending construction, a reservation system under review, a fee increase
rumored but not confirmed, etc.).
