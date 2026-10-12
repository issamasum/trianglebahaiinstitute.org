import { Routes } from '@angular/router';
import { Landing } from './landing/landing.component';
import { Layout } from './layout/layout.component';
import { PlaceholderPage } from './shared/placeholder-page/placeholder-page.component';
import { NotFound } from './shared/not-found/not-found.component';

export const routes: Routes = [
  {
    path: '',
    component: Layout,
    children: [
      {
        path: '',
        pathMatch: 'full',
        component: Landing,
      },
      {
        path: 'check-in',
        component: PlaceholderPage,
        data: {
          title: 'Check-In at TBI',
          eyebrow: 'Coming Soon',
          description:
            'Event check-in is being prepared now. Soon you will be able to register your visit.',
        },
      },
      {
        path: 'bookstore',
        component: PlaceholderPage,
        data: {
          title: 'Institute Bookstore',
          eyebrow: 'Coming Soon',
          description:
            'The bookstore experience is not live yet. We are building browsing and checkout tools for the Institute.',
        },
      },
      {
        path: 'coordinate',
        component: PlaceholderPage,
        data: {
          title: 'Coordinate TBI',
          eyebrow: 'Coming Soon',
          description:
            'Coordinator tools for events, facility usage, and reporting are still on the way.',
        },
      },
      {
        path: 'sign-in',
        component: PlaceholderPage,
        data: {
          title: 'Sign In',
          eyebrow: 'Coming Soon',
          description:
            'Authentication is not available yet. Sign-in and account access will arrive in a future update.',
        },
      },
      {
        path: 'contact',
        component: PlaceholderPage,
        data: {
          title: 'Contact',
          eyebrow: 'Coming Soon',
          description:
            "We are preparing a proper contact page with the best ways to reach the Triangle Baha'i Institute team.",
        },
      },
      {
        path: 'terms',
        component: PlaceholderPage,
        data: {
          title: 'Terms and Conditions',
          eyebrow: 'Coming Soon',
          description:
            'The full terms and conditions page is not published yet, but it will be available here soon.',
        },
      },
      {
        path: 'privacy',
        component: PlaceholderPage,
        data: {
          title: 'Privacy Policy',
          eyebrow: 'Coming Soon',
          description:
            'Our privacy policy page is still being finalized and will be published here when ready.',
        },
      },
      {
        path: 'cookies',
        component: PlaceholderPage,
        data: {
          title: 'Cookies Policy',
          eyebrow: 'Coming Soon',
          description:
            'Cookie usage details are being documented and will be shared on this page soon.',
        },
      },
      {
        path: '404',
        component: NotFound,
      },
    ],
  },
  {
    path: '**',
    redirectTo: '/404',
  },
];
