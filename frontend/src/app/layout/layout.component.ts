import { Component } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { FRAGMENTS, ROUTE_PATHS } from '../core/route-paths';

interface NavLink {
  label: string;
  route: string;
  fragment?: string;
}

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, MatToolbarModule, MatButtonModule],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss',
})
export class Layout {
  readonly routes = ROUTE_PATHS;

  readonly navLinks: NavLink[] = [
    { label: 'Home', route: ROUTE_PATHS.home },
    { label: 'Features', route: ROUTE_PATHS.home, fragment: FRAGMENTS.features },
  ];

  readonly footerLinks: NavLink[] = [
    { label: 'Terms and Conditions', route: ROUTE_PATHS.terms },
    { label: 'Privacy Policy', route: ROUTE_PATHS.privacy },
    { label: 'Cookies Policies', route: ROUTE_PATHS.cookies },
  ];
}
