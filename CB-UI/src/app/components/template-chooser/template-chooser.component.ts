import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-template-chooser',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './template-chooser.component.html',
  styleUrl: './template-chooser.component.scss'
})
export class TemplateChooserComponent {
  @Input() showTemplate: boolean = false;
  templates = [{ name: 'Modern' }, { name: 'Professional' }, { name: 'Minimal' }];
  selectedTemplate!: { name: string };

  @Output() toggleTemplateModal: EventEmitter<{name: string}> = new EventEmitter<{name: string}>();
  
  confirmTemplate() {
    this.showTemplate = false;
    this.toggleTemplateModal.emit(this.selectedTemplate)
  }

  selectTemplate(t: any) { 
    this.selectedTemplate = t; 
  }
}
