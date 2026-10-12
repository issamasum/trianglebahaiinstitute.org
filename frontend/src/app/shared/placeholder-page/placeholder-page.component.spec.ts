import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, provideRouter } from '@angular/router';
import { PlaceholderPage } from './placeholder-page.component';
import { PageTitleService } from '../../page-title.service';

async function setup(data: unknown) {
  await TestBed.configureTestingModule({
    imports: [PlaceholderPage],
    providers: [provideRouter([]), { provide: ActivatedRoute, useValue: { snapshot: { data } } }],
  }).compileComponents();
  const fixture = TestBed.createComponent(PlaceholderPage);
  fixture.detectChanges();
  return fixture;
}

describe('PlaceholderPage', () => {
  it('uses the route data title', async () => {
    await setup({ title: 'Sign In' });
    expect(TestBed.inject(PageTitleService).title()).toBe('Sign In');
  });

  it('falls back to Coming Soon without a title', async () => {
    await setup({});
    expect(TestBed.inject(PageTitleService).title()).toBe('Coming Soon');
  });

  it('falls back when data is undefined', async () => {
    await setup(undefined);
    expect(TestBed.inject(PageTitleService).title()).toBe('Coming Soon');
  });
});
