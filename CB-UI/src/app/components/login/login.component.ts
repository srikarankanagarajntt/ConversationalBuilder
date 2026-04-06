import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  portalId: string = '';

  constructor(private router: Router) {
    if (sessionStorage.getItem('portalId')) {
      this.portalId = JSON.stringify(sessionStorage.getItem('portalId'));
      this.router.navigate(['/chat']);
    }
  }

  login() {
    if (this.portalId && this.portalId?.length > 0) {
      sessionStorage.setItem('portalId', this.portalId);
      this.router.navigate(['/chat']);
    }
  }

}
