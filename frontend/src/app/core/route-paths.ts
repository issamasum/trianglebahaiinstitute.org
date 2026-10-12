/** Single source of truth for app URLs and anchor fragments. */
export const ROUTE_PATHS = {
  home: '/',
  checkIn: '/check-in',
  bookstore: '/bookstore',
  coordinate: '/coordinate',
  signIn: '/sign-in',
  contact: '/contact',
  terms: '/terms',
  privacy: '/privacy',
  cookies: '/cookies',
  notFound: '/404',
} as const;

export const FRAGMENTS = {
  features: 'features',
} as const;
