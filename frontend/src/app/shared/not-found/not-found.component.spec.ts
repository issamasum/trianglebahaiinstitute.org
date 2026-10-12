import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { NotFound } from './not-found.component';
import { PageTitleService } from '../../page-title.service';

describe('NotFound', () => {
  it('sets the page title', async () => {
    await TestBed.configureTestingModule({
      imports: [NotFound],
      providers: [provideRouter([])],
    }).compileComponents();
    const fixture = TestBed.createComponent(NotFound);
    fixture.detectChanges();
    expect(TestBed.inject(PageTitleService).title()).toBe('Page Not Found');
  });
});
