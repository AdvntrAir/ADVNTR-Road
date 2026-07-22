/**
 * AMENDED intel collection schema — ADVNTR Road
 * v0.3 · July 2026
 *
 * This REPLACES the `intel` collection block in
 * apps/web/src/content.config.ts. Leave `fieldNotes` exactly as it is.
 *
 * WHAT CHANGED AND WHY
 *
 * Every existing field is preserved. Nothing is removed, nothing renamed —
 * the June 29 entry still validates against this. Additions are either
 * optional or carry defaults, so existing content does not need migrating.
 *
 * Added at issue level:
 *   thinWeek        — honest slow weeks instead of padding
 *   ctaPlaceSlug    — the CTA anchor, derived by the pipeline (never authored)
 *   ctaSuppressed   — true when the week is too heavy for a promotional CTA
 *   harvestStats    — audit trail for the harvest-wide/publish-narrow funnel
 *   watchList       — single-source items held back, rechecked next week
 *
 * Added per story:
 *   placeSlug       — registry slug. Drives tags, CTA, and guide matching.
 *                     parkOrRegion stays as the human-readable display label.
 *   topicSlug       — closed vocabulary
 *   tier            — lead | feature | brief. Drives CTA weighting and layout.
 *   action          — what the reader does about it
 *   take            — THE PRODUCT. <=40 words, public-facing, opinionated.
 *   confidence      — confirmed | reported
 *   primarySource*  — per-story verification anchor
 *   storyDate       — per-story publication date, for hard date filtering
 *   severity + involves* — CTA suppression flags
 *   affectsGuides   — richer per-story guide impact
 *
 * IMPORTANT — adventureRoadAngle is now INTERNAL.
 * It currently renders publicly in [slug].astro as "Angle: ...", but its
 * content is editorial notes to self. `take` is the public field. See the
 * template patch note at the bottom of this file.
 */

const intel = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/intel' }),
  schema: z.object({
    // ---- unchanged ----
    title: z.string(),
    coverageWindowStart: z.coerce.date(),
    coverageWindowEnd: z.coerce.date(),
    publishedDate: z.coerce.date(),
    trailheadSummary: z.string(),

    // ---- new, issue level ----
    thinWeek: z.boolean().default(false),
    ctaPlaceSlug: z.string().optional(),
    ctaSuppressed: z.boolean().default(false),

    topStories: z.array(
      z.object({
        // ---- unchanged ----
        storyRank: z.number(),
        parkOrRegion: z.string(),
        topic: z.string(),
        relevanceScore: z.number().optional(),
        impactScore: z.number().optional(),
        urgencyScore: z.number().optional(),
        visitorValueScore: z.number().optional(),
        explorerImpact: z.string().optional(),
        adventureRoadAngle: z.string().optional(), // INTERNAL — see note above

        // ---- new: identity and classification ----
        storyId: z.string(),        // stable slug, cross-edition dedupe
        placeSlug: z.string(),      // must exist in intel-place-registry.yaml
        topicSlug: z.enum([
          'closures', 'wildfire', 'weather', 'wildlife', 'fees',
          'reservations', 'legislation', 'infrastructure', 'crowding',
          'conservation', 'safety', 'access',
        ]),
        tier: z.enum(['lead', 'feature', 'brief']),
        action: z.enum(['plan-change', 'book-now', 'awareness-only']),

        // ---- new: THE PRODUCT ----
        take: z.string().max(260),

        // ---- new: verification ----
        confidence: z.enum(['confirmed', 'reported']),
        storyDate: z.coerce.date(),
        primarySourceUrl: z.string().url(),
        primarySourcePublisher: z.string(),
        primarySourceConfirmed: z.boolean(),
        corroboratingUrls: z.array(z.string().url()).default([]),

        // ---- new: CTA suppression ----
        severity: z.enum(['low', 'moderate', 'high']).default('low'),
        involvesFatality: z.boolean().default(false),
        involvesInjury: z.boolean().default(false),
        involvesSearchAndRescue: z.boolean().default(false),
        involvesActiveEvacuation: z.boolean().default(false),

        // ---- new: living-edition mechanism ----
        affectsGuides: z.array(
          z.object({
            guideSlug: z.string(),
            impact: z.enum([
              'content-stale', 'fee-changed', 'access-changed',
              'link-broken', 'monitor',
            ]),
            note: z.string().optional(),
          })
        ).default([]),
      })
    ),

    // ---- unchanged ----
    affectedGuides: z.array(z.string()).default([]),
    recommendedContentAngles: z.array(z.string()).default([]),
    sourceUrls: z.array(z.string()).default([]),
    optionalJson: z.record(z.string(), z.unknown()).optional(),
    beehiivUrl: z.string().optional(),
    status: z.enum(['placeholder', 'draft', 'published']).default('placeholder'),

    // ---- new: audit + carryover ----
    harvestStats: z.object({
      candidatesFound: z.number(),
      clearedVerification: z.number(),
      droppedSingleSource: z.number(),
      droppedOutsideWindow: z.number(),
      droppedDuplicate: z.number(),
      droppedPriorEdition: z.number().default(0),
    }).optional(),

    watchList: z.array(
      z.object({
        storyId: z.string(),
        headline: z.string(),
        reason: z.enum([
          'single-source', 'date-unverifiable', 'url-unresolvable',
          'outside-window', 'awaiting-primary',
        ]),
        sourceUrl: z.string().optional(),
        firstSeen: z.coerce.date(),
        weeksCarried: z.number().default(1),
      })
    ).default([]),
  }),
});

/* ---------------------------------------------------------------------------
 * TEMPLATE PATCHES REQUIRED — apps/web/src/pages/intel/[slug].astro
 *
 * 1. Stop rendering adventureRoadAngle. Delete this line:
 *
 *      {s.adventureRoadAngle && <p class="intel-article__feed-angle">Angle: {s.adventureRoadAngle}</p>}
 *
 *    Replace with the take, which is the public-facing opinion:
 *
 *      <p class="intel-article__feed-take">{s.take}</p>
 *
 *    The .intel-article__feed-angle styling can be reused; the take wants
 *    more visual weight than an italic aside, since it is the reason the
 *    page exists.
 *
 * 2. explorerImpact stays where it is, but should only render for
 *    tier lead and feature — briefs are take-only:
 *
 *      {s.tier !== 'brief' && s.explorerImpact && ( ... )}
 *
 * 3. confidence === 'reported' should render a visible marker. The reader
 *    should be able to tell what is confirmed from what is circulating.
 *    This is a feature, not a disclaimer.
 *
 * 4. Sources: link primarySourceUrl per story. Currently sourceUrls is an
 *    unused flat array at issue level.
 *
 * 5. NEW ROUTE — apps/web/src/pages/intel/tag/[slug].astro
 *    [slug].astro matches one segment only, so tag hubs need their own file.
 *    Index these; noindex the dated editions.
 * ------------------------------------------------------------------------- */
