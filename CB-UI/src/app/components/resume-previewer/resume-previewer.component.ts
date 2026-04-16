import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-resume-previewer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './resume-previewer.component.html',
  styleUrl: './resume-previewer.component.scss'
})
export class ResumePreviewerComponent {
 showPreview = false;
 @Output() resetTemplate: EventEmitter<void> = new EventEmitter<void>;

 constructor() { 
  console.log('ResumePreviewerComponent initialized');
 }

 reset() {
  this.resetTemplate.emit()
 }
}
