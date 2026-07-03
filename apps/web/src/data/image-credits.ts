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

export const imageCredits: ImageCredit[] = (raw as Omit<ImageCredit, 'usage'>[])
  .filter((entry) => entry.file.startsWith('cover-photo'))
  .map((entry) => ({ ...entry, usage: guideLabels[entry.guide] ?? entry.guide }));

/**
 * The Mount Rainier cover-photo.png has no attribution record in
 * guides/mount-rainier-np/assets/image-attributions.json — it was never
 * documented in the PDF pipeline either. Flagged here rather than guessed.
 * Do not treat this image as cleared for reuse beyond this placeholder use
 * until Matt verifies its source and license.
 */
export const unverifiedImageCredits = [
  {
    file: 'mount-rainier-np.png',
    usage: 'Mount Rainier guide card on homepage (launch library, status: Pending Verification)',
    note: 'No source/license recorded in the PDF pipeline for this image. Verify before any public reuse beyond this placeholder.',
  },
];

/** Original ADVNTR Road brand assets — no external credit required. */
export const brandAssetCredits = [
  { file: 'advntr-road-green.png / -rust.png / -white.png', usage: 'Site logo (header, footer)', note: 'Original ADVNTR Road brand asset.' },
  { file: 'topo-lines.svg', usage: 'Hero and section background motif', note: 'Original ADVNTR Road brand asset.' },
];
