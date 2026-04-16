import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-template-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './template-page.component.html',
  styleUrl: './template-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class TemplatePageComponent {

  constructor(private router: Router) { }

  templates = [{ name: 'Modern' }, { name: 'Professional' }, { name: 'Minimal' }];
  selected = { name: 'Modern' };

  selectTemplate(t: any) {
    this.selected = t;
    console.log('Selected template:', t);
  }

  confirmTemplate() {
    //     this.showTemplate = false;

    // setTimeout(() => {
    //   this.showPreview = true;
    // }, 800);
    this.router.navigate(['/import']);
  }

  goToImportScreen() {
    this.router.navigate(['/import']);
  }

}
