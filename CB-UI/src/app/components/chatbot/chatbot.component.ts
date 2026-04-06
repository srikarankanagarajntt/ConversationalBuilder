import { ChangeDetectorRef, Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';
import { Message } from '../../models/Message';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ResumePreviewerComponent } from '../resume-previewer/resume-previewer.component';
import { TemplateChooserComponent } from '../template-chooser/template-chooser.component';

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule, TemplateChooserComponent, ResumePreviewerComponent],
  templateUrl: './chatbot.component.html',
  styleUrl: './chatbot.component.scss'
})
export class ChatbotComponent {
  messages: Message[] = [];
  input: string = '';

  showTemplate = false;
  showPreview = false;

  selected: any = null;

  mediaRecorder!: MediaRecorder;
  audioChunks: Blob[] = [];
  isRecordingInProgress: boolean = false
  @ViewChild('messageArea', { static: false }) messageArea!: ElementRef;

  @Output() newMessageAdded: EventEmitter<void> = new EventEmitter()

  constructor(private cdr: ChangeDetectorRef) { }

  selectTemplate(t: any) {
    this.selected = t;
  }

  confirmTemplate(selectedTemplate: any) {
    this.showTemplate = false;

    setTimeout(() => {
      this.showPreview = true;
    }, 800);
  }

  send() {
    if (!this.input) return;
    this.messages.push({ type: 'sender', text: this.input });
    this.input = '';

    // simulate backends
    setTimeout(() => {
      this.messages.push({ type: 'receiver', text: 'Got it! Please wait while I process...' });
      setTimeout(() => {
        this.messageArea.nativeElement.scrollTop = this.messageArea.nativeElement.scrollHeight
      }, 100);
    }, 500);

  }

  onFileUpload(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.messages.push({ type: 'sender', text: '📄 ' + file.name });
    }
  }

  recordVoice() {
    if (this.isRecordingInProgress) {
      this.isRecordingInProgress = false;
      this.stopRecording();
    } else {
      this.isRecordingInProgress = true;
      this.startRecording();
    }
  }

  async startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    this.mediaRecorder = new MediaRecorder(stream);

    this.mediaRecorder.ondataavailable = (event) => {
      this.audioChunks.push(event.data);
    };

    this.mediaRecorder.start();
  }

  stopRecording() {
    this.mediaRecorder.stop();

    this.mediaRecorder.onstop = () => {
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
      this.audioChunks = [];
      this.sendAudioToBackend(audioBlob);
    };
  }

  sendAudioToBackend(audioBlob: Blob) {
    const formData = new FormData();
    formData.append('file', audioBlob, 'voice.webm');

    this.messages.push({ type: 'sender', text: 'Audio recording added' });
    this.newMessageAdded.emit();

    setTimeout(() => {
      this.messages.push({ type: 'receiver', text: 'Got it! Please wait while I process...' });
      this.cdr.detectChanges();
      setTimeout(() => {
        this.messageArea.nativeElement.scrollTop = this.messageArea.nativeElement.scrollHeight
      }, 200);
    }, 500);

    this.cdr.detectChanges();

    // Example API call
    // this.http.post('/api/upload-audio', formData).subscribe(res => {
    //   console.log(res);
    // });
  }


  reset() {
    this.showPreview = false;
    this.selected = null;
    this.messages = [];
  }
}
