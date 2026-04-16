import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-user-mandatory-info',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-mandatory-info.component.html',
  styleUrl: './user-mandatory-info.component.scss'
})
export class UserMandatoryInfoComponent {

  user: any = {};

  constructor(private router: Router) {}

  goToChat() {
    this.router.navigate(['/chat'])
  }
}
