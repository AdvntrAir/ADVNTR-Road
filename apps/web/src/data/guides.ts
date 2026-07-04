export type GuideStatus =
  | 'free'
  | 'available'
  | 'coming-soon'
  | 'paid-guide-coming'
  | 'pending-verification';

export interface Guide {
  slug: string;
  title: string;
  region: string;
  format: string;
  status: GuideStatus;
  statusLabel: string;
  teaser: string;
  description: string;
  coverImage: string;
  ctaLabel: string;
  ctaHref: string;
  ctaExternal: boolean;
  secondaryLabel?: string;
  launchOrder: number;
}

/**
 * CTA hrefs for the two free guides route through /r/ redirects (see public/_redirects)
 * so the PDF destination can change without a rebuild. Both source PDFs live in the
 * "3. Stage 3 - Claude Code - Guides" Google Drive folder and are shared "anyone with
 * the link, viewer" — confirmed via Drive MCP on 2026-07-03.
 */
export const guides: Guide[] = [
  {
    slug: 'olympic-national-park',
    title: 'Olympic National Park',
    region: 'Washington, Pacific Northwest',
    format: 'Park Guide',
    status: 'free',
    statusLabel: 'Free Launch Guide',
    teaser: 'Coast, rain forest, and the mountains in between.',
    description:
      'Three ecosystems on one peninsula: alpine ridgelines, river-valley rain forest, and a coastline that runs on tide tables. This guide tells you which corner to anchor from, not just what to see.',
    coverImage: '/images/guides/olympic-np.jpg',
    ctaLabel: 'Get the free guide',
    ctaHref: '/r/olympic-np-free-guide',
    ctaExternal: true,
    secondaryLabel: 'PDF · Field Edition 2026',
    launchOrder: 1,
  },
  {
    slug: 'oregon-coast',
    title: 'Oregon Coast',
    region: 'US-101, Oregon',
    format: 'Corridor Guide',
    status: 'free',
    statusLabel: 'Free Launch Guide',
    teaser: 'Three hundred miles of public coastline and working fishing towns.',
    description:
      'Three hundred and sixty-three miles of US-101, split into the three coasts it actually is — postcard north, working-port middle, cliff-and-quiet south — with the tide windows that make or break the signature stops.',
    coverImage: '/images/guides/oregon-coast.jpg',
    ctaLabel: 'Get the free guide',
    ctaHref: '/r/oregon-coast-free-guide',
    ctaExternal: true,
    secondaryLabel: 'PDF · Field Edition 2026',
    launchOrder: 2,
  },
  {
    slug: 'north-cascades-national-park',
    title: 'North Cascades National Park',
    region: 'Washington, Pacific Northwest',
    format: 'Park Guide',
    status: 'paid-guide-coming',
    statusLabel: 'Paid Guide Coming',
    teaser: 'The American Alps. Dramatic peaks, remote backcountry.',
    description:
      'Two hours from Seattle and off the grid the moment you cross Marblemount. Built, verified, and ready — the purchase link goes live with the rest of the paid library.',
    coverImage: '/images/guides/north-cascades.jpg',
    ctaLabel: 'Purchase link coming soon',
    ctaHref: '#subscribe',
    ctaExternal: false,
    launchOrder: 3,
  },
  {
    slug: 'olympic-peninsula-loop',
    title: 'Olympic Peninsula Loop',
    region: 'Washington, Pacific Northwest',
    format: 'Loop Route Guide',
    status: 'coming-soon',
    statusLabel: 'Coming Soon',
    teaser: 'The full loop around the peninsula — US-101 as a circuit, not a corridor.',
    description:
      'The Olympic National Park guide covers the park interior. This companion route guide covers the full 101 loop around the outside of it — gateway towns, ferries, and the drive itself as the destination.',
    coverImage: '/images/guides/olympic-np.jpg',
    ctaLabel: 'Join the list for updates',
    ctaHref: '#subscribe',
    ctaExternal: false,
    launchOrder: 4,
  },
  {
    slug: 'mount-rainier-national-park',
    title: 'Mount Rainier National Park',
    region: 'Washington, Pacific Northwest',
    format: 'Park Guide',
    status: 'pending-verification',
    statusLabel: 'Pending Verification',
    teaser: 'The volcano that dominates the horizon from three states.',
    description:
      'Drafted and built, but 2026 brought real changes — the Fairfax Bridge closure, a dropped timed-entry system, an Ohanapecosh rehab. We hold this one back from sale until every closure line is re-verified against current NPS sources.',
    coverImage: '/images/guides/mount-rainier-np.jpg',
    ctaLabel: 'Verification in progress',
    ctaHref: '#subscribe',
    ctaExternal: false,
    launchOrder: 5,
  },
  {
    slug: 'columbia-river-gorge',
    title: 'Columbia River Gorge',
    region: 'Oregon & Washington border',
    format: 'Corridor Guide',
    status: 'coming-soon',
    statusLabel: 'Coming Soon',
    teaser: 'Waterfalls, windsurfers, and the most dramatic river canyon in the Northwest.',
    description:
      'The next corridor guide after the coast: waterfall alley, wind-sport towns, and a river canyon that splits two states. Research is underway.',
    coverImage: '/images/guides/oregon-coast.jpg',
    ctaLabel: 'Join the list for updates',
    ctaHref: '#subscribe',
    ctaExternal: false,
    launchOrder: 6,
  },
];

export const freeGuides = guides.filter((g) => g.status === 'free');
export const launchLibrary = [...guides].sort((a, b) => a.launchOrder - b.launchOrder);
