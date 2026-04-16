import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-experience-selector',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './experience-selector.component.html',
  styleUrl: './experience-selector.component.scss'
})
export class ExperienceSelectorComponent {

  experienceOptions = ['Fresher', '1 Year', '2 Years', '3 Years']; 
  selectedExperience: string = '';
  customExperience: string = '';

  selectExperience(exp: string) { 
    this.selectedExperience = exp; 
  }

  goToTemplateSelectionPage() {

  }

}
