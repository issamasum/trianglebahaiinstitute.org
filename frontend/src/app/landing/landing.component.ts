import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { FRAGMENTS, ROUTE_PATHS } from '../core/route-paths';

interface Feature {
  title: string;
  icon: string;
  theme: 'lime' | 'gold' | 'olive';
  description: string;
  route: string;
}

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [RouterLink, MatButtonModule, MatIconModule, MatCardModule],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.scss',
})
export class Landing {
  readonly routes = ROUTE_PATHS;
  readonly featuresFragment = FRAGMENTS.features;

  readonly features: Feature[] = [
    {
      title: 'Check-In at TBI',
      icon: 'event',
      theme: 'lime',
      route: ROUTE_PATHS.checkIn,
      description: "Check in for an event being held at the Triangle Baha'i Institute facility.",
    },
    {
      title: 'Institute Bookstore',
      icon: 'menu_book',
      theme: 'gold',
      route: ROUTE_PATHS.bookstore,
      description: 'Browse the Institute bookstore and check out books at your leisure.',
    },
    {
      title: 'Coordinate TBI',
      icon: 'bar_chart',
      theme: 'olive',
      route: ROUTE_PATHS.coordinate,
      description: 'Entry point for coordinators to manage events, check-in, and more.',
    },
  ];
}
