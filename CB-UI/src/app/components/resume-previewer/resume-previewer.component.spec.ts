import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResumePreviewerComponent } from './resume-previewer.component';

describe('ResumePreviewerComponent', () => {
  let component: ResumePreviewerComponent;
  let fixture: ComponentFixture<ResumePreviewerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResumePreviewerComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ResumePreviewerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
