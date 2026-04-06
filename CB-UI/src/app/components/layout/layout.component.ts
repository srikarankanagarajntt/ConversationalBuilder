import { ChangeDetectorRef, Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatbotComponent } from '../chatbot/chatbot.component';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, ChatbotComponent],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss'
})
export class LayoutComponent {

  collapsed = false;
  history = ['Resume 1', 'Resume 2'];
  portalId: string = '';

  @ViewChild('chatbot', { static: false }) chatbot!: ChatbotComponent;

  constructor(private cdr: ChangeDetectorRef) {
    this.portalId = JSON.stringify(sessionStorage.getItem('portalId'))?.toUpperCase();
  }

  onNewMessageAdded() {
    this.cdr.detectChanges();
  }
}
