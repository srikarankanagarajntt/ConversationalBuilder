export interface PreviewResponse {
    sessionId: string;
    templateId: string;
    previewData: PreviewData;
}

export interface PreviewData {
    sessionId: string;
    meta: Meta;
    header: Header;
    professionalSummary: string[];
    technicalSkills: TechnicalSkills;
    currentResponsibilities: string[];
    workExperience: WorkExperience[];
    personalDetails: PersonalDetails;
    declaration: Declaration;
}

export interface Meta {
    templateVersion: string;
    sourceType: string;
    language: string;
    lastUpdated: string;
}

export interface Header {
    fullName: string;
    portalId: string;
    headline: string;
    jobTitle: string;
    location: Location;
    contact: Contact;
    personal: Personal;
}

export interface Location {
    companyName: string;
    addressLine1: string;
    addressLine2: string;
    city: string;
    postalCode: string;
    country: string;
}

export interface Contact {
    phoneNumber: string;
    emailId: string;
    officialEmailId: string;
}

export interface Personal {
    nationality: string;
}

export interface TechnicalSkills {
    primary: Skill[];
    secondary: Skill[];
}

export interface Skill {
    skillName: string;
    category: string;
    proficiency: string;
}

export interface WorkExperience {
    employer: string;
    employmentPeriod: EmploymentPeriod;
    position: string;
    projectTitle: string;
    client: string;
    technology: string[];
    projectDescription: string;
    responsibilities: string[];
}

export interface EmploymentPeriod {
    start: string;
    end: string;
    displayText: string;
}

export interface PersonalDetails {
    languagesKnown: string[];
    permanentAddress: string;
}

export interface Declaration {
    statement: string;
    place: string;
    signatureName: string;
}