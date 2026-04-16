import { ChangeDetectorRef, Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatbotComponent } from '../chatbot/chatbot.component';
import { ChatbotService } from '../../services/chatbot.service';
import { Session } from '../../models/Session';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, ChatbotComponent],
  providers: [ChatbotService],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss'
})
export class LayoutComponent {

  collapsed = false;
  history = ['Resume 1', 'Resume 2'];
  portalId: string = '';
  sessionId: string = '';

  @ViewChild('chatbot', { static: false }) chatbot!: ChatbotComponent;

  constructor(private cdr: ChangeDetectorRef, private chatbotService: ChatbotService) {
    this.portalId = JSON.stringify(sessionStorage.getItem('portalId'))?.toUpperCase();
    this.sessionId = JSON.stringify(sessionStorage.getItem('sessionId'));
  }

  onNewMessageAdded() {
    this.cdr.detectChanges();
  }

  getSession() {
    const sessionId = JSON.stringify(sessionStorage.getItem('sessionId'));
    this.chatbotService.sessionGet(sessionId).subscribe(
      (session: Session) => {
        console.log('Session data:', session);
      },
      (error) => {
        console.error('Error fetching session:', error);
      }
    );
  }
}
