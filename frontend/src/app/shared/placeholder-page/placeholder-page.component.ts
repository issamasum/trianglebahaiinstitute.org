import { Component, computed, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { PageTitleService } from '../../page-title.service';
import { ROUTE_PATHS } from '../../core/route-paths';

interface PlaceholderPageData {
  title?: string;
  eyebrow?: string;
  description?: string;
  ctaLabel?: string;
  ctaRoute?: string;
}

@Component({
  selector: 'app-placeholder-page',
  standalone: true,
  imports: [RouterLink, MatButtonModule],
  templateUrl: './placeholder-page.component.html',
  styleUrl: './placeholder-page.component.scss',
})
export class PlaceholderPage {
  private readonly route = inject(ActivatedRoute);
  private readonly pageTitle = inject(PageTitleService);

  readonly routes = ROUTE_PATHS;
  readonly data = computed(
    () => (this.route.snapshot.data as PlaceholderPageData | undefined) ?? {},
  );

  constructor() {
    this.pageTitle.setTitle(this.data().title ?? 'Coming Soon');
  }
}
