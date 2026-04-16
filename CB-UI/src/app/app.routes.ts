import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { LayoutComponent } from './components/layout/layout.component';
import { ExperienceSelectorComponent } from './components/experience-selector/experience-selector.component';
import { HomeComponent } from './components/home/home.component';
import { TemplatePageComponent } from './components/template-page/template-page.component';
import { ImportPageComponent } from './components/import-page/import-page.component';
import { UserMandatoryInfoComponent } from './components/user-mandatory-info/user-mandatory-info.component';

export const routes: Routes = [
    { path: '', component: LoginComponent },
    { path: 'home', component: HomeComponent },
    { path: 'experience', component: ExperienceSelectorComponent },
    { path: 'chat', component: LayoutComponent },
    { path: 'template', component: TemplatePageComponent},
    { path: 'import', component: ImportPageComponent },
    { path: 'user-info', component: UserMandatoryInfoComponent }
];
