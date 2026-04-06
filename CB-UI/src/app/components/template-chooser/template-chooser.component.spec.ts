import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TemplateChooserComponent } from './template-chooser.component';

describe('TemplateChooserComponent', () => {
  let component: TemplateChooserComponent;
  let fixture: ComponentFixture<TemplateChooserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TemplateChooserComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(TemplateChooserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
