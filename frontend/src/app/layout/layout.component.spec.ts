import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { Layout } from './layout.component';
import { FRAGMENTS, ROUTE_PATHS } from '../core/route-paths';

describe('Layout', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Layout],
      providers: [provideRouter([])],
    }).compileComponents();
  });

  it('creates with nav and footer links', () => {
    const fixture = TestBed.createComponent(Layout);
    fixture.detectChanges();
    const c = fixture.componentInstance;
    expect(c.routes).toBe(ROUTE_PATHS);
    expect(c.navLinks[1].fragment).toBe(FRAGMENTS.features);
    expect(c.footerLinks.length).toBe(3);
  });
});
