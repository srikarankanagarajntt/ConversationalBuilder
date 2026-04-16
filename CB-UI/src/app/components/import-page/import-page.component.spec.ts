import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImportPageComponent } from './import-page.component';

describe('ImportPageComponent', () => {
  let component: ImportPageComponent;
  let fixture: ComponentFixture<ImportPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ImportPageComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ImportPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
