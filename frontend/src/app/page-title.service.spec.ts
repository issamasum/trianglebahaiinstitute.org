import { TestBed } from '@angular/core/testing';
import { PageTitleService } from './page-title.service';

describe('PageTitleService', () => {
  let service: PageTitleService;

  beforeEach(() => {
    service = TestBed.inject(PageTitleService);
  });

  it('starts empty', () => {
    expect(service.title()).toBe('');
  });

  it('sets title and document title', () => {
    service.setTitle('Home');
    expect(service.title()).toBe('Home');
    expect(document.title).toBe('Home – myTBI');
  });

  it('uses default document title when empty', () => {
    service.setTitle('');
    expect(document.title).toBe('myTBI');
  });
});
