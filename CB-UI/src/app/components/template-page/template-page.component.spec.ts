import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TemplatePageComponent } from './template-page.component';

describe('TemplatePageComponent', () => {
  let component: TemplatePageComponent;
  let fixture: ComponentFixture<TemplatePageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TemplatePageComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(TemplatePageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
