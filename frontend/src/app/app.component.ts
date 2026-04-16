import { Component, OnInit, SecurityContext } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { DomSanitizer } from '@angular/platform-browser';

import { ConversationResponse, CvApiService, SessionResponse, TemplateOption, PersonalInfo } from './services/cv-api.service';
import { environment } from '../environments/environment';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface TemplateWithPreview extends TemplateOption {
  previewImageUrl?: string;
  isLoading?: boolean;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  userId = 'user-' + Math.random().toString(36).substr(2, 9);
  sessionId = '';
  message = '';
  llmPrompt = 'Im a software engineer with 5 years of experience in web development. Summarize my profile for a CV.';

  conversationHistory: Message[] = [];
  assistantReply = '';
  transcript = '';
  llmOutput = '';
  errorMessage = '';
  missingFields: string[] = [];
  loading = false;
  recording = false;
  sidebarOpen = false;
  showSummaryForm = false;
  showCvPreview = false;
  showTemplateModal = false;
  showPersonalInfoModal = false;
  pendingExportFormat: 'pdf' | 'docx' | 'pptx' | 'json' | null = null;
  cvData: any = null;
  templates: TemplateWithPreview[] = [];
  selectedTemplateId: string | null = null;

  // Personal info form fields
  personalFullName = '';
  personalEmail = '';
  personalPhone = '';
  personalLocation = '';
  personalSummary = '';
  personalSkills: string[] = [];
  personalSkillsInput = '';
  
  // Form validation errors
  formErrors: { [key: string]: string } = {
    fullName: '',
    email: ''
  };

  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];

  constructor(private readonly api: CvApiService, private readonly http: HttpClient, private readonly sanitizer: DomSanitizer) {}

  ngOnInit(): void {
    this.createSessionOnLoad();
  }

  hasAssistantMessages(): boolean {
    return this.conversationHistory.some(m => m.role === 'assistant');
  }

  private createSessionOnLoad(): void {
    this.loading = true;
    this.errorMessage = '';
    this.api.createSession(this.userId).subscribe({
      next: (res: SessionResponse) => {
        this.sessionId = res.sessionId;
        this.loading = false;
        // Add an initial greeting to conversation
        this.conversationHistory.push({
          role: 'assistant',
          content: "Hello! I'm your AI CV Assistant. Let's build your professional CV together. Upload a resume or say Hi to continue!",
          timestamp: new Date(),
        });
      },
      error: () => {
        this.errorMessage = 'Failed to create session. Please refresh the page.';
        this.loading = false;
      },
    });
  }

  sendMessage(): void {
    if (!this.sessionId || !this.message.trim()) {
      return;
    }

    const userMessage = this.message.trim();
    // Add user message to conversation
    this.conversationHistory.push({
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
    });

    this.loading = true;
    this.errorMessage = '';
    this.api.sendMessage(this.sessionId, userMessage).subscribe({
      next: (res: ConversationResponse) => {
        this.assistantReply = res.reply;
        // Add assistant reply to conversation
        this.conversationHistory.push({
          role: 'assistant',
          content: this.assistantReply,
          timestamp: new Date(),
        });
        this.transcript = '';
        this.missingFields = res.missingFields;
        this.cvData = (res as any).cvDraft || null;
        this.message = '';
        
        // Show personal info modal if indicated
        if (res.showPersonalInfoModal) {
          this.showPersonalInfoModal = true;
        }
        
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to send message.';
        this.loading = false;
      },
    });
  }

  async toggleRecording(): Promise<void> {
    if (this.recording) {
      this.stopRecording();
      return;
    }

    if (!this.sessionId) {
      this.errorMessage = 'Create a session before recording.';
      return;
    }

    await this.startRecording();
  }

  private async startRecording(): Promise<void> {
    this.errorMessage = '';
    this.audioChunks = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);

      this.mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        const mimeType = this.audioChunks[0]?.type || 'audio/webm';
        const audioBlob = new Blob(this.audioChunks, { type: mimeType });
        this.recording = false;

        // Release microphone access after each recording.
        this.mediaRecorder?.stream.getTracks().forEach((track) => track.stop());
        this.mediaRecorder = null;

        if (audioBlob.size > 0) {
          this.sendVoiceMessage(audioBlob);
        }
      };

      this.mediaRecorder.start();
      this.recording = true;
    } catch {
      this.errorMessage = 'Microphone access failed. Check browser permissions.';
      this.recording = false;
    }
  }

  private stopRecording(): void {
    if (this.mediaRecorder && this.recording) {
      this.mediaRecorder.stop();
    }
  }

  private sendVoiceMessage(audioBlob: Blob): void {
    this.loading = true;
    this.errorMessage = '';

    this.api.sendVoiceMessage(this.sessionId, audioBlob).subscribe({
      next: (res: ConversationResponse) => {
        this.transcript = res.transcript ?? '';
        this.assistantReply = res.reply;
        
        // Add voice message and reply to conversation
        this.conversationHistory.push({
          role: 'user',
          content: this.transcript,
          timestamp: new Date(),
        });
        this.conversationHistory.push({
          role: 'assistant',
          content: this.assistantReply,
          timestamp: new Date(),
        });

        this.missingFields = res.missingFields;
        this.cvData = (res as any).cvDraft || null;
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to process voice message.';
        this.loading = false;
      },
    });
  }

  testLlm(): void {
    if (!this.llmPrompt.trim()) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.api.testLlm(this.llmPrompt).subscribe({
      next: (res: { model: string; output: string }) => {
        this.llmOutput = res.output;
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'LLM test call failed.';
        this.loading = false;
      },
    });
  }

  toggleSummaryForm(): void {
    this.showSummaryForm = !this.showSummaryForm;
    this.llmOutput = '';
  }

  formatFieldName(field: string): string {
    // Convert "personalInfo.fullName" to "Full Name"
    // Remove the prefix (personalInfo., experience., etc.)
    const fieldName = field.split('.').pop() || field;
    
    // Convert camelCase to Title Case
    return fieldName
      .replace(/([A-Z])/g, ' $1') // Insert space before capitals
      .replace(/^./, (c) => c.toUpperCase()) // Capitalize first letter
      .trim();
  }

  playAssistantReply(): void {
    if (!this.assistantReply.trim()) {
      this.errorMessage = 'No assistant message to play.';
      return;
    }
  }

  exportCv(format: 'pdf' | 'docx' | 'pptx' | 'json'): void {
    if (!this.sessionId) {
      this.errorMessage = 'No active session to export.';
      return;
    }

    if (!this.cvData) {
      this.errorMessage = 'No CV data to export. Continue the conversation to gather information.';
      return;
    }

    // Show preview instead of immediate download
    this.showCvPreview = true;
    this.pendingExportFormat = format;
    this.errorMessage = '';
  }

  downloadCv(): void {
    if (!this.sessionId || !this.pendingExportFormat) {
      this.errorMessage = 'Export session lost. Please try again.';
      return;
    }

    const format = this.pendingExportFormat;
    this.loading = true;
    this.errorMessage = '';
    this.api.exportCv(this.sessionId, format).subscribe({
      next: (res: { jobId: string; downloadUrl: string }) => {
        this.downloadFile(res.downloadUrl, format);
        this.showCvPreview = false;
        this.pendingExportFormat = null;
        this.loading = false;
      },
      error: () => {
        this.errorMessage = `Failed to export CV as ${format.toUpperCase()}.`;
        this.loading = false;
      },
    });
  }

  closeCvPreview(): void {
    this.showCvPreview = false;
    this.pendingExportFormat = null;
    this.errorMessage = '';
  }

  private downloadFile(downloadUrl: string, format: string): void {
    // Extract file ID from the download URL (e.g., /api/download/file-id)
    const fileId = downloadUrl.split('/').pop();
    if (!fileId) {
      this.errorMessage = 'Invalid download URL.';
      return;
    }

    this.api.downloadFile(fileId).subscribe({
      next: (blob: Blob) => {
        const filename = `resume.${format}`;
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      },
      error: () => {
        this.errorMessage = `Failed to download ${format.toUpperCase()} file.`;
      },
    });
  }

  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }

  onFileUpload(event: Event): void {
    const input = event.target as HTMLInputElement;
    const files = input.files;

    if (!files || files.length === 0) {
      return;
    }

    const file = files[0];
    
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
      this.errorMessage = 'Invalid file type. Please upload PDF, DOCX, or TXT file.';
      return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      this.errorMessage = 'File size exceeds 10MB limit.';
      return;
    }

    this.uploadFile(file);
    
    // Reset input
    input.value = '';
  }

  private uploadFile(file: File): void {
    if (!this.sessionId) {
      this.errorMessage = 'Please start a new chat session first.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    const formData = new FormData();
    formData.append('file', file);
    formData.append('sessionId', this.sessionId);

    this.http.post<any>(`${environment.apiBaseUrl}/upload/cv`, formData).subscribe({
      next: (response: any) => {
        // Update CV data if available
        if (response.extracted_data) {
          const header = response.extracted_data.header || {};
          const skills = response.extracted_data.technicalSkills || {};
          const experience = response.extracted_data.workExperience || [];
          
          this.cvData = { 
            ...this.cvData,
            personalInfo: {
              fullName: header.fullName || '',
              email: header.email || '',
              phone: header.phone || '',
              location: header.location || '',
              linkedin: header.linkedin || '',
              summary: Array.isArray(response.extracted_data.professionalSummary)
                ? response.extracted_data.professionalSummary.join(' ')
                : (response.extracted_data.professionalSummary || ''),
            },
            skills: this.extractSkillsFromTechnical(skills),
            experience: experience,
          };

          // Send extracted CV data to conversation service for LLM processing
          this.sendExtractedCvToConversation(response.extracted_data);
        } else {
          this.loading = false;
          this.errorMessage = 'No data extracted from resume.';
        }
      },
      error: (error) => {
        this.loading = false;
        const errorMsg = error.error?.detail || error.error?.message || 'Failed to upload resume. Please try again.';
        this.errorMessage = `Upload failed: ${errorMsg}`;
        
        this.conversationHistory.push({
          role: 'assistant',
          content: `❌ ${errorMsg}`,
          timestamp: new Date(),
        });
        
        this.scrollToBottom();
      },
    });
  }

  private sendExtractedCvToConversation(extractedData: any): void {
    // Format extracted CV data as a structured message for the LLM
    const cvMessage = this.formatCvDataAsMessage(extractedData);

    // Add user message to conversation history
    this.conversationHistory.push({
      role: 'user',
      content: `📄 Resume uploaded\n\n${cvMessage}`,
      timestamp: new Date(),
    });

    // Send to conversation endpoint for LLM processing
    this.api.sendMessage(this.sessionId, cvMessage).subscribe({
      next: (res: ConversationResponse) => {
        // Add LLM response to conversation
        this.conversationHistory.push({
          role: 'assistant',
          content: res.reply,
          timestamp: new Date(),
        });

        this.transcript = '';
        this.missingFields = res.missingFields;
        this.message = '';
        this.loading = false;

        // Show personal info modal if indicated
        if (res.showPersonalInfoModal) {
          this.showPersonalInfoModal = true;
        }

        this.scrollToBottom();
      },
      error: (error) => {
        this.loading = false;
        const errorMsg = error.error?.detail || error.error?.message || 'Failed to process resume.';
        this.errorMessage = `Processing failed: ${errorMsg}`;
        
        this.conversationHistory.push({
          role: 'assistant',
          content: `❌ ${errorMsg}`,
          timestamp: new Date(),
        });
        
        this.scrollToBottom();
      },
    });
  }

  private formatCvDataAsMessage(data: any): string {
    const lines: string[] = [];

    // Header (personal info)
    const header = data.header || {};
    if (header.fullName || header.email) {
      lines.push('**Extracted Resume Information:**');
      lines.push('');
      if (header.fullName) lines.push(`**Name:** ${header.fullName}`);
      if (header.jobTitle) lines.push(`**Current Title:** ${header.jobTitle}`);
      if (header.email) lines.push(`**Email:** ${header.email}`);
      if (header.phone) lines.push(`**Phone:** ${header.phone}`);
      if (header.location) lines.push(`**Location:** ${header.location}`);
      lines.push('');
    }

    // Professional summary
    const summary = data.professionalSummary || [];
    if (Array.isArray(summary) && summary.length > 0) {
      lines.push('**Professional Summary:**');
      summary.forEach((s: string) => lines.push(`• ${s}`));
      lines.push('');
    }

    // Technical skills
    const skills = data.technicalSkills || {};
    const primarySkills = skills.primary || [];
    if (primarySkills.length > 0) {
      lines.push('**Primary Skills:** ' + primarySkills.map((s: any) => s.skill_name || s).join(', '));
    }
    const secondarySkills = skills.secondary || [];
    if (secondarySkills.length > 0) {
      lines.push('**Secondary Skills:** ' + secondarySkills.map((s: any) => s.skill_name || s).join(', '));
      lines.push('');
    }

    // Work experience
    const experience = data.workExperience || [];
    if (experience.length > 0) {
      lines.push('**Work Experience:**');
      experience.forEach((exp: any, index: number) => {
        lines.push(`${index + 1}. **${exp.position}** at ${exp.employer} (${exp.duration || 'N/A'})`);
        if (exp.project_description) {
          lines.push(`   ${exp.project_description}`);
        }
      });
    }

    return lines.join('\n');
  }

  private extractSkillsFromTechnical(technicalSkills: any): string[] {
    const skills: string[] = [];
    
    if (technicalSkills.primary) {
      technicalSkills.primary.forEach((skill: any) => {
        if (typeof skill === 'string') {
          skills.push(skill);
        } else if (skill.skill_name) {
          skills.push(skill.skill_name);
        }
      });
    }
    
    if (technicalSkills.secondary) {
      technicalSkills.secondary.forEach((skill: any) => {
        if (typeof skill === 'string') {
          skills.push(skill);
        } else if (skill.skill_name) {
          skills.push(skill.skill_name);
        }
      });
    }
    
    return skills;
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      const messagesContainer = document.querySelector('.chat-main');
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 100);
  }



  showTemplateSelector(): void {
    if (!this.sessionId) {
      this.errorMessage = 'Create a session before selecting a template.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.api.getTemplates().subscribe({
      next: (res: any) => {
        this.templates = res.templates;
        // Generate previews for all templates
        this.generateTemplatePreview();
        this.showTemplateModal = true;
        this.selectedTemplateId = null;
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to load templates.';
        this.loading = false;
      },
    });
  }

  private generateTemplatePreview(): void {
    this.templates.forEach((template: TemplateWithPreview) => {
      template.isLoading = true;
      
      // First check if backend provided a preview image
      if (template.previewImageUrl) {
        template.isLoading = false;
        return;
      }
      
      if (template.previewImageBase64) {
        try {
          template.previewImageUrl = `data:image/png;base64,${template.previewImageBase64}`;
          template.isLoading = false;
          return;
        } catch (error) {
          console.error('Error processing preview image:', error);
        }
      }
      
      // Fallback: Generate preview from template file
      if (template.fileBase64) {
        try {
          const byteCharacters = atob(template.fileBase64);
          const byteNumbers = new Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }
          const byteArray = new Uint8Array(byteNumbers);
          const blob = new Blob([byteArray], { type: this.getMimeType(template.fileType) });

          // Generate preview based on file type
          if (template.fileType === 'docx') {
            this.generateDocxPreview(blob, template);
          } else if (template.fileType === 'pptx') {
            this.generatePptxPreview(blob, template);
          } else {
            this.setDefaultPreview(template);
          }
        } catch (error) {
          console.error('Error generating preview:', error);
          this.setDefaultPreview(template);
        }
      } else {
        this.setDefaultPreview(template);
      }
    });
  }

  private getMimeType(fileType: string): string {
    const mimeTypes: { [key: string]: string } = {
      'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    };
    return mimeTypes[fileType] || 'application/octet-stream';
  }

  private generateDocxPreview(blob: Blob, template: TemplateWithPreview): void {
    // Use a temporary div to render the docx preview
    const tempDiv = document.createElement('div');
    tempDiv.style.width = '100%';
    tempDiv.style.height = '300px';
    tempDiv.style.overflow = 'hidden';

    // Import docx-preview dynamically
    import('docx-preview').then((module) => {
      module.renderAsync(blob, tempDiv).then(() => {
        // Convert the rendered content to a canvas and then to an image
        this.convertDivToImage(tempDiv, template);
      }).catch((error) => {
        console.error('Error rendering docx:', error);
        this.setDefaultPreview(template);
      });
    }).catch(() => {
      this.setDefaultPreview(template);
    });
  }

  private convertDivToImage(element: HTMLElement, template: TemplateWithPreview): void {
    try {
      // Use html2canvas if available, otherwise use a canvas approach
      const canvas = document.createElement('canvas');
      canvas.width = 280;
      canvas.height = 300;
      const ctx = canvas.getContext('2d');
      
      if (ctx) {
        // Create a gradient background to simulate document preview
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, '#f5f5f5');
        gradient.addColorStop(1, '#e8e8e8');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 280, 300);

        // Add border
        ctx.strokeStyle = '#ccc';
        ctx.lineWidth = 1;
        ctx.strokeRect(0, 0, 280, 300);

        // Add text
        ctx.fillStyle = '#333';
        ctx.font = 'bold 14px Arial';
        ctx.fillText('DOCX Preview', 10, 30);
        ctx.font = '12px Arial';
        ctx.fillText(template.templateName, 10, 50);
        
        template.previewImageUrl = canvas.toDataURL('image/png');
      }
      template.isLoading = false;
    } catch (error) {
      console.error('Error converting to image:', error);
      this.setDefaultPreview(template);
    }
  }

  private generatePptxPreview(blob: Blob, template: TemplateWithPreview): void {
    // For PPTX, create a simple preview since we need a library to properly extract slides
    const canvas = document.createElement('canvas');
    canvas.width = 280;
    canvas.height = 300;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
      // Create a gradient background
      const gradient = ctx.createLinearGradient(0, 0, 0, 300);
      gradient.addColorStop(0, '#e8f5e9');
      gradient.addColorStop(1, '#c8e6c9');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 280, 300);

      // Add border
      ctx.strokeStyle = '#66bb6a';
      ctx.lineWidth = 2;
      ctx.strokeRect(0, 0, 280, 300);

      // Add presentation icon and text
      ctx.fillStyle = '#333';
      ctx.font = 'bold 14px Arial';
      ctx.fillText('PPTX Preview', 10, 30);
      ctx.font = '12px Arial';
      ctx.fillText(template.templateName, 10, 50);
      ctx.fillText('Presentation File', 10, 80);
      
      // Draw slides indicator
      ctx.fillStyle = '#fff';
      ctx.fillRect(10, 100, 120, 80);
      ctx.fillRect(150, 100, 120, 80);
      
      ctx.fillStyle = '#66bb6a';
      ctx.font = '10px Arial';
      ctx.fillText('Slide 1', 50, 145);
      ctx.fillText('Slide 2', 190, 145);

      template.previewImageUrl = canvas.toDataURL('image/png');
    }
    template.isLoading = false;
  }

  private setDefaultPreview(template: TemplateWithPreview): void {
    // Create a default preview canvas
    const canvas = document.createElement('canvas');
    canvas.width = 280;
    canvas.height = 300;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
      const gradient = ctx.createLinearGradient(0, 0, 0, 300);
      gradient.addColorStop(0, '#f0f0f0');
      gradient.addColorStop(1, '#d9d9d9');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 280, 300);

      ctx.strokeStyle = '#999';
      ctx.lineWidth = 1;
      ctx.strokeRect(0, 0, 280, 300);

      ctx.fillStyle = '#666';
      ctx.font = 'bold 14px Arial';
      ctx.fillText('Template Preview', 10, 30);
      ctx.font = '12px Arial';
      ctx.fillText(template.templateName, 10, 50);
      ctx.fillText(template.fileType.toUpperCase(), 10, 70);

      template.previewImageUrl = canvas.toDataURL('image/png');
    }
    template.isLoading = false;
  }

  selectTemplate(): void {
    if (!this.sessionId || !this.selectedTemplateId) {
      this.errorMessage = 'Please select a template first.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.api.selectTemplate(this.sessionId, this.selectedTemplateId).subscribe({
      next: () => {
        this.showTemplateModal = false;
        this.errorMessage = '';
        this.loading = false;
        this.conversationHistory.push({
          role: 'assistant',
          content: `Template "${this.selectedTemplateId}" has been selected for your CV.`,
          timestamp: new Date(),
        });
      },
      error: () => {
        this.errorMessage = 'Failed to select template.';
        this.loading = false;
      },
    });
  }

  closeTemplateModal(): void {
    this.showTemplateModal = false;
    this.selectedTemplateId = null;
    this.errorMessage = '';
  }

  addSkill(): void {
    if (this.personalSkillsInput.trim()) {
      this.personalSkills.push(this.personalSkillsInput.trim());
      this.personalSkillsInput = '';
    }
  }

  removeSkill(index: number): void {
    this.personalSkills.splice(index, 1);
  }

  submitPersonalInfo(): void {
    // Clear previous errors
    this.formErrors = { fullName: '', email: '' };
    
    // Validate form
    let isValid = true;
    
    if (!this.personalFullName.trim()) {
      this.formErrors.fullName = 'Full name is required';
      isValid = false;
    }
    
    if (!this.personalEmail.trim()) {
      this.formErrors.email = 'Email is required';
      isValid = false;
    } else if (!this.isValidEmail(this.personalEmail)) {
      this.formErrors.email = 'Please enter a valid email address';
      isValid = false;
    }
    
    if (!isValid) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.api.submitPersonalInfo(
      this.sessionId,
      this.personalFullName,
      this.personalEmail,
      this.personalPhone,
      this.personalLocation,
      this.personalSummary,
      this.personalSkills
    ).subscribe({
      next: (res: ConversationResponse) => {
        this.assistantReply = res.reply;
        this.conversationHistory.push({
          role: 'assistant',
          content: this.assistantReply,
          timestamp: new Date(),
        });
        this.missingFields = res.missingFields;
        this.cvData = (res as any).cvDraft || null;
        this.showPersonalInfoModal = false;
        
        // Clear form
        this.personalFullName = '';
        this.personalEmail = '';
        this.personalPhone = '';
        this.personalLocation = '';
        this.personalSummary = '';
        this.personalSkills = [];
        this.personalSkillsInput = '';
        this.formErrors = { fullName: '', email: '' };
        
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to save personal information.';
        this.loading = false;
      },
    });
  }

  validateEmail(): void {
    if (!this.personalEmail.trim()) {
      this.formErrors.email = 'Email is required';
    } else if (!this.isValidEmail(this.personalEmail)) {
      this.formErrors.email = 'Please enter a valid email address';
    } else {
      this.formErrors.email = '';
    }
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  closePersonalInfoModal(): void {
    this.showPersonalInfoModal = false;
    this.errorMessage = '';
  }

  createNewSession(): void {
    this.sessionId = '';
    this.message = '';
    this.conversationHistory = [];
    this.transcript = '';
    this.assistantReply = '';
    this.errorMessage = '';
    this.cvData = null;
    this.sidebarOpen = false;
    this.createSessionOnLoad();
  }
}
