import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExperienceSelectorComponent } from './experience-selector.component';

describe('ExperienceSelectorComponent', () => {
  let component: ExperienceSelectorComponent;
  let fixture: ComponentFixture<ExperienceSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ExperienceSelectorComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ExperienceSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
