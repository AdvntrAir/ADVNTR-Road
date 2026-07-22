import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * Field Notes — the editorial essay layer. Durable, literary, not time-boxed.
 * Source: local Markdown now; can be swapped for a Beehiiv-RSS-backed
 * collection later without changing how the homepage consumes it (see
 * src/lib/content-adapter.ts).
 */
const fieldNotes = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/field-notes' }),
  schema: z.object({
    title: z.string(),
    excerpt: z.string(),
    publishedDate: z.coerce.date().optional(),
    status: z.enum(['placeholder', 'draft', 'published']).default('placeholder'),
    contentAngle: z.string().optional(),
  }),
});

/**
 * The Trailhead — weekly National Park Intel Packs. Field schema mirrors the
 * spec in ADVNTR_Road_Website_Launch_Report.md ("National Park Intel content
 * model"). One collection entry per issue; `topStories` holds the ranked
 * items inside that issue.
 *
 * v0.3 · July 2026 — amended per intel/content.config.INTEL-PATCH.ts.
 * placeSlug/topicSlug/tier/take/confidence/storyDate/primarySource* are
 * required per story: Stage A (stage_a_research.py) always emits them, and
 * Stage B (validate.py) fails the build before a file lacking them ever
 * reaches this collection. There is no historical entry for this schema to
 * stay backward-compatible with — the June 29 placeholder was removed rather
 * than hand-backfilled, since inventing its source URLs and takes would be
 * exactly the build-time authoring the pipeline's one rule prohibits.
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
        adventureRoadAngle: z.string().optional(), // INTERNAL — editorial note, never rendered publicly

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
        take: z.string().max(340),

        // ---- new: verification ----
        confidence: z.enum(['confirmed', 'reported']),
        storyDate: z.coerce.date(),
        primarySourceUrl: z.string().url(),
        primarySourcePublisher: z.string(),
        primarySourceConfirmed: z.boolean(),
        corroboratingUrls: z.array(z.string().url()).default([]),

        // ---- new: CTA suppression ----
        severity: z.enum(['low', 'medium', 'high']).default('low'),
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

export const collections = { 'field-notes': fieldNotes, intel };
