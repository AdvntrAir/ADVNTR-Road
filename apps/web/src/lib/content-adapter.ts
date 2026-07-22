import { getCollection } from 'astro:content';
import { fetchBeehiivPosts } from './rss';

/**
 * Content adapter pattern: the homepage asks for "field notes" or "trailhead"
 * previews and doesn't care whether the data came from Beehiiv RSS or local
 * Markdown. Swap or add a source (e.g. a future native MDX pipeline) by
 * editing this file only.
 */

export interface PreviewCard {
  title: string;
  excerpt: string;
  href: string;
  date: Date | null;
  source: 'beehiiv-rss' | 'local-fallback';
}

// Below this many classified RSS items, prefer curated local fallback content —
// a single ambiguous or unrelated post shouldn't bump five curated placeholders.
const MIN_RSS_ITEMS = 3;

export async function getFieldNotesPreview(limit = 5): Promise<{ cards: PreviewCard[]; source: 'beehiiv-rss' | 'local-fallback' }> {
  const rssPosts = await fetchBeehiivPosts();
  const fieldNotesRss = rssPosts.filter((p) => p.classification === 'field-notes');

  if (fieldNotesRss.length >= MIN_RSS_ITEMS) {
    return {
      source: 'beehiiv-rss',
      cards: fieldNotesRss.slice(0, limit).map((p) => ({
        title: p.title,
        excerpt: p.excerpt,
        href: p.link,
        date: p.publishedDate,
        source: 'beehiiv-rss' as const,
      })),
    };
  }

  const local = await getCollection('field-notes');
  return {
    source: 'local-fallback',
    cards: local.slice(0, limit).map((entry) => ({
      title: entry.data.title,
      excerpt: entry.data.excerpt,
      href: `/field-notes/${entry.id}`,
      date: entry.data.publishedDate ?? null,
      source: 'local-fallback' as const,
    })),
  };
}

export interface TrailheadPreview {
  title: string;
  coverageWindowStart: Date;
  coverageWindowEnd: Date;
  summary: string;
  topStories: { rank: number; parkOrRegion: string; topic: string }[];
  affectedGuides: string[];
  href: string;
  source: 'beehiiv-rss' | 'local-fallback';
}

export async function getLatestTrailhead(): Promise<TrailheadPreview | null> {
  const rssPosts = await fetchBeehiivPosts();
  const trailheadRss = rssPosts.filter((p) => p.classification === 'trailhead');

  if (trailheadRss.length >= 1) {
    const latest = trailheadRss[0];
    return {
      title: latest.title,
      coverageWindowStart: latest.publishedDate ?? new Date(),
      coverageWindowEnd: latest.publishedDate ?? new Date(),
      summary: latest.excerpt,
      topStories: [],
      affectedGuides: [],
      href: latest.link,
      source: 'beehiiv-rss',
    };
  }

  const local = await getCollection('intel', (entry) => entry.data.status === 'published');
  if (local.length === 0) return null;
  const latest = local.sort((a, b) => b.data.publishedDate.getTime() - a.data.publishedDate.getTime())[0];
  return {
    title: latest.data.title,
    coverageWindowStart: latest.data.coverageWindowStart,
    coverageWindowEnd: latest.data.coverageWindowEnd,
    summary: latest.data.trailheadSummary,
    topStories: latest.data.topStories
      .sort((a, b) => a.storyRank - b.storyRank)
      .slice(0, 3)
      .map((s) => ({ rank: s.storyRank, parkOrRegion: s.parkOrRegion, topic: s.topic })),
    affectedGuides: latest.data.affectedGuides,
    href: `/intel/${latest.id}`,
    source: 'local-fallback',
  };
}
