import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { Landing } from './landing.component';
import { FRAGMENTS, ROUTE_PATHS } from '../core/route-paths';

describe('Landing', () => {
  it('exposes features and routes', async () => {
    await TestBed.configureTestingModule({
      imports: [Landing],
      providers: [provideRouter([])],
    }).compileComponents();
    const fixture = TestBed.createComponent(Landing);
    fixture.detectChanges();
    const c = fixture.componentInstance;
    expect(c.routes).toBe(ROUTE_PATHS);
    expect(c.featuresFragment).toBe(FRAGMENTS.features);
    expect(c.features.map((f) => f.route)).toEqual([
      ROUTE_PATHS.checkIn,
      ROUTE_PATHS.bookstore,
      ROUTE_PATHS.coordinate,
    ]);
  });
});
