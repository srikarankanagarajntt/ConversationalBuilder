import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {

  constructor(private router: Router) { }

  templates = [{ name: 'Modern' }, { name: 'Professional' }, { name: 'Minimal' }, { name: 'Creative' }, { name: 'Elegant' }, { name: 'Sleek' }];
  selectedTemplate!: { name: string };


  startFlow() {
    //this.currentScreen = 'experience';
    this.router.navigate(['/template']);
  }

  carouselIndex = 0;

  ngOnInit() {
    setInterval(() => {
      this.carouselIndex = (this.carouselIndex + 1) % 3;
    }, 2000); // change every 2 seconds
  }

  getClass(index: number) {
    const pos = (index - this.carouselIndex + 3) % 3;

    if (pos === 0) return 'carousel-center';
    if (pos === 1) return 'carousel-right';
    return 'carousel-left';
  }

  confirmTemplate() {
   // this.showTemplate = false;
   // this.toggleTemplateModal.emit(this.selectedTemplate)
  }

  selectTemplate(t: any) { 
    this.selectedTemplate = t; 
  }

}
