import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { ChatbotService } from '../../services/chatbot.service';
import { SessionCreateRequest } from '../../models/SessionCreateRequest';
import { SessionCreateResponse } from '../../models/SessionCreateResponse';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  providers: [ChatbotService],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  portalId: string = '';

  constructor(private router: Router, private chatbotService: ChatbotService) {
    // const savedPortalId = sessionStorage.getItem('portalId');
    // const savedSessionId = sessionStorage.getItem('sessionId');
    // if (savedPortalId && savedPortalId.length > 0 && savedSessionId && savedSessionId.length > 0) {
    //   this.router.navigate(['/chat']);
    // }
  }

  login() {
    if (this.portalId && this.portalId?.length > 0) {
      sessionStorage.setItem('portalId', this.portalId);
      const sessionCreateRequest: SessionCreateRequest = {
        userId: this.portalId
      };
      this.chatbotService.sessionCreate(sessionCreateRequest).subscribe({
        next: (session: SessionCreateResponse) => {
          sessionStorage.setItem('sessionId', session.sessionId);
          this.router.navigate(['/chat']);
        },
        error: (err) => {
          alert('Failed to create session. Please try again.');
        }
      });
    }
  }

}
