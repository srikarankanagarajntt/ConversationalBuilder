import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-import-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './import-page.component.html',
  styleUrl: './import-page.component.scss'
})
export class ImportPageComponent {
  importChoice = 'upload'; // default choice

  constructor(private router: Router) { }

  onFileUpload(event: any) {
    const file = event.target.files[0];
    this.router.navigate(['/chat']);
  }

  goToTemplateScreen() {
    this.router.navigate(['/template']);
  }

  goToChatScreen() {
    // Logic to navigate to chat screen
    this.router.navigate(['/user-info']);
  }
}
