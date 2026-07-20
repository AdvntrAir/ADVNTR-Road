# ADVNTR Road — Build Spec: Content Schema (YAML)
### Use when: adding schema fields, fixing input validation, YAML parsing

 
### Rendering rules — read before populating
 
The template uses conditional rendering throughout. Fields marked **[REQUIRED]**
must be present or the build fails. Fields marked **[CONDITIONAL]** trigger
component rendering when populated; the section degrades to prose-only when
absent. Never invent data to fill a conditional field — omit it and let the
prose carry it.
 
**Conditional rendering logic:**
- `gateway_towns` present → renders gateway town cards in Section 02
- `gateway_towns` absent → Section 02 renders prose only
- `zone.highlights` present → renders highlights sidebar per zone in Section 04
- `zone.highlights` absent → zone renders prose only
- `businesses` present → renders business listing cards in Section 06
- `businesses` absent → Section 06 renders prose only
- `fees` / `permits` present → renders structured blocks in Section 07
- `fees` / `permits` absent → Section 07 renders prose only
- `checklist` present → renders checkbox component in Section 08
- `resources` present → renders resource link cards in Section 08
- `series` present → renders "coming next" block on back cover
```yaml
# ═══════════════════════════════════════════════════════════
# ADVNTR Road — Universal Guide Content Schema
# Source: destination.md → Gemini extraction → this file
# Version: 2.0 · June 2026
# ═══════════════════════════════════════════════════════════
 
guide:
 
  # ── METADATA ─────────────────────────────────────────────
  # [REQUIRED] All fields below are required.
 
  id:        "[guide-id]"            # URL-safe slug: olympic-np, north-cascades
  title:     "[Destination Name]"    # Full official name
  subtitle:  "[One evocative line]"  # Italic on cover, e.g. "Coast, Rain Forest, and the Mountains in Between"
  edition:   "2026 Field Edition"
  region:    "[Region]"              # e.g. Pacific Northwest / American West
  url:       "road.advntr.io/[guide-id]"
  published: "[Month Year]"
  verified:  "[Month Year]"          # Date research was last verified against official sources
  cover_map: "assets/cover-map.jpg"  # [CONDITIONAL] — omit if not ready; cover renders without it
 
  stats:                             # [REQUIRED] 4 items — Space Mono uppercase in hero
    - "[LOCATION, STATE]"
    - "[~SIZE ACRES or relevant stat]"
    - "[KEY CHARACTERISTIC]"
    - "UPDATED [MONTH YEAR]"
 
  map_bounds:                        # [REQUIRED] — bounding box for all map API calls
    north: 0.0000
    south: 0.0000
    east:  0.0000
    west:  0.0000
 
  # ── FIXED SECTIONS ───────────────────────────────────────
  # Sections 01–03 and 05–08 are fixed — same id, eyebrow, and file
  # name for every guide. Only title and subhead are destination-specific.
  # The template loops over this array; section order here = page order in PDF.
  # map_key values reference the maps block below.
 
  sections:
 
    - id:      "orientation"
      file:    "01-orientation"          # guides/[id]/prose/01-orientation.md
      eyebrow: "Orientation"
      title:   "[Destination-specific title]"      # e.g. "Where You Are"
      subhead: "[Destination-specific subhead]"    # e.g. "Three ecosystems, one peninsula."
      map_key: "orientation"             # [CONDITIONAL] — omit if no orientation map
 
    - id:      "before-you-arrive"
      file:    "02-before-you-arrive"
      eyebrow: "Before You Arrive"
      title:   "[Destination-specific title]"      # e.g. "The Drive In"
      subhead: "[Destination-specific subhead]"
      map_key: "gateway_towns"           # [CONDITIONAL]
      show_gateway_towns: true           # [CONDITIONAL] — omit if gateway_towns[] is empty
 
    - id:      "where-to-sleep"
      file:    "03-where-to-sleep"
      eyebrow: "Where to Sleep"
      title:   "[Destination-specific title]"      # e.g. "Where You Sleep Matters"
      subhead: "[Destination-specific subhead]"
      map_key: "campground_reference"    # [CONDITIONAL]
      show_campgrounds: true             # [REQUIRED for this section]
 
    # Section 04 — Experience Zones — is NOT listed here.
    # Zones are a separate loop rendered between sections 03 and 05.
    # See zones[] block below.
 
    - id:      "what-to-do"
      file:    "05-what-to-do"
      eyebrow: "What to Do"
      title:   "[Destination-specific title]"      # e.g. "The Work of Being Here"
      subhead: "[Destination-specific subhead]"
 
    - id:      "eat-resupply"
      file:    "06-eat-resupply"
      eyebrow: "Eat + Resupply"
      title:   "[Destination-specific title]"      # e.g. "Feeding Yourself"
      subhead: "[Destination-specific subhead]"
      show_businesses: true              # [CONDITIONAL] — omit if businesses[] is empty
 
    - id:      "field-notes"
      file:    "07-field-notes"
      eyebrow: "Field Notes"
      title:   "[Destination-specific title]"      # e.g. "What You Actually Need to Know"
      subhead: "[Destination-specific subhead]"
      show_fees: true                    # [CONDITIONAL] — omit if fees{} is empty
      show_permits: true                 # [CONDITIONAL] — omit if permits{} is empty
 
    - id:      "before-you-leave"
      file:    "08-before-you-leave"
      eyebrow: "Before You Leave"
      title:   "[Destination-specific title]"      # e.g. "Before You Leave Home"
      subhead: "[Destination-specific subhead]"
      show_checklist: true               # [CONDITIONAL] — omit if checklist[] is empty
      show_resources: true               # [CONDITIONAL] — omit if resources[] is empty
 
  # ── EXPERIENCE ZONES (Section 04) ────────────────────────
  # [REQUIRED] — minimum 1 zone, maximum 5.
  # Each zone renders as a full section between 03 and 05.
  # Each zone has its own prose file, optional map, optional highlights.
  # Zone section numbers are auto-calculated: 04a, 04b, 04c...
  # file values reference guides/[id]/prose/ directory.
 
  zones:
    - id:      "[zone-slug]"             # e.g. alpine, rainforest, coast
      file:    "04a-[zone-slug]"         # e.g. 04a-alpine
      eyebrow: "[Zone eyebrow]"          # e.g. "The Alpine"
      title:   "[Zone title]"            # e.g. "Above the Treeline"
      subhead: "[Zone subhead]"          # e.g. "Where the road ends and the view begins."
      map_key: "[zone-slug]"             # [CONDITIONAL] — references maps block below
      highlights:                        # [CONDITIONAL] — omit entire block if thin data
        - label: "[Short label]"         # e.g. "High Ridge Trail"
          note:  "[One-line description]"
          tags:  [consensus]             # optional — same badge system as campgrounds
        - label: "[Short label]"
          note:  "[One-line description]"
        - label: "[Short label]"
          note:  "[One-line description]"
 
    - id:      "[zone-slug]"             # [CONDITIONAL] — add or remove zone blocks as needed
      file:    "04b-[zone-slug]"
      eyebrow: "[Zone eyebrow]"
      title:   "[Zone title]"
      subhead: "[Zone subhead]"
      map_key: "[zone-slug]"             # [CONDITIONAL]
      highlights:                        # [CONDITIONAL]
        - label: ""
          note:  ""
 
    # Add zones 04c, 04d, 04e following same pattern.
    # Maximum 5 zones. Delete unused zone blocks entirely.
 
  # ── CAMPGROUNDS ──────────────────────────────────────────
  # [REQUIRED] — minimum 1 entry. All sub-fields required per brand
  # content rules unless marked [CONDITIONAL].
  # verified_date and verified_source must reflect an actual check
  # against NPS.gov, Recreation.gov, or a direct call.
 
  campgrounds:
    - id:      "[campground-slug]"       # e.g. hoh_rain_forest
      name:    "[Campground Name]"
      region:  "[REGION LABEL]"          # Uppercase — rendered as Space Mono label
                                         # e.g. "HOH RAIN FOREST, OLYMPIC NP"
      type:    "[nps|state|private|forest-service|blm]"
      featured: false                    # true = Buff top border — use for 1–2 standouts only
      lat:     0.0000
      lng:     0.0000
      open:    "[Date range or Year-round]"  # [CONDITIONAL]
      reservations:
        method: "[Recreation.gov|Call|First-come|Concessionaire]"
        type:   "[reservable|first-come]"
        fills:  "[e.g. Weeks in advance May–Sep]"   # [CONDITIONAL]
        url:    "[booking URL]"          # [CONDITIONAL] — include affiliate params
      hookups: "[none|electric|electric-water|full]"
      max_length: "[e.g. 21ft|35ft|No limit]"
      dump_station: "[Yes $X/use|No]"   # [CONDITIONAL]
      showers:  "[Yes|No]"              # [CONDITIONAL]
      pets:
        allowed:      true
        restrictions: "[e.g. On leash, campground only — no trails]"  # [CONDITIONAL]
      badges:                            # [CONDITIONAL] — include applicable badges only
        - consensus                      # 🎯 multiple sources agree
        - hidden-gem                     # 💡 underreported, single source
        - reservable                     # 🏕️ book ahead, fills fast
        - heads-up                       # ⚠️ time-sensitive condition
        - dog-friendly                   # 🐾 verified pet access
        - big-rig                        # 🚐 35ft+ confirmed
      editorial: >                       # [REQUIRED] — 2–4 sentences, honest and specific
        [Write what the campground experience actually feels like.
        What makes it worth choosing or worth avoiding.
        Be specific. No generic travel writing.]
      verified_date:   "[Month Year]"
      verified_source: "[NPS.gov|Recreation.gov|Direct call]"
      website:   "[official NPS or park page URL]"   # [CONDITIONAL]
      maps_url:  "https://maps.google.com/?q=[lat],[lng]"
 
    # Add additional campground blocks following same pattern.
    # No maximum — include every campground with enough data for a card.
    # Campgrounds with thin data stay in prose (03-where-to-sleep.md).
 
  # ── GATEWAY TOWNS ────────────────────────────────────────
  # [CONDITIONAL] — omit entire block if no gateway towns in destination.md.
  # If present, renders gateway town cards in Section 02.
  # If absent, Section 02 renders prose only from 02-before-you-arrive.md.
 
  gateway_towns:
    - id:       "[town-slug]"            # e.g. port-angeles
      name:     "[Town Name]"
      role:     "[Primary hub|Eastern entry|Fuel stop|etc.]"
      distance: "[X miles from park entrance]"   # [CONDITIONAL]
      services:                          # [CONDITIONAL] — list what's available
        - fuel
        - grocery
        - propane
        - laundry
        - rv-dump
        - medical
      rv_options:                        # [CONDITIONAL]
        - name:    "[RV Park Name]"
          website: "[URL]"
          hookups: "[Full|Electric|None]"
          pull_through: true
          notes:   "[One sentence]"
      dining:                            # [CONDITIONAL]
        - "[Restaurant name — one-line note]"
      editorial: >                       # [CONDITIONAL] — 1–3 sentences
        [What makes this town useful or interesting. Honest.
        Not a tourism board description.]
 
    # Add additional gateway town blocks as needed.
    # Delete entire block if no gateway towns exist for this destination.
 
  # ── BUSINESSES ───────────────────────────────────────────
  # [CONDITIONAL] — omit entire block if no businesses with card-quality data.
  # If present, renders business listing cards in Section 06.
  # If absent, Section 06 renders prose only from 06-eat-resupply.md.
 
  businesses:
    - id:       "[business-slug]"        # e.g. lake_crescent_lodge
      name:     "[Business Name]"
      type:     "[Restaurant|Cafe|Grocery|Fuel|Gear|Lodge|General store]"
      region:   "[REGION LABEL]"         # Uppercase Space Mono label
      lat:      0.0000                   # [CONDITIONAL]
      lng:      0.0000                   # [CONDITIONAL]
      phone:    "[+1 xxx-xxx-xxxx]"      # [CONDITIONAL]
      website:  "[URL]"                  # [CONDITIONAL]
      maps_url: "[Google Maps URL]"      # [CONDITIONAL]
      hours:    "[e.g. Daily 7am–9pm, May–Oct]"  # [CONDITIONAL]
      badges:                            # [CONDITIONAL]
        - consensus
        - hidden-gem
      editorial: >                       # [REQUIRED if card is rendered] — 2–4 sentences
        [What's actually good here. Specific dish, specific reason.
        No adjectives without evidence.]
      verified_date: "[Month Year]"
 
    # Add additional business blocks as needed.
    # Businesses with thin data stay in prose (06-eat-resupply.md).
 
  # ── FEES ─────────────────────────────────────────────────
  # [CONDITIONAL] — omit entire block if not verified for this destination.
  # If present, renders structured fees block in Section 07.
  # All values verified against official source at published date.
 
  fees:
    entrance_vehicle:    "$[X] / 7-day"
    entrance_motorcycle: "$[X] / 7-day"   # [CONDITIONAL]
    entrance_person:     "$[X] / 7-day"   # [CONDITIONAL] — walk-in/bike
    annual_park:         "$[X]"           # [CONDITIONAL]
    america_beautiful:   true             # [CONDITIONAL] — accepted yes/no
    cashless:            true             # [CONDITIONAL]
    free_days:           "[list 2026 free entrance days]"  # [CONDITIONAL]
    camping_range:       "$[X]–$[X]/night"
    dump_station:        "$[X]/use"       # [CONDITIONAL]
    backcountry_permit:  "$[X]"           # [CONDITIONAL]
    other:                               # [CONDITIONAL] — tribal permits, special use, etc.
      - name: "[Permit name]"
        fee:  "$[X]"
        note: "[Where to get it, what it covers]"
 
  # ── PERMITS ──────────────────────────────────────────────
  # [CONDITIONAL] — omit entire block if permits not required or not verified.
 
  permits:
    backcountry_required: true
    platform:   "[Recreation.gov|Self-register|Ranger station]"
    window:     "[e.g. Up to 6 months in advance]"  # [CONDITIONAL]
    walkup:     "[Yes|Limited|No]"
    bear_canister_required: true          # [CONDITIONAL]
    bear_canister_rental:                 # [CONDITIONAL]
      available: true
      location:  "[Where to rent]"
    other:                               # [CONDITIONAL]
      - name: "[Permit name]"
        required_for: "[What activity/area]"
        cost: "$[X]"
        source: "[URL or location]"
 
  # ── CHECKLIST ────────────────────────────────────────────
  # [CONDITIONAL] — renders checkbox component in Section 08.
  # Items are pre-trip planning tasks, not a packing list.
 
  checklist:
    - "[Book campground reservations — Recreation.gov opens X months out]"
    - "[Purchase/verify park pass or America the Beautiful pass]"
    - "[Download offline maps — Gaia GPS or AllTrails — before losing cell service]"
    - "[Check current road conditions and alerts at [official URL]]"
    - "[Fill fuel tank before entering — last reliable station at [town]]"
    - "[Add item specific to this destination]"
 
  # ── RESOURCES ────────────────────────────────────────────
  # [CONDITIONAL] — renders resource link cards in Section 08.
  # Official and trusted sources only. No blogs. No aggregators.
 
  resources:
    - name: "[Official source name]"     # e.g. "National Park Service — Olympic NP"
      url:  "[URL]"
      use:  "[What it's for]"            # e.g. "Road conditions, alerts, campground status"
      when: "[When to use it]"           # e.g. "Check within 48 hours of arrival"
 
    - name: "Recreation.gov"
      url:  "https://www.recreation.gov"
      use:  "Campground reservations and wilderness permits"
      when: "Open your booking window the day it goes live"
 
    # Add additional resources as needed.
 
  # ── SERIES (Back cover) ───────────────────────────────────
  # [CONDITIONAL] — renders "coming next" block on back cover.
  # Lives in series.yaml at project root; referenced here for completeness.
  # Update series.yaml once — all rebuilt guides pick up the change.
  # series.yaml format:
  #
  # series:
  #   - title: "North Cascades National Park"
  #     teaser: "The American Alps. Dramatic peaks, remote backcountry."
  #   - title: "Mount Rainier National Park"
  #     teaser: "The volcano that dominates the horizon from three states."
  #   - title: "Oregon Coast"
  #     teaser: "Three hundred miles of public coastline and working fishing towns."
  #   - title: "Columbia River Gorge"
  #     teaser: "Waterfalls, windsurfers, and the most dramatic river canyon in the Northwest."
 
  # ── MAPS ─────────────────────────────────────────────────
  # [CONDITIONAL] — each map key is referenced by map_key fields above.
  # Only define maps you have coordinates for.
  # size format: "WxH" in pixels — scale=2 is applied automatically (retina).
  # bounds must be a subset of guide.map_bounds.
  # Marker types: campground (circle, Brunswick) | gateway (square, Buff)
  #               trailhead (triangle, Moss Green) | viewpoint (diamond, Payne's Gray)
 
  maps:
    orientation:                         # Overview map — Section 01
      center_lat: 0.0000
      center_lng: 0.0000
      zoom: 9
      size: "760x440"
      bounds:
        north: 0.0000
        south: 0.0000
        east:  0.0000
        west:  0.0000
      markers:
        - label: "[GATEWAY TOWN]"
          lat:   0.0000
          lng:   0.0000
          type:  "gateway"
 
    gateway_towns:                       # [CONDITIONAL] — Section 02
      center_lat: 0.0000
      center_lng: 0.0000
      zoom: 9
      size: "760x380"
      bounds:
        north: 0.0000
        south: 0.0000
        east:  0.0000
        west:  0.0000
      markers:
        - label: "[TOWN NAME]"
          lat:   0.0000
          lng:   0.0000
          type:  "gateway"
 
    campground_reference:                # Section 03
      center_lat: 0.0000
      center_lng: 0.0000
      zoom: 10
      size: "760x480"
      bounds:
        north: 0.0000
        south: 0.0000
        east:  0.0000
        west:  0.0000
      markers:
        - label: "[CAMPGROUND NAME]"
          lat:   0.0000
          lng:   0.0000
          type:  "campground"
 
    # Zone maps — one per zone that has a map_key.
    # Key name must match the zone's map_key value exactly.
    # Add or remove zone map blocks to match zones[] above.
 
    "[zone-slug]":                       # [CONDITIONAL] — Section 04a
      center_lat: 0.0000
      center_lng: 0.0000
      zoom: 11
      size: "760x440"
      bounds:
        north: 0.0000
        south: 0.0000
        east:  0.0000
        west:  0.0000
      markers:
        - label: "[TRAILHEAD OR FEATURE]"
          lat:   0.0000
          lng:   0.0000
          type:  "trailhead"
        - label: "[CAMPGROUND IN THIS ZONE]"
          lat:   0.0000
          lng:   0.0000
          type:  "campground"
 
    "[zone-slug-2]":                     # [CONDITIONAL] — Section 04b
      center_lat: 0.0000
      center_lng: 0.0000
      zoom: 11
      size: "760x440"
      bounds:
        north: 0.0000
        south: 0.0000
        east:  0.0000
        west:  0.0000
      markers:
        - label: ""
          lat:   0.0000
          lng:   0.0000
          type:  "trailhead"
 
    # Add additional zone maps as needed. Delete unused map blocks.
```
 
### Prose file reference
 
Each `file` value in sections[] and zones[] maps to a `.md` file in
`guides/[guide-id]/prose/`. The build script converts these to HTML via
the `markdown` library with `extra` and `tables` extensions enabled.
 
```
guides/[guide-id]/prose/
├── 01-orientation.md
├── 02-before-you-arrive.md
├── 03-where-to-sleep.md
├── 04a-[zone-slug].md       ← one file per zone
├── 04b-[zone-slug].md       ← [CONDITIONAL]
├── 04c-[zone-slug].md       ← [CONDITIONAL]
├── 04d-[zone-slug].md       ← [CONDITIONAL]
├── 04e-[zone-slug].md       ← [CONDITIONAL]
├── 05-what-to-do.md
├── 06-eat-resupply.md
├── 07-field-notes.md
└── 08-before-you-leave.md
```
 
Fixed section prose files are always required. Zone prose files are
required for each zone defined in zones[]. The build script logs a
warning and renders an empty section if a prose file is missing — it
does not fail the build.
 
---
 
## 9. MAP PIPELINE
 
### Requirements
 
