import { XMLParser } from 'fast-xml-parser';

export interface RssPost {
  title: string;
  link: string;
  excerpt: string;
  publishedDate: Date | null;
  categories: string[];
  classification: 'trailhead' | 'field-notes';
}

const RSS_URL = import.meta.env.PUBLIC_BEEHIIV_RSS_URL || 'https://rss.beehiiv.com/feeds/CYY7cCTNl3.xml';

const TRAILHEAD_KEYWORDS = ['national park intel', 'park intel', 'weekly intel', 'the trailhead', 'trailhead'];

function classify(title: string, categories: string[]): 'trailhead' | 'field-notes' {
  const haystack = [title, ...categories].join(' ').toLowerCase();
  if (TRAILHEAD_KEYWORDS.some((kw) => haystack.includes(kw))) return 'trailhead';
  // Ambiguous posts fall through to Field Notes per the homepage fallback rule —
  // documented in ADVNTR_Road_Website_Launch_Report.md ("Beehiiv RSS classification").
  return 'field-notes';
}

function stripHtml(input: string): string {
  return input.replace(/<[^>]*>/g, '').trim();
}

/**
 * Fetches and parses the public Beehiiv RSS feed at build time. Never throws —
 * a failed fetch (offline build, feed down, malformed XML) returns an empty
 * array so the static build always succeeds and callers fall back to local
 * content. This must stay a public, credential-free request.
 */
export async function fetchBeehiivPosts(): Promise<RssPost[]> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    const res = await fetch(RSS_URL, { signal: controller.signal });
    clearTimeout(timeout);
    if (!res.ok) return [];

    const xml = await res.text();
    const parser = new XMLParser({ ignoreAttributes: false });
    const parsed = parser.parse(xml);
    const items = parsed?.rss?.channel?.item;
    if (!items) return [];

    const list = Array.isArray(items) ? items : [items];
    return list.map((item: Record<string, unknown>): RssPost => {
      const title = String(item.title ?? 'Untitled');
      const rawCategory = item.category;
      const categories = Array.isArray(rawCategory)
        ? rawCategory.map(String)
        : rawCategory
          ? [String(rawCategory)]
          : [];
      const pubDate = item.pubDate ? new Date(String(item.pubDate)) : null;
      const description = String(item.description ?? item['content:encoded'] ?? '');
      return {
        title,
        link: String(item.link ?? ''),
        excerpt: stripHtml(description).slice(0, 220),
        publishedDate: pubDate && !Number.isNaN(pubDate.getTime()) ? pubDate : null,
        categories,
        classification: classify(title, categories),
      };
    });
  } catch {
    return [];
  }
}
