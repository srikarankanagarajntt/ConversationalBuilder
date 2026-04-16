import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserMandatoryInfoComponent } from './user-mandatory-info.component';

describe('UserMandatoryInfoComponent', () => {
  let component: UserMandatoryInfoComponent;
  let fixture: ComponentFixture<UserMandatoryInfoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserMandatoryInfoComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(UserMandatoryInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
