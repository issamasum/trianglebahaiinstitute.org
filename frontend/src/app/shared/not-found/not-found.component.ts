import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { PageTitleService } from '../../page-title.service';
import { ROUTE_PATHS } from '../../core/route-paths';

@Component({
  selector: 'app-not-found',
  standalone: true,
  imports: [RouterLink, MatButtonModule],
  templateUrl: './not-found.component.html',
  styleUrl: './not-found.component.scss',
})
export class NotFound {
  private readonly pageTitle = inject(PageTitleService);

  readonly routes = ROUTE_PATHS;

  constructor() {
    this.pageTitle.setTitle('Page Not Found');
  }
}
