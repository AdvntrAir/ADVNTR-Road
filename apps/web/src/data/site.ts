export const site = {
  name: 'ADVNTR Road',
  parentBrand: 'ADVNTR.io',
  url: 'https://road.advntr.io',
  description:
    'Opinionated, verified, beautifully built road trip guides for national parks, coast roads, and the long way around. Tools do not have opinions. We do.',
  thesis: 'Tools do not have opinions. We do.',
  contactEmail: 'hello@advntr.io',
  beehiivPublicationUrl: 'https://advntr-road.beehiiv.com',
  nav: [
    { label: 'Guides', href: '#guides' },
    { label: 'Why ADVNTR Road', href: '#why' },
    { label: 'Free Guides', href: '#free-guides' },
    { label: 'The Trailhead', href: '#trailhead' },
    { label: 'Field Notes', href: '#field-notes' },
    { label: 'Subscribe', href: '#subscribe' },
  ],
  footerLinks: {
    product: [
      { label: 'Guides', href: '#guides' },
      { label: 'The Trailhead', href: '#trailhead' },
      { label: 'Field Notes', href: '#field-notes' },
      { label: 'Subscribe', href: '#subscribe' },
    ],
    legal: [
      { label: 'Affiliate Disclosure', href: '/affiliate-disclosure' },
      { label: 'Accuracy Disclaimer', href: '/accuracy-disclaimer' },
      { label: 'Privacy Policy', href: '/privacy' },
      { label: 'Terms', href: '/terms' },
      { label: 'Image Credits', href: '/image-credits' },
    ],
  },
} as const;
