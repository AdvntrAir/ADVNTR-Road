import raw from './_image-attributions-raw.json';

export interface ImageCredit {
  file: string;
  title: string;
  credit: string;
  license: string;
  source: string;
  guide: string;
  usage: string;
}

const guideLabels: Record<string, string> = {
  'olympic-national-park': 'Olympic National Park guide (cover used on homepage)',
  'oregon-coast': 'Oregon Coast guide (cover used on homepage)',
  'north-cascades-national-park': 'North Cascades guide (cover used on homepage)',
  'mount-rainier-national-park': 'Mount Rainier guide (cover used on homepage)',
};

/**
 * Cover photos are recorded under the 'cover-photo' filename in most guides'
 * attribution JSON. Mount Rainier's cover was swapped to reflection-lake.jpg
 * (its own documented, public-domain entry below) after the original
 * cover-photo.png turned out to have no recorded source or license.
 */
export const imageCredits: ImageCredit[] = (raw as Omit<ImageCredit, 'usage'>[])
  .filter((entry) => entry.file.startsWith('cover-photo') || entry.file === 'reflection-lake.jpg')
  .map((entry) => ({ ...entry, usage: guideLabels[entry.guide] ?? entry.guide }));

/** No images currently lack a documented source/license. */
export const unverifiedImageCredits: { file: string; usage: string; note: string }[] = [];

/** Original ADVNTR Road brand assets — no external credit required. */
export const brandAssetCredits = [
  { file: 'advntr-road-logo-horizontal.png', usage: 'Site logo (header, footer)', note: 'Original ADVNTR Road brand asset.' },
  { file: 'advntr-road-green.png', usage: 'Organization logo (structured data)', note: 'Original ADVNTR Road brand asset.' },
  { file: 'topo-lines.svg', usage: 'Hero and section background motif', note: 'Original ADVNTR Road brand asset.' },
];
