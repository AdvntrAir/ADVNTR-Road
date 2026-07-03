/**
 * INTERNAL ONLY — not rendered on any public route.
 * Signals extracted from Weekly National Park Intel Packs that a guide needs
 * an update pass before its next edition. Fields match the spec in
 * ADVNTR_Road_Website_Launch_Report.md ("Guide update queue").
 */
export interface GuideUpdateSignal {
  guide: string;
  issue: string;
  sourceStory: string;
  urgency: 'low' | 'medium' | 'high';
  updateNeeded: string;
  verificationSource: string;
  status: 'open' | 'in-progress' | 'resolved';
}

export const guideUpdateQueue: GuideUpdateSignal[] = [
  {
    guide: 'olympic-national-park',
    issue: 'The Trailhead — Week of June 29, 2026',
    sourceStory: 'Hoh and Rialto crowd timing',
    urgency: 'medium',
    updateNeeded: 'Hoh and Rialto crowd timing updates — arrival-time guidance needs to move earlier for summer.',
    verificationSource: 'NPS Olympic current conditions page',
    status: 'open',
  },
  {
    guide: 'north-cascades-national-park',
    issue: 'The Trailhead — Week of June 29, 2026',
    sourceStory: 'Cascade River Road, Cascade Pass, and Stehekin logistics',
    urgency: 'medium',
    updateNeeded: 'Cascade River Road, Cascade Pass, and Stehekin logistics updates.',
    verificationSource: 'NPS North Cascades roads & closures page',
    status: 'open',
  },
  {
    guide: 'mount-rainier-national-park',
    issue: 'The Trailhead — Week of June 29, 2026',
    sourceStory: '2026 closure language verification',
    urgency: 'high',
    updateNeeded: 'Verified 2026 closure language required before publication (Fairfax Bridge, Ohanapecosh, Sunrise Road).',
    verificationSource: 'NPS Mount Rainier alerts & conditions page',
    status: 'open',
  },
  {
    guide: 'utah-desert-guides (planned)',
    issue: 'The Trailhead — Week of June 29, 2026',
    sourceStory: 'Early-season fire and smoke planning',
    urgency: 'low',
    updateNeeded: 'Fire and smoke planning notes needed for future Utah desert guides.',
    verificationSource: 'InciWeb / regional air quality index',
    status: 'open',
  },
  {
    guide: 'zion-national-park (planned)',
    issue: 'The Trailhead — Week of June 29, 2026',
    sourceStory: 'Early-season fire and smoke planning',
    urgency: 'low',
    updateNeeded: 'Candidate for summer safety editorial alongside Grand Canyon.',
    verificationSource: 'NPS Zion current conditions page',
    status: 'open',
  },
  {
    guide: 'grand-canyon-national-park (planned)',
    issue: 'The Trailhead — Week of June 29, 2026',
    sourceStory: 'Early-season fire and smoke planning',
    urgency: 'low',
    updateNeeded: 'Candidate for summer safety editorial alongside Zion.',
    verificationSource: 'NPS Grand Canyon current conditions page',
    status: 'open',
  },
  {
    guide: 'canyonlands-national-park (planned)',
    issue: 'The Trailhead — Week of June 29, 2026',
    sourceStory: 'Utah fire season',
    urgency: 'low',
    updateNeeded: 'Needles District fire closure awareness needed for future Utah guides, if still active.',
    verificationSource: 'NPS Canyonlands alerts page',
    status: 'open',
  },
];
