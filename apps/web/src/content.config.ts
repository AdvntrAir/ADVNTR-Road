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
 */
const intel = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/intel' }),
  schema: z.object({
    title: z.string(),
    coverageWindowStart: z.coerce.date(),
    coverageWindowEnd: z.coerce.date(),
    publishedDate: z.coerce.date(),
    trailheadSummary: z.string(),
    topStories: z.array(
      z.object({
        storyRank: z.number(),
        parkOrRegion: z.string(),
        topic: z.string(),
        relevanceScore: z.number().optional(),
        impactScore: z.number().optional(),
        urgencyScore: z.number().optional(),
        visitorValueScore: z.number().optional(),
        explorerImpact: z.string().optional(),
        adventureRoadAngle: z.string().optional(),
      })
    ),
    affectedGuides: z.array(z.string()).default([]),
    recommendedContentAngles: z.array(z.string()).default([]),
    sourceUrls: z.array(z.string()).default([]),
    optionalJson: z.record(z.string(), z.unknown()).optional(),
    beehiivUrl: z.string().optional(),
    status: z.enum(['placeholder', 'draft', 'published']).default('placeholder'),
  }),
});

export const collections = { 'field-notes': fieldNotes, intel };
